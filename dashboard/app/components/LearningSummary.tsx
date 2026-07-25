'use client';

import { useEffect, useMemo, useState } from 'react';
import { doc, onSnapshot } from 'firebase/firestore';
import { onValue, ref } from 'firebase/database';
import { getDb, getRtdb } from '../lib/firebase';
import { toMillis, type StrategyWeight, type MemoryReport } from '../lib/types';

/**
 * LearningSummary — il "cervello" in una vista sola. SOLO LETTURA.
 * Legge:
 *   - strategy_weights/current  (pesi strategia×regime + updated_at)
 *   - memory/30                 (win rate complessivo, trade totali)
 *   - /trailing_keep (RTDB)     (trailing adattato per strategia dal bot)
 * e sintetizza cosa sta imparando il bot: quante combinazioni monitora, quante
 * sta rafforzando / penalizzando / facendo rientrare in prova, e quando ha
 * ricalcolato l'ultima volta (il learning gira ogni ora). Non scrive nulla.
 */

type WeightsDoc = { weights?: StrategyWeight[]; updated_at?: number };

const STRONG = 0.9; // >= in forma · < sotto osservazione

function ago(ms: number | null): string {
  if (ms == null) return '—';
  const s = Math.max(0, Math.floor((Date.now() - ms) / 1000));
  if (s < 60) return `${s}s fa`;
  const m = Math.floor(s / 60);
  if (m < 60) return `${m} min fa`;
  const h = Math.floor(m / 60);
  if (h < 48) return `${h}h fa`;
  return `${Math.floor(h / 24)}g fa`;
}

