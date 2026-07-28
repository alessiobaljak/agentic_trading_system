'use client';

import type { Position } from '../lib/types';

const REG_SHORT: Record<string, string> = {
  bull_trending: 'bull',
  bear_trending: 'bear',
  sideways: 'sideways',
};

function fmt(n: number | undefined | null, d = 2): string {
  if (n == null || !Number.isFinite(n)) return '—';
  return n.toLocaleString(undefined, { maximumFractionDigits: d });
}

/**
 * Metriche operative di una posizione APERTA (striscia + contesto). SOLO lettura.
 * Riusata dal grafico persistente (Operatività) e dal dettaglio.
 */
export default function PositionMetrics({ position }: { position: Position }) {
  const p = position;
  const long = (p.direction ?? '').toLowerCase() === 'long';
  const entry = p.entry_price ?? 0;
  const mark = p.mark_price ?? entry;
  const stop = p.stop_price ?? 0;
  const tp = p.take_profit_price ?? 0;
  const lev = p.leverage && p.leverage > 0 ? p.leverage : 1;
  const qty = p.quantity ?? 0;
  const upnl = p.unrealized_pnl ?? 0;

  const risk = Math.abs(entry - stop);
  const curR = risk > 0 ? (long ? mark - entry : entry - mark) / risk : null;
  const distSL = mark > 0 && stop > 0 ? ((long ? mark - stop : stop - mark) / mark) * 100 : null;
  const distTP = mark > 0 && tp > 0 ? ((long ? tp - mark : mark - tp) / mark) * 100 : null;
  const notional = entry * qty;
  const margin = notional / lev;

  const M = ({ label, children }: { label: string; children: React.ReactNode }) => (
    <div className="metric">
      <span className="m-label">{label}</span>
      <span className="m-val">{children}</span>
    </div>
  );

  return (
    <>
      <div className="metric-strip" style={{ marginBottom: 10 }}>
        <M label="Entry">{fmt(entry, 4)}</M>
        <M label="Mark">{fmt(mark, 4)}</M>
        <M label="R attuale">
          <span className={curR != null && curR >= 0 ? 'pos' : 'neg'}>
            {curR != null ? `${curR >= 0 ? '+' : ''}${fmt(curR)}R` : '—'}
          </span>
        </M>
        <M label="Dist. Stop">{distSL != null ? `${fmt(distSL, 1)}%` : '—'}</M>
        <M label="Dist. TP">{distTP != null ? `${fmt(distTP, 1)}%` : '—'}</M>
        <M label="Leva">{lev}x</M>
        <M label="uPnL">
          <span className={upnl >= 0 ? 'pos' : 'neg'}>{upnl >= 0 ? '+' : ''}{fmt(upnl)}</span>
        </M>
        <M label="Notional">${fmt(notional, 0)}</M>
        <M label="Margine">${fmt(margin, 0)}</M>
        <M label="Held">{p.held_hours != null ? `${fmt(p.held_hours, 1)}h` : '—'}</M>
      </div>

      <div className="detail-ctx muted">
        SL <span className="mono">{fmt(stop, 4)}</span> · TP <span className="mono">{fmt(tp, 4)}</span>
        {p.accrued_funding != null && p.accrued_funding !== 0 && (
          <> · funding maturato <span className="mono neg">-{fmt(p.accrued_funding)}</span></>
        )}
        {' · '}all&apos;ingresso:
        {p.regime_at_entry ? ` regime ${REG_SHORT[p.regime_at_entry] ?? p.regime_at_entry}` : ''}
        {p.confidence_at_entry != null ? ` · conv. ${fmt(p.confidence_at_entry, 0)}` : ''}
        {p.sentiment_at_entry != null ? ` · sentiment ${fmt(p.sentiment_at_entry)}` : ''}
        {p.fear_greed_at_entry != null ? ` · F&G ${Math.round(p.fear_greed_at_entry)}` : ''}
      </div>

      {p.tp_ladder && p.tp_ladder.length > 0 && (
        <div style={{ margin: '2px 0 4px' }}>
          <div className="muted" style={{ fontSize: 10, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 4 }}>
            Take-profit scaglionati · {p.scale_stage ?? p.tp_ladder.filter((t) => t.hit).length}/{p.tp_ladder.length} raggiunti
          </div>
          <div className="chip-row">
            {p.tp_ladder.map((t, i) => (
              <span
                key={i}
                className="mini-chip"
                style={
                  t.hit
                    ? { background: 'rgba(63,185,80,0.16)', borderColor: 'rgba(63,185,80,0.4)', color: 'var(--green)' }
                    : undefined
                }
                title={`${Math.round(t.fraction * 100)}% della size a ${t.r != null ? `${t.r}R` : ''} ${t.hit ? '· raggiunto' : '· in attesa'}`}
              >
                {t.hit ? '✓ ' : ''}TP{i + 1}
                {t.r != null ? ` · ${t.r}R` : ''}
                <span className="mono">{fmt(t.price, 4)}</span>
                <span className="muted" style={{ fontSize: 10 }}>{Math.round(t.fraction * 100)}%</span>
              </span>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
