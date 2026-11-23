import assert from 'node:assert/strict'
import { test } from 'node:test'
import { connectWebSocket } from './websocket.js'

test('parses messages and reconnects with backoff after a closed socket', () => {
  const originalWebSocket = globalThis.WebSocket
  const originalWindow = globalThis.window
  const sockets = []
  const statuses = []
  const messages = []
  const timers = new Map()
  let nextTimerId = 0

  class FakeWebSocket {
    constructor(url) {
      this.url = url
      this.listeners = new Map()
      sockets.push(this)
    }

    addEventListener(type, listener) {
      const listeners = this.listeners.get(type) ?? []
      listeners.push(listener)
      this.listeners.set(type, listeners)
    }

    emit(type, event = {}) {
      for (const listener of this.listeners.get(type) ?? []) listener(event)
    }

    close() {
      this.emit('close')
    }
  }

  globalThis.WebSocket = FakeWebSocket
  globalThis.window = {
    setTimeout(callback, delay) {
      const id = ++nextTimerId
      timers.set(id, { callback, delay })
      return id
    },
    clearTimeout(id) {
      timers.delete(id)
    },
  }

  try {
    const disconnect = connectWebSocket('ws://example.test/monitoring', {
      onMessage: (message) => messages.push(message),
      onStatusChange: (status, error) => statuses.push({ status, error }),
    })

    sockets[0].emit('open')
    sockets[0].emit('message', { data: '{"type":"STATS_UPDATE"}' })
    sockets[0].emit('message', { data: '{bad json' })
    sockets[0].emit('close')

    assert.deepEqual(messages, [{ type: 'STATS_UPDATE' }])
    assert.equal(statuses[0].status, 'connected')
    assert.equal(statuses[1].status, 'invalid-message')
    assert.ok(statuses[1].error instanceof Error)
    assert.equal(statuses[2].status, 'disconnected')
    assert.equal([...timers.values()][0].delay, 1000)

    const retry = [...timers.entries()][0]
    timers.delete(retry[0])
    retry[1].callback()
    assert.equal(sockets.length, 2)

    disconnect()
    assert.equal(timers.size, 0)
  } finally {
    if (originalWebSocket === undefined) delete globalThis.WebSocket
    else globalThis.WebSocket = originalWebSocket
    if (originalWindow === undefined) delete globalThis.window
    else globalThis.window = originalWindow
  }
})
