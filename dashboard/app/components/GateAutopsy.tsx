'use client';

import { useEffect, useMemo, useState } from 'react';
import { doc, onSnapshot } from 'firebase/firestore';
import { getDb } from '../lib/firebase';
import { CHROME, STATO, durata, formatta } from '../lib/viz';
import { useOrologio } from './GateCervello';

/**
 * DOVE MUOIONO LE CANDIDATE.
 *
 * Il gate rispondeva sì/no e buttava via il motivo. Con oltre ventimila valutazioni
 * per passata questo significa ripetere ventimila esperimenti senza conservarne
 * l'esito: se non passa nessuno non si sa se muoiono per pochi trade, perché il
 * profitto non batte i costi, o perché crollano sui dati mai visti. E senza saperlo
 * l'unica reazione possibile è abbassare le soglie a caso, cioè validare rumore.
 *
 * DUE LETTURE, E SERVONO ENTRAMBE — per questo sono un interruttore e non due liste
 * affiancate: messe una accanto all'altra sembrano la stessa cosa misurata due volte,
 * mentre dicono cose opposte.
 *
 *   * CHI FERMA — il criterio messo peggio per ciascuna candidata: dov'è il collo di
 *     bottiglia.
 *   * CHI È COINVOLTO — quante volte un criterio compare, anche non da solo. Un
 *     criterio presente in quasi tutte le bocciature non sta selezionando: sta
 *     descrivendo la qualità media delle candidate. Allentarlo non convertirebbe
 *     nessuno, perché quelle candidate fallirebbero comunque altri cinque controlli.
 *     È la lezione che ha fatto riscrivere la scelta della leva del supervisore.
 *
 * INTERATTIVO PERCHÉ SERVE, non per decorazione: cliccando un criterio la tabella
 * sotto mostra solo le candidate fermate da QUELLO. È la domanda che ci si fa
 * davvero guardando l'istogramma ("chi sono quelle 40 lì?"), e prima richiedeva di
 * andarsele a cercare a mano nel documento su Firebase.
 *
 * UNA RIGA IN CHIARO, IL RESTO CHIUSO (25 set 2026). Il pannello era il più lungo
 * della scheda e la sua risposta sta in una frase per autopsia: quante valutate,
 * quante passate, chi ferma di più, quante a un passo, e di QUANDO è. Il dettaglio
 * si apre. E le due autopsie non si sommano più: `discover` è di stamattina,
 * `current` (optimizer sulle strategie base) può essere di giorni fa — si sceglie
 * quale guardare, con la sua età accanto.
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

/** Cosa vuol dire ogni criterio, in italiano: un'etichetta tecnica senza glossa è
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

type Vista = 'binding' | 'involved';
type Fonte = 'dis' | 'cur';

export default function GateAutopsy() {
  const [cur, setCur] = useState<Rep | null>(null);
  const [dis, setDis] = useState<Rep | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [vista, setVista] = useState<Vista>('binding');
  const [scelto, setScelto] = useState<string | null>(null);
  const [fonte, setFonte] = useState<Fonte>('dis');
  const now = useOrologio();

  useEffect(() => {
    try {
      const db = getDb();
      const a = onSnapshot(doc(db, 'gate_autopsy', 'current'),
        (s) => { setCur(s.exists() ? (s.data() as Rep) : null); setLoaded(true); },
        () => setLoaded(true));
      const b = onSnapshot(doc(db, 'gate_autopsy', 'discover'),
        (s) => setDis(s.exists() ? (s.data() as Rep) : null), () => {});
      return () => { a(); b(); };
    } catch {
      setLoaded(true);
      return;
    }
  }, []);

  /** UNA autopsia per volta, scelta dall'interruttore: la discovery porta il
   *  volume (oltre ventimila valutazioni ogni 3 ore), l'optimizer le strategie
   *  base (~1500, di rado). Sommarle mischiava due date. */
  const rep = fonte === 'dis' ? dis : cur;
  const tot = useMemo(() => {
    const ordina = (m: Record<string, number> | undefined) =>
      Object.entries(m ?? {}).map(([k, v]) => [k, Number(v || 0)] as [string, number]).sort((x, y) => y[1] - x[1]);
    const near = [...(rep?.near_misses ?? [])].sort((a, b) => (b.shortfall ?? -9) - (a.shortfall ?? -9));
    return {
      binding: ordina(rep?.binding),
      involved: ordina(rep?.involved),
      diagnosed: Number(rep?.diagnosed ?? 0),
      near,
    };
  }, [rep]);

  /** La frase che riassume un'autopsia, con la sua età. */
  const riassunto = (r: Rep | null, nome: string) => {
    if (!r) return <span className="muted">{nome}: nessuna autopsia.</span>;
    const ev = Number(r.evaluated ?? 0);
    const pa = Number(r.passed ?? 0);
    const primo = Object.entries(r.binding ?? {}).sort((x, y) => Number(y[1]) - Number(x[1]))[0];
    const dg = Number(r.diagnosed ?? 0);
    return (
      <>
        <b>{nome}</b>
        {r.updated_at ? <span className="muted"> ({durata(now - r.updated_at)} fa)</span> : null}: {formatta(ev)} valutate,{' '}
        {formatta(pa)} passate{ev > 0 ? ` (${((pa / ev) * 100).toFixed(2)}%)` : ''}
        {primo ? (
          <>
            {' '}· ferma di più <b>{primo[0]}</b>{dg > 0 ? ` (${Math.round((Number(primo[1]) / dg) * 100)}% delle bocciate)` : ''}
          </>
        ) : null}
        {r.near_miss_count != null ? <> · {formatta(r.near_miss_count)} a un passo</> : null}
      </>
    );
  };

  const dati = vista === 'binding' ? tot.binding : tot.involved;
  const max = Math.max(1, ...dati.map(([, v]) => v));

  /** Un criterio presente in ≥90% delle bocciature descrive il mercato, non seleziona. */
  const universali = tot.involved
    .filter(([, v]) => tot.diagnosed && v >= 0.9 * tot.diagnosed)
    .map(([k]) => k);

  const nearMostrati = scelto ? tot.near.filter((n) => n.binding === scelto) : tot.near;

  return (
    <div className="panel">
      <h2>Perché le candidate non passano</h2>
      <p className="subtitle">
        L&apos;autopsia dell&apos;ultima passata: dove muoiono le candidate. È il dato su
        cui il supervisore sceglie dove intervenire.
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
          <div style={{ fontSize: 13, lineHeight: 1.6, marginBottom: 6 }}>
            <div>{riassunto(dis, 'Discovery')}</div>
            <div>{riassunto(cur, 'Optimizer (strategie base)')}</div>
          </div>
          <details>
            <summary style={{ cursor: 'pointer', fontSize: 12, color: 'var(--text-dim)', marginBottom: 10 }}>
              dettaglio: criteri, a un passo, filtro per criterio
            </summary>
          <div style={{ display: 'flex', gap: 6, marginBottom: 12, flexWrap: 'wrap' }}>
            <button
              onClick={() => setFonte('dis')}
              className={`btn ${fonte === 'dis' ? 'btn-primary' : 'btn-ghost'}`}
              style={{ padding: '4px 12px', fontSize: 12 }}
              aria-pressed={fonte === 'dis'}
              disabled={!dis}
            >
              Discovery
            </button>
            <button
              onClick={() => setFonte('cur')}
              className={`btn ${fonte === 'cur' ? 'btn-primary' : 'btn-ghost'}`}
              style={{ padding: '4px 12px', fontSize: 12 }}
              aria-pressed={fonte === 'cur'}
              disabled={!cur}
            >
              Optimizer
            </button>
            <span style={{ width: 8 }} />
            <button
              onClick={() => setVista('binding')}
              className={`btn ${vista === 'binding' ? 'btn-primary' : 'btn-ghost'}`}
              style={{ padding: '4px 12px', fontSize: 12 }}
              aria-pressed={vista === 'binding'}
            >
              Chi le ferma
            </button>
            <button
              onClick={() => setVista('involved')}
              className={`btn ${vista === 'involved' ? 'btn-primary' : 'btn-ghost'}`}
              style={{ padding: '4px 12px', fontSize: 12 }}
              aria-pressed={vista === 'involved'}
            >
              Chi è coinvolto
            </button>
            {scelto && (
              <button
                onClick={() => setScelto(null)}
                className="btn btn-ghost"
                style={{ padding: '4px 12px', fontSize: 12 }}
              >
                ✕ togli il filtro «{scelto}»
              </button>
            )}
          </div>

          <p className="muted" style={{ fontSize: 12, marginTop: -4, marginBottom: 10 }}>
            {vista === 'binding'
              ? 'Il criterio messo peggio per ciascuna candidata: dov’è il collo di bottiglia.'
              : 'Quante volte ogni criterio compare, anche insieme ad altri: descrive il terreno, non il filtro.'}
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {dati.slice(0, 10).map(([k, v]) => {
              const attivo = scelto === k;
              const perc = tot.diagnosed ? (v / tot.diagnosed) * 100 : 0;
              return (
                <button
                  key={k}
                  onClick={() => setScelto(attivo ? null : k)}
                  title={SIGNIFICATO[k] ?? k}
                  aria-pressed={attivo}
                  style={{
                    display: 'block',
                    width: '100%',
                    textAlign: 'left',
                    background: attivo ? 'var(--accent-soft)' : 'transparent',
                    border: '1px solid transparent',
                    borderColor: attivo ? 'var(--border)' : 'transparent',
                    borderRadius: 8,
                    // area cliccabile generosa: la barra è alta 6px, il bersaglio no
                    padding: '7px 9px',
                    cursor: 'pointer',
                    color: 'inherit',
                    font: 'inherit',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
                    <span>{k}</span>
                    <span className="muted" style={{ fontVariantNumeric: 'tabular-nums' }}>
                      {formatta(v)} · {perc.toFixed(0)}%
                    </span>
                  </div>
                  <div
                    style={{
                      height: 6,
                      background: CHROME.griglia,
                      borderRadius: 3,
                      overflow: 'hidden',
                      margin: '4px 0 3px',
                    }}
                  >
                    <div
                      style={{
                        width: `${(v / max) * 100}%`,
                        height: '100%',
                        background: universali.includes(k) && vista === 'involved'
                          ? STATO.attenzione
                          : 'var(--accent)',
                        borderRadius: 3,
                      }}
                    />
                  </div>
                  {SIGNIFICATO[k] && (
                    <div className="muted" style={{ fontSize: 11 }}>
                      {SIGNIFICATO[k]}
                    </div>
                  )}
                </button>
              );
            })}
          </div>

          {universali.length > 0 && vista === 'involved' && (
            <p style={{ fontSize: 12, marginTop: 10, color: STATO.attenzione }}>
              ⚠ {universali.join(', ')} compare in quasi tutte le bocciature: sta
              descrivendo la qualità media delle candidate, non facendo da filtro.
              Allentarlo non ne convertirebbe nessuna — fallirebbero comunque gli altri
              criteri.
            </p>
          )}

          <div className="muted" style={{ fontSize: 12, margin: '16px 0 6px' }}>
            A UN PASSO — fermate da un solo criterio
            {scelto && <> · filtrate su <b>{scelto}</b></>}
            {' '}({nearMostrati.length})
          </div>
          {nearMostrati.length === 0 ? (
            <p className="muted" style={{ fontSize: 13 }}>
              {scelto
                ? 'Nessun quasi-passaggio su questo criterio: le candidate che ferma fallivano anche altro.'
                : 'Nessuna. Vuol dire che non esiste una soglia che ne sbloccherebbe qualcuna: il problema non è il gate, sono le candidate.'}
            </p>
          ) : (
            <div style={{ overflowX: 'auto', maxHeight: 300, overflowY: 'auto' }}>
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
                <tbody style={{ fontVariantNumeric: 'tabular-nums' }}>
                  {nearMostrati.slice(0, 40).map((n, i) => (
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
          </details>
        </>
      )}
    </div>
  );
}
