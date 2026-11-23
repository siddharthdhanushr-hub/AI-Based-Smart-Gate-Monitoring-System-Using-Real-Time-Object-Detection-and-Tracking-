import assert from 'node:assert/strict'
import { test } from 'node:test'
import { apiBaseUrl, requestJson } from './api.js'

async function withMockedFetch(mockFetch, callback) {
  const originalFetch = globalThis.fetch
  const originalWindow = globalThis.window
  globalThis.fetch = mockFetch
  globalThis.window = {
    setTimeout,
    clearTimeout,
  }

  try {
    await callback()
  } finally {
    globalThis.fetch = originalFetch
    if (originalWindow === undefined) delete globalThis.window
    else globalThis.window = originalWindow
  }
}

test('requests JSON from the configured backend and parses the response', async () => {
  await withMockedFetch(async (url, options) => {
    assert.equal(url.toString(), `${apiBaseUrl}/api/monitoring/stats`)
    assert.equal(options.headers.Accept, 'application/json')
    return new Response('{"total_entries":4}', {
      status: 200,
      headers: { 'Content-Type': 'application/json' },
    })
  }, async () => {
    assert.deepEqual(await requestJson('/api/monitoring/stats'), { total_entries: 4 })
  })
})

test('surfaces backend HTTP errors to the caller', async () => {
  await withMockedFetch(async () => new Response('database unavailable', {
    status: 503,
    statusText: 'Service Unavailable',
  }), async () => {
    await assert.rejects(requestJson('/api/monitoring/stats'), /503 Service Unavailable.*database unavailable/)
  })
})
