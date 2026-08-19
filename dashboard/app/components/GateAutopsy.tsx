'use client';

import { useEffect, useMemo, useState } from 'react';
import { doc, onSnapshot } from 'firebase/firestore';
import { getDb } from '../lib/firebase';

/**
 * DOVE MUOIONO LE CANDIDATE.
 *
 * Il gate rispondeva sì/no e buttava via il motivo. Con oltre ventimila valutazioni
 * per passata questo significa ripetere ventimila esperimenti senza conservarne
 * l'esito: se non passa nessuno non si sa se muoiono per pochi trade, perché il
 * profitto non batte i costi, o perché crollano sui dati mai visti. E senza saperlo
 * l'unica reazione possibile è abbassare le soglie a caso, cioè validare rumore.
 *
 * Due letture, e servono entrambe:
 *
 *   * CHI FERMA — il criterio messo peggio per ciascuna candidata. Dice dov'è il
 *     collo di bottiglia della ricerca.
 *   * CHI È COINVOLTO — quante volte ogni criterio compare, anche non da solo. Un
 *     criterio presente in quasi tutte le bocciature non sta selezionando: sta
 *     descrivendo la qualità media delle candidate. Allentarlo non convertirebbe
 *     nessuno, perché quelle candidate fallirebbero comunque altri cinque controlli.
 *     È la lezione che ha fatto riscrivere la scelta della leva del supervisore.
 *
 * I QUASI-PASSAGGI sono le candidate fermate da UN SOLO criterio e per poco: le
 * uniche che un allentamento convertirebbe davvero, e i semi da cui la discovery
 * muta al giro dopo.
 */
type Near = {
  key?: string;
  binding?: string;
  shortfall?: number;
  pf?: number;
  trades?: number;
  t_stat?: number;
};
type Rep = {
  updated_at?: number;
  evaluated?: number;
  passed?: number;
  diagnosed?: number;
  binding?: Record<string, number>;
  involved?: Record<string, number>;
  near_misses?: Near[];
  near_miss_count?: number;
};

/** Cosa vuol dire ogni criterio, in italiano. Un'etichetta tecnica senza glossa è
 *  un'informazione che chi guarda deve andarsi a cercare altrove. */
const SIGNIFICATO: Record<string, string> = {
  trades: 'pochi segnali: la strategia spara troppo poco',
  pf: 'il profitto lordo non batte i costi (fee + spread + funding)',
  win_rate: 'vince troppo di rado perché i guadagni ripaghino le perdite',
  total_return: 'profittevole, ma di troppo poco per valere il rischio',
  consistency: 'guadagna in un periodo e perde negli altri',
  oos_windows: 'tutti i trade in una sola finestra: un’osservazione, non un walk-forward',
  recovery: 'la curva scava buche troppo profonde rispetto a quanto rende',
  pf_ex_top: 'regge solo grazie ai suoi pochi colpi migliori: fortuna, non edge',
  regime: 'in almeno un regime di mercato perde in modo conclamato',
  holdout: 'funziona dove l’abbiamo scelta e non sui dati mai visti: sovradattamento',
};

