'use client';

import { useEffect, useMemo, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { onAuthStateChanged, signOut, type User } from 'firebase/auth';
import { getRtdb, getAuthInstance } from '../lib/firebase';
import { toMillis, type BotStatus as BotStatusT } from '../lib/types';

import BotStatus from './BotStatus';
import DecisionStatus from './DecisionStatus';
import EquityCurve from './EquityCurve';
import Positions from './Positions';
import ClosedTrades from './ClosedTrades';
import StrategyWeights from './StrategyWeights';
import Heatmap from './Heatmap';
import OptimizedStrategies from './OptimizedStrategies';
import Insights from './Insights';
import RiskControl from './RiskControl';
import KillSwitch from './KillSwitch';

const HEARTBEAT_STALE_MS = 5 * 60 * 1000;

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

/** Striscia vitali sempre visibile: non perdi mai il polso del bot cambiando tab. */
function Vitals() {
  const [status, setStatus] = useState<BotStatusT | null>(null);
  const [equity, setEquity] = useState<number | null>(null);
  const [now, setNow] = useState(0);

  useEffect(() => {
    const db = getRtdb();
    const unsubStatus = onValue(ref(db, 'bot_status'), (snap) => {
      setStatus(snap.exists() ? (snap.val() as BotStatusT) : null);
    });
    const unsubEquity = onValue(ref(db, 'account/equity'), (snap) => {
      setEquity(snap.exists() ? Number(snap.val()) : null);
    });
    setNow(Date.now());
    const tick = setInterval(() => setNow(Date.now()), 15000);
    return () => {
      unsubStatus();
      unsubEquity();
      clearInterval(tick);
    };
  }, []);

  const heartbeatMs = toMillis(status?.heartbeat ?? status?.updated_at ?? null);
  const online = heartbeatMs != null && now > 0 && now - heartbeatMs < HEARTBEAT_STALE_MS;
  const dryRun = status?.dry_run ?? true;

  return (
    <div className="vitals">
      <span className={`badge ${online ? 'green' : 'red'}`}>
        <span className="dot" style={{ background: online ? 'var(--green)' : 'var(--red)' }} />
        {online ? 'ONLINE' : 'OFFLINE'}
      </span>
      <span className={`badge ${dryRun ? 'amber' : 'red'}`}>{dryRun ? 'DRY_RUN' : 'LIVE'}</span>
      <span className="badge gray">{status?.regime ?? 'n/a'}</span>
      {equity != null && (
        <span className="equity mono">
          ${equity.toLocaleString(undefined, { maximumFractionDigits: 2 })}
        </span>
      )}
    </div>
  );
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
          <div className="vitals">
            <Vitals />
            {user && (
              <>
                <span className="muted" style={{ fontSize: 12 }}>{user.email ?? user.uid}</span>
                <button onClick={() => signOut(getAuthInstance())} className="btn btn-ghost" style={{ padding: '4px 10px', fontSize: 12 }}>
                  Esci
                </button>
              </>
            )}
          </div>
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

      <div className="grid">
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
