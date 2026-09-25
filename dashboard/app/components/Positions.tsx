'use client';

import { Fragment, useEffect, useState } from 'react';
import { onValue, ref, serverTimestamp, set } from 'firebase/database';
import { getRtdb } from '../lib/firebase';
import type { Position } from '../lib/types';
import { STATO } from '../lib/viz';
import PositionMetrics from './PositionMetrics';

/**
 * POSIZIONI APERTE (RTDB `/positions`).
 *
 * Il dettaglio di una posizione si apre NELLA RIGA, non in una finestra sopra
 * (25 set 2026): la finestra modale copriva la tabella e sul telefono non si
 * chiudeva bene; la riga espansa mostra le stesse metriche (`PositionMetrics`) e
 * un bottone per portare la coin sul grafico in fondo alla scheda.
 *
 * La colonna «Rischio %» e' `risk_effective_pct` × 100: la frazione di equity che
 * si perde se lo stop ORIGINALE scatta. E' il numero che il tetto per direzione
 * somma, e prima non si vedeva da nessuna parte se non nel controllo orario.
 */
type Pos = Position & {
  /** frazione dell'equity a rischio con lo stop originale (scritta dall'executor) */
  risk_effective_pct?: number | null;
  /** keep del profit-lock scelto dal gate per la coppia (25 set) */
  profit_lock_keep?: number | null;
};

function fmt(n: number | undefined | null, digits = 2): string {
  if (n == null || !Number.isFinite(n)) return '—';
  return n.toLocaleString('it-IT', { maximumFractionDigits: digits });
}

