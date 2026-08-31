import unittest

from shared.conversation import ConversationService, MessageRole


class TextInteractionCoreTests(unittest.TestCase):
    def test_reminder_intent_parses_and_creates_task(self) -> None:
        service = ConversationService()
        conversation = service.create_conversation("user-42", "Daily review")

        response, assistant_message = service.send_message(
            conversation.conversation_id,
            "user-42",
            "Remind me tomorrow at 9 AM to review the project.",
        )

        self.assertEqual(response.tool_call.name, "task.create")
        self.assertEqual(assistant_message.role, MessageRole.ASSISTANT)
        self.assertIn("reminder", assistant_message.content.lower())

        tasks = service.task_manager.list("user-42")
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0].name, "Review the project")
        self.assertTrue(tasks[0].schedule.run_at)

    def test_general_chat_without_tool_call_returns_plain_response(self) -> None:
        service = ConversationService()
        conversation = service.create_conversation("user-2", "Random chat")

        response, assistant_message = service.send_message(
            conversation.conversation_id,
            "user-2",
            "How is the weather today?",
        )

        self.assertIsNone(response.tool_call)
        self.assertIn("weather", assistant_message.content.lower())

    def test_user_cannot_access_other_users_conversation(self) -> None:
        service = ConversationService()
        conversation = service.create_conversation("user-1", "Private")

        with self.assertRaises(PermissionError):
            service.send_message(conversation.conversation_id, "user-2", "Hello")


if __name__ == "__main__":
    unittest.main()
