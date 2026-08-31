from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum
import re
from uuid import uuid4

from shared.task_runtime import TaskManager
from shared.tasks import TaskDefinition, TaskSchedule, TaskState, TaskType


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


@dataclass(frozen=True)
class ToolCall:
    name: str
    arguments: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class ConversationMessage:
    message_id: str
    conversation_id: str
    user_id: str
    role: MessageRole
    content: str
    created_at: str


@dataclass
class Conversation:
    conversation_id: str
    user_id: str
    title: str
    messages: list[ConversationMessage] = field(default_factory=list)


@dataclass(frozen=True)
class ConversationResponse:
    tool_call: ToolCall | None
    assistant_message: ConversationMessage


class ConversationService:
    def __init__(self, task_manager: TaskManager | None = None) -> None:
        self._task_manager = task_manager or TaskManager()
        self._conversations: dict[str, Conversation] = {}

    @property
    def task_manager(self) -> TaskManager:
        return self._task_manager

    def create_conversation(self, user_id: str, title: str) -> Conversation:
        conversation_id = f"conversation-{uuid4().hex[:12]}"
        conversation = Conversation(conversation_id=conversation_id, user_id=user_id, title=title)
        self._conversations[conversation_id] = conversation
        return conversation

    def get_conversation(self, conversation_id: str, user_id: str) -> Conversation:
        conversation = self._conversations[conversation_id]
        if conversation.user_id != user_id:
            raise PermissionError("user does not have access to this conversation")
        return conversation

    def send_message(self, conversation_id: str, user_id: str, text: str) -> tuple[ConversationResponse, ConversationMessage]:
        conversation = self.get_conversation(conversation_id, user_id)
        self._append_message(
            conversation,
            user_id,
            MessageRole.USER,
            text,
        )

        if self._is_reminder_request(text):
            task_definition = self._create_reminder_task(conversation.user_id, text)
            tool_call = ToolCall(name="task.create", arguments={"task_id": task_definition.task_id, "user_id": task_definition.user_id})
            content = (
                f"Reminder created for {task_definition.name} at {task_definition.schedule.run_at}."
            )
            assistant_message = self._append_message(
                conversation,
                user_id,
                MessageRole.ASSISTANT,
                content,
            )
            return ConversationResponse(tool_call=tool_call, assistant_message=assistant_message), assistant_message

        content = f"I can help with that. You asked about: {text}"
        assistant_message = self._append_message(
            conversation,
            user_id,
            MessageRole.ASSISTANT,
            content,
        )
        return ConversationResponse(tool_call=None, assistant_message=assistant_message), assistant_message

    @staticmethod
    def _is_reminder_request(text: str) -> bool:
        lowered = text.lower()
        return "remind" in lowered or "reminder" in lowered

    @staticmethod
    def _parse_reminder_text(text: str) -> tuple[str, datetime]:
        scheduled_time = _next_time_for_reminder(text)
        task_name = _extract_task_name(text)
        return task_name, scheduled_time

    def _create_reminder_task(self, user_id: str, text: str) -> TaskDefinition:
        task_name, scheduled_time = self._parse_reminder_text(text)
        task_definition = TaskDefinition(
            task_id=f"task-{uuid4().hex[:12]}",
            user_id=user_id,
            name=task_name,
            type=TaskType.REMINDER,
            state=TaskState.QUEUED,
            schedule=TaskSchedule(run_at=scheduled_time.isoformat(), timezone="UTC"),
            payload={"source": "conversation", "raw_message": text},
        )
        self._task_manager.create(task_definition)
        return task_definition

    @staticmethod
    def _append_message(conversation: Conversation, user_id: str, role: MessageRole, content: str) -> ConversationMessage:
        message = ConversationMessage(
            message_id=f"message-{uuid4().hex[:12]}",
            conversation_id=conversation.conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            created_at=datetime.now(UTC).isoformat(),
        )
        conversation.messages.append(message)
        return message


def _next_time_for_reminder(text: str) -> datetime:
    now = datetime.now(UTC)
    lowered = text.lower()
    if "tomorrow" in lowered:
        base = now + timedelta(days=1)
    else:
        base = now

    match = re.search(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", lowered)
    if match:
        hour = int(match.group(1))
        minute = int(match.group(2) or 0)
        if match.group(3):
            suffix = match.group(3).lower()
            if suffix == "pm" and hour != 12:
                hour += 12
            if suffix == "am" and hour == 12:
                hour = 0
        if hour > 23 or minute > 59:
            hour = 9
            minute = 0
        return base.replace(hour=hour, minute=minute, second=0, microsecond=0)

    return base.replace(hour=9, minute=0, second=0, microsecond=0)


def _extract_task_name(text: str) -> str:
    match = re.search(r"to\s+(.+?)(?:\.|$)", text, flags=re.IGNORECASE)
    if not match:
        return "Reminder"
    name = match.group(1).strip()
    if not name:
        return "Reminder"
    return name[0].upper() + name[1:]