export default function Positions({ onSelect }: { onSelect?: (p: Position) => void } = {}) {
  const [positions, setPositions] = useState<Pos[]>([]);
  const [loaded, setLoaded] = useState(false);
  // simboli con una chiusura manuale in coda (il bot non li ha ancora processati)
  const [pending, setPending] = useState<Set<string>>(new Set());
  // simbolo per cui è aperto il dialog di conferma
  const [confirm, setConfirm] = useState<string | null>(null);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  // righe espanse (metriche nella riga)
  const [aperte, setAperte] = useState<Set<string>>(new Set());

  useEffect(() => {
    const db = getRtdb();
    const unsub = onValue(ref(db, 'positions'), (snap) => {
      const val = snap.val() as Record<string, Pos> | null;
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

  const toggle = (sym: string) =>
    setAperte((prev) => {
      const next = new Set(prev);
      if (next.has(sym)) next.delete(sym);
      else next.add(sym);
      return next;
    });

  const totalUpnl = positions.reduce((acc, p) => acc + (p.unrealized_pnl ?? 0), 0);
  const rischioTot = positions.reduce((acc, p) => acc + (p.risk_effective_pct ?? 0), 0) * 100;
  const COLONNE = 13;

  return (
    <div className="panel">
      <h2>Posizioni aperte</h2>
      <p className="subtitle">Clicca una riga per le metriche; da li&apos; puoi portarla sul grafico in fondo</p>
      {!loaded ? (
        <p className="muted">Caricamento…</p>
      ) : positions.length === 0 ? (
        <p className="muted">Nessuna posizione aperta.</p>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table>
            <thead>
              <tr>
                <th>Coin</th>
                <th>Strategia</th>
                <th>Lato</th>
                <th>Ingresso</th>
                <th>Prezzo</th>
                <th>Quantita&apos;</th>
                <th>Leva</th>
                <th title="frazione dell'equity persa se scatta lo stop originale">Rischio %</th>
                <th>Stop</th>
                <th>TP</th>
                <th title="Ore aperta · funding maturato (già scalato dall'uPnL)">Aperta da / Fund.</th>
                <th>uPnL</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {positions.map((p) => {
                const upnl = p.unrealized_pnl ?? 0;
                const side = (p.direction ?? '').toLowerCase();
                const isPending = pending.has(p.symbol);
                const aperta = aperte.has(p.symbol);
                const rischio = p.risk_effective_pct != null ? p.risk_effective_pct * 100 : null;
                return (
                  <Fragment key={p.symbol}>
                    <tr
                      onClick={() => toggle(p.symbol)}
                      style={{ cursor: 'pointer', background: aperta ? 'var(--bg-elev)' : undefined }}
                      title={aperta ? 'Chiudi il dettaglio' : 'Apri il dettaglio'}
                      aria-expanded={aperta}
                    >
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
                      <td className="mono" style={{ color: rischio != null && rischio > 1.5 ? STATO.attenzione : undefined }}>
                        {rischio == null ? '—' : `${fmt(rischio, 2)}%`}
                      </td>
                      <td className="mono">
                        {/* lo stop EFFETTIVO: `stop_price` e' la base (pareggio dopo
                            il primo TP) e non include la protezione del profitto, che
                            si ricalcola a ogni tick. Mostrare la base faceva credere
                            di essere protetti al pareggio quando lo si era molto piu'
                            in alto — e spinge a chiudere a mano una posizione gia' al
                            sicuro. */}
                        {fmt(p.effective_stop ?? p.stop_price, 4)}
                        {p.effective_stop != null && p.stop_price != null
                          && p.effective_stop !== p.stop_price && (
                          <span
                            title={`protezione del profitto attiva (base ${fmt(p.stop_price, 4)})`}
                            style={{ marginLeft: 4, color: STATO.buono }}
                          >
                            🔒
                          </span>
                        )}
                      </td>
                      <td className="mono">
                        {p.tp_ladder && p.tp_ladder.length > 0 ? (
                          <div style={{ display: 'flex', flexDirection: 'column', gap: 2, alignItems: 'flex-end' }}>
                            {p.tp_ladder.map((t, i) => (
                              <span
                                key={i}
                                style={{ fontSize: 11, whiteSpace: 'nowrap', color: t.hit ? 'var(--green)' : 'var(--text-dim)' }}
                                title={`TP${i + 1}${t.r != null ? ` · ${t.r}R` : ''} · ${Math.round(t.fraction * 100)}% ${t.hit ? '· raggiunto' : ''}`}
                              >
                                {t.hit ? '✓ ' : ''}
                                {t.r != null ? `${t.r}R ` : ''}
                                {fmt(t.price, 4)}
                              </span>
                            ))}
                          </div>
                        ) : (
                          fmt(p.take_profit_price, 4)
                        )}
                      </td>
                      <td className="mono muted" style={{ fontSize: 12, whiteSpace: 'nowrap' }}>
                        {p.held_hours != null ? `${p.held_hours.toFixed(1)}h` : '—'}
                        {p.accrued_funding != null && p.accrued_funding !== 0
                          ? ` · -${p.accrued_funding.toFixed(2)}`
                          : ''}
                      </td>
                      <td className={`mono ${upnl >= 0 ? 'pos' : 'neg'}`}>
                        {upnl >= 0 ? '+' : ''}
                        {fmt(upnl)}
                        {p.trailing_active ? ' ↑' : ''}
                        {/* dopo un TP parziale l'uPnL e' SOLO il residuo: senza il
                            totale (residuo + gia' incassato) una posizione in utile
                            sembra in perdita */}
                        {p.realized_partial != null && p.realized_partial !== 0 && (() => {
                          const tot = upnl + (p.realized_partial ?? 0);
                          return (
                            <div
                              className={tot >= 0 ? 'pos' : 'neg'}
                              style={{ fontSize: 11, opacity: 0.85 }}
                              title={`Gia' incassato dai TP parziali: ${(p.realized_partial ?? 0) >= 0 ? '+' : ''}${fmt(p.realized_partial)} · totale posizione = residuo + incassato`}
                            >
                              tot {tot >= 0 ? '+' : ''}{fmt(tot)}
                            </div>
                          );
                        })()}
                      </td>
                      <td style={{ textAlign: 'right' }}>
                        <button
                          className="btn btn-danger"
                          style={{ padding: '4px 10px', fontSize: 12 }}
                          onClick={(e) => { e.stopPropagation(); setConfirm(p.symbol); }}
                          disabled={isPending}
                          title={isPending ? 'Chiusura in coda' : 'Chiudi questa posizione'}
                        >
                          {isPending ? 'In chiusura…' : 'Chiudi'}
                        </button>
                      </td>
                    </tr>
                    {aperta ? (
                      <tr style={{ background: 'var(--bg-elev)' }}>
                        <td colSpan={COLONNE} style={{ textAlign: 'left', padding: '8px 12px 12px' }}>
                          <PositionMetrics position={p} />
                          {onSelect ? (
                            <button
                              className="btn btn-ghost"
                              style={{ padding: '4px 12px', fontSize: 12, marginTop: 6 }}
                              onClick={(e) => { e.stopPropagation(); onSelect(p); }}
                            >
                              Vedi sul grafico ↓
                            </button>
                          ) : null}
                        </td>
                      </tr>
                    ) : null}
                  </Fragment>
                );
              })}
            </tbody>
            <tfoot>
              <tr>
                <td colSpan={7} style={{ textAlign: 'right', fontWeight: 600 }}>
                  Totale
                </td>
                <td className="mono" style={{ fontWeight: 700 }} title="somma del rischio aperto (stop originali)">
                  {fmt(rischioTot, 2)}%
                </td>
                <td colSpan={3} style={{ textAlign: 'right', fontWeight: 600 }}>uPnL totale</td>
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
