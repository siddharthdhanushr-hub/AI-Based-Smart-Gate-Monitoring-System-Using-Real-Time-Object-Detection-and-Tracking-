export const demoSummary = {
  peopleDetected: 1284,
  vehiclesDetected: 392,
  entries: 1048,
  exits: 628,
  peopleEntered: 812,
  peopleExited: 472,
  vehiclesEntered: 236,
  vehiclesExited: 156,
}

export const demoAnalytics = {
  activity: [
    { day: 'Mon', entries: 68, exits: 46 },
    { day: 'Tue', entries: 82, exits: 54 },
    { day: 'Wed', entries: 74, exits: 58 },
    { day: 'Thu', entries: 93, exits: 63 },
    { day: 'Fri', entries: 86, exits: 51 },
    { day: 'Sat', entries: 54, exits: 34 },
    { day: 'Sun', entries: 42, exits: 27 },
  ],
  hourly: [
    { hour: '06:00', detections: 12, entries: 8, exits: 4, people: 8, vehicles: 4 },
    { hour: '08:00', detections: 36, entries: 23, exits: 13, people: 25, vehicles: 11 },
    { hour: '10:00', detections: 28, entries: 17, exits: 11, people: 20, vehicles: 8 },
    { hour: '12:00', detections: 18, entries: 10, exits: 8, people: 13, vehicles: 5 },
    { hour: '14:00', detections: 25, entries: 15, exits: 10, people: 18, vehicles: 7 },
    { hour: '16:00', detections: 41, entries: 25, exits: 16, people: 30, vehicles: 11 },
    { hour: '18:00', detections: 33, entries: 18, exits: 15, people: 24, vehicles: 9 },
    { hour: '20:00', detections: 14, entries: 8, exits: 6, people: 10, vehicles: 4 },
  ],
  monthly: Array.from({ length: 30 }, (_, index) => ({
    day: `Day ${String(index + 1).padStart(2, '0')}`,
    entries: 38 + ((index * 17 + 11) % 65),
    exits: 25 + ((index * 13 + 7) % 48),
  })),
}

export const demoEvents = [
  { id: 'EVT-02841', date: 'Oct 21, 2024', time: '10:42:18 AM', objectType: 'Person', trackingId: 'TRK-0092', direction: 'Entry', cameraId: 'CAM-01' },
  { id: 'EVT-02840', date: 'Oct 21, 2024', time: '10:39:51 AM', objectType: 'Vehicle', trackingId: 'TRK-0091', direction: 'Exit', cameraId: 'CAM-01' },
  { id: 'EVT-02839', date: 'Oct 21, 2024', time: '10:35:07 AM', objectType: 'Person', trackingId: 'TRK-0090', direction: 'Entry', cameraId: 'CAM-01' },
  { id: 'EVT-02838', date: 'Oct 21, 2024', time: '10:28:43 AM', objectType: 'Person', trackingId: 'TRK-0089', direction: 'Exit', cameraId: 'CAM-01' },
  { id: 'EVT-02837', date: 'Oct 21, 2024', time: '10:21:16 AM', objectType: 'Vehicle', trackingId: 'TRK-0088', direction: 'Entry', cameraId: 'CAM-01' },
  { id: 'EVT-02836', date: 'Oct 21, 2024', time: '10:17:30 AM', objectType: 'Person', trackingId: 'TRK-0087', direction: 'Entry', cameraId: 'CAM-01' },
  { id: 'EVT-02835', date: 'Oct 21, 2024', time: '10:09:02 AM', objectType: 'Vehicle', trackingId: 'TRK-0086', direction: 'Exit', cameraId: 'CAM-01' },
  { id: 'EVT-02834', date: 'Oct 21, 2024', time: '09:58:24 AM', objectType: 'Person', trackingId: 'TRK-0085', direction: 'Entry', cameraId: 'CAM-01' },
  { id: 'EVT-02833', date: 'Oct 21, 2024', time: '09:47:13 AM', objectType: 'Person', trackingId: 'TRK-0084', direction: 'Exit', cameraId: 'CAM-01' },
  { id: 'EVT-02832', date: 'Oct 21, 2024', time: '09:31:56 AM', objectType: 'Vehicle', trackingId: 'TRK-0083', direction: 'Entry', cameraId: 'CAM-01' },
]

export const demoAlerts = [
  { id: 'ALT-014', title: 'Camera connection interrupted', description: 'The North entrance camera stream is not connected in this demo environment.', date: 'Oct 21, 2024', time: '10:18 AM', severity: 'warning', status: 'Open', category: 'Camera' },
  { id: 'ALT-013', title: 'Monitoring service status unavailable', description: 'Connect a backend service to receive live monitoring health updates.', date: 'Oct 21, 2024', time: '09:52 AM', severity: 'warning', status: 'Open', category: 'System' },
]
