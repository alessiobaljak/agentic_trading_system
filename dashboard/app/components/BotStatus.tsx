'use client';

import { useEffect, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { getRtdb } from '../lib/firebase';
import { toMillis, type BotStatus as BotStatusT, type Position, type RiskState } from '../lib/types';

// 5 min: lo scan di mercato (ogni 4h) puo' bloccare il ciclo 1-3 min mentre
// scarica le candele dell'intero universo; 2 min era troppo stretto e faceva
// sfarfallare il badge su OFFLINE pur essendo il bot vivo.
const HEARTBEAT_STALE_MS = 5 * 60 * 1000; // 5 minutes

type DecisionStatusT = {
  ts?: number;
  regime?: string;
  assets_evaluated?: number;
  signals_found?: number;
  best_symbol?: string | null;
  best_strategy?: string | null;
  best_confidence?: number | null;
  best_adjusted?: number | null;
  threshold?: number;
  outcome?: string; // "flat" | "decided" | "opened"
  reason?: string;
};

function timeAgo(ms: number | null): string {
  if (ms == null) return 'unknown';
  const diff = Date.now() - ms;
  if (diff < 0) return 'just now';
  const s = Math.floor(diff / 1000);
  if (s < 60) return `${s}s fa`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m} min fa`;
  const h = Math.floor(m / 60);
  return `${h}h fa`;
}

function decisionAgo(ts?: number): string {
  if (!ts) return '—';
  return timeAgo(ts < 1e12 ? ts * 1000 : ts);
}

export default function BotStatus() {
  const [status, setStatus] = useState<BotStatusT | null>(null);
  const [riskState, setRiskState] = useState<RiskState | null>(null);
  const [equity, setEquity] = useState<number | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [decision, setDecision] = useState<DecisionStatusT | null>(null);
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
    const unsubDec = onValue(ref(db, 'decision_status'), (snap) => {
      setDecision(snap.exists() ? (snap.val() as DecisionStatusT) : null);
    });
    // re-evaluate heartbeat freshness every 15s even without new data
    const tick = setInterval(() => setNow(Date.now()), 15000);
    return () => {
      unsubStatus();
      unsubRisk();
      unsubEquity();
      unsubPos();
      unsubDec();
      clearInterval(tick);
    };
  }, []);

  // --- scomposizione dell'equity (equity MtM e uPnL vivono ora nella top bar) ---
  //   margine usato  = somma(notional/leva) bloccato come collaterale
  //   margine libero = equity MtM - margine usato (liquidita' per nuovi trade)
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

  const effLeverage = riskState?.effective_leverage ?? status?.effective_leverage;
  const effRisk = riskState?.effective_risk_per_trade ?? status?.effective_risk_per_trade;

  // --- ultima decisione (grafica) ---
  const opened = decision?.outcome === 'opened' || decision?.outcome === 'decided';
  const thr = decision?.threshold ?? 30;
  const best = decision?.best_adjusted ?? null;
  const pctScale = (v: number) => Math.max(0, Math.min(100, v));
  const fillPct = best != null ? pctScale(best) : 0;
  const thrPct = pctScale(thr);
  const aboveThr = best != null && best >= thr;

  return (
    <div className="panel">
      <div className="status-strip">
        <div className="left">
          <strong style={{ fontSize: 16 }}>Trading Bot</strong>
        </div>
        <div className="status-badges">
          <span className={`badge ${running ? 'green' : 'red'}`}>
            <span className="dot" style={{ background: running ? 'var(--green)' : 'var(--red)' }} />
            {status?.state ? status.state.toUpperCase() : 'UNKNOWN'}
          </span>
          <span className={`badge ${online ? 'green' : 'red'}`}>{online ? 'ONLINE' : 'OFFLINE'}</span>
          <span className={`badge ${dryRun ? 'amber' : 'red'}`}>{dryRun ? 'DRY_RUN' : 'LIVE'}</span>
          <span className="badge gray">regime: {status?.regime ?? 'n/a'}</span>
        </div>
      </div>

      <div className="stat-grid">
        {equity != null && (
          <>
            <div className="stat-tile accent">
              <div className="stat-label">Bilancio · realizzato</div>
              <div className="stat-value">{usd(equity)}</div>
              <div className="stat-sub">capitale + PnL chiuso</div>
            </div>
            <div className="stat-tile">
              <div className="stat-label">Margine usato</div>
              <div className="stat-value">{usd(marginUsed)}</div>
              <div className="stat-sub">collaterale bloccato</div>
            </div>
            <div className="stat-tile good">
              <div className="stat-label">Margine libero</div>
              <div className="stat-value">{freeMargin != null ? usd(freeMargin) : '—'}</div>
              <div className="stat-sub">liquidità per nuovi trade</div>
            </div>
          </>
        )}

        <div className="stat-tile warnb">
          <div className="stat-label">Leva effettiva</div>
          <div className="stat-value">{effLeverage != null ? `${effLeverage}x` : '—'}</div>
          <div className="stat-sub">
            {effLeverage != null ? 'guidata da conviction + learning' : 'in attesa di pubblicazione'}
          </div>
        </div>

        <div className="stat-tile warnb">
          <div className="stat-label">Rischio / trade</div>
          <div className="stat-value">{effRisk != null ? `${(effRisk * 100).toFixed(2)}%` : '—'}</div>
          <div className="stat-sub">
            {effRisk != null ? 'sotto i cap di sicurezza' : 'in attesa di pubblicazione'}
          </div>
        </div>
      </div>

      {/* ---- Ultima decisione, in forma grafica ---- */}
      <div className="decision-block">
        <div className="decision-head">
          <span className="decision-outcome" style={{ color: opened ? 'var(--green)' : 'var(--text-dim)' }}>
            <span
              className="dot"
              style={{ background: opened ? 'var(--green)' : 'var(--text-faint)', width: 10, height: 10 }}
            />
            {opened ? 'HA OPERATO' : 'FLAT'}
          </span>
          <span className="muted" style={{ fontSize: 12 }}>
            ultima decisione · {decisionAgo(decision?.ts)} · regime {decision?.regime ?? '—'}
          </span>
        </div>

        <div className="muted" style={{ fontSize: 12.5, marginTop: 6 }}>
          {decision?.reason ?? 'In attesa del primo ciclo di decisione.'}
        </div>

        {best != null && (
          <div className="meter">
            <div className="meter-top">
              <span className="muted">
                Conviction miglior segnale
                {decision?.best_symbol ? (
                  <>
                    {' · '}
                    <strong style={{ color: 'var(--text)' }}>{decision.best_symbol}</strong>{' '}
                    <span className="mono">{decision.best_strategy ?? ''}</span>
                  </>
                ) : null}
              </span>
              <strong className="mono" style={{ color: aboveThr ? 'var(--green)' : 'var(--amber)' }}>
                {best.toFixed(0)} / soglia {thr}
              </strong>
            </div>
            <div className="meter-track">
              <div
                className="meter-fill"
                style={{
                  width: `${fillPct}%`,
                  background: aboveThr
                    ? 'linear-gradient(90deg, var(--accent), var(--teal))'
                    : 'linear-gradient(90deg, var(--amber), #f2c65a)',
                }}
              />
              <div className="meter-thresh" style={{ left: `${thrPct}%` }} title={`soglia ${thr}`} />
            </div>
          </div>
        )}

        <div className="decision-mini">
          <span className="mini-chip">
            <span className="mono">{decision?.assets_evaluated ?? 0}</span> asset valutati
          </span>
          <span className="mini-chip">
            <span className="mono">{decision?.signals_found ?? 0}</span> segnali trovati
          </span>
          <span className="mini-chip">
            <span className="dot" style={{ background: 'var(--amber)' }} />
            posizioni aperte <span className="mono">{positions.length}</span>
          </span>
        </div>
      </div>

      <div className="muted" style={{ marginTop: 12, fontSize: 12 }}>
        Heartbeat: {timeAgo(heartbeatMs)}
      </div>
    </div>
  );
}
