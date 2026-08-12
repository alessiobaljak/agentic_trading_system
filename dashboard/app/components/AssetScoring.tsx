'use client';

import { useEffect, useState } from 'react';
import { doc, onSnapshot } from 'firebase/firestore';
import { getDb } from '../lib/firebase';

/**
 * Perché quella coin e non un'altra: il punteggio con i sei fattori aperti.
 *
 * Il totale (0..1) dice quanto un asset è adatto, il dettaglio dice perché. Due
 * fattori NON sono "più è meglio" e vale la pena saperlo leggendo la tabella:
 *   · funding — l'ottimo è ZERO. Un funding estremo è un costo di mantenimento
 *     che erode ogni trade tenuto per ore.
 *   · volatilità — è una fascia: troppo poca non paga i costi, troppa fa saltare
 *     gli stop per rumore.
 *
 * Oggi il punteggio NON filtra: l'universo lo decide il GATE 1. È scritto a ogni
 * scan per poter verificare nel tempo se predice davvero l'esito. Le esclusioni
 * strutturali sono calcolate sempre ma applicate solo fuori dalla parità col
 * backtest — il badge in alto dice quale dei due casi è attivo.
 */
type Row = {
  symbol: string;
  score: number;
  components?: Record<string, number>;
  excluded?: string[];
  recent_stops?: number;
};
type Doc = { updated_at?: number; assets?: Row[]; exclusions_enforced?: boolean };

const FACTORS = ['momentum', 'social', 'volume', 'funding', 'volatility', 'liquidity'] as const;
const SHORT: Record<string, string> = {
  momentum: 'mom', social: 'social', volume: 'vol',
  funding: 'fund', volatility: 'volat', liquidity: 'liq',
};

/** Verde alto, ambra medio, rosso basso: stessa scala per ogni fattore. */
function cell(v: number | undefined): string {
  if (v === undefined) return 'var(--muted)';
  if (v >= 0.66) return 'var(--green)';
  if (v >= 0.33) return 'var(--amber)';
  return 'var(--red)';
}

export default function AssetScoring() {
  const [d, setD] = useState<Doc | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [all, setAll] = useState(false);

  useEffect(() => {
    const unsub = onSnapshot(
      doc(getDb(), 'asset_scores', 'current'),
      (s) => { setD(s.exists() ? (s.data() as Doc) : null); setLoaded(true); },
      () => setLoaded(true),
    );
    return () => unsub();
  }, []);

  const rows = d?.assets ?? [];
  const shown = all ? rows : rows.slice(0, 15);
  const cellStyle = { padding: '5px 8px' } as const;

  return (
    <div className="panel">
      <h2>Punteggio degli asset</h2>
      <p className="subtitle">
        Sei fattori, ognuno 0–1. Attenzione a due: <b>funding</b> premia lo zero (un
        funding estremo è un costo che erode ogni trade tenuto per ore) e{' '}
        <b>volatilità</b> premia una fascia (troppa fa saltare gli stop per rumore).
      </p>

      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : !rows.length ? (
        <p className="muted">
          Nessun punteggio ancora pubblicato. Si popola al primo market scan (ogni 4h)
          con il bot aggiornato sul VPS.
        </p>
      ) : (
        <>
          <p className="muted" style={{ fontSize: 12, marginTop: 0 }}>
            {d?.exclusions_enforced
              ? '🔴 Le esclusioni strutturali sono ATTIVE: le coin barrate non vengono operate.'
              : '⚪ Parità col backtest: le esclusioni sono calcolate ma NON applicate — il '
                + 'gate non le modella, e filtrare in live ciò che ha validato creerebbe una '
                + 'divergenza fra promesso ed eseguito.'}
          </p>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
              <thead>
                <tr style={{ textAlign: 'left', color: 'var(--muted)' }}>
                  <th style={cellStyle}>Coin</th>
                  <th style={{ ...cellStyle, textAlign: 'right' }}>Totale</th>
                  {FACTORS.map((f) => (
                    <th key={f} style={{ ...cellStyle, textAlign: 'right' }}>{SHORT[f]}</th>
                  ))}
                  <th style={cellStyle}>Stato</th>
                </tr>
              </thead>
              <tbody>
                {shown.map((r) => {
                  const out = (r.excluded ?? []).length > 0;
                  return (
                    <tr key={r.symbol} style={{ borderTop: '1px solid #28303d',
                                                opacity: out ? 0.55 : 1 }}>
                      <td style={{ ...cellStyle, fontWeight: 600,
                                   textDecoration: out ? 'line-through' : undefined }}>
                        {r.symbol}
                      </td>
                      <td style={{ ...cellStyle, textAlign: 'right', fontWeight: 700,
                                   color: cell(r.score) }}>
                        {r.score.toFixed(3)}
                      </td>
                      {FACTORS.map((f) => (
                        <td key={f} style={{ ...cellStyle, textAlign: 'right',
                                             color: cell(r.components?.[f]) }}>
                          {r.components?.[f] !== undefined
                            ? r.components[f].toFixed(2) : '—'}
                        </td>
                      ))}
                      <td style={{ ...cellStyle, fontSize: 12,
                                   color: out ? 'var(--red)' : 'var(--green)' }}>
                        {out ? (r.excluded ?? []).join('; ')
                             : (r.recent_stops ? `${r.recent_stops} stop recenti` : 'ok')}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {rows.length > 15 && (
            <button className="btn" style={{ marginTop: 10 }} onClick={() => setAll(!all)}>
              {all ? 'Mostra solo le prime 15' : `Mostra tutte (${rows.length})`}
            </button>
          )}
          <p className="muted" style={{ fontSize: 11, marginTop: 8 }}>
            Ultimo scan:{' '}
            {d?.updated_at ? new Date(d.updated_at * 1000).toLocaleString('it-IT') : '—'}
          </p>
        </>
      )}
    </div>
  );
}
