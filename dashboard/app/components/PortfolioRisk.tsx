'use client';

import { useEffect, useMemo, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { getRtdb } from '../lib/firebase';

/**
 * Quanto si sta rischiando DAVVERO, adesso.
 *
 * Due numeri che fino a ieri non esistevano da nessuna parte:
 *
 * 1. RISCHIO EFFETTIVO per posizione. L'impostazione dice 1%, ma il cap
 *    per-posizione limita il nozionale e il rischio vero finisce altrove — per
 *    giunta variabile con la distanza dello stop. Qui si vede la differenza.
 *
 * 2. RISCHIO APERTO TOTALE. Con 9-12 posizioni contemporanee su coin che si
 *    muovono quasi tutte con BTC, è la somma che determina quanto puoi perdere in
 *    una giornata storta — non il rischio della singola posizione.
 */
type Pos = {
  direction?: string;
  quantity?: number;
  entry_price?: number;
  unrealized_pnl?: number;
  leverage?: number;
  risk_effective_pct?: number;
};

export default function PortfolioRisk() {
  const [positions, setPositions] = useState<Record<string, Pos>>({});
  const [equity, setEquity] = useState<number | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const db = getRtdb();
    const u1 = onValue(ref(db, '/positions'), (s) => {
      setPositions((s.val() as Record<string, Pos>) || {});
      setLoaded(true);
    }, () => setLoaded(true));
    const u2 = onValue(ref(db, '/account/equity'),
      (s) => setEquity(s.val() != null ? Number(s.val()) : null), () => {});
    return () => { u1(); u2(); };
  }, []);

  const rows = useMemo(
    () => Object.entries(positions).filter(([, p]) => p && typeof p === 'object'),
    [positions]);
  const totalRisk = rows.reduce((a, [, p]) => a + Number(p.risk_effective_pct ?? 0), 0);
  const upnl = rows.reduce((a, [, p]) => a + Number(p.unrealized_pnl ?? 0), 0);

  // oltre questa soglia una giornata storta costa una fetta seria di equity
  const heavy = totalRisk >= 0.06;
  const cellStyle = { padding: '6px 8px' } as const;

  return (
    <div className="panel">
      <h2>Rischio di portafoglio</h2>
      <p className="subtitle">
        Il <b>rischio effettivo</b> è quanto si perde davvero se lo stop viene toccato.
        Diverge dall&apos;impostazione quando il cap per-posizione limita il nozionale — che
        è il caso normale, non l&apos;eccezione.
      </p>

      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : !rows.length ? (
        <p className="muted">Nessuna posizione aperta.</p>
      ) : (
        <>
          <div style={{ display: 'flex', gap: 22, flexWrap: 'wrap', marginBottom: 12 }}>
            <div>
              <div style={{ fontSize: 22, fontWeight: 700,
                            color: heavy ? 'var(--red)' : 'var(--green)' }}>
                {(totalRisk * 100).toFixed(2)}%
              </div>
              <div style={{ fontSize: 11, color: 'var(--muted)' }}>
                rischio aperto totale
              </div>
            </div>
            <div>
              <div style={{ fontSize: 22, fontWeight: 700 }}>{rows.length}</div>
              <div style={{ fontSize: 11, color: 'var(--muted)' }}>posizioni aperte</div>
            </div>
            <div>
              <div style={{ fontSize: 22, fontWeight: 700,
                            color: upnl >= 0 ? 'var(--green)' : 'var(--red)' }}>
                {upnl >= 0 ? '+' : ''}{upnl.toFixed(2)}
              </div>
              <div style={{ fontSize: 11, color: 'var(--muted)' }}>uPnL (USDT)</div>
            </div>
            {equity != null && (
              <div>
                <div style={{ fontSize: 22, fontWeight: 700 }}>
                  {(totalRisk * equity).toFixed(2)}
                </div>
                <div style={{ fontSize: 11, color: 'var(--muted)' }}>
                  USDT a rischio se saltano tutti gli stop
                </div>
              </div>
            )}
          </div>

          {heavy && (
            <p style={{ color: 'var(--red)', fontSize: 12, marginTop: 0 }}>
              Rischio aperto elevato: su coin correlate gli stop possono saltare insieme.
            </p>
          )}

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
              <thead>
                <tr style={{ textAlign: 'left', color: 'var(--muted)' }}>
                  <th style={cellStyle}>Coin</th>
                  <th style={cellStyle}>Dir</th>
                  <th style={{ ...cellStyle, textAlign: 'right' }}>Leva</th>
                  <th style={{ ...cellStyle, textAlign: 'right' }}>Rischio</th>
                  <th style={{ ...cellStyle, textAlign: 'right' }}>uPnL</th>
                </tr>
              </thead>
              <tbody>
                {rows
                  .sort((a, b) => Number(b[1].risk_effective_pct ?? 0)
                                - Number(a[1].risk_effective_pct ?? 0))
                  .map(([sym, p]) => (
                  <tr key={sym} style={{ borderTop: '1px solid #28303d' }}>
                    <td style={{ ...cellStyle, fontWeight: 600 }}>{sym}</td>
                    <td style={{ ...cellStyle,
                                 color: p.direction === 'short' ? 'var(--red)' : 'var(--green)' }}>
                      {p.direction ?? '—'}
                    </td>
                    <td style={{ ...cellStyle, textAlign: 'right' }}>{p.leverage ?? '—'}x</td>
                    <td style={{ ...cellStyle, textAlign: 'right' }}>
                      {p.risk_effective_pct != null
                        ? `${(Number(p.risk_effective_pct) * 100).toFixed(2)}%`
                        : '—'}
                    </td>
                    <td style={{ ...cellStyle, textAlign: 'right',
                                 color: Number(p.unrealized_pnl ?? 0) >= 0
                                   ? 'var(--green)' : 'var(--red)' }}>
                      {Number(p.unrealized_pnl ?? 0).toFixed(2)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="muted" style={{ fontSize: 11, marginTop: 8 }}>
            Le posizioni senza rischio indicato sono state aperte prima che il campo
            esistesse: si popola da sola sulle prossime.
          </p>
        </>
      )}
    </div>
  );
}
