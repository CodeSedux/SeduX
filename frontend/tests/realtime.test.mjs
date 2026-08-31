import assert from 'node:assert/strict';
import test from 'node:test';

import { ReconnectingStream, isStreamEvent } from '../src/realtime.js';

class FakeSocket {
  static instances = [];

  constructor(url) {
    this.url = url;
    this.listeners = new Map();
    FakeSocket.instances.push(this);
  }

  addEventListener(name, listener) {
    this.listeners.set(name, listener);
  }

  emit(name, value = {}) {
    this.listeners.get(name)?.(value);
  }

  close() {
    this.emit('close');
  }
}

test('stream events require the versioned envelope', () => {
  assert.equal(isStreamEvent({
    version: 'v1',
    type: 'emotion_state',
    sequence: 0,
    request_id: 'request-1',
    payload: {},
  }), true);
  assert.equal(isStreamEvent({ version: 'v1', type: 'unknown', sequence: 0, request_id: 'request-1', payload: {} }), false);
  assert.equal(isStreamEvent({ version: 'v1', type: 'llm_chunk', sequence: -1, request_id: 'request-1', payload: {} }), false);
});

test('stream reconnects with capped retries and stops after close', (context) => {
  FakeSocket.instances = [];
  const statuses = [];
  const scheduled = [];
  const originalSetTimeout = globalThis.setTimeout;
  globalThis.setTimeout = (callback, delay) => {
    scheduled.push({ callback, delay });
    return scheduled.length;
  };
  context.after(() => {
    globalThis.setTimeout = originalSetTimeout;
  });

  const stream = new ReconnectingStream('ws://localhost/stream', {
    WebSocketImpl: FakeSocket,
    maxRetries: 2,
    onStatus: (status) => statuses.push(status),
  });
  stream.connect();
  FakeSocket.instances[0].emit('close');
  assert.equal(scheduled[0].delay, 1000);
  scheduled[0].callback();
  FakeSocket.instances[1].emit('close');
  assert.equal(scheduled[1].delay, 2000);
  scheduled[1].callback();
  FakeSocket.instances[2].emit('close');
  assert.equal(statuses.at(-1), 'unavailable');

  stream.close();
  assert.equal(statuses.at(-1), 'closed');
});