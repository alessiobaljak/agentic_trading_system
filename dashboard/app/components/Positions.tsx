'use client';

import { useEffect, useState } from 'react';
import { onValue, ref, serverTimestamp, set } from 'firebase/database';
import { getRtdb } from '../lib/firebase';
import type { Position } from '../lib/types';

function fmt(n: number | undefined, digits = 2): string {
  if (n == null || !Number.isFinite(n)) return '—';
  return n.toLocaleString(undefined, { maximumFractionDigits: digits });
}

export default function Positions() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [loaded, setLoaded] = useState(false);
  // simboli con una chiusura manuale in coda (il bot non li ha ancora processati)
  const [pending, setPending] = useState<Set<string>>(new Set());
  // simbolo per cui è aperto il dialog di conferma
  const [confirm, setConfirm] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const db = getRtdb();
    const unsub = onValue(ref(db, 'positions'), (snap) => {
      const val = snap.val() as Record<string, Position> | null;
      const list = val
        ? Object.entries(val).map(([symbol, p]) => ({ ...p, symbol: p.symbol ?? symbol }))
        : [];
      list.sort((a, b) => (a.symbol > b.symbol ? 1 : -1));
      setPositions(list);
      setLoaded(true);
    });
    return () => unsub();
  }, []);

  // riflette le richieste di chiusura ancora in coda su /commands/close_position
  useEffect(() => {
    const db = getRtdb();
    const unsub = onValue(ref(db, 'commands/close_position'), (snap) => {
      const val = snap.val() as Record<string, unknown> | null;
      setPending(new Set(val ? Object.keys(val) : []));
    });
    return () => unsub();
  }, []);

  const requestClose = async (symbol: string) => {
    setError(null);
    setSending(true);
    try {
      const db = getRtdb();
      await set(ref(db, `commands/close_position/${symbol}`), true);
      await set(ref(db, `commands/close_position_meta/${symbol}`), {
        requested_by: 'dashboard',
        requested_at: serverTimestamp(),
      }).catch(() => undefined);
      setConfirm(null);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Chiusura non riuscita.');
    } finally {
      setSending(false);
    }
  };

  const totalUpnl = positions.reduce((acc, p) => acc + (p.unrealized_pnl ?? 0), 0);

  return (
    <div className="panel">
      <h2>Open Positions</h2>
      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : positions.length === 0 ? (
        <p className="muted">No open positions.</p>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Strategy</th>
                <th>Side</th>
                <th>Entry</th>
                <th>Mark</th>
                <th>Qty</th>
                <th>Lev</th>
                <th>Stop</th>
                <th>TP</th>
                <th>uPnL</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {positions.map((p) => {
                const upnl = p.unrealized_pnl ?? 0;
                const side = (p.direction ?? '').toLowerCase();
                const isPending = pending.has(p.symbol);
                return (
                  <tr key={p.symbol}>
                    <td>
                      <strong>{p.symbol}</strong>
                      {p.dry_run ? <span className="badge amber" style={{ marginLeft: 6 }}>sim</span> : null}
                    </td>
                    <td className="muted">{p.strategy ?? '—'}</td>
                    <td className={side === 'long' ? 'pos' : side === 'short' ? 'neg' : ''}>
                      {p.direction ? p.direction.toUpperCase() : '—'}
                    </td>
                    <td className="mono">{fmt(p.entry_price, 4)}</td>
                    <td className="mono">{fmt(p.mark_price, 4)}</td>
                    <td className="mono">{fmt(p.quantity, 4)}</td>
                    <td className="mono">{p.leverage != null ? `${p.leverage}x` : '—'}</td>
                    <td className="mono">{fmt(p.stop_price, 4)}</td>
                    <td className="mono">{fmt(p.take_profit_price, 4)}</td>
                    <td className={`mono ${upnl >= 0 ? 'pos' : 'neg'}`}>
                      {upnl >= 0 ? '+' : ''}
                      {fmt(upnl)}
                      {p.trailing_active ? ' ↑' : ''}
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <button
                        className="btn btn-danger"
                        style={{ padding: '4px 10px', fontSize: 12 }}
                        onClick={() => setConfirm(p.symbol)}
                        disabled={isPending}
                        title={isPending ? 'Chiusura in coda' : 'Chiudi questa posizione'}
                      >
                        {isPending ? 'In chiusura…' : 'Chiudi'}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
            <tfoot>
              <tr>
                <td colSpan={9} style={{ textAlign: 'right', fontWeight: 600 }}>
                  Total unrealized PnL
                </td>
                <td className={`mono ${totalUpnl >= 0 ? 'pos' : 'neg'}`} style={{ fontWeight: 700 }}>
                  {totalUpnl >= 0 ? '+' : ''}
                  {fmt(totalUpnl)}
                </td>
                <td />
              </tr>
            </tfoot>
          </table>
        </div>
      )}

      {error && <div className="warn">{error}</div>}

      {confirm && (
        <div className="dialog-overlay" role="dialog" aria-modal="true">
          <div className="dialog">
            <h3>Chiudere {confirm}?</h3>
            <p>
              Il bot chiuderà la posizione <strong>{confirm}</strong> al prossimo tick, al prezzo di
              mercato corrente, registrando il PnL realizzato. L&apos;azione non si annulla.
            </p>
            <div className="dialog-actions">
              <button className="btn" onClick={() => setConfirm(null)} disabled={sending}>
                Annulla
              </button>
              <button
                className="btn btn-danger"
                onClick={() => requestClose(confirm)}
                disabled={sending}
              >
                {sending ? 'Invio…' : 'Sì, chiudi'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