function Barre({ dati, tot }: { dati: [string, number][]; tot: number }) {
  if (!dati.length) return <p className="muted" style={{ fontSize: 13 }}>—</p>;
  const max = Math.max(...dati.map(([, v]) => v)) || 1;
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
      {dati.map(([k, v]) => (
        <div key={k}>
          <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
            <span>{k}</span>
            <span className="muted">
              {v.toLocaleString('it-IT')} · {tot ? ((v / tot) * 100).toFixed(0) : '0'}%
            </span>
          </div>
          <div
            style={{
              height: 6,
              background: 'var(--border-soft)',
              borderRadius: 3,
              overflow: 'hidden',
              margin: '3px 0 2px',
            }}
          >
            <div
              style={{
                width: `${(v / max) * 100}%`,
                height: '100%',
                background: 'var(--accent)',
                borderRadius: 3,
              }}
            />
          </div>
          {SIGNIFICATO[k] && (
            <div className="muted" style={{ fontSize: 11 }}>
              {SIGNIFICATO[k]}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default function GateAutopsy() {
  const [cur, setCur] = useState<Rep | null>(null);
  const [dis, setDis] = useState<Rep | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    try {
      const db = getDb();
      const a = onSnapshot(
        doc(db, 'gate_autopsy', 'current'),
        (s) => { setCur(s.exists() ? (s.data() as Rep) : null); setLoaded(true); },
        () => setLoaded(true),
      );
      const b = onSnapshot(
        doc(db, 'gate_autopsy', 'discover'),
        (s) => setDis(s.exists() ? (s.data() as Rep) : null),
        () => {},
      );
      return () => { a(); b(); };
    } catch {
      setLoaded(true);
      return;
    }
  }, []);

  /** Le due autopsie sommate: la discovery porta il volume, l'optimizer le
   *  strategie base. Per capire dove si muore contano insieme. */
  const tot = useMemo(() => {
    const somma = (f: (r: Rep) => Record<string, number> | undefined) => {
      const out: Record<string, number> = {};
      for (const r of [cur, dis]) {
        if (!r) continue;
        for (const [k, v] of Object.entries(f(r) ?? {})) out[k] = (out[k] ?? 0) + Number(v || 0);
      }
      return Object.entries(out).sort((x, y) => y[1] - x[1]);
    };
    const evaluated = Number(cur?.evaluated ?? 0) + Number(dis?.evaluated ?? 0);
    const passed = Number(cur?.passed ?? 0) + Number(dis?.passed ?? 0);
    const diagnosed = Number(cur?.diagnosed ?? 0) + Number(dis?.diagnosed ?? 0);
    const near = [...(cur?.near_misses ?? []), ...(dis?.near_misses ?? [])]
      .sort((a, b) => (b.shortfall ?? -9) - (a.shortfall ?? -9))
      .slice(0, 12);
    return { binding: somma((r) => r.binding), involved: somma((r) => r.involved),
             evaluated, passed, diagnosed, near };
  }, [cur, dis]);

  /** Un criterio presente in ≥90% delle bocciature descrive il mercato, non seleziona. */
  const universali = tot.involved
    .filter(([, v]) => tot.diagnosed && v >= 0.9 * tot.diagnosed)
    .map(([k]) => k);

  return (
    <div className="panel">
      <h2>Perché le candidate non passano</h2>
      <p className="subtitle">
        L&apos;autopsia dell&apos;ultima passata: su cosa si fermano le strategie
        provate, e quali erano a un passo. È il dato su cui il supervisore sceglie dove
        intervenire — senza, si tarerebbe al buio.
      </p>

      {!loaded ? (
        <p className="muted">Caricamento…</p>
      ) : !cur && !dis ? (
        <p className="muted">
          Nessuna autopsia disponibile. Viene scritta a ogni passata dell&apos;optimizer
          (ogni 3 ore).
        </p>
      ) : (
        <>
          <div style={{ display: 'flex', gap: 18, flexWrap: 'wrap', fontSize: 13, marginBottom: 12 }}>
            <span>
              valutate <b>{tot.evaluated.toLocaleString('it-IT')}</b>
            </span>
            <span style={{ color: tot.passed > 0 ? 'var(--green)' : undefined }}>
              passate <b>{tot.passed.toLocaleString('it-IT')}</b>
            </span>
            <span>
              quasi-passaggi{' '}
              <b>
                {(Number(cur?.near_miss_count ?? 0) + Number(dis?.near_miss_count ?? 0)).toLocaleString('it-IT')}
              </b>
            </span>
          </div>

          <div className="grid grid-2" style={{ gap: 18 }}>
            <div>
              <div className="muted" style={{ fontSize: 12, marginBottom: 8 }}>
                CHI LE FERMA (il criterio messo peggio)
              </div>
              <Barre dati={tot.binding.slice(0, 8)} tot={tot.diagnosed} />
            </div>
            <div>
              <div className="muted" style={{ fontSize: 12, marginBottom: 8 }}>
                CHI È COINVOLTO (anche non da solo)
              </div>
              <Barre dati={tot.involved.slice(0, 8)} tot={tot.diagnosed} />
            </div>
          </div>

          {universali.length > 0 && (
            <p style={{ fontSize: 12, marginTop: 12, color: 'var(--amber)' }}>
              {universali.join(', ')} compare in quasi tutte le bocciature: sta
              descrivendo la qualità media delle candidate, non facendo da filtro.
              Allentarlo non ne convertirebbe nessuna — fallirebbero comunque gli altri
              criteri.
            </p>
          )}

          <div className="muted" style={{ fontSize: 12, margin: '16px 0 6px' }}>
            A UN PASSO (fermate da un solo criterio)
          </div>
          {tot.near.length === 0 ? (
            <p className="muted" style={{ fontSize: 13 }}>
              Nessuna. Vuol dire che non esiste una soglia che ne sbloccherebbe qualcuna:
              il problema non è il gate, sono le candidate.
            </p>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', fontSize: 12, borderCollapse: 'collapse' }}>
                <thead>
                  <tr className="muted" style={{ textAlign: 'left' }}>
                    <th style={{ padding: '4px 8px 4px 0' }}>coppia</th>
                    <th style={{ padding: '4px 8px' }}>ferma su</th>
                    <th style={{ padding: '4px 8px' }}>quanto manca</th>
                    <th style={{ padding: '4px 8px' }}>PF</th>
                    <th style={{ padding: '4px 8px' }}>trade</th>
                  </tr>
                </thead>
                <tbody>
                  {tot.near.map((n, i) => (
                    <tr key={`${n.key}-${i}`} style={{ borderTop: '1px solid var(--border-soft)' }}>
                      <td style={{ padding: '4px 8px 4px 0', whiteSpace: 'nowrap' }}>{n.key}</td>
                      <td style={{ padding: '4px 8px' }}>{n.binding}</td>
                      <td style={{ padding: '4px 8px' }}>
                        {n.shortfall != null ? `${(Math.abs(n.shortfall) * 100).toFixed(1)}%` : '—'}
                      </td>
                      <td style={{ padding: '4px 8px' }}>{n.pf?.toFixed?.(2) ?? '—'}</td>
                      <td style={{ padding: '4px 8px' }}>{n.trades ?? '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}
