import { useEffect, useMemo, useRef, useState } from 'react'
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import {
  Activity,
  AlertTriangle,
  ArrowDownLeft,
  ArrowRight,
  ArrowUpRight,
  Bell,
  Camera,
  CarFront,
  Check,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  CircleHelp,
  Clock3,
  Download,
  ExternalLink,
  LayoutDashboard,
  ListFilter,
  LockKeyhole,
  Maximize,
  Menu,
  MoreHorizontal,
  Radio,
  RefreshCw,
  Search,
  Settings,
  Shield,
  ShieldAlert,
  Users,
  VideoOff,
} from 'lucide-react'
import {
  Link,
  NavLink,
  Route,
  Routes,
  useLocation,
} from 'react-router-dom'
import { useMonitoring } from './hooks/useMonitoring'
import './styles/global.css'

const navigation = [
  { label: 'Overview', path: '/', icon: LayoutDashboard },
  { label: 'Live monitoring', path: '/live', icon: Camera },
  { label: 'Analytics', path: '/analytics', icon: Activity },
  { label: 'Activity history', path: '/activity', icon: Clock3 },
  { label: 'Alerts', path: '/alerts', icon: ShieldAlert },
]

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const [currentTime, setCurrentTime] = useState(() => new Date())
  const monitoring = useMonitoring()
  const location = useLocation()
  const activePage = navigation.find((item) => item.path === location.pathname)
  const serviceLabel = monitoring.isDemo
    ? 'Demo environment'
    : monitoring.serviceStatus === 'online'
      ? 'Backend online'
      : monitoring.serviceStatus === 'connecting'
        ? 'Connecting to backend'
        : 'Backend unavailable'
  const serviceTone = monitoring.isDemo
    ? 'system-demo'
    : monitoring.serviceStatus === 'online'
      ? 'system-online'
      : 'system-unavailable'

  useEffect(() => {
    const timer = window.setInterval(() => setCurrentTime(new Date()), 30000)
    return () => window.clearInterval(timer)
  }, [])

  return (
    <div className="app-shell">
      {sidebarOpen && (
        <button
          aria-label="Close navigation"
          className="sidebar-backdrop"
          onClick={() => setSidebarOpen(false)}
        />
      )}
      <aside className={`sidebar ${sidebarOpen ? 'sidebar-open' : ''}`}>
        <Link className="brand" to="/" onClick={() => setSidebarOpen(false)}>
          <span className="brand-mark"><Shield size={22} strokeWidth={2.2} /></span>
          <span className="brand-copy">
            <strong>Gatewatch</strong>
            <small>SMART GATE SYSTEM</small>
          </span>
        </Link>

        <div className="workspace-switcher">
          <span className="workspace-icon"><Radio size={16} /></span>
          <span><strong>North entrance</strong><small>Gate 01 · Main campus</small></span>
          <ChevronDown size={15} className="switcher-chevron" />
        </div>

        <p className="nav-caption">WORKSPACE</p>
        <nav className="primary-nav" aria-label="Main navigation">
          {navigation.map(({ label, path, icon: Icon, badge }) => (
            <NavLink
              key={path}
              end={path === '/'}
              to={path}
              className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              onClick={() => setSidebarOpen(false)}
            >
              <Icon size={18} strokeWidth={1.8} />
              <span>{label}</span>
              {badge && <span className="nav-badge">{badge}</span>}
            </NavLink>
          ))}
        </nav>
        <p className="nav-caption nav-caption-lower">PREFERENCES</p>
        <NavLink
          to="/settings"
          className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          onClick={() => setSidebarOpen(false)}
        >
          <Settings size={18} strokeWidth={1.8} />
          <span>Settings</span>
        </NavLink>

        <div className="sidebar-spacer" />
        <div className="sidebar-help">
          <span className="help-icon"><CircleHelp size={17} /></span>
          <div><strong>Need a hand?</strong><small>Visit the help center</small></div>
          <ArrowRight size={15} />
        </div>
        <div className="sidebar-profile">
          <div className="avatar">AG</div>
          <div className="profile-copy"><strong>Amith Gowda</strong><small>Administrator</small></div>
          <MoreHorizontal size={18} className="profile-more" />
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <button
            aria-label="Open navigation"
            className="icon-button mobile-menu"
            onClick={() => setSidebarOpen(true)}
          >
            <Menu size={20} />
          </button>
          <div className="breadcrumb">
            <span>Workspace</span><ChevronRight size={14} /><strong>{activePage?.label ?? 'Settings'}</strong>
          </div>
          <div className="topbar-actions">
            <div className={`system-pill ${serviceTone}`}><span className="status-dot" />{serviceLabel}</div>
            <time className="topbar-clock" dateTime={currentTime.toISOString()}>{currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</time>
            <Link to="/alerts" className="icon-button notification-button" aria-label="Notifications">
              <Bell size={19} />{monitoring.alerts?.length > 0 && <i />}
            </Link>
            <div className="topbar-divider" />
            <div className="topbar-user">
              <div className="avatar avatar-small">AG</div>
              <span><strong>Amith Gowda</strong><small>Admin</small></span>
              <ChevronDown size={15} />
            </div>
          </div>
        </header>

        {monitoring.isDemo && (
          <div className="demo-banner">
            <span className="demo-indicator" />
            <strong>DEMO MODE</strong>
            <span>Sample data is for layout preview only and is not live monitoring data.</span>
            <Link to="/settings">Configure connection <ArrowRight size={14} /></Link>
          </div>
        )}
        {!monitoring.isDemo && monitoring.isLoading && (
          <div className="connection-banner" role="status"><RefreshCw size={15} /> Loading monitoring data from the backend...</div>
        )}
        {!monitoring.isDemo && monitoring.errors.length > 0 && (
          <div className="connection-banner connection-error" role="alert">
            <AlertTriangle size={16} />
            <span><strong>Some backend data could not be loaded.</strong> {monitoring.errors.join(' ')}</span>
            <button className="text-button" onClick={() => monitoring.refresh()} disabled={monitoring.isLoading}>Retry</button>
          </div>
        )}

        <div className="page-content">
          <Routes>
            <Route path="/" element={<Dashboard monitoring={monitoring} currentTime={currentTime} />} />
            <Route path="/live" element={<LiveMonitoring monitoring={monitoring} />} />
            <Route path="/analytics" element={<Analytics monitoring={monitoring} />} />
            <Route path="/activity" element={<ActivityHistory monitoring={monitoring} />} />
            <Route path="/alerts" element={<Alerts monitoring={monitoring} />} />
            <Route path="/settings" element={<SettingsPage monitoring={monitoring} />} />
            <Route path="*" element={<Dashboard monitoring={monitoring} />} />
          </Routes>
        </div>
        <footer className="app-footer">
          <span>Gatewatch <span className="footer-dot">·</span> Monitoring workspace</span>
          <span><span className={`footer-status ${monitoring.isDemo ? 'footer-status-demo' : monitoring.serviceStatus === 'online' ? '' : 'footer-status-unavailable'}`} /> {monitoring.isDemo ? 'Demo data active' : `API ${monitoring.serviceStatus} · WebSocket ${monitoring.websocketStatus}`}</span>
        </footer>
      </main>
    </div>
  )
}

