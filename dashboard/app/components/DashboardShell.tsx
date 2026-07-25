'use client';

import { useEffect, useMemo, useState, type ReactNode } from 'react';
import { onAuthStateChanged, signOut, type User } from 'firebase/auth';
import { getAuthInstance } from '../lib/firebase';

import BotStatus from './BotStatus';
import DecisionStatus from './DecisionStatus';
import EquityCurve from './EquityCurve';
import Positions from './Positions';
import ClosedTrades from './ClosedTrades';
import StrategyWeights from './StrategyWeights';
import TrailingLearning from './TrailingLearning';
import Heatmap from './Heatmap';
import OptimizedStrategies from './OptimizedStrategies';
import Insights from './Insights';
import RiskControl from './RiskControl';
import KillSwitch from './KillSwitch';
import TopVitals from './TopVitals';

type TabId = 'panoramica' | 'operativita' | 'apprendimento' | 'strategie' | 'rischio';

/* --- icone (inline SVG, stroke = currentColor) ---------------------------- */
function Icon({ id }: { id: TabId }) {
  const p: Record<TabId, ReactNode> = {
    panoramica: (
      <>
        <rect x="3" y="3" width="7" height="7" rx="1.5" />
        <rect x="14" y="3" width="7" height="7" rx="1.5" />
        <rect x="14" y="14" width="7" height="7" rx="1.5" />
        <rect x="3" y="14" width="7" height="7" rx="1.5" />
      </>
    ),
    operativita: (
      <>
        <path d="M3 12h4l3 7 4-14 3 7h4" />
      </>
    ),
    apprendimento: (
      <>
        <path d="M12 3l9 5-9 5-9-5 9-5z" />
        <path d="M21 8v5" />
        <path d="M7 10.5V15c0 1.5 2.5 3 5 3s5-1.5 5-3v-4.5" />
      </>
    ),
    strategie: (
      <>
        <circle cx="12" cy="12" r="8" />
        <circle cx="12" cy="12" r="3.5" />
        <path d="M12 2v3M12 19v3M2 12h3M19 12h3" />
      </>
    ),
    rischio: (
      <>
        <path d="M12 3l7 3v6c0 4.5-3 7.5-7 9-4-1.5-7-4.5-7-9V6l7-3z" />
      </>
    ),
  };
  return (
    <svg
      className="nav-ico"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.9"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {p[id]}
    </svg>
  );
}

const TABS: { id: TabId; label: string; title: string; intro: string }[] = [
  {
    id: 'panoramica',
    label: 'Panoramica',
    title: 'Panoramica',
    intro: 'Stato del bot, equity mark-to-market, ultima decisione e curva di equity.',
  },
  {
    id: 'operativita',
    label: 'Operatività',
    title: 'Operatività',
    intro: 'Posizioni aperte e trade chiusi (con verdetto sul trailing).',
  },
  {
    id: 'apprendimento',
    label: 'Apprendimento',
    title: 'Apprendimento',
    intro: 'Pesi strategia × regime, heatmap e insight del learning.',
  },
  {
    id: 'strategie',
    label: 'Strategie',
    title: 'Strategie · GATE 1',
    intro: 'Registro delle coppie validate dal backtest walk-forward.',
  },
  {
    id: 'rischio',
    label: 'Rischio',
    title: 'Rischio',
    intro: 'Parametri di rischio e kill switch di emergenza.',
  },
];

function isTab(v: string): v is TabId {
  return TABS.some((t) => t.id === v);
}

export default function DashboardShell() {
  const [tab, setTab] = useState<TabId>('panoramica');
  const [user, setUser] = useState<User | null>(null);

  // deep-link + persistenza al refresh via hash (#operativita)
  useEffect(() => {
    const sync = () => {
      const h = window.location.hash.replace('#', '');
      if (isTab(h)) setTab(h);
    };
    sync();
    window.addEventListener('hashchange', sync);
    return () => window.removeEventListener('hashchange', sync);
  }, []);

  useEffect(() => {
    try {
      const unsub = onAuthStateChanged(getAuthInstance(), (u) => setUser(u));
      return () => unsub();
    } catch {
      /* auth non inizializzata: ignora, il gate lo gestisce a monte */
    }
  }, []);

  const select = (id: TabId) => {
    setTab(id);
    if (typeof window !== 'undefined') window.location.hash = id;
  };

  const current = useMemo(() => TABS.find((t) => t.id === tab) ?? TABS[0], [tab]);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <span className="logo" aria-hidden="true">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 15c3 0 3-6 6-6s3 6 6 6 3-4 6-4" />
            </svg>
          </span>
          <span>
            Agentic Trading
            <span className="brand-sub">crypto futures · autonomo</span>
          </span>
        </div>

        <div className="nav-section-label">Navigazione</div>
        <nav className="sidebar-nav" role="tablist">
          {TABS.map((t) => (
            <button
              key={t.id}
              role="tab"
              aria-selected={tab === t.id}
              className={`nav-item ${tab === t.id ? 'active' : ''}`}
              onClick={() => select(t.id)}
            >
              <Icon id={t.id} />
              {t.label}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <span className="dry-pill">
            <span className="dot" style={{ background: 'var(--amber)' }} />
            DRY_RUN · paper
          </span>
          {user && (
            <>
              <span className="sidebar-user" title={user.email ?? user.uid}>
                {user.email ?? user.uid}
              </span>
              <button
                onClick={() => signOut(getAuthInstance())}
                className="btn btn-ghost"
                style={{ padding: '6px 12px', fontSize: 12 }}
              >
                Esci
              </button>
            </>
          )}
        </div>
      </aside>

      <main className="main">
        <header className="main-top">
          <div>
            <div className="page-title">{current.title}</div>
            <span className="page-sub">{current.intro}</span>
          </div>
          <TopVitals />
        </header>

        <div className="grid" key={tab} style={{ marginTop: 16 }}>
          {tab === 'panoramica' && (
            <>
              <BotStatus />
              <div className="grid grid-2">
                <EquityCurve />
                <DecisionStatus />
              </div>
            </>
          )}

          {tab === 'operativita' && (
            <>
              <Positions />
              <ClosedTrades />
            </>
          )}

          {tab === 'apprendimento' && (
            <>
              <div className="grid grid-2">
                <StrategyWeights />
                <Heatmap />
              </div>
              <TrailingLearning />
              <Insights />
            </>
          )}

          {tab === 'strategie' && <OptimizedStrategies />}

          {tab === 'rischio' && (
            <div className="grid grid-2">
              <RiskControl />
              <KillSwitch />
            </div>
          )}
        </div>
      </main>
    </div>
  );
}
