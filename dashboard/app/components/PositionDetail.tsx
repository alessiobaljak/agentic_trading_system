'use client';

import { useEffect } from 'react';
import type { Position } from '../lib/types';
import PositionChart from './PositionChart';

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
 * Dettaglio posizione: grafico prezzo (TradingView, tutti i timeframe) + metriche
 * operative professionali. SOLO lettura del dato gia' in memoria (nessuna scrittura).
 */
export default function PositionDetail({
  position,
  onClose,
}: {
  position: Position;
  onClose: () => void;
}) {
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

  // Esc per chiudere
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => e.key === 'Escape' && onClose();
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  const M = ({ label, children }: { label: string; children: React.ReactNode }) => (
    <div className="metric">
      <span className="m-label">{label}</span>
      <span className="m-val">{children}</span>
    </div>
  );

  return (
    <div className="dialog-overlay" role="dialog" aria-modal="true" onClick={onClose}>
      <div className="dialog dialog-lg" onClick={(e) => e.stopPropagation()}>
        <div className="detail-head">
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
            <strong style={{ fontSize: 17 }}>{p.symbol}</strong>
            <span className={`badge ${long ? 'green' : 'red'}`}>{long ? 'LONG' : 'SHORT'}</span>
            <span className="muted mono" style={{ fontSize: 12 }}>{p.strategy ?? ''}</span>
            {p.trailing_active && <span className="badge amber">trailing ↑</span>}
            {p.scaled_out && <span className="badge gray">scaled-out</span>}
          </div>
          <button className="btn btn-ghost" style={{ padding: '4px 12px' }} onClick={onClose}>
            Chiudi ✕
          </button>
        </div>

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
          <M label="Held">
            {p.held_hours != null ? `${fmt(p.held_hours, 1)}h` : '—'}
          </M>
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

        <div className="detail-chart">
          <PositionChart symbol={p.symbol} interval="60" />
        </div>
      </div>
    </div>
  );
}
