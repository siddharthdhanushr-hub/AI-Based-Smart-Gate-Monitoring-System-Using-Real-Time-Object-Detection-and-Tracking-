export function connectWebSocket(url, { onMessage, onStatusChange } = {}) {
  if (!url) {
    throw new Error('A WebSocket URL is required.')
  }

  let socket
  let retryTimer
  let stopped = false
  let retryDelay = 1000

  const scheduleRetry = () => {
    if (stopped) return
    retryTimer = window.setTimeout(connect, retryDelay)
    retryDelay = Math.min(retryDelay * 2, 30000)
  }

  const connect = () => {
    if (stopped) return
    try {
      socket = new WebSocket(url)
    } catch (error) {
      onStatusChange?.('error', error)
      scheduleRetry()
      return
    }
    socket.addEventListener('open', () => {
      retryDelay = 1000
      onStatusChange?.('connected')
    })
    socket.addEventListener('message', (event) => {
      try {
        onMessage?.(JSON.parse(event.data))
      } catch (error) {
        onStatusChange?.('invalid-message', error)
      }
    })
    socket.addEventListener('error', (event) => onStatusChange?.('error', event))
    socket.addEventListener('close', () => {
      onStatusChange?.('disconnected')
      scheduleRetry()
    })
  }

  connect()

  return () => {
    stopped = true
    window.clearTimeout(retryTimer)
    socket?.close()
  }
}
