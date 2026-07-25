'use client';

import { useEffect, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { getRtdb } from '../lib/firebase';
import { toMillis, type BotStatus as BotStatusT, type Position, type RiskState } from '../lib/types';

// 5 min: lo scan di mercato (ogni 4h) puo' bloccare il ciclo 1-3 min mentre
// scarica le candele dell'intero universo; 2 min era troppo stretto e faceva
// sfarfallare il badge su OFFLINE pur essendo il bot vivo.
const HEARTBEAT_STALE_MS = 5 * 60 * 1000; // 5 minutes

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
  const [positions, setPositions] = useState<Position[]>([]);
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
    const unsubPos = onValue(ref(db, 'positions'), (snap) => {
      const val = snap.val() as Record<string, Position> | null;
      setPositions(val ? Object.values(val) : []);
    });
    // re-evaluate heartbeat freshness every 15s even without new data
    const tick = setInterval(() => setNow(Date.now()), 15000);
    return () => {
      unsubStatus();
      unsubRisk();
      unsubEquity();
      unsubPos();
      clearInterval(tick);
    };
  }, []);

  // --- scomposizione dell'equity ---
  // Il bot pubblica /account/equity = capitale iniziale + PnL REALIZZATO (non
  // include il PnL delle posizioni aperte, ne' sottrae il margine). Qui deriviamo
  // il quadro completo dai dati delle posizioni:
  //   uPnL aperto        = somma dei PnL non realizzati
  //   equity mark-to-mkt = bilancio realizzato + uPnL aperto (patrimonio reale ora)
  //   margine usato      = somma(notional/leva) bloccato come collaterale
  //   margine libero     = equity MtM - margine usato (liquidita' per nuovi trade)
  const uPnl = positions.reduce((s, p) => s + (p.unrealized_pnl ?? 0), 0);
  const marginUsed = positions.reduce((s, p) => {
    const notional = (p.entry_price ?? 0) * (p.quantity ?? 0);
    const lev = p.leverage && p.leverage > 0 ? p.leverage : 1;
    return s + notional / lev;
  }, 0);
  const equityMtm = equity != null ? equity + uPnl : null;
  const freeMargin = equityMtm != null ? equityMtm - marginUsed : null;
  const usd = (n: number) => `$${n.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;

  const heartbeatMs = toMillis(status?.heartbeat ?? status?.updated_at ?? null);
  const online = heartbeatMs != null && now - heartbeatMs < HEARTBEAT_STALE_MS;
  const running = (status?.state ?? '').toLowerCase() === 'running';
  const dryRun = status?.dry_run ?? true;

  // Effective values may come from bot_status or a dedicated risk_state path.
  const effLeverage = riskState?.effective_leverage ?? status?.effective_leverage;
  const effRisk = riskState?.effective_risk_per_trade ?? status?.effective_risk_per_trade;

  return (
    <div className="panel">
      <div className="status-strip">
        <div className="left">
          <strong style={{ fontSize: 16 }}>Trading Bot</strong>
        </div>
        <div className="status-badges">
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

          <span className="badge gray">regime: {status?.regime ?? 'n/a'}</span>
        </div>
      </div>

      <div className="stat-grid">
        {equityMtm != null && (
          <div className="stat-tile hero accent">
            <div className="stat-label">Equity · mark-to-market</div>
            <div className="stat-value">{usd(equityMtm)}</div>
            <div className="stat-sub">
              patrimonio reale ora (bilancio + uPnL aperto)
            </div>
          </div>
        )}

        {equity != null && (
          <>
            <div className="stat-tile">
              <div className="stat-label">Bilancio · realizzato</div>
              <div className="stat-value">{usd(equity)}</div>
            </div>

            <div className={`stat-tile ${uPnl >= 0 ? 'good' : 'bad'}`}>
              <div className="stat-label">uPnL aperto</div>
              <div className={`stat-value ${uPnl >= 0 ? 'pos' : 'neg'}`}>
                {uPnl >= 0 ? '+' : ''}
                {usd(uPnl).replace('$', '')}
              </div>
            </div>

            <div className="stat-tile">
              <div className="stat-label">Margine usato</div>
              <div className="stat-value">{usd(marginUsed)}</div>
            </div>

            <div className="stat-tile">
              <div className="stat-label">Margine libero</div>
              <div className="stat-value">
                {freeMargin != null ? usd(freeMargin) : '—'}
              </div>
            </div>
          </>
        )}

        <div className="stat-tile warnb">
          <div className="stat-label">Leva effettiva</div>
          <div className="stat-value">
            {effLeverage != null ? `${effLeverage}x` : '—'}
          </div>
          <div className="stat-sub">
            {effLeverage != null ? 'guidata da conviction + learning' : 'in attesa di pubblicazione'}
          </div>
        </div>

        <div className="stat-tile warnb">
          <div className="stat-label">Rischio / trade</div>
          <div className="stat-value">
            {effRisk != null ? `${(effRisk * 100).toFixed(2)}%` : '—'}
          </div>
          <div className="stat-sub">
            {effRisk != null ? 'sotto i cap di sicurezza' : 'in attesa di pubblicazione'}
          </div>
        </div>
      </div>

      <div className="muted" style={{ marginTop: 12, fontSize: 12 }}>
        Heartbeat: {timeAgo(heartbeatMs)}
      </div>
    </div>
  );
}
