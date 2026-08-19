'use client';

import { useEffect, useMemo, useState, type ReactNode } from 'react';
import { onAuthStateChanged, signOut, type User } from 'firebase/auth';
import { getAuthInstance } from '../lib/firebase';

import BotStatus from './BotStatus';
import DailySnapshot from './DailySnapshot';
import EquityCurve from './EquityCurve';
import OperativitaTab from './OperativitaTab';
import StrategyWeights from './StrategyWeights';
import TrailingLearning from './TrailingLearning';
import Heatmap from './Heatmap';
import OptimizedStrategies from './OptimizedStrategies';
import Insights from './Insights';
import RiskControl from './RiskControl';
import KillSwitch from './KillSwitch';
import TopVitals from './TopVitals';
import LearningSummary from './LearningSummary';
import SentimentAnalysis from './SentimentAnalysis';
import RegimeIntelligence from './RegimeIntelligence';
import AssetScoring from './AssetScoring';
import LearningEvolution from './LearningEvolution';
import PortfolioRisk from './PortfolioRisk';
import ReconcilerStatus from './ReconcilerStatus';
import OperatingCosts from './OperatingCosts';
import OrchestratorShadow from './OrchestratorShadow';
import SupervisorDecisions from './SupervisorDecisions';
import GateAutopsy from './GateAutopsy';
import GateFunnel from './GateFunnel';
import GateEvolution from './GateEvolution';
import ClaudeChat from './ClaudeChat';

type TabId =
  | 'panoramica'
  | 'operativita'
  | 'apprendimento'
  | 'ricerca'
  | 'sentiment'
  | 'strategie'
  | 'claude'
  | 'impostazioni';
