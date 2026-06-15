'use client';

import { useEffect, useState } from 'react';
import { collection, limit, onSnapshot, orderBy, query } from 'firebase/firestore';
import { getDb } from '../lib/firebase';

/**
 * Trade chiusi (Firestore `trades`), ordinati per uscita. Mostra PnL e motivo.
 * Così i risultati realizzati si vedono dalla dashboard, senza query manuali.
 */
type Trade = {
  symbol: string;
  strategy: string;
  direction: string;
  pnl: number;
  pnl_pct: number;
  exit_reason: string;
  exit_ts?: number;
};

export default function ClosedTrades() {
  const [rows, setRows] = useState<Trade[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const q = query(collection(getDb(), 'trades'), orderBy('exit_ts', 'desc'), limit(30));
    const unsub = onSnapshot(
      q,
      (snap) => {
        setRows(snap.docs.map((d) => d.data() as Trade));
        setLoaded(true);
      },
      () => setLoaded(true),
    );
    return () => unsub();
  }, []);

  const total = rows.reduce((s, t) => s + (t.pnl ?? 0), 0);

  return (
    <div className="panel">
      <h2>Closed Trades</h2>
      <p className="subtitle">Ultimi trade chiusi (paper) · PnL realizzato</p>
      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : rows.length === 0 ? (
        <p className="muted">Nessun trade chiuso ancora (le posizioni aperte non hanno ancora toccato TP/SL).</p>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ textAlign: 'left', color: '#8b96a5' }}>
                <th style={{ padding: '6px 8px' }}>Coin</th>
                <th style={{ padding: '6px 8px' }}>Strategia</th>
                <th style={{ padding: '6px 8px' }}>Side</th>
                <th style={{ padding: '6px 8px' }}>Uscita</th>
                <th style={{ padding: '6px 8px', textAlign: 'right' }}>PnL</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((t, i) => (
                <tr key={i} style={{ borderTop: '1px solid #28303d' }}>
                  <td style={{ padding: '6px 8px', fontWeight: 600 }}>{t.symbol}</td>
                  <td style={{ padding: '6px 8px' }}>{t.strategy}</td>
                  <td style={{ padding: '6px 8px' }}>{t.direction}</td>
                  <td style={{ padding: '6px 8px', color: '#8b96a5' }}>{t.exit_reason}</td>
                  <td
                    style={{
                      padding: '6px 8px',
                      textAlign: 'right',
                      color: (t.pnl ?? 0) >= 0 ? '#3fb950' : '#f85149',
                    }}
                  >
                    {(t.pnl ?? 0).toFixed(2)}
                  </td>
                </tr>
              ))}
              <tr style={{ borderTop: '2px solid #28303d', fontWeight: 700 }}>
                <td style={{ padding: '6px 8px' }} colSpan={4}>
                  Totale realizzato
                </td>
                <td
                  style={{ padding: '6px 8px', textAlign: 'right', color: total >= 0 ? '#3fb950' : '#f85149' }}
                >
                  {total.toFixed(2)}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
