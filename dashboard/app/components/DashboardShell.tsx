'use client';

import { useEffect, useMemo, useState } from 'react';
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

type TabId = 'panoramica' | 'operativita' | 'apprendimento' | 'strategie' | 'rischio';

const TABS: { id: TabId; label: string; intro: string }[] = [
  { id: 'panoramica', label: 'Panoramica', intro: 'Stato del bot, ultima decisione e curva di equity.' },
  { id: 'operativita', label: 'Operatività', intro: 'Posizioni aperte e trade chiusi (con verdetto sul trailing).' },
  { id: 'apprendimento', label: 'Apprendimento', intro: 'Pesi strategia × regime, heatmap e insight del learning.' },
  { id: 'strategie', label: 'Strategie (GATE 1)', intro: 'Registro delle coppie validate dal backtest walk-forward.' },
  { id: 'rischio', label: 'Rischio', intro: 'Parametri di rischio e kill switch di emergenza.' },
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

  const intro = useMemo(() => TABS.find((t) => t.id === tab)?.intro ?? '', [tab]);

  return (
    <div>
      <div className="topbar">
        <div className="topbar-row">
          <div className="brand">
            Agentic Trading
            <span className="brand-dim">· paper</span>
          </div>
          {user && (
            <div className="vitals">
              <span className="muted" style={{ fontSize: 12 }}>{user.email ?? user.uid}</span>
              <button onClick={() => signOut(getAuthInstance())} className="btn btn-ghost" style={{ padding: '4px 10px', fontSize: 12 }}>
                Esci
              </button>
            </div>
          )}
        </div>
        <div className="tabs" role="tablist">
          {TABS.map((t) => (
            <button
              key={t.id}
              role="tab"
              aria-selected={tab === t.id}
              className={`tab ${tab === t.id ? 'active' : ''}`}
              onClick={() => select(t.id)}
            >
              {t.label}
            </button>
          ))}
        </div>
      </div>

      <p className="section-intro">{intro}</p>

      <div className="grid" key={tab}>
        {tab === 'panoramica' && (
          <>
            <BotStatus />
            <DecisionStatus />
            <EquityCurve />
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
    </div>
  );
}