type NavId = Exclude<TabId, 'impostazioni'>;

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
    operativita: <path d="M3 12h4l3 7 4-14 3 7h4" />,
    // ricerca: una lente — questa tab guarda DENTRO il gate, non i risultati
    ricerca: (
      <>
        <circle cx="11" cy="11" r="7" />
        <path d="M20 20l-4.2-4.2" />
      </>
    ),
    // claude: un fumetto, perche' e' l'unico posto della dashboard dove si SCRIVE
    claude: <path d="M21 12a8 8 0 0 1-8 8H4l2.2-2.6A8 8 0 1 1 21 12z" />,
    apprendimento: (
      <>
        <path d="M12 3l9 5-9 5-9-5 9-5z" />
        <path d="M21 8v5" />
        <path d="M7 10.5V15c0 1.5 2.5 3 5 3s5-1.5 5-3v-4.5" />
      </>
    ),
    sentiment: (
      <>
        <path d="M4 16a8 8 0 0 1 16 0" />
        <path d="M12 16l4-3.5" />
        <circle cx="12" cy="16" r="1.4" />
      </>
    ),
    strategie: (
      <>
        <circle cx="12" cy="12" r="8" />
        <circle cx="12" cy="12" r="3.5" />
        <path d="M12 2v3M12 19v3M2 12h3M19 12h3" />
      </>
    ),
    impostazioni: (
      <>
        <circle cx="12" cy="12" r="3" />
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
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

const META: Record<TabId, { label: string; title: string; intro: string }> = {
  panoramica: {
    label: 'Panoramica',
    title: 'Panoramica',
    intro: 'Stato del bot, equity mark-to-market, ultima decisione e curva di equity.',
  },
  operativita: {
    label: 'Operatività',
    title: 'Operatività',
    intro: 'Posizioni aperte e trade chiusi (con verdetto sul trailing).',
  },
  apprendimento: {
    label: 'Apprendimento',
    title: 'Apprendimento',
    intro: 'Cosa sta imparando il bot: pesi strategia × regime, trailing adattivo e diario.',
  },
  sentiment: {
    label: 'Sentiment',
    title: 'Sentiment analysis',
    intro: 'Fear & Greed di mercato e sentiment delle coin: la fonte che orienta le decisioni.',
  },
  ricerca: {
    label: 'Ricerca',
    title: 'Ricerca · dentro il GATE 1',
    intro:
      'Le decisioni che il sistema prende da solo, dove muoiono le candidate e come '
      + 'si muove il fronte di validazione nel tempo.',
  },
  claude: {
    label: 'Claude',
    title: 'Claude',
    intro:
      'Scrivi al sistema da qui: la domanda arriva a una sessione di Claude con '
      + 'accesso al repo, che risponde nel thread.',
  },
  strategie: {
    label: 'Strategie',
    title: 'Strategie · GATE 1',
    intro: 'Catalogo delle strategie validate dal backtest walk-forward.',
  },
  impostazioni: {
    label: 'Impostazioni',
    title: 'Impostazioni · Rischio',
    intro: 'Parametri di leva e rischio, entro i cap di sicurezza applicati dal bot.',
  },
};

const NAV: NavId[] = ['panoramica', 'operativita', 'apprendimento', 'ricerca',
                      'sentiment', 'strategie', 'claude'];

function isTab(v: string): v is TabId {
  return v in META;
}

export default function DashboardShell() {
  const [tab, setTab] = useState<TabId>('panoramica');
  const [user, setUser] = useState<User | null>(null);
  const [collapsed, setCollapsed] = useState(false);

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

  // preferenza sidebar compressa
  useEffect(() => {
    try {
      setCollapsed(localStorage.getItem('sidebar_collapsed') === '1');
    } catch {
      /* ignore */
    }
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

  const toggleCollapse = () => {
    setCollapsed((c) => {
      const next = !c;
      try {
        localStorage.setItem('sidebar_collapsed', next ? '1' : '0');
      } catch {
        /* ignore */
      }
      return next;
    });
  };

  const current = useMemo(() => META[tab], [tab]);

  return (
    <div className="app-shell">
      <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-brand">
          <span className="logo" aria-hidden="true">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 15c3 0 3-6 6-6s3 6 6 6 3-4 6-4" />
            </svg>
          </span>
          <span className="brand-text">
            Agentic Trading
            <span className="brand-sub">crypto futures · autonomo</span>
          </span>
        </div>

        <button className="sidebar-toggle" onClick={toggleCollapse} title={collapsed ? 'Espandi' : 'Comprimi'} aria-label="comprimi/espandi menu">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ transform: collapsed ? 'rotate(180deg)' : 'none' }}>
            <path d="M15 18l-6-6 6-6" />
          </svg>
          <span className="toggle-label">Comprimi</span>
        </button>

        <div className="nav-section-label">Navigazione</div>
        <nav className="sidebar-nav" role="tablist">
          {NAV.map((id) => (
            <button
              key={id}
              role="tab"
              aria-selected={tab === id}
              title={META[id].label}
              className={`nav-item ${tab === id ? 'active' : ''}`}
              onClick={() => select(id)}
            >
              <Icon id={id} />
              <span className="nav-label">{META[id].label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button
            role="tab"
            aria-selected={tab === 'impostazioni'}
            title="Impostazioni"
            className={`nav-item ${tab === 'impostazioni' ? 'active' : ''}`}
            onClick={() => select('impostazioni')}
          >
            <Icon id="impostazioni" />
            <span className="nav-label">Impostazioni</span>
          </button>

          <span className="dry-pill" title="Paper trading (DRY_RUN)">
            <span className="dot" style={{ background: 'var(--amber)' }} />
            <span className="dry-text">DRY_RUN · paper</span>
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
                <span className="nav-label">Esci</span>
                <span aria-hidden="true" style={{ display: collapsed ? 'inline' : 'none' }}>⎋</span>
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
          <div className="top-vitals">
            <TopVitals />
            <KillSwitch variant="button" />
          </div>
        </header>

        <div className="grid" key={tab} style={{ marginTop: 16 }}>
          {tab === 'panoramica' && (
            <>
              <BotStatus />
              <div className="grid grid-2">
                <EquityCurve />
                <DailySnapshot />
              </div>
              <div className="grid grid-2">
                <RegimeIntelligence />
                <PortfolioRisk />
              </div>
            </>
          )}

          {tab === 'operativita' && (
            <>
              <OperativitaTab />
              <OperatingCosts />
            </>
          )}

          {tab === 'apprendimento' && (
            <>
              <LearningSummary />
              <div className="grid grid-2">
                <StrategyWeights />
                <Heatmap />
              </div>
              <LearningEvolution />
              <OrchestratorShadow />
              <TrailingLearning />
              <Insights />
            </>
          )}

          {tab === 'ricerca' && (
            <>
              <GateFunnel />
              <GateEvolution />
              <SupervisorDecisions />
              <GateAutopsy />
            </>
          )}

          {tab === 'claude' && <ClaudeChat />}

          {tab === 'sentiment' && <SentimentAnalysis />}

          {tab === 'strategie' && (
            <>
              <OptimizedStrategies />
              <AssetScoring />
            </>
          )}

          {tab === 'impostazioni' && (
            <>
              <RiskControl />
              <KillSwitch />
              <ReconcilerStatus />
            </>
          )}
        </div>
      </main>
    </div>
  );
}
