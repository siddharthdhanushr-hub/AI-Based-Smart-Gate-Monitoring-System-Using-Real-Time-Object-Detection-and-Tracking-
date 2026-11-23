import { requestJson } from './api.js'

function asObject(value, label) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    throw new Error(`${label} response must be an object.`)
  }
  return value
}

function asArray(value, label) {
  if (!Array.isArray(value)) {
    throw new Error(`${label} response must contain an array.`)
  }
  return value
}

function metric(value) {
  if (value == null || value === '') return null
  const parsed = Number(value)
  return Number.isFinite(parsed) ? parsed : null
}

function requiredMetric(value, label) {
  const parsed = metric(value)
  if (parsed == null) throw new Error(`${label} is missing or invalid.`)
  return parsed
}

function dateTimeParts(value, label = 'timestamp') {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) throw new Error(`${label} is invalid.`)
  return {
    date: date.toLocaleDateString('en-US', { month: 'short', day: '2-digit', year: 'numeric' }),
    time: date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
  }
}

function normalizeDirection(value) {
  const direction = String(value ?? '').toUpperCase()
  if (direction === 'ENTRY') return 'Entry'
  if (direction === 'EXIT') return 'Exit'
  throw new Error(`Unknown event direction: ${value ?? '(missing)'}.`)
}

function normalizeObjectType(className) {
  return String(className).toLowerCase() === 'person' ? 'Person' : 'Vehicle'
}

function normalizeEvent(event, { realtime = false } = {}) {
  asObject(event, 'Event')
  const id = event.event_id
  const timestamp = event.timestamp
  const className = event.class_name
  if (id == null || className == null || timestamp == null) {
    throw new Error('Event is missing event_id, class_name, or timestamp.')
  }
  if (event.track_id == null) throw new Error('Event is missing track_id.')
  const confidence = event.confidence == null ? null : requiredMetric(event.confidence, 'Event confidence')
  if (!realtime && confidence == null) throw new Error('Event is missing confidence.')

  const { date, time } = dateTimeParts(timestamp, 'Event timestamp')
  return {
    id: String(id),
    date,
    time,
    objectType: normalizeObjectType(className),
    className: String(className),
    trackingId: event.track_id == null ? '' : String(event.track_id),
    direction: normalizeDirection(event.direction),
    ...(confidence == null ? {} : { confidence }),
  }
}

function normalizeAlert(alert, { realtime = false } = {}) {
  asObject(alert, 'Alert')
  const alertType = alert.alert_type
  const message = alert.message
  const timestamp = alert.timestamp
  if (alertType == null || message == null || timestamp == null) {
    throw new Error('Alert is missing alert_type, message, or timestamp.')
  }
  if (!realtime && alert.id == null) throw new Error('Alert is missing id.')
  if (alert.severity == null) throw new Error('Alert is missing severity.')
  if (!realtime && typeof alert.is_resolved !== 'boolean') {
    throw new Error('Alert is missing is_resolved.')
  }

  const { date, time } = dateTimeParts(timestamp, 'Alert timestamp')
  const type = String(alertType)
  return {
    id: String(alert.id ?? `${type}-${timestamp}`),
    title: type.toLowerCase().replace(/_/g, ' ').replace(/\b\w/g, (letter) => letter.toUpperCase()),
    description: String(message),
    date,
    time,
    severity: String(alert.severity).toLowerCase(),
    status: alert.is_resolved ? 'Resolved' : 'Open',
    category: type.toLowerCase().includes('camera') ? 'Camera' : 'System',
    ...(realtime ? {} : { metadata: alert.metadata ?? null }),
  }
}

export function normalizeStats(value) {
  const stats = asObject(value, 'Monitoring stats')
  const today = asObject(stats.today, 'Monitoring stats today')
  const byClass = asObject(stats.by_class, 'Monitoring stats by_class')
  const classCounts = Object.entries(byClass).map(([className, counts]) => [
    className,
    asObject(counts, `by_class.${className}`),
  ])
  const person = byClass.person ? asObject(byClass.person, 'by_class.person') : null
  const vehicleCounts = classCounts.filter(([className]) => className !== 'person')
  const totalByClass = (key) => vehicleCounts.reduce(
    (total, [className, counts]) => total + requiredMetric(counts[key], `by_class.${className}.${key}`),
    0,
  )

  if (typeof stats.is_active !== 'boolean') {
    throw new Error('Monitoring stats is_active is missing or invalid.')
  }

  return {
    entries: requiredMetric(stats.total_entries, 'total_entries'),
    exits: requiredMetric(stats.total_exits, 'total_exits'),
    peopleDetected: null,
    vehiclesDetected: null,
    peopleEntered: requiredMetric(today.people_entries, 'today.people_entries'),
    peopleExited: requiredMetric(today.people_exits, 'today.people_exits'),
    vehiclesEntered: requiredMetric(today.vehicle_entries, 'today.vehicle_entries'),
    vehiclesExited: requiredMetric(today.vehicle_exits, 'today.vehicle_exits'),
    peopleCrossings: person
      ? requiredMetric(person.entry, 'by_class.person.entry') + requiredMetric(person.exit, 'by_class.person.exit')
      : null,
    vehicleCrossings: vehicleCounts.length ? totalByClass('entry') + totalByClass('exit') : null,
    isActive: stats.is_active,
    timestamp: stats.timestamp ?? null,
  }
}

