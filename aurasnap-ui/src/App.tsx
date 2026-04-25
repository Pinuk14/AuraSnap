import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster } from 'react-hot-toast';
import Dashboard from './pages/Dashboard';
import AddEvent from './pages/AddEvent';
import UpdateEvents from './pages/UpdateEvents';
import Capture from './pages/Capture';
import Magic from './pages/Magic';
import Watermark from './pages/Watermark';
import SettingsPage from './pages/SettingsPage';
import { apiFetch } from './api';
import type { Settings } from './api';
import GlassFilter from './components/GlassFilter';
import LiquidToggle from './components/LiquidToggle';

type Page = 'dashboard' | 'add-event' | 'update-events' | 'capture' | 'magic' | 'watermark' | 'settings';

const NAV_ITEMS: { id: Page; label: string; icon: string }[] = [
  { id: 'dashboard',     label: 'Dashboard',    icon: '⊞' },
  { id: 'add-event',     label: 'Add Event',    icon: '⊕' },
  { id: 'update-events', label: 'Manage Events',icon: '☰' },
  { id: 'capture',       label: 'Capture',      icon: '⊙' },
  { id: 'magic',         label: 'Magic',        icon: '✦' },
  { id: 'watermark',     label: 'Watermark',    icon: '▧' },
  { id: 'settings',      label: 'Settings',     icon: '⚙' },
];

const PAGE_COMPONENTS: Record<Page, React.ReactNode> = {
  dashboard:     <Dashboard />,
  'add-event':   <AddEvent />,
  'update-events': <UpdateEvents />,
  capture:       <Capture />,
  magic:         <Magic />,
  watermark:     <Watermark />,
  settings:      <SettingsPage />,
};

export default function App() {
  const [page, setPage] = useState<Page>('dashboard');
  const [phone, setPhone] = useState('');
  const [isDark, setIsDark] = useState(true);

  useEffect(() => {
    apiFetch<Settings>('/settings').then(s => setPhone(s.Number ?? '')).catch(() => {});
  }, []);

  const toggleTheme = (val: boolean) => {
    setIsDark(!val);
    if (val) {
      document.body.classList.add('light-theme');
    } else {
      document.body.classList.remove('light-theme');
    }
  };

  return (
    <>
      {/* SVG Glass Filters — rendered once for all Liquid Glass components */}
      <GlassFilter />
      {/* Animated aurora background */}
      <div className="aurora-bg">
        <div className="aurora-blob aurora-blob-1" />
        <div className="aurora-blob aurora-blob-2" />
        <div className="aurora-blob aurora-blob-3" />
      </div>

      <div style={{ display: 'flex', height: '100vh', position: 'relative', zIndex: 1, justifyContent: 'flex-start' }}>
        {/* ─── SIDEBAR ─────────────────────────────────────── */}
        <aside className="sidebar">
          <div className="sidebar-header">
            <div className="sidebar-logo">AuraSnap</div>
            <div className="sidebar-tagline">Capture • Recognize • Deliver</div>
          </div>

          <nav className="sidebar-nav" style={{ marginTop: '32px' }}>
            {NAV_ITEMS.map(item => (
              <button
                key={item.id}
                className={`nav-btn${page === item.id ? ' active' : ''}`}
                onClick={() => setPage(item.id)}
              >
                <div className="nav-icon">{item.icon}</div>
                <span className="nav-label">{item.label}</span>
              </button>
            ))}
          </nav>

          <div className="sidebar-bottom">
            <div className="sidebar-divider" />
            <div style={{ padding: '4px 8px' }}>
              <LiquidToggle
                label="Theme"
                size="sm"
                checked={!isDark}
                onChange={toggleTheme}
              />
            </div>
            
            {phone && (
              <div className="phone-badge">
                <span className="nav-icon" style={{ fontSize: '0.9rem', opacity: 0.7 }}>📱</span>
                <span style={{ fontWeight: 600 }}>{phone}</span>
              </div>
            )}

            <div style={{ marginTop: '24px', opacity: 0.6 }}>
              <p style={{ fontFamily: 'var(--font-elegant)', fontSize: '0.65rem', fontStyle: 'italic', lineHeight: 1.5 }}>
                "Photography is the art of freezing moments, so they can live forever in our memories."
              </p>
            </div>
          </div>
        </aside>

        {/* ─── MAIN CONTENT ────────────────────────────────── */}
        <main className="main-content">
          <div className="content-inner">
            <AnimatePresence mode="wait">
              <motion.div
                key={page}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                transition={{ duration: 0.25 }}
              >
                {PAGE_COMPONENTS[page]}
              </motion.div>
            </AnimatePresence>
          </div>
        </main>
      </div>

      <Toaster
        position="bottom-right"
        toastOptions={{
          style: {
            background: 'rgba(20,14,35,0.95)',
            color: 'var(--color-text-primary)',
            border: '1px solid var(--color-glass-border)',
            backdropFilter: 'blur(16px)',
            fontFamily: 'var(--font-ui)',
            fontSize: '0.875rem',
          },
          success: { iconTheme: { primary: '#4ecd70', secondary: '#0a0612' } },
          error:   { iconTheme: { primary: '#f06292', secondary: '#0a0612' } },
        }}
      />
    </>
  );
}
