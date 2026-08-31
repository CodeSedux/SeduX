const EVENT_TYPES = new Set([
  'voice_chunk',
  'stt_result',
  'llm_chunk',
  'tts_audio',
  'avatar_update',
  'emotion_state',
]);

export function isStreamEvent(value) {
  return Boolean(
    value
    && value.version === 'v1'
    && EVENT_TYPES.has(value.type)
    && Number.isInteger(value.sequence)
    && value.sequence >= 0
    && typeof value.request_id === 'string'
    && value.payload
    && typeof value.payload === 'object',
  );
}

export class ReconnectingStream {
  constructor(url, { onEvent, onStatus = () => {}, maxRetries = 5, WebSocketImpl = globalThis.WebSocket } = {}) {
    this.url = url;
    this.onEvent = onEvent;
    this.onStatus = onStatus;
    this.maxRetries = maxRetries;
    this.WebSocketImpl = WebSocketImpl;
    this.retryCount = 0;
    this.socket = null;
    this.closed = false;
  }

  connect() {
    if (!this.WebSocketImpl || this.closed) return;
    this.onStatus('connecting');
    this.socket = new this.WebSocketImpl(this.url);
    this.socket.addEventListener('open', () => {
      this.retryCount = 0;
      this.onStatus('connected');
    });
    this.socket.addEventListener('message', (message) => {
      try {
        const event = JSON.parse(message.data);
        if (isStreamEvent(event)) this.onEvent?.(event);
      } catch {
        this.onStatus('invalid-event');
      }
    });
    this.socket.addEventListener('close', () => this.scheduleReconnect());
  }

  scheduleReconnect() {
    if (this.closed || this.retryCount >= this.maxRetries) {
      this.onStatus(this.closed ? 'closed' : 'unavailable');
      return;
    }
    const delay = Math.min(1000 * (2 ** this.retryCount), 30000);
    this.retryCount += 1;
    this.onStatus('reconnecting');
    globalThis.setTimeout(() => this.connect(), delay);
  }

  close() {
    this.closed = true;
    this.socket?.close();
  }
}