export function normalizeEvents(value) {
  const response = asObject(value, 'Monitoring events')
  return {
    total: requiredMetric(response.total_count, 'total_count'),
    events: asArray(response.events, 'Monitoring events').map((event) => normalizeEvent(event)),
  }
}

export function normalizeDailyAnalytics(value) {
  const response = asObject(value, 'Daily analytics')
  return asArray(response.data, 'Daily analytics').map((row) => {
    asObject(row, 'Daily analytics row')
    if (typeof row.date !== 'string') throw new Error('Daily analytics row is missing date.')
    return {
      day: row.date,
      date: row.date,
      entries: requiredMetric(row.entries, 'Daily analytics entries'),
      exits: requiredMetric(row.exits, 'Daily analytics exits'),
      people: requiredMetric(row.people, 'Daily analytics people'),
      vehicles: requiredMetric(row.vehicles, 'Daily analytics vehicles'),
    }
  }).sort((left, right) => left.date.localeCompare(right.date))
}

export function normalizeHourlyAnalytics(value) {
  const response = asObject(value, 'Hourly analytics')
  return asArray(response.hourly_distribution, 'Hourly analytics').map((row) => {
    asObject(row, 'Hourly analytics row')
    if (typeof row.hour !== 'string') throw new Error('Hourly analytics row is missing hour.')
    const people = requiredMetric(row.people, 'Hourly analytics people')
    const vehicles = requiredMetric(row.vehicles, 'Hourly analytics vehicles')
    return {
      hour: row.hour,
      entries: requiredMetric(row.entries, 'Hourly analytics entries'),
      exits: requiredMetric(row.exits, 'Hourly analytics exits'),
      people,
      vehicles,
      detections: people + vehicles,
    }
  })
}

export function normalizeAlerts(value) {
  const response = asObject(value, 'Alerts')
  return asArray(response.alerts, 'Alerts').map((alert) => normalizeAlert(alert))
}

export async function fetchMonitoringEventsPage({ limit = 200, offset = 0 } = {}, signal) {
  const query = new URLSearchParams({ limit: String(limit), offset: String(offset) })
  return normalizeEvents(await requestJson(`/api/monitoring/events?${query}`, { signal }))
}

export function normalizeRealtimeMessage(message) {
  asObject(message, 'WebSocket message')
  const payload = asObject(message.payload, 'WebSocket payload')

  switch (message.type) {
    case 'STATS_UPDATE':
      return {
        type: message.type,
        payload: {
          entries: metric(payload.total_entries),
          exits: metric(payload.total_exits),
          currentTrackedObjects: metric(payload.current_tracked_objects),
          cameraFps: metric(payload.camera_fps),
        },
      }
    case 'GATE_CROSSING':
      return { type: message.type, payload: normalizeEvent(payload, { realtime: true }) }
    case 'SYSTEM_ALERT':
      return { type: message.type, payload: normalizeAlert(payload, { realtime: true }) }
    default:
      return null
  }
}

export async function fetchMonitoringData(signal) {
  const endpoints = [
    { key: 'stats', label: 'Monitoring stats', path: '/api/monitoring/stats', normalize: normalizeStats },
    { key: 'events', label: 'Monitoring events', path: '/api/monitoring/events?limit=200', normalize: normalizeEvents },
    { key: 'daily', label: 'Daily analytics', path: '/api/analytics/daily?days=30', normalize: normalizeDailyAnalytics },
    { key: 'hourly', label: 'Hourly analytics', path: '/api/analytics/hourly', normalize: normalizeHourlyAnalytics },
    { key: 'alerts', label: 'Alerts', path: '/api/alerts?limit=100', normalize: normalizeAlerts },
  ]

  const results = await Promise.allSettled(
    endpoints.map(({ path }) => requestJson(path, { signal })),
  )
  const data = {}
  const errors = []
  let successfulEndpoints = 0

  results.forEach((result, index) => {
    const endpoint = endpoints[index]
    if (result.status === 'rejected') {
      errors.push(`${endpoint.label}: ${result.reason instanceof Error ? result.reason.message : String(result.reason)}`)
      return
    }

    try {
      data[endpoint.key] = endpoint.normalize(result.value)
      successfulEndpoints += 1
    } catch (error) {
      errors.push(`${endpoint.label}: ${error instanceof Error ? error.message : String(error)}`)
    }
  })

  return { data, errors, successfulEndpoints }
}

export function normalizeRealtimeEvent(payload) {
  return normalizeEvent(payload, { realtime: true })
}

export function normalizeRealtimeAlert(payload) {
  return normalizeAlert(payload, { realtime: true })
}
