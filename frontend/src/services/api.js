export const apiBaseUrl = import.meta.env?.VITE_API_BASE_URL?.trim() || 'http://localhost:8000'
const requestTimeoutMs = 10000

export function getCameraStreamUrl() {
  const configuredUrl = import.meta.env.VITE_CAMERA_STREAM_URL?.trim()
  return configuredUrl || new URL('/api/video/stream', apiBaseUrl).toString()
}

export function getMonitoringWebSocketUrl() {
  const configuredUrl = import.meta.env.VITE_WEBSOCKET_URL?.trim()
  if (configuredUrl) {
    const url = new URL(configuredUrl)
    if (url.protocol !== 'ws:' && url.protocol !== 'wss:') {
      throw new Error('VITE_WEBSOCKET_URL must use ws:// or wss://.')
    }
    return url.toString()
  }

  const url = new URL(apiBaseUrl)
  url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:'
  url.pathname = '/ws/monitoring'
  url.search = ''
  url.hash = ''
  return url.toString()
}

export async function requestJson(path, { signal, ...options } = {}) {
  if (!path) {
    throw new Error('A backend endpoint path is required.')
  }

  const controller = new AbortController()
  const timeout = window.setTimeout(() => controller.abort(), requestTimeoutMs)
  const abortRequest = () => controller.abort(signal.reason)
  if (signal?.aborted) abortRequest()
  else signal?.addEventListener('abort', abortRequest, { once: true })

  try {
    const response = await fetch(new URL(path, `${apiBaseUrl}/`), {
      ...options,
      signal: controller.signal,
      headers: {
        Accept: 'application/json',
        ...(options.body !== undefined ? { 'Content-Type': 'application/json' } : {}),
        ...options.headers,
      },
    })

    const body = await response.text()
    if (!response.ok) {
      throw new Error(`Backend request failed (${response.status} ${response.statusText}): ${body || 'No error details returned.'}`)
    }

    if (!body) return null
    try {
      return JSON.parse(body)
    } catch (error) {
      throw new Error(`Backend returned invalid JSON: ${error instanceof Error ? error.message : String(error)}`)
    }
  } catch (error) {
    if (controller.signal.aborted && !signal?.aborted) {
      throw new Error(`Backend request timed out after ${requestTimeoutMs / 1000} seconds.`)
    }
    throw error
  } finally {
    window.clearTimeout(timeout)
    signal?.removeEventListener('abort', abortRequest)
  }
}