function PageHeading({ eyebrow, title, description, actions }) {
  return (
    <div className="page-heading">
      <div>
        <div className="eyebrow">{eyebrow}</div>
        <h1>{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {actions && <div className="heading-actions">{actions}</div>}
    </div>
  )
}

function Dashboard({ monitoring, currentTime }) {
  const [period, setPeriod] = useState('7 days')
  const summary = monitoring.summary
  const cameraFeedUrl = monitoring.isDemo || monitoring.isActive ? monitoring.cameraUrl : ''
  const activityData = period === '30 days'
    ? monitoring.analytics?.monthly ?? []
    : monitoring.analytics?.activity ?? []
  const summaryRows = [
    ['Generated at', currentTime.toISOString()],
    ['Data mode', monitoring.isDemo ? 'Demo sample' : 'Backend'],
    ['People detected', summary?.peopleDetected],
    ['Vehicles detected', summary?.vehiclesDetected],
    ['Total entries', summary?.entries],
    ['Total exits', summary?.exits],
    ['People entered', summary?.peopleEntered],
    ['People exited', summary?.peopleExited],
    ['Vehicles entered', summary?.vehiclesEntered],
    ['Vehicles exited', summary?.vehiclesExited],
  ]

  return (
    <>
      <PageHeading
        eyebrow={currentTime.toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' }).toUpperCase()}
        title="Welcome back, Amith"
        description="Here's what's happening at your gates today."
        actions={<button className="button button-secondary" disabled={!summary} onClick={() => downloadCsv(`gatewatch-summary-${dateFileSuffix(currentTime)}.csv`, [['Metric', 'Value'], ...summaryRows])}><Download size={16} /> Export report</button>}
      />
      <div className="overview-strip">
        <div className="overview-location"><span className="location-pin"><Radio size={16} /></span><span><strong>North entrance</strong><small>Gate 01 monitoring</small></span></div>
        <div className="overview-meta">
          <span className={`status-dot ${monitoring.cameraConnected ? '' : 'status-dot-muted'}`} />Camera {monitoring.cameraConnected ? 'online' : 'offline'}
          {!monitoring.isDemo && Number.isFinite(summary?.currentTrackedObjects) && <><span className="meta-separator" />Tracked <strong>{summary.currentTrackedObjects}</strong></>}
          {!monitoring.isDemo && Number.isFinite(summary?.cameraFps) && <><span className="meta-separator" /><strong>{summary.cameraFps} FPS</strong></>}
          <span className="meta-separator" /> Data source <strong>{monitoring.isDemo ? 'Demo' : monitoring.serviceStatus === 'online' ? 'Backend' : 'Unavailable'}</strong>
        </div>
        <Link to="/live" className="text-button">View camera <ArrowRight size={14} /></Link>
      </div>

      <section className="stats-grid" aria-label="Detection overview">
        <StatCard title="People detected" value={summary?.peopleDetected} icon={Users} tone="blue" />
        <StatCard title="Vehicles detected" value={summary?.vehiclesDetected} icon={CarFront} tone="violet" />
        <StatCard title="Total entries" value={summary?.entries} icon={ArrowDownLeft} tone="green" />
        <StatCard title="Total exits" value={summary?.exits} icon={ArrowUpRight} tone="orange" />
      </section>
      {!monitoring.isDemo && summary && (
        <p className="data-contract-note">The backend reports gate crossings, not total per-frame detections; people and vehicle detection totals are unavailable.</p>
      )}

      <div className="dashboard-grid">
        <section className="panel camera-panel">
          <div className="panel-heading">
            <div><h2>Live camera</h2><p>North entrance · Camera 01</p></div>
            <span className={`live-badge ${monitoring.cameraConnected ? 'live' : 'offline'}`}><span />{monitoring.cameraConnected ? 'LIVE' : 'OFFLINE'}</span>
          </div>
          <CameraFeed key={cameraFeedUrl} url={cameraFeedUrl} connected={monitoring.cameraConnected} onConnectionChange={monitoring.setCameraConnected} emptyTitle={monitoring.isActive === false ? 'Monitoring is stopped' : undefined} emptyText={monitoring.isActive === false ? 'Start monitoring to view the live camera feed.' : undefined} />
          <div className="camera-footer">
            <span><Camera size={15} /> Gate 01 / North entrance</span>
            <Link to="/live" className="text-button">Open monitor <ExternalLink size={14} /></Link>
          </div>
        </section>

        <section className="panel activity-panel">
          <div className="panel-heading panel-heading-spread">
            <div><h2>Gate activity</h2><p>Entries and exits over time</p></div>
            <label className="select-button">
              <select aria-label="Gate activity period" value={period} onChange={(event) => setPeriod(event.target.value)}>
                <option>7 days</option>
                <option>30 days</option>
              </select>
              <ChevronDown size={14} />
            </label>
          </div>
          {activityData.length ? (
            <div className="chart-area chart-area-tall">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={activityData} margin={{ top: 10, right: 8, left: -18, bottom: 0 }}>
                  <CartesianGrid stroke="#edf0f4" vertical={false} />
                  <XAxis dataKey="day" tickLine={false} axisLine={false} tick={{ fill: '#9299a6', fontSize: 11 }} dy={8} />
                  <YAxis tickLine={false} axisLine={false} tick={{ fill: '#9299a6', fontSize: 11 }} />
                  <Tooltip contentStyle={tooltipStyle} />
                  <Line type="monotone" dataKey="entries" name="Entries" stroke="#3678ec" strokeWidth={2.5} dot={false} activeDot={{ r: 4 }} />
                  <Line type="monotone" dataKey="exits" name="Exits" stroke="#a78bfa" strokeWidth={2.5} dot={false} activeDot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : <EmptyState title="No activity data yet" text="Activity will appear when monitoring data is available." />}
          <div className="chart-legend"><span><i className="legend-blue" /> Entries</span><span><i className="legend-purple" /> Exits</span></div>
        </section>
      </div>

      <div className="dashboard-grid lower-grid">
        <section className="panel events-panel">
          <div className="panel-heading panel-heading-spread">
            <div><h2>Recent activity</h2><p>Latest events across your gates</p></div>
            <Link to="/activity" className="text-button">View all <ArrowRight size={14} /></Link>
          </div>
          <EventTable events={(monitoring.events ?? []).slice(0, 5)} compact />
        </section>
        <section className="panel alerts-panel">
          <div className="panel-heading panel-heading-spread">
            <div><h2>System status</h2><p>Health and recent notifications</p></div>
            <Link to="/alerts" className="text-button">All alerts <ArrowRight size={14} /></Link>
          </div>
          <div className="health-item"><span className="health-icon health-green"><Radio size={16} /></span><span><strong>Camera connection</strong><small>North entrance · {monitoring.cameraConnected ? 'Connected' : 'Not connected'}</small></span><span className={`health-state ${monitoring.cameraConnected ? 'state-green' : 'state-muted'}`}>{monitoring.cameraConnected ? 'Online' : 'Offline'}</span></div>
          <div className="health-item"><span className="health-icon health-blue"><Activity size={16} /></span><span><strong>Monitoring service</strong><small>{monitoring.isDemo ? 'Backend not configured' : `WebSocket ${monitoring.websocketStatus}`}</small></span><span className={`health-state ${monitoring.isDemo ? 'state-muted' : monitoring.isActive ? 'state-green' : 'state-muted'}`}>{monitoring.isDemo ? 'Demo' : monitoring.isActive ? 'Active' : monitoring.isActive === false ? 'Stopped' : 'Unknown'}</span></div>
          {(monitoring.alerts ?? []).slice(0, 1).map((alert) => <div className="alert-preview" key={alert.id}><span className="alert-preview-icon"><AlertTriangle size={15} /></span><span><strong>{alert.title}</strong><small>{alert.time}</small></span><ChevronRight size={15} /></div>)}
        </section>
      </div>
    </>
  )
}

function StatCard({ title, value, icon: Icon, tone }) {
  return (
    <article className="stat-card">
      <div className="stat-card-top"><span className={`stat-icon ${tone}`}><Icon size={19} strokeWidth={1.9} /></span></div>
      <div className="stat-title">{title}</div>
      <div className="stat-value">{value == null ? '—' : Number(value).toLocaleString()}</div>
    </article>
  )
}

function CameraFeed({ url, connected, large = false, onConnectionChange, emptyTitle, emptyText }) {
  const [videoFailed, setVideoFailed] = useState(false)
  const [videoLoading, setVideoLoading] = useState(Boolean(url))
  const imageRef = useRef(null)
  const requestFullscreen = () => imageRef.current?.requestFullscreen?.()

  return (
    <div className={`camera-feed ${large ? 'camera-feed-large' : ''}`}>
      {url && !videoFailed ? (
        <>
          <img
            ref={imageRef}
            src={url}
            alt="Live gate camera stream"
            onLoad={() => { setVideoFailed(false); setVideoLoading(false); onConnectionChange?.(true) }}
            onError={() => { setVideoFailed(true); setVideoLoading(false); onConnectionChange?.(false) }}
            onDoubleClick={requestFullscreen}
          />
          {videoLoading && <div className="camera-loading" role="status"><RefreshCw size={17} /> Connecting to camera stream…</div>}
        </>
      ) : (
        <div className="camera-empty">
          <div className="camera-empty-icon">{videoFailed ? <AlertTriangle size={24} /> : <VideoOff size={25} />}</div>
          <strong>{videoFailed ? 'Camera stream unavailable' : emptyTitle ?? 'No camera stream connected'}</strong>
          <span>{videoFailed ? 'Check the backend service and camera connection.' : emptyText ?? 'Connect a camera stream to view live footage here.'}</span>
          <span className="camera-empty-status"><i /> {videoFailed ? 'Stream unavailable' : url ? 'Waiting for stream' : connected ? 'Stream connected' : 'Camera offline'}</span>
        </div>
      )}
      {url && !videoFailed && <button className="camera-fullscreen" aria-label="View full screen" onClick={requestFullscreen}><Maximize size={16} /></button>}
      <div className="camera-overlay"><span><Radio size={13} /> CAM 01</span><span>16:9</span></div>
    </div>
  )
}

function LiveMonitoring({ monitoring }) {
  const [streamAttempt, setStreamAttempt] = useState(0)
  const cameraFeedUrl = monitoring.isDemo || monitoring.isActive ? monitoring.cameraUrl : ''
  const canRetryStream = Boolean(monitoring.cameraUrl && (monitoring.isDemo || monitoring.isActive))
  const retryStream = () => {
    monitoring.setCameraConnected(false)
    setStreamAttempt((attempt) => attempt + 1)
  }
  const cameraActionPending = monitoring.cameraAction !== null
  const cameraActionLabel = monitoring.isActive
    ? monitoring.cameraAction === 'stopping' ? 'Stopping...' : 'Stop monitoring'
    : monitoring.cameraAction === 'starting' ? 'Starting...' : 'Start monitoring'
  const detectionCountLabel = monitoring.isDemo ? 'detected' : 'crossing events'
  const peopleCount = monitoring.isDemo ? monitoring.summary?.peopleDetected : monitoring.summary?.peopleCrossings
  const vehicleCount = monitoring.isDemo ? monitoring.summary?.vehiclesDetected : monitoring.summary?.vehicleCrossings

  return (
    <>
      <PageHeading
        eyebrow="CAMERA CENTER"
        title="Live monitoring"
        description="Monitor your gate cameras and connection health."
        actions={monitoring.isDemo ? (
          <span className="health-state state-muted">Backend camera controls unavailable in demo mode</span>
        ) : (
          <>
            <button className="button button-secondary" onClick={monitoring.isActive ? monitoring.stopMonitoring : monitoring.startMonitoring} disabled={cameraActionPending}>
              <Radio size={15} /> {cameraActionLabel}
            </button>
            <button className="button button-secondary" onClick={retryStream} disabled={!canRetryStream} title={canRetryStream ? 'Reload the backend MJPEG stream' : 'Start monitoring before retrying the stream'}>
              <RefreshCw size={15} /> Retry stream
            </button>
            <button className="button button-secondary" onClick={() => monitoring.refresh()} disabled={monitoring.isLoading}>
              <RefreshCw size={15} /> Refresh data
            </button>
          </>
        )}
      />
      {monitoring.cameraError && <div className="connection-banner connection-error" role="alert"><AlertTriangle size={16} />{monitoring.cameraError}</div>}
      <div className="live-layout">
        <section className="panel live-view-panel">
          <div className="panel-heading"><div><h2>North entrance</h2><p>Camera 01 · Main campus gate</p></div><span className={`live-badge ${monitoring.cameraConnected ? 'live' : 'offline'}`}><span />{monitoring.cameraConnected ? 'LIVE' : 'OFFLINE'}</span></div>
          <CameraFeed key={`${cameraFeedUrl}-${streamAttempt}`} url={cameraFeedUrl} connected={monitoring.cameraConnected} onConnectionChange={monitoring.setCameraConnected} large emptyTitle={monitoring.isActive === false ? 'Monitoring is stopped' : undefined} emptyText={monitoring.isActive === false ? 'Start monitoring to view the live camera feed.' : undefined} />
          <div className="camera-description"><span><Camera size={15} /> Camera 01</span><span><Clock3 size={15} /> Stream status: {monitoring.cameraConnected ? 'Connected' : monitoring.isActive === false ? 'Monitoring stopped' : 'Unavailable'}</span></div>
        </section>
        <section className="panel live-side-panel">
          <div className="panel-heading"><div><h2>Detection summary</h2><p>Current session</p></div></div>
          <div className="detection-count"><span className="stat-icon blue"><Users size={18} /></span><span><small>People {detectionCountLabel}</small><strong>{formatMetric(peopleCount)}</strong></span></div>
          <div className="detection-count"><span className="stat-icon violet"><CarFront size={18} /></span><span><small>Vehicle {detectionCountLabel}</small><strong>{formatMetric(vehicleCount)}</strong></span></div>
          {!monitoring.isDemo && Number.isFinite(monitoring.summary?.currentTrackedObjects) && <div className="detection-count"><span className="stat-icon green"><Activity size={18} /></span><span><small>Currently tracked</small><strong>{formatMetric(monitoring.summary.currentTrackedObjects)}</strong></span></div>}
          <div className="live-divider" />
          <h3 className="mini-section-title">Detection legend</h3>
          <div className="legend-row"><span className="detection-swatch person-swatch" />Person <span className="legend-note">Overlay if present</span></div>
          <div className="legend-row"><span className="detection-swatch vehicle-swatch" />Vehicle <span className="legend-note">Overlay if present</span></div>
          <div className="info-note"><CircleHelp size={15} /> Bounding boxes and tracking labels are displayed only when included in the camera stream.</div>
        </section>
      </div>
    </>
  )
}

function Analytics({ monitoring }) {
  const [period, setPeriod] = useState('7 days')
  const stats = monitoring.summary
  const charts = monitoring.analytics
  const activityForPeriod = period === '30 days' ? charts?.monthly : charts?.activity
  const peopleComparison = monitoring.isDemo ? stats?.peopleDetected : stats?.peopleCrossings
  const vehicleComparison = monitoring.isDemo ? stats?.vehiclesDetected : stats?.vehicleCrossings
  const hasComparisonData = Number.isFinite(peopleComparison) && Number.isFinite(vehicleComparison)

  return (
    <>
      <PageHeading eyebrow="INSIGHTS" title="Statistics & analytics" description="Understand movement patterns across your gates." actions={<div className="filter-select"><ListFilter size={15} /><select value={period} onChange={(event) => setPeriod(event.target.value)}><option>Today</option><option>7 days</option><option>30 days</option></select><ChevronDown size={14} /></div>} />
      <section className="stats-grid analytics-stats">
        <StatCard title={monitoring.isDemo ? 'People detected' : 'People crossing events'} value={monitoring.isDemo ? stats?.peopleDetected : stats?.peopleCrossings} icon={Users} tone="blue" />
        <StatCard title="People entered today" value={stats?.peopleEntered} icon={ArrowDownLeft} tone="green" />
        <StatCard title="People exited today" value={stats?.peopleExited} icon={ArrowUpRight} tone="orange" />
        <StatCard title={monitoring.isDemo ? 'Vehicles detected' : 'Vehicle crossing events'} value={monitoring.isDemo ? stats?.vehiclesDetected : stats?.vehicleCrossings} icon={CarFront} tone="violet" />
        <StatCard title="Vehicles entered today" value={stats?.vehiclesEntered} icon={ArrowDownLeft} tone="green" />
        <StatCard title="Vehicles exited today" value={stats?.vehiclesExited} icon={ArrowUpRight} tone="orange" />
      </section>
      <div className="analytics-grid">
        <section className="panel analytics-wide">
          <div className="panel-heading panel-heading-spread"><div><h2>{period === 'Today' ? 'Hourly entries & exits' : 'Entries & exits'}</h2><p>{period === 'Today' ? 'Gate crossings by hour today' : `Activity during the last ${period.toLowerCase()}`}</p></div><div className="chart-legend chart-legend-inline"><span><i className="legend-blue" /> Entries</span><span><i className="legend-purple" /> Exits</span></div></div>
          {period === 'Today' && charts?.hourly?.length ? (
            <div className="chart-area analytics-chart"><ResponsiveContainer width="100%" height="100%"><LineChart data={charts.hourly} margin={{ top: 12, right: 12, left: -16, bottom: 2 }}><CartesianGrid stroke="#edf0f4" vertical={false} /><XAxis dataKey="hour" tickLine={false} axisLine={false} tick={{ fill: '#9299a6', fontSize: 11 }} dy={8} /><YAxis tickLine={false} axisLine={false} tick={{ fill: '#9299a6', fontSize: 11 }} /><Tooltip contentStyle={tooltipStyle} /><Line type="monotone" dataKey="entries" name="Entries" stroke="#3678ec" strokeWidth={2.5} dot={{ r: 3, fill: '#3678ec' }} /><Line type="monotone" dataKey="exits" name="Exits" stroke="#a78bfa" strokeWidth={2.5} dot={{ r: 3, fill: '#a78bfa' }} /></LineChart></ResponsiveContainer></div>
          ) : period !== 'Today' && activityForPeriod?.length ? (
            <div className="chart-area analytics-chart"><ResponsiveContainer width="100%" height="100%"><LineChart data={activityForPeriod} margin={{ top: 12, right: 12, left: -16, bottom: 2 }}><CartesianGrid stroke="#edf0f4" vertical={false} /><XAxis dataKey="day" tickLine={false} axisLine={false} tick={{ fill: '#9299a6', fontSize: 11 }} dy={8} /><YAxis tickLine={false} axisLine={false} tick={{ fill: '#9299a6', fontSize: 11 }} /><Tooltip contentStyle={tooltipStyle} /><Line type="monotone" dataKey="entries" name="Entries" stroke="#3678ec" strokeWidth={2.5} dot={{ r: 3, fill: '#3678ec' }} /><Line type="monotone" dataKey="exits" name="Exits" stroke="#a78bfa" strokeWidth={2.5} dot={{ r: 3, fill: '#a78bfa' }} /></LineChart></ResponsiveContainer></div>
          ) : <EmptyState title="No activity data for this period" text="Analytics will appear when historical data is available." />}
        </section>
        <section className="panel">
          <div className="panel-heading"><div><h2>{monitoring.isDemo ? 'People vs. vehicles' : 'Crossing events by type'}</h2><p>{monitoring.isDemo ? 'Detection totals' : 'Entry and exit counts combined'}</p></div></div>
          {hasComparisonData ? <div className="comparison-wrap"><div className="chart-area donut-chart"><ResponsiveContainer width="100%" height="100%"><PieChart><Pie data={[{ name: 'People', value: peopleComparison }, { name: 'Vehicles', value: vehicleComparison }]} dataKey="value" innerRadius={62} outerRadius={83} paddingAngle={4} stroke="none"><Cell fill="#3678ec" /><Cell fill="#a78bfa" /></Pie><Tooltip contentStyle={tooltipStyle} /></PieChart></ResponsiveContainer><div className="donut-label"><strong>{formatMetric(peopleComparison + vehicleComparison)}</strong><small>{monitoring.isDemo ? 'Total' : 'Crossings'}</small></div></div><div className="comparison-legend"><span><i className="legend-blue" />People <strong>{formatMetric(peopleComparison)}</strong></span><span><i className="legend-purple" />Vehicles <strong>{formatMetric(vehicleComparison)}</strong></span></div></div> : <EmptyState title="No comparison data" text="Data will appear when available." />}
        </section>
        <section className="panel analytics-wide">
          <div className="panel-heading"><div><h2>Hourly activity</h2><p>People and vehicles by hour</p></div></div>
          {charts?.hourly?.length ? <div className="chart-area analytics-chart"><ResponsiveContainer width="100%" height="100%"><BarChart data={charts.hourly} margin={{ top: 10, right: 10, left: -18, bottom: 0 }}><CartesianGrid stroke="#edf0f4" vertical={false} /><XAxis dataKey="hour" tickLine={false} axisLine={false} tick={{ fill: '#9299a6', fontSize: 11 }} /><YAxis tickLine={false} axisLine={false} tick={{ fill: '#9299a6', fontSize: 11 }} /><Tooltip contentStyle={tooltipStyle} /><Bar dataKey="people" name="People" fill="#3678ec" radius={[4, 4, 0, 0]} maxBarSize={26} /><Bar dataKey="vehicles" name="Vehicles" fill="#a78bfa" radius={[4, 4, 0, 0]} maxBarSize={26} /></BarChart></ResponsiveContainer></div> : <EmptyState title="No hourly data available" text="Hourly activity will appear when monitoring data is available." />}
        </section>
        <section className="panel">
          <div className="panel-heading"><div><h2>Daily movement</h2><p>Entries and exits for the latest {period === '30 days' ? '30 days' : '7 available days'}</p></div></div>
          {activityForPeriod?.length ? <div className="chart-area analytics-chart-small"><ResponsiveContainer width="100%" height="100%"><BarChart data={activityForPeriod} margin={{ top: 10, right: 4, left: -22, bottom: 0 }}><CartesianGrid stroke="#edf0f4" vertical={false} /><XAxis dataKey="day" tickLine={false} axisLine={false} tick={{ fill: '#9299a6', fontSize: 10 }} /><YAxis tickLine={false} axisLine={false} tick={{ fill: '#9299a6', fontSize: 10 }} /><Tooltip contentStyle={tooltipStyle} /><Bar dataKey="entries" name="Entries" fill="#3678ec" radius={[3, 3, 0, 0]} /><Bar dataKey="exits" name="Exits" fill="#a78bfa" radius={[3, 3, 0, 0]} /></BarChart></ResponsiveContainer></div> : <EmptyState title="No daily data available" text="Daily movement will appear when available." />}
        </section>
      </div>
    </>
  )
}

function ActivityHistory({ monitoring }) {
  const [search, setSearch] = useState('')
  const [objectType, setObjectType] = useState('All types')
  const [direction, setDirection] = useState('All directions')
  const [date, setDate] = useState('')
  const [sortOrder, setSortOrder] = useState('Newest first')
  const [page, setPage] = useState(1)
  const pageSize = 8
  const filteredEvents = useMemo(() => (monitoring.events ?? []).filter((event) => {
    const query = search.toLowerCase()
    return (!query || [event.id, event.date, event.time, event.objectType, event.className, event.trackingId, event.direction, event.cameraId].some((value) => String(value ?? '').toLowerCase().includes(query)))
      && (objectType === 'All types' || event.objectType === objectType)
      && (direction === 'All directions' || event.direction === direction)
      && (!date || dateInputValue(event.date) === date)
  }).sort((a, b) => {
    const timeA = new Date(`${a.date} ${a.time}`).getTime()
    const timeB = new Date(`${b.date} ${b.time}`).getTime()
    return sortOrder === 'Newest first' ? timeB - timeA : timeA - timeB
  }), [monitoring.events, search, objectType, direction, date, sortOrder])
  const pages = Math.max(1, Math.ceil(filteredEvents.length / pageSize))
  const visibleEvents = filteredEvents.slice((page - 1) * pageSize, page * pageSize)
  const historyDescription = monitoring.eventsTotal > monitoring.events.length
    ? `Search and review events. ${monitoring.events.length} of ${monitoring.eventsTotal} backend records loaded.`
    : 'Search and review events recorded by your monitoring system.'

  return (
    <>
      <PageHeading eyebrow="EVENT LOG" title="Activity history" description={historyDescription} actions={<button className="button button-secondary" disabled={!filteredEvents.length} onClick={() => downloadCsv(`gatewatch-activity-${dateFileSuffix(new Date())}.csv`, [['Event ID', 'Date', 'Time', 'Object Type', 'Tracking ID', 'Direction', 'Camera ID'], ...filteredEvents.map((event) => [event.id, event.date, event.time, event.className ?? event.objectType, event.trackingId, event.direction, event.cameraId])])}><Download size={16} /> Export loaded events</button>} />
      <section className="panel history-panel">
        <div className="history-toolbar">
          <div className="search-field"><Search size={16} /><input placeholder="Search events..." value={search} onChange={(event) => { setSearch(event.target.value); setPage(1) }} /></div>
          <label className="date-filter"><span>Date</span><input aria-label="Filter by date" type="date" value={date} onChange={(event) => { setDate(event.target.value); setPage(1) }} /></label>
          <div className="filter-select"><ListFilter size={15} /><select value={objectType} onChange={(event) => { setObjectType(event.target.value); setPage(1) }}><option>All types</option><option>Person</option><option>Vehicle</option></select><ChevronDown size={14} /></div>
          <div className="filter-select"><select aria-label="Filter by direction" value={direction} onChange={(event) => { setDirection(event.target.value); setPage(1) }}><option>All directions</option><option>Entry</option><option>Exit</option></select><ChevronDown size={14} /></div>
          <div className="filter-select sort-select"><select aria-label="Sort events" value={sortOrder} onChange={(event) => setSortOrder(event.target.value)}><option>Newest first</option><option>Oldest first</option></select><ChevronDown size={14} /></div>
        </div>
        <EventTable events={visibleEvents} />
        {monitoring.canLoadMoreEvents && <div className="load-more-events"><button className="button button-secondary" onClick={monitoring.loadMoreEvents} disabled={monitoring.isLoadingMoreEvents}>{monitoring.isLoadingMoreEvents && <RefreshCw size={14} />}{monitoring.isLoadingMoreEvents ? 'Loading older events…' : `Load older events (${monitoring.eventsTotal - monitoring.events.length} remaining)`}</button></div>}
        <div className="table-pagination"><span>Showing <strong>{filteredEvents.length ? (page - 1) * pageSize + 1 : 0}–{Math.min(page * pageSize, filteredEvents.length)}</strong> of <strong>{filteredEvents.length}</strong> events</span><div><button aria-label="Previous page" disabled={page <= 1} onClick={() => setPage((current) => current - 1)}><ChevronLeft size={16} /></button><span>Page <strong>{page}</strong> of {pages}</span><button aria-label="Next page" disabled={page >= pages} onClick={() => setPage((current) => current + 1)}><ChevronRight size={16} /></button></div></div>
      </section>
    </>
  )
}

function EventTable({ events, compact = false }) {
  return (
    <div className={`table-scroll ${compact ? 'compact-table' : ''}`}>
      <table className="event-table">
        <thead><tr><th>EVENT</th><th>DATE & TIME</th><th>OBJECT</th><th>TRACKING ID</th><th>DIRECTION</th><th>CAMERA</th></tr></thead>
        <tbody>
          {events.map((event) => <tr key={event.id}><td><span className="event-id">{event.id}</span></td><td><span className="table-date">{event.date}</span><small className="table-time">{event.time}</small></td><td><span className={`object-tag ${event.objectType === 'Person' ? 'object-person' : 'object-vehicle'}`}>{event.objectType === 'Person' ? <Users size={13} /> : <CarFront size={13} />}{event.className ? event.className[0].toUpperCase() + event.className.slice(1) : event.objectType}</span></td><td><span className="tracking-id">{event.trackingId || '—'}</span></td><td><span className={`direction-tag ${event.direction === 'Entry' ? 'direction-entry' : 'direction-exit'}`}>{event.direction === 'Entry' ? <ArrowDownLeft size={13} /> : <ArrowUpRight size={13} />}{event.direction}</span></td><td>{event.cameraId || '—'}</td></tr>)}
          {!events.length && <tr><td colSpan="6"><EmptyState title="No activity records found" text="Try changing your search or filters." compact /></td></tr>}
        </tbody>
      </table>
    </div>
  )
}

function Alerts({ monitoring }) {
  const [activeFilter, setActiveFilter] = useState('All alerts')
  const filters = monitoring.isDemo
    ? ['All alerts', 'Unread', 'System', 'Camera']
    : ['All alerts', 'Open', 'System', 'Camera']
  const [readIds, setReadIds] = useState(() => new Set(
    (monitoring.alerts ?? []).filter((alert) => alert.isRead).map((alert) => alert.id),
  ))
  const alerts = monitoring.alerts ?? []
  const unreadCount = alerts.filter((alert) => !readIds.has(alert.id)).length
  const visibleAlerts = alerts.filter((alert) => {
    if (activeFilter === 'Unread') return !readIds.has(alert.id)
    if (activeFilter === 'Open') return alert.status === 'Open'
    if (activeFilter === 'System' || activeFilter === 'Camera') {
      return String(alert.category ?? '').toLowerCase() === activeFilter.toLowerCase()
    }
    return true
  })

  const markAllAsRead = () => {
    setReadIds((current) => new Set([...current, ...alerts.map((alert) => alert.id)]))
  }
  const toggleRead = (alert) => {
    setReadIds((current) => {
      const next = new Set(current)
      if (next.has(alert.id)) next.delete(alert.id)
      else next.add(alert.id)
      return next
    })
  }

  return (
    <>
      <PageHeading
        eyebrow="SYSTEM NOTIFICATIONS"
        title="Alerts"
        description="Review system and camera notifications from your monitoring service."
        actions={monitoring.isDemo && <button className="button button-secondary" onClick={markAllAsRead} disabled={!unreadCount}><Check size={16} /> Mark all as read</button>}
      />
      <section className="panel alerts-page-panel">
        <div className="alert-filter-tabs">
          {filters.map((filter) => (
            <button key={filter} className={activeFilter === filter ? 'selected' : ''} onClick={() => setActiveFilter(filter)}>
              {filter}{filter === 'All alerts' && <span>{alerts.length}</span>}{filter === 'Unread' && unreadCount > 0 && <span>{unreadCount}</span>}
            </button>
          ))}
        </div>
        {visibleAlerts.length ? visibleAlerts.map((alert) => {
          const isRead = readIds.has(alert.id)
          return (
            <article className={`alert-row ${isRead ? 'alert-row-read' : ''}`} key={alert.id}>
              <div className={`alert-icon ${alert.severity === 'critical' ? 'alert-critical' : alert.severity === 'info' ? 'alert-info' : 'alert-warning'}`}><AlertTriangle size={17} /></div>
              <div className="alert-main">
                <div className="alert-title-row"><strong>{alert.title}</strong><span className={`severity-tag ${alert.severity}`}>{alert.severity}</span></div>
                <p>{alert.description}</p>
                <small><Clock3 size={13} />{alert.date} · {alert.time}</small>
              </div>
              <span className={`alert-status ${alert.status === 'Resolved' ? 'resolved' : ''}`}>{alert.status}</span>
              {monitoring.isDemo && <button className="button button-secondary alert-read-button" onClick={() => toggleRead(alert)}>{isRead ? 'Mark unread' : 'Mark read'}</button>}
            </article>
          )
        }) : <EmptyState title={activeFilter === 'Unread' ? 'You’re all caught up' : 'No alerts in this category'} text={activeFilter === 'Unread' ? 'New unread alerts from your monitoring system will show here.' : 'Alerts from your monitoring system will show here.'} />}
      </section>
    </>
  )
}

function SettingsPage({ monitoring }) {
  const apiStatusLabel = monitoring.isDemo
    ? 'Demo data enabled'
    : monitoring.serviceStatus === 'online'
      ? 'Connected'
      : monitoring.serviceStatus === 'connecting'
        ? 'Connecting'
        : 'Unavailable'

  return (
    <>
      <PageHeading eyebrow="WORKSPACE CONFIGURATION" title="Settings" description="Review the configured backend services and development mode." />
      <section className="panel settings-panel">
        <div className="settings-title"><span className="settings-icon"><LockKeyhole size={18} /></span><div><h2>Backend connection</h2><p>REST, WebSocket, and camera stream addresses are configured through the frontend environment.</p></div></div>
        <div className="settings-status-row"><div><strong>Data source</strong><small>{monitoring.isDemo ? 'Local sample data; not live monitoring data' : monitoring.apiBaseUrl}</small></div><span className={`health-state ${monitoring.isDemo ? 'state-muted' : monitoring.serviceStatus === 'online' ? 'state-green' : 'state-orange'}`}>{apiStatusLabel}</span></div>
        <div className="settings-status-row"><div><strong>Realtime channel</strong><small>{monitoring.isDemo ? 'Disabled in demo mode' : monitoring.websocketStatus}</small></div><span className={`health-state ${monitoring.websocketStatus === 'connected' ? 'state-green' : 'state-muted'}`}>{monitoring.isDemo ? 'Demo mode' : monitoring.websocketStatus}</span></div>
        <div className="settings-status-row"><div><strong>Monitoring service</strong><small>{monitoring.isActive == null ? 'Active state not confirmed' : monitoring.isActive ? 'Backend confirmed monitoring is active' : 'Backend confirmed monitoring is stopped'}</small></div><span className={`health-state ${monitoring.isActive ? 'state-green' : 'state-muted'}`}>{monitoring.isActive == null ? 'Unknown' : monitoring.isActive ? 'Active' : 'Stopped'}</span></div>
        <div className="settings-status-row"><div><strong>Camera stream</strong><small>{monitoring.cameraUrl || 'No camera stream URL configured'}</small></div><span className={`health-state ${monitoring.cameraConnected ? 'state-green' : 'state-muted'}`}>{monitoring.cameraConnected ? 'Playing' : 'Not connected'}</span></div>
        <div className="settings-callout"><CircleHelp size={17} /><span>Production integration follows the repository's <code>docs/api_contract.md</code>. Set <code>VITE_DEMO_MODE=false</code> and configure <code>VITE_API_BASE_URL</code> before starting Vite to use the FastAPI endpoints.</span></div>
        <div className="settings-actions"><span className="settings-footnote">Restart the Vite development server after editing <code>.env.local</code>.</span></div>
      </section>
    </>
  )
}

function EmptyState({ title, text, compact = false }) {
  return <div className={`empty-state ${compact ? 'empty-state-compact' : ''}`}><span><Search size={18} /></span><strong>{title}</strong><p>{text}</p></div>
}

function dateInputValue(value) {
  const dateText = String(value ?? '')
  const isoDate = dateText.match(/^\d{4}-\d{2}-\d{2}/)
  if (isoDate) return isoDate[0]

  const parsedDate = new Date(dateText)
  if (Number.isNaN(parsedDate.getTime())) return ''

  const year = parsedDate.getFullYear()
  const month = String(parsedDate.getMonth() + 1).padStart(2, '0')
  const day = String(parsedDate.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function dateFileSuffix(date) {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  return `${year}-${month}-${day}`
}

function downloadCsv(filename, rows) {
  const csv = rows
    .map((row) => row.map((value) => `"${String(value ?? '').replace(/"/g, '""')}"`).join(','))
    .join('\r\n')
  const file = new Blob([`\uFEFF${csv}`], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(file)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.setTimeout(() => URL.revokeObjectURL(url), 0)
}

function formatMetric(value) {
  return value == null ? '—' : Number(value).toLocaleString()
}

const tooltipStyle = { border: '1px solid #e8ebf0', borderRadius: 9, boxShadow: '0 8px 24px rgba(26, 43, 74, .10)', fontSize: 12 }

export default App
