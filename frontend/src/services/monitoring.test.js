import assert from 'node:assert/strict'
import { test } from 'node:test'
import { normalizeAlerts, normalizeDailyAnalytics, normalizeEvents, normalizeHourlyAnalytics, normalizeRealtimeMessage, normalizeStats } from './monitoring.js'

test('normalizes stats without claiming unavailable detection totals', () => {
  const stats = normalizeStats({
    timestamp: '2026-11-23T12:00:00Z',
    is_active: true,
    total_entries: 42,
    total_exits: 11,
    net_inside: 31,
    today: { entries: 8, exits: 3, people_entries: 5, people_exits: 2, vehicle_entries: 3, vehicle_exits: 1 },
    by_class: {
      person: { entry: 5, exit: 2 },
      car: { entry: 3, exit: 1 },
      bicycle: { entry: 1, exit: 0 },
      motorcycle: { entry: 0, exit: 0 },
      bus: { entry: 0, exit: 0 },
      truck: { entry: 0, exit: 0 },
    },
  })

  assert.equal(stats.entries, 42)
  assert.equal(stats.exits, 11)
  assert.equal(stats.peopleDetected, null)
  assert.equal(stats.vehiclesDetected, null)
  assert.equal(stats.peopleCrossings, 7)
  assert.equal(stats.vehicleCrossings, 5)
  assert.equal(stats.vehiclesEntered, 3)
})

test('normalizes paginated events and preserves backend object classes', () => {
  const events = normalizeEvents({
    total_count: 21,
    limit: 1,
    offset: 0,
    events: [{
      id: 1,
      event_id: 'evt-1',
      track_id: 14,
      class_id: 2,
      class_name: 'car',
      direction: 'ENTRY',
      confidence: 0.94,
      bbox: [1, 2, 3, 4],
      centroid: [2, 4],
      timestamp: '2026-11-23T10:00:00Z',
      snapshot_path: null,
    }],
  })

  assert.equal(events.total, 21)
  assert.equal(events.events[0].id, 'evt-1')
  assert.equal(events.events[0].objectType, 'Vehicle')
  assert.equal(events.events[0].className, 'car')
  assert.equal(events.events[0].direction, 'Entry')
})

test('normalizes daily and hourly analytics using their contract fields', () => {
  const daily = normalizeDailyAnalytics({
    days: 2,
    data: [
      { date: '2026-11-23', entries: 8, exits: 3, people: 7, vehicles: 4 },
      { date: '2026-11-22', entries: 6, exits: 3, people: 7, vehicles: 2 },
    ],
  })
  const hourly = normalizeHourlyAnalytics({
    date: '2026-11-23',
    hourly_distribution: [{ hour: '09:00', entries: 2, exits: 1, people: 2, vehicles: 1 }],
  })

  assert.deepEqual(daily.map((row) => row.date), ['2026-11-22', '2026-11-23'])
  assert.equal(hourly[0].detections, 3)
  assert.equal(hourly[0].entries, 2)
})

test('normalizes alerts and real-time event messages', () => {
  const alerts = normalizeAlerts({
    total: 1,
    alerts: [{
      id: 1,
      alert_type: 'CAMERA_DISCONNECTED',
      severity: 'CRITICAL',
      message: 'Camera stream unavailable',
      timestamp: '2026-11-23T11:00:00Z',
      is_resolved: false,
      metadata: { camera: 'CAM-01' },
    }],
  })
  const message = normalizeRealtimeMessage({
    type: 'GATE_CROSSING',
    payload: {
      event_id: 'evt-live',
      track_id: 15,
      class_name: 'person',
      direction: 'EXIT',
      confidence: 0.91,
      timestamp: '2026-11-23T09:00:00Z',
    },
  })

  assert.equal(alerts[0].category, 'Camera')
  assert.equal(alerts[0].status, 'Open')
  assert.equal(message.payload.id, 'evt-live')
  assert.equal(message.payload.objectType, 'Person')
  assert.equal(message.payload.direction, 'Exit')
})

test('rejects malformed backend event data instead of silently inventing fields', () => {
  assert.throws(() => normalizeEvents({
    total_count: 1,
    events: [{ event_id: 'evt-bad', track_id: 1, class_name: 'person', confidence: 0.9, timestamp: 'bad', direction: 'sideways' }],
  }), /timestamp is invalid|Unknown event direction/)
})