export default function LearningSummary() {
  const [wdoc, setWdoc] = useState<WeightsDoc | null>(null);
  const [mem, setMem] = useState<MemoryReport | null>(null);
  const [trailing, setTrailing] = useState<Record<string, number>>({});
  const [loaded, setLoaded] = useState(false);
  const [, setNow] = useState(Date.now());

  useEffect(() => {
    const db = getDb();
    const u1 = onSnapshot(
      doc(db, 'strategy_weights', 'current'),
      (snap) => {
        setWdoc(snap.exists() ? (snap.data() as WeightsDoc) : null);
        setLoaded(true);
      },
      () => setLoaded(true),
    );
    const u2 = onSnapshot(doc(db, 'memory', '30'), (snap) =>
      setMem(snap.exists() ? (snap.data() as MemoryReport) : null),
    );
    const u3 = onValue(ref(getRtdb(), 'trailing_keep'), (snap) =>
      setTrailing(snap.exists() ? (snap.val() as Record<string, number>) : {}),
    );
    const tick = setInterval(() => setNow(Date.now()), 30000);
    return () => {
      u1();
      u2();
      u3();
      clearInterval(tick);
    };
  }, []);

  const s = useMemo(() => {
    const weights = wdoc?.weights ?? [];
    const strong = weights.filter((w) => (w.weight ?? 1) >= STRONG && (w.sample_size ?? 0) > 0);
    const penalized = weights.filter((w) => (w.weight ?? 1) < STRONG && (w.sample_size ?? 0) > 0);
    const probation = weights.filter((w) => (w.sample_size ?? 0) === 0 && (w.weight ?? 1) < 1);
    const topStrong = [...strong].sort((a, b) => (b.weight ?? 0) - (a.weight ?? 0)).slice(0, 4);
    const topPenalized = [...penalized].sort((a, b) => (a.weight ?? 0) - (b.weight ?? 0)).slice(0, 4);
    return {
      groups: weights.length,
      strong,
      penalized,
      probation,
      topStrong,
      topPenalized,
    };
  }, [wdoc]);

  const lastMs = toMillis(wdoc?.updated_at ?? null);
  const trailingCount = Object.keys(trailing).length;
  const wr = mem?.overall_win_rate;
  const totalTrades = mem?.total_trades;

  if (loaded && s.groups === 0) {
    return (
      <div className="panel">
        <h2>Il cervello del bot · learning</h2>
        <p className="subtitle">Adattamento pesi strategia × regime · ricalcolo ogni ora</p>
        <p className="muted">
          Il learning non ha ancora prodotto pesi: servono trade chiusi determinati dalle strategie.
          Appena arrivano, qui vedrai in tempo reale cosa il bot sta rafforzando e cosa penalizzando.
        </p>
      </div>
    );
  }

  return (
    <div className="panel">
      <h2>Il cervello del bot · learning</h2>
      <p className="subtitle">
        Adattamento dei pesi strategia × regime · il bot ricalcola ogni ora leggendo i propri trade
      </p>

      <div className="stat-grid">
        <div className="stat-tile accent">
          <div className="stat-label">Combinazioni monitorate</div>
          <div className="stat-value">{s.groups}</div>
          <div className="stat-sub">strategia × regime sotto apprendimento</div>
        </div>
        <div className="stat-tile good">
          <div className="stat-label">In forma</div>
          <div className="stat-value pos">{s.strong.length}</div>
          <div className="stat-sub">peso ≥ {STRONG} · rafforzate</div>
        </div>
        <div className="stat-tile bad">
          <div className="stat-label">Sotto osservazione</div>
          <div className="stat-value neg">{s.penalized.length}</div>
          <div className="stat-sub">peso &lt; {STRONG} · penalizzate</div>
        </div>
        <div className="stat-tile warnb">
          <div className="stat-label">In rientro (prova)</div>
          <div className="stat-value">{s.probation.length}</div>
          <div className="stat-sub">recupero graduale verso 1.0</div>
        </div>
        <div className="stat-tile">
          <div className="stat-label">Win rate complessivo</div>
          <div className="stat-value">{wr != null ? `${(wr * 100).toFixed(0)}%` : '—'}</div>
          <div className="stat-sub">{totalTrades != null ? `${totalTrades} trade (30g)` : 'da memory/30'}</div>
        </div>
        <div className="stat-tile accent">
          <div className="stat-label">Trailing adattato</div>
          <div className="stat-value">{trailingCount || '—'}</div>
          <div className="stat-sub">{trailingCount ? 'strategie con trail appreso' : 'in attesa di dati'}</div>
        </div>
      </div>

      <div className="learn-narrative">
        <span className="live-dot" />
        Ultimo ricalcolo <strong>{ago(lastMs)}</strong>. Il bot sta monitorando{' '}
        <strong>{s.groups}</strong> combinazioni strategia × regime:{' '}
        <span className="pos">{s.strong.length} in forma</span>,{' '}
        <span className="neg">{s.penalized.length} sotto osservazione</span> e{' '}
        <strong>{s.probation.length}</strong> in rientro di prova. Le penalizzate abbassano
        automaticamente la size e la leva; passano solo con segnali forti finché non recuperano.
      </div>

      {(s.topStrong.length > 0 || s.topPenalized.length > 0) && (
        <div style={{ marginTop: 12 }}>
          {s.topPenalized.length > 0 && (
            <>
              <div className="muted" style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 2 }}>
                Più penalizzate ora
              </div>
              <div className="chip-row">
                {s.topPenalized.map((w) => (
                  <span key={`p-${w.strategy}-${w.regime}`} className="mini-chip">
                    <span className="dot" style={{ background: 'var(--red)' }} />
                    {w.strategy} · {w.regime}
                    <span className="mono">{(w.weight ?? 0).toFixed(2)}</span>
                  </span>
                ))}
              </div>
            </>
          )}
          {s.topStrong.length > 0 && (
            <>
              <div className="muted" style={{ fontSize: 11, textTransform: 'uppercase', letterSpacing: '0.05em', margin: '10px 0 2px' }}>
                Più solide ora
              </div>
              <div className="chip-row">
                {s.topStrong.map((w) => (
                  <span key={`s-${w.strategy}-${w.regime}`} className="mini-chip">
                    <span className="dot" style={{ background: 'var(--green)' }} />
                    {w.strategy} · {w.regime}
                    <span className="mono">{(w.weight ?? 0).toFixed(2)}</span>
                  </span>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
