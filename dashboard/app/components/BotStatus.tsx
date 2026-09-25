'use client';

import { useEffect, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { getRtdb } from '../lib/firebase';
import { toMillis, type BotStatus as BotStatusT, type Position } from '../lib/types';
import { useControllo } from '../lib/controllo';

/**
 * Lo stato VIVO del bot (25 set 2026): la striscia dei badge (stato, online,
 * regime) e l'ultima decisione, letti dal RTDB in tempo reale. Vive dentro
 * la scheda Controllo sotto la testa, che invece e' oraria: qui si vede se il
 * bot sta girando ADESSO e cosa ha deciso all'ultimo ciclo.
 *
 * I tile «bilancio / margine / leva effettiva / rischio per trade» sono stati
 * tolti: la leva e il rischio effettivi non venivano piu' pubblicati (tile
 * sempre «in attesa di pubblicazione») e l'equity sta nella top bar e nel
 * controllo. Il badge DRY_RUN sta nella testa del controllo, non qui: una
 * cosa, un posto.
 *
 * «Online» = battito piu' giovane di `controllo.salute.soglia_online_s`
 * (900 s: lo scan di mercato ogni 4 h puo' bloccare il ciclo qualche minuto,
 * e 2-5 min facevano sfarfallare il badge). La soglia e' del bot, cosi' la
 * dashboard e il comando ops `controllo` dicono la stessa cosa.
 */
const SOGLIA_ONLINE_DEFAULT_S = 900;

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
  if (ms == null) return 'mai visto';
  const diff = Date.now() - ms;
  if (diff < 0) return 'adesso';
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
  const [positions, setPositions] = useState<Position[]>([]);
  const [decision, setDecision] = useState<DecisionStatusT | null>(null);
  const [now, setNow] = useState(Date.now());
  const { doc: controllo } = useControllo();

  useEffect(() => {
    const db = getRtdb();
    const unsubStatus = onValue(ref(db, 'bot_status'), (snap) => {
      setStatus(snap.exists() ? (snap.val() as BotStatusT) : null);
    });
    const unsubPos = onValue(ref(db, 'positions'), (snap) => {
      const val = snap.val() as Record<string, Position> | null;
      setPositions(val ? Object.values(val) : []);
    });
    const unsubDec = onValue(ref(db, 'decision_status'), (snap) => {
      setDecision(snap.exists() ? (snap.val() as DecisionStatusT) : null);
    });
    // l'eta' del battito va ricalcolata anche senza dati nuovi
    const tick = setInterval(() => setNow(Date.now()), 15000);
    return () => {
      unsubStatus();
      unsubPos();
      unsubDec();
      clearInterval(tick);
    };
  }, []);

  const sogliaMs = (controllo?.salute?.soglia_online_s ?? SOGLIA_ONLINE_DEFAULT_S) * 1000;
  const heartbeatMs = toMillis(status?.heartbeat ?? status?.updated_at ?? null);
  const online = heartbeatMs != null && now - heartbeatMs < sogliaMs;
  const running = (status?.state ?? '').toLowerCase() === 'running';

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
          <strong style={{ fontSize: 16 }}>Bot adesso</strong>
        </div>
        <div className="status-badges">
          <span className={`badge ${running ? 'green' : 'red'}`}>
            <span className="dot" style={{ background: running ? 'var(--green)' : 'var(--red)' }} />
            {status?.state ? status.state.toUpperCase() : 'SCONOSCIUTO'}
          </span>
          <span className={`badge ${online ? 'green' : 'red'}`} title={`battito ${timeAgo(heartbeatMs)} · soglia ${sogliaMs / 1000} s`}>
            {online ? 'ONLINE' : 'OFFLINE'}
          </span>
          <span className="badge gray">regime: {status?.regime ?? 'n/d'}</span>
          {status?.price_stream === false && (
            <span className="badge amber" title="lo stream dei prezzi e' spento: il bot usa le candele">
              stream prezzi OFF
            </span>
          )}
        </div>
      </div>

      {/* ---- Ultima decisione, in forma grafica ---- */}
      <div className="decision-block" style={{ marginTop: 0 }}>
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
                    : 'linear-gradient(90deg, var(--amber), var(--amber))',
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
        Battito: {timeAgo(heartbeatMs)}
      </div>
    </div>
  );
}
