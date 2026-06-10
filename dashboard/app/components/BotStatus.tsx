'use client';

import { useEffect, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { getRtdb } from '../lib/firebase';
import { toMillis, type BotStatus as BotStatusT, type RiskState } from '../lib/types';

const HEARTBEAT_STALE_MS = 2 * 60 * 1000; // 2 minutes

function timeAgo(ms: number | null): string {
  if (ms == null) return 'unknown';
  const diff = Date.now() - ms;
  if (diff < 0) return 'just now';
  const s = Math.floor(diff / 1000);
  if (s < 60) return `${s}s ago`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  return `${h}h ago`;
}

export default function BotStatus() {
  const [status, setStatus] = useState<BotStatusT | null>(null);
  const [riskState, setRiskState] = useState<RiskState | null>(null);
  const [equity, setEquity] = useState<number | null>(null);
  const [now, setNow] = useState(Date.now());

  useEffect(() => {
    const db = getRtdb();
    const unsubStatus = onValue(ref(db, 'bot_status'), (snap) => {
      setStatus(snap.exists() ? (snap.val() as BotStatusT) : null);
    });
    const unsubRisk = onValue(ref(db, 'risk_state'), (snap) => {
      setRiskState(snap.exists() ? (snap.val() as RiskState) : null);
    });
    const unsubEquity = onValue(ref(db, 'account/equity'), (snap) => {
      setEquity(snap.exists() ? Number(snap.val()) : null);
    });
    // re-evaluate heartbeat freshness every 15s even without new data
    const tick = setInterval(() => setNow(Date.now()), 15000);
    return () => {
      unsubStatus();
      unsubRisk();
      unsubEquity();
      clearInterval(tick);
    };
  }, []);

  const heartbeatMs = toMillis(status?.heartbeat ?? status?.updated_at ?? null);
  const online = heartbeatMs != null && now - heartbeatMs < HEARTBEAT_STALE_MS;
  const running = (status?.state ?? '').toLowerCase() === 'running';
  const dryRun = status?.dry_run ?? true;

  // Effective values may come from bot_status or a dedicated risk_state path.
  const effLeverage = riskState?.effective_leverage ?? status?.effective_leverage;
  const effRisk = riskState?.effective_risk_per_trade ?? status?.effective_risk_per_trade;

  return (
    <div className="panel">
      <div className="header-bar">
        <div className="left">
          <strong style={{ fontSize: 16 }}>Trading Bot</strong>

          <span className={`badge ${running ? 'green' : 'red'}`}>
            <span
              className="dot"
              style={{ background: running ? 'var(--green)' : 'var(--red)' }}
            />
            {status?.state ? status.state.toUpperCase() : 'UNKNOWN'}
          </span>

          <span className={`badge ${online ? 'green' : 'red'}`}>
            {online ? 'ONLINE' : 'OFFLINE'}
          </span>

          <span className={`badge ${dryRun ? 'amber' : 'red'}`}>
            {dryRun ? 'DRY_RUN' : 'LIVE'}
          </span>

          <span className="badge gray">
            regime: {status?.regime ?? 'n/a'}
          </span>
        </div>

        <div className="kpi">
          {equity != null && (
            <div className="item">
              <div className="label">Equity</div>
              <div className="value mono">
                ${equity.toLocaleString(undefined, { maximumFractionDigits: 2 })}
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="muted" style={{ marginTop: 10, fontSize: 12 }}>
        Heartbeat: {timeAgo(heartbeatMs)}
        {' · '}
        Effective leverage:{' '}
        {effLeverage != null ? (
          <strong className="mono">{effLeverage}x</strong>
        ) : (
          <span className="muted">shown when the bot publishes it</span>
        )}
        {' · '}
        Effective risk/trade:{' '}
        {effRisk != null ? (
          <strong className="mono">{(effRisk * 100).toFixed(2)}%</strong>
        ) : (
          <span className="muted">shown when published</span>
        )}
      </div>
    </div>
  );
}
