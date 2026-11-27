import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { demoAlerts, demoAnalytics, demoEvents, demoSummary } from '../data/demoData'
import { apiBaseUrl, getCameraStreamUrl, getMonitoringWebSocketUrl, requestJson } from '../services/api'
import {
  fetchMonitoringEventsPage,
  fetchMonitoringData,
  normalizeRealtimeMessage,
} from '../services/monitoring'
import { connectWebSocket } from '../services/websocket'

const isDemo = import.meta.env.VITE_DEMO_MODE !== 'false'

function messageOf(error) {
  if (error instanceof Error) return error.message
  if (error && typeof error === 'object' && 'message' in error && error.message) {
    return String(error.message)
  }
  if (error && typeof error === 'object') return 'WebSocket connection error.'
  return String(error)
}

export function useMonitoring() {
  const [cameraConnected, setCameraConnected] = useState(false)
  const [summary, setSummary] = useState(isDemo ? demoSummary : null)
  const [analytics, setAnalytics] = useState(isDemo ? demoAnalytics : null)
  const [events, setEvents] = useState(isDemo ? demoEvents : [])
  const [eventsTotal, setEventsTotal] = useState(isDemo ? demoEvents.length : 0)
  const [eventsOffset, setEventsOffset] = useState(isDemo ? demoEvents.length : 0)
  const [isLoadingMoreEvents, setIsLoadingMoreEvents] = useState(false)
  const [alerts, setAlerts] = useState(isDemo ? demoAlerts : [])
  const [isActive, setIsActive] = useState(null)
  const [isLoading, setIsLoading] = useState(!isDemo)
  const [serviceStatus, setServiceStatus] = useState(isDemo ? 'demo' : 'connecting')
  const [websocketStatus, setWebsocketStatus] = useState(isDemo ? 'demo' : 'connecting')
  const [errors, setErrors] = useState([])
  const [cameraAction, setCameraAction] = useState(null)
  const [cameraError, setCameraError] = useState('')
  const [selectedSource, setSelectedSource] = useState(import.meta.env.VITE_CAMERA_SOURCE || 'ai/dataset/sample_gate.mp4')
  const realtimeEventIds = useRef(new Set())

  const refresh = useCallback(async (signal, { showLoading = true } = {}) => {
    if (isDemo) return

    if (showLoading) setIsLoading(true)
    const result = await fetchMonitoringData(signal)
    if (signal?.aborted) return

    if (result.data.stats) {
      setSummary(result.data.stats)
      setIsActive(result.data.stats.isActive)
    }
    if (result.data.events) {
      realtimeEventIds.current = new Set(result.data.events.events.map((event) => event.id))
      setEvents(result.data.events.events)
      setEventsTotal(result.data.events.total)
      setEventsOffset(result.data.events.events.length)
    }
    if (result.data.daily) {
      setAnalytics((current) => ({
        ...current,
        activity: result.data.daily.slice(-7),
        monthly: result.data.daily,
        hourly: current?.hourly ?? [],
      }))
    }
    if (result.data.hourly) {
      setAnalytics((current) => ({
        ...current,
        activity: current?.activity ?? [],
        monthly: current?.monthly ?? [],
        hourly: result.data.hourly,
      }))
    }
    if (result.data.alerts) setAlerts(result.data.alerts)

    setErrors(result.errors)
    setServiceStatus(result.successfulEndpoints > 0 ? 'online' : 'unavailable')
    setIsLoading(false)
  }, [])

  const loadMoreEvents = useCallback(async () => {
    if (isDemo || isLoadingMoreEvents || eventsOffset >= eventsTotal) return

    setIsLoadingMoreEvents(true)
    try {
      const page = await fetchMonitoringEventsPage({ offset: eventsOffset })
      for (const event of page.events) realtimeEventIds.current.add(event.id)
      setEvents((current) => {
        const existingIds = new Set(current.map((event) => event.id))
        const newEvents = page.events.filter((event) => !existingIds.has(event.id))
        return [...current, ...newEvents]
      })
      setEventsTotal(page.total)
      setEventsOffset((current) => current + page.events.length)
    } catch (error) {
      setErrors((current) => [...current, `More activity records: ${messageOf(error)}`])
    } finally {
      setIsLoadingMoreEvents(false)
    }
  }, [eventsOffset, eventsTotal, isLoadingMoreEvents])

  useEffect(() => {
    if (isDemo) return undefined

    const controller = new AbortController()
    const timer = window.setTimeout(() => {
      void refresh(controller.signal, { showLoading: false })
    }, 0)
    return () => {
      window.clearTimeout(timer)
      controller.abort()
    }
  }, [refresh])

  const handleRealtimeMessage = useCallback((message) => {
    const normalized = normalizeRealtimeMessage(message)
    if (!normalized) return

    if (normalized.type === 'STATS_UPDATE') {
      const update = normalized.payload
      setSummary((current) => ({
        ...current,
        entries: update.entries ?? current?.entries ?? null,
        exits: update.exits ?? current?.exits ?? null,
        currentTrackedObjects: update.currentTrackedObjects ?? current?.currentTrackedObjects ?? null,
        cameraFps: update.cameraFps ?? current?.cameraFps ?? null,
      }))
    } else if (normalized.type === 'GATE_CROSSING') {
      const event = normalized.payload
      if (realtimeEventIds.current.has(event.id)) return
      realtimeEventIds.current.add(event.id)
      if (realtimeEventIds.current.size > 1000) {
        realtimeEventIds.current.delete(realtimeEventIds.current.values().next().value)
      }
      setEvents((current) => [event, ...current.filter((item) => item.id !== event.id)].slice(0, 200))
      setEventsTotal((current) => current + 1)
      setSummary((current) => {
        if (!current) return current
        const key = event.direction === 'Entry' ? 'entries' : 'exits'
        const breakdown = event.objectType === 'Person' ? 'people' : 'vehicle'
        const crossingKey = `${breakdown}Crossings`
        const todayKey = `${breakdown}${event.direction === 'Entry' ? 'Entered' : 'Exited'}`
        return {
          ...current,
          [key]: current[key] == null ? null : current[key] + 1,
          [crossingKey]: current[crossingKey] == null ? null : current[crossingKey] + 1,
          [todayKey]: current[todayKey] == null ? null : current[todayKey] + 1,
        }
      })
    } else if (normalized.type === 'SYSTEM_ALERT') {
      const alert = normalized.payload
      setAlerts((current) => [alert, ...current.filter((item) => item.id !== alert.id)].slice(0, 100))
    }
  }, [])

  useEffect(() => {
    if (isDemo) return undefined

    let disconnect
    let cancelled = false
    const timer = window.setTimeout(() => {
      if (cancelled) return
      try {
        disconnect = connectWebSocket(getMonitoringWebSocketUrl(), {
          onMessage: handleRealtimeMessage,
          onStatusChange: (status, error) => {
            if (status !== 'invalid-message') setWebsocketStatus(status)
            if (error) {
              const detail = `WebSocket: ${messageOf(error)}`
              setErrors((current) => current.includes(detail) ? current : [...current, detail])
            }
          },
        })
      } catch (error) {
        setWebsocketStatus('error')
        setErrors((current) => [...current, `WebSocket: ${messageOf(error)}`])
      }
    }, 0)

    return () => {
      cancelled = true
      window.clearTimeout(timer)
      disconnect?.()
    }
  }, [handleRealtimeMessage])

  const startMonitoring = useCallback(async (sourceOverride) => {
    setCameraAction('starting')
    setCameraError('')
    const sourceToUse = sourceOverride || selectedSource || 'ai/dataset/sample_gate.mp4'
    try {
      const result = await requestJson('/api/camera/start', {
        method: 'POST',
        body: JSON.stringify({ source: sourceToUse }),
      })
      if (result?.status !== 'success' || result.is_running !== true) {
        setIsActive(result?.is_running === false ? false : null)
        throw new Error(result?.message || 'The backend did not confirm that monitoring started.')
      }

      setCameraConnected(false)
      await refresh()
      setIsActive(true)
    } catch (error) {
      setCameraError(`Could not start monitoring: ${messageOf(error)}`)
    } finally {
      setCameraAction(null)
    }
  }, [refresh, selectedSource])

  const switchSource = useCallback(async (sourceType, sourceValue) => {
    setSelectedSource(sourceValue)
    setCameraError('')
    if (isDemo) return
    try {
      const result = await requestJson('/api/camera/source', {
        method: 'POST',
        body: JSON.stringify({ source_type: sourceType, source_value: sourceValue }),
      })
      if (result?.status !== 'success') {
        throw new Error(result?.message || 'Failed to switch camera source.')
      }
      setCameraConnected(false)
      await refresh()
    } catch (error) {
      setCameraError(`Could not switch camera source: ${messageOf(error)}`)
    }
  }, [refresh])

  const stopMonitoring = useCallback(async () => {
    setCameraAction('stopping')
    setCameraError('')
    try {
      const result = await requestJson('/api/camera/stop', { method: 'POST' })
      if (result?.status !== 'success' || result.is_running !== false) {
        setIsActive(result?.is_running === true ? true : null)
        throw new Error(result?.message || 'The backend did not confirm that monitoring stopped.')
      }

      setCameraConnected(false)
      await refresh()
      setIsActive(false)
    } catch (error) {
      setCameraError(`Could not stop monitoring: ${messageOf(error)}`)
    } finally {
      setCameraAction(null)
    }
  }, [refresh])

  const cameraUrl = useMemo(() => {
    const configuredUrl = import.meta.env.VITE_CAMERA_STREAM_URL?.trim()
    if (configuredUrl) return configuredUrl
    return isDemo ? '' : getCameraStreamUrl()
  }, [])

  return {
    isDemo,
    summary,
    analytics,
    events,
    eventsTotal,
    canLoadMoreEvents: !isDemo && eventsOffset < eventsTotal,
    isLoadingMoreEvents,
    loadMoreEvents,
    alerts,
    cameraUrl,
    cameraConnected,
    setCameraConnected,
    isActive,
    isLoading,
    serviceStatus,
    websocketStatus,
    errors,
    refresh,
    selectedSource,
    setSelectedSource,
    switchSource,
    cameraAction,
    cameraError,
    startMonitoring,
    stopMonitoring,
    apiBaseUrl,
  }
}
