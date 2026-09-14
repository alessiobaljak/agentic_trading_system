'use client';

import { useEffect, useMemo, useState } from 'react';
import { doc, onSnapshot } from 'firebase/firestore';
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  LabelList,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { getDb } from '../lib/firebase';
import { CHROME, GATE_RAMP, STATO } from '../lib/viz';

/**
 * IL CRUSCOTTO DELLA MATURAZIONE — chi è a che punto, e da quando.
 *
 * Richiesta del proprietario il 14 settembre: «ho bisogno di vedere quali strategie e
 * coin sono a 1 e in che data, quali a 2, e quali a 3 o quando lo saranno».
 *
 * La domanda vera dietro la richiesta è un'altra, ed è la ragione per cui questo
 * pannello esiste invece di essere una tabella in più: **la fila si muove?** Il
 * catalogo delle strategie dice cosa c'è; l'evoluzione dice come cresce il totale.
 * Nessuno dei due dice se una singola coppia sta AVANZANDO o è ferma — ed è
 * esattamente la differenza fra "ci stiamo arrivando" e "stiamo aspettando una cosa
 * che non arriverà".
 *
 * TRE DISTINZIONI CHE LA TABELLA DEVE FARE, perché ognuna è costata un difetto:
 *
 *  1. IDONEA ≠ VALIDATA. Una coppia a 2/3 con la finestra scaduta si valida al primo
 *     giro in cui ripassa il gate: può succedere oggi. Il calendario vecchio
 *     stampava solo «validata il <data>», che si leggeva come una promessa.
 *
 *  2. FINESTRA SCADUTA ≠ SCADENZA MANCATA. Chi non ripassa non viene bocciato: nella
 *     discovery il verdetto scatta solo sui passaggi. Resta idoneo e riprova ogni
 *     giorno con un giorno di dati in più. Il gruppo degli idonei si ACCUMULA.
 *
 *  3. FERMA ≠ IN ATTESA. Se la coin esce dal top-N per volume, nessuno valuta più le
 *     sue coppie: non prendono conferme né fallimenti. Restano lì con una data
 *     accanto che nessuno onorerà. È successo a ORCAUSDT il 13 settembre con otto
 *     coppie a 2/3. Qui quelle righe sono marcate FERMA, in arancione, e non
 *     mostrano nessuna data.
 *
 * I colori sono la rampa ordinale validata di lib/viz.ts (più conferme = più chiaro),
 * perché 1 → 2 → 3 sono gradini della stessa scala, non categorie diverse. Il verde
 * di «validata» è un colore di stato e viaggia sempre con l'etichetta accanto.
 */

type PairRec = {
  symbol?: string;
  strategy?: string;
  generated?: boolean;
  pass_count?: number;
  window_start?: number;
  last_pass_data_end?: number;
  last_seen_at?: number;
  last_pf?: number;
};
type Reg = { pairs?: string | Record<string, PairRec>; validated?: string[] };
type Timeline = { min_passes?: number };

/** Una settimana di dati nuovi fra due conferme (OPTIMIZER_NEW_DATA_MIN_HOURS). */
const FINESTRA_S = 168 * 3600;
/** Oltre questi giorni senza essere valutata, la coppia è ferma (OPTIMIZER_FRESH_DAYS). */
const FRESCA_G = 3;
const MIN_PASSES_DEFAULT = 3;

type Stato = 'validata' | 'idonea' | 'attesa' | 'ferma';

type Riga = {
  key: string;
  coin: string;
  strategia: string;
  generata: boolean;
  passi: number;
  ultimaConferma: number;
  finestraChiude: number;
  stato: Stato;
  /** da quanti giorni è idonea (se lo è), o fra quanti lo diventa */
  giorni: number;
  pf?: number;
};

const GIORNO = 86_400_000;
const data = (ts: number) =>
  ts > 0 ? new Date(ts * 1000).toLocaleDateString('it-IT', { day: '2-digit', month: 'short' }) : '—';

const COLORE: Record<Stato, string> = {
  validata: STATO.buono,
  idonea: GATE_RAMP.due,
  attesa: GATE_RAMP.uno,
  ferma: STATO.serio,
};
const ETICHETTA: Record<Stato, string> = {
  validata: 'validata',
  idonea: 'idonea ora',
  attesa: 'in attesa',
  ferma: 'ferma',
};

export default function GateMaturazione() {
  const [reg, setReg] = useState<Reg | null>(null);
  const [minPasses, setMinPasses] = useState(MIN_PASSES_DEFAULT);
  const [loaded, setLoaded] = useState(false);
  const [livello, setLivello] = useState<'tutti' | 1 | 2 | 3>('tutti');
  const [cerca, setCerca] = useState('');
  const [perCoin, setPerCoin] = useState(false);
  const [quante, setQuante] = useState(40);

  useEffect(() => {
    const db = getDb();
    if (!db) {
      setLoaded(true);
      return;
    }
    const u1 = onSnapshot(
      doc(db, 'strategy_registry', 'validated'),
      (snap) => {
        setReg(snap.exists() ? (snap.data() as Reg) : null);
        setLoaded(true);
      },
      () => setLoaded(true),
    );
    // la soglia NON si scrive a mano qui: se il backend la cambiasse, il cruscotto
    // mostrerebbe una scala che non esiste più. Fallback al default se manca.
    const u2 = onSnapshot(
      doc(db, 'gate_history', 'timeline'),
      (snap) => {
        const t = snap.exists() ? (snap.data() as Timeline) : null;
        if (t?.min_passes) setMinPasses(t.min_passes);
      },
      () => {},
    );
    return () => {
      u1();
      u2();
    };
  }, []);

  const righe = useMemo<Riga[]>(() => {
    if (!reg) return [];
    let pairs: Record<string, PairRec> = {};
    try {
      pairs = typeof reg.pairs === 'string' ? JSON.parse(reg.pairs) : (reg.pairs ?? {});
    } catch {
      return [];
    }
    const ora = Date.now();
    const out: Riga[] = [];
    for (const [key, r] of Object.entries(pairs)) {
      const passi = Number(r.pass_count ?? 0);
      if (passi <= 0) continue; // senza nemmeno una conferma non c'è niente da seguire
      const visto = Number(r.last_seen_at ?? 0) * 1000;
      const ws = Number(r.window_start ?? 0);
      const chiude = ws > 0 ? (ws + FINESTRA_S) * 1000 : 0;
      const ferma = visto > 0 && ora - visto > FRESCA_G * GIORNO;
      let stato: Stato;
      if (passi >= minPasses) stato = 'validata';
      else if (ferma) stato = 'ferma';
      else if (chiude > 0 && chiude <= ora) stato = 'idonea';
      else stato = 'attesa';
      out.push({
        key,
        coin: r.symbol ?? key.split('|')[0],
        strategia: r.strategy ?? key.split('|')[1] ?? '—',
        generata: Boolean(r.generated),
        passi,
        ultimaConferma: Number(r.last_pass_data_end ?? 0),
        finestraChiude: chiude / 1000,
        stato,
        giorni: chiude > 0 ? Math.round((chiude - ora) / GIORNO) : 0,
        pf: r.last_pf,
      });
    }
    // prima chi è più avanti, poi chi è più vicino al traguardo
    return out.sort(
      (a, b) => b.passi - a.passi || a.finestraChiude - b.finestraChiude || a.coin.localeCompare(b.coin),
    );
  }, [reg, minPasses]);

  const riepilogo = useMemo(() => {
    const perLivello = new Map<number, { coppie: number; coin: Set<string> }>();
    for (const r of righe) {
      const l = Math.min(r.passi, minPasses);
      if (!perLivello.has(l)) perLivello.set(l, { coppie: 0, coin: new Set() });
      const v = perLivello.get(l)!;
      v.coppie += 1;
      v.coin.add(r.coin);
    }
    const aUnPasso = righe.filter((r) => r.passi === minPasses - 1);
    return {
      livelli: [...Array(minPasses).keys()].map((i) => {
        const l = i + 1;
        const v = perLivello.get(l);
        return { livello: l, coppie: v?.coppie ?? 0, coin: v?.coin.size ?? 0 };
      }),
      idoneeOra: aUnPasso.filter((r) => r.stato === 'idonea'),
      ferme: righe.filter((r) => r.stato === 'ferma'),
    };
  }, [righe, minPasses]);

  /** Quante coppie a un passo diventano idonee, per giorno. La prima barra è
   *  «già idonee»: sono un accumulo, non un evento di quel giorno. */
  const calendario = useMemo(() => {
    const aUnPasso = righe.filter((r) => r.passi === minPasses - 1 && r.stato !== 'ferma');
    const ora = Date.now();
    // la chiave è il timestamp, non l'etichetta: ordinare per stringa metterebbe
    // "01 ott" prima di "15 set"
    const perGiorno = new Map<number, number>();
    let gia = 0;
    for (const r of aUnPasso) {
      if (r.finestraChiude * 1000 <= ora) gia += 1;
      else perGiorno.set(r.finestraChiude, (perGiorno.get(r.finestraChiude) ?? 0) + 1);
    }
    const futuri = [...perGiorno.entries()]
      .sort(([a], [b]) => a - b)
      .map(([ts, n]) => ({ giorno: data(ts), n, adesso: false }));
    return [{ giorno: 'già idonee', n: gia, adesso: true }, ...futuri];
  }, [righe, minPasses]);

  const perCoinRighe = useMemo(() => {
    const m = new Map<string, { coin: string; livelli: number[]; prima: number; ferme: number }>();
    for (const r of righe) {
      if (!m.has(r.coin)) {
        m.set(r.coin, { coin: r.coin, livelli: Array(minPasses).fill(0), prima: Infinity, ferme: 0 });
      }
      const v = m.get(r.coin)!;
      v.livelli[Math.min(r.passi, minPasses) - 1] += 1;
      if (r.stato === 'ferma') v.ferme += 1;
      else if (r.passi === minPasses - 1) v.prima = Math.min(v.prima, r.finestraChiude);
    }
    return [...m.values()].sort(
      (a, b) =>
        b.livelli[minPasses - 1] - a.livelli[minPasses - 1] ||
        b.livelli[minPasses - 2] - a.livelli[minPasses - 2] ||
        a.coin.localeCompare(b.coin),
    );
  }, [righe, minPasses]);

  const filtrate = useMemo(() => {
    const q = cerca.trim().toUpperCase();
    return righe.filter(
      (r) =>
        (livello === 'tutti' || Math.min(r.passi, minPasses) === livello) &&
        (!q || r.coin.includes(q) || r.strategia.toUpperCase().includes(q)),
    );
  }, [righe, livello, cerca, minPasses]);

  useEffect(() => setQuante(40), [livello, cerca, perCoin]);

  const cell = { padding: '6px 8px' } as const;
  /* globals.css allinea `th`/`td` a DESTRA (tabelle di numeri). Coin, strategia e
     stato sono testo: a destra si leggono male e la colonna sembra disallineata. */
  const cellaTesto = { padding: '6px 8px', textAlign: 'left' } as const;
  /* I FILTRI NON POSSONO USARE `.nav-item`: e' la voce della sidebar, quindi
     display:flex a larghezza piena. Riusata qui, ogni filtro diventava un blocco a
     tutta riga e la barra spariva — si vede solo renderizzando, non compilando. */
  const chip = (attivo: boolean) =>
    ({
      padding: '4px 12px',
      fontSize: 12,
      borderRadius: 999,
      cursor: 'pointer',
      border: `1px solid ${attivo ? '#3f7fd0' : '#223049'}`,
      background: attivo ? 'rgba(63,127,208,.18)' : '#0f1726',
      color: attivo ? '#cfe0f7' : '#8b96a5',
      whiteSpace: 'nowrap',
    }) as const;

  if (!loaded) {
    return (
      <div className="panel">
        <h2>Maturazione delle strategie</h2>
        <p className="muted">Loading…</p>
      </div>
    );
  }

  return (
    <div className="panel">
      <h2>Maturazione delle strategie</h2>
      <p className="subtitle">
        Chi è a che punto verso le <b>{minPasses} conferme</b>, e da quando. Una conferma
        richiede una settimana di dati nuovi: <b>idonea</b> vuol dire che la settimana è
        passata e la coppia si valida al primo giro in cui ripassa il gate — anche oggi.
        Chi non ripassa <b>non viene bocciato</b>: resta idoneo e riprova ogni giorno.
      </p>

      {righe.length === 0 ? (
        <p className="muted">
          Nessuna coppia ha ancora una prima conferma: non c&apos;è ancora niente da seguire.
        </p>
      ) : (
        <>
          {/* stat-grid e non grid-2: i livelli sono MIN_PASSES, cioe' tre oggi ma non
              per definizione. Una griglia a due colonne fissa ne manderebbe uno a capo
              da solo, e cambiando la soglia il riquadro si romperebbe in silenzio. */}
          <div className="stat-grid" style={{ marginBottom: 16 }}>
            {riepilogo.livelli.map((l) => (
              <div
                key={l.livello}
                className={`stat-tile${l.livello === minPasses ? ' good' : ''}`}
              >
                <div className="stat-label">
                  {l.livello === minPasses ? 'Validate' : `${l.livello} conferma${l.livello > 1 ? 'e' : ''}`}
                </div>
                <div className="stat-value">{l.coppie}</div>
                <div className="stat-sub">su {l.coin} coin distinte</div>
              </div>
            ))}
          </div>

          <div
            style={{
              background: '#131c2e',
              border: '1px solid #223049',
              borderRadius: 10,
              padding: '10px 12px',
              marginBottom: 16,
            }}
          >
            <b style={{ color: COLORE.idonea }}>
              {riepilogo.idoneeOra.length} coppie possono validarsi oggi
            </b>
            <span className="muted">
              {' '}
              su {new Set(riepilogo.idoneeOra.map((r) => r.coin)).size} coin — hanno {minPasses - 1}{' '}
              conferme e la finestra già scaduta.
            </span>
            {riepilogo.ferme.length > 0 && (
              <div style={{ marginTop: 6 }}>
                <b style={{ color: COLORE.ferma }}>{riepilogo.ferme.length} ferme</b>
                <span className="muted">
                  {' '}
                  — la coin non è più nell&apos;universo scansionato, quindi non avanzano né
                  falliscono.
                </span>
              </div>
            )}
          </div>

          <h3 style={{ fontSize: 14, margin: '0 0 8px' }}>Quando diventano idonee</h3>
          <div style={{ width: '100%', height: 180 }}>
            <ResponsiveContainer>
              <BarChart data={calendario} margin={{ top: 18, right: 8, left: -18, bottom: 0 }}>
                <CartesianGrid stroke={CHROME.griglia} vertical={false} />
                {/* minTickGap: a 400px otto etichette si accavallano fino a
                    diventare una riga sola di caratteri. Meglio saltarne qualcuna. */}
                <XAxis
                  dataKey="giorno"
                  stroke={CHROME.asse}
                  tick={{ fontSize: 11 }}
                  minTickGap={8}
                />
                <YAxis stroke={CHROME.asse} tick={{ fontSize: 11 }} allowDecimals={false} />
                <Tooltip
                  contentStyle={{
                    background: CHROME.superficie,
                    border: `1px solid ${CHROME.griglia}`,
                    borderRadius: 8,
                    fontSize: 12,
                  }}
                  formatter={(v: number) => [`${v} coppie`, 'diventano idonee']}
                />
                <Bar dataKey="n" radius={[4, 4, 0, 0]} maxBarSize={38}>
                  <LabelList dataKey="n" position="top" fill="#9fb0c9" fontSize={11} />
                  {calendario.map((c) => (
                    <Cell key={c.giorno} fill={c.adesso ? COLORE.idonea : COLORE.attesa} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
          <p className="muted" style={{ fontSize: 12, margin: '4px 0 16px' }}>
            La prima barra è un <b>accumulo</b>, non un evento di oggi: chi diventa idoneo
            resta idoneo. Le altre sono il giorno in cui scade la settimana di attesa.
          </p>

          <div
            className="chip-row"
            style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center', marginBottom: 10 }}
          >
            {(['tutti', ...riepilogo.livelli.map((l) => l.livello)] as const).map((l) => (
              <button
                key={String(l)}
                onClick={() => setLivello(l as 'tutti' | 1 | 2 | 3)}
                style={chip(livello === l)}
              >
                {l === 'tutti' ? 'Tutte' : l === minPasses ? 'Validate' : `${l} conferma${l > 1 ? 'e' : ''}`}
              </button>
            ))}
            <input
              value={cerca}
              onChange={(e) => setCerca(e.target.value)}
              placeholder="cerca coin o strategia…"
              style={{
                background: '#0f1726',
                border: '1px solid #223049',
                borderRadius: 8,
                color: 'inherit',
                padding: '5px 10px',
                fontSize: 12,
                minWidth: 160,
              }}
            />
            <button
              onClick={() => setPerCoin((v) => !v)}
              style={chip(perCoin)}
            >
              {perCoin ? 'per coppia' : 'per coin'}
            </button>
          </div>

          <div style={{ overflowX: 'auto' }}>
            {perCoin ? (
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                <thead>
                  <tr style={{ textAlign: 'left', color: '#8b96a5' }}>
                    <th style={cellaTesto}>Coin</th>
                    {riepilogo.livelli.map((l) => (
                      <th key={l.livello} style={cell}>
                        {l.livello === minPasses ? 'validate' : `${l.livello} conf.`}
                      </th>
                    ))}
                    <th style={cellaTesto}>Prima validazione possibile</th>
                    <th style={cell}>Ferme</th>
                  </tr>
                </thead>
                <tbody>
                  {perCoinRighe.slice(0, quante).map((c) => (
                    <tr key={c.coin} style={{ borderTop: '1px solid #1c2740' }}>
                      <td style={cellaTesto}>
                        <b>{c.coin}</b>
                      </td>
                      {c.livelli.map((n, i) => (
                        <td key={i} style={{ ...cell, color: n ? undefined : '#5f6d84' }}>
                          {n || '·'}
                        </td>
                      ))}
                      <td style={cellaTesto}>
                        {c.prima === Infinity ? (
                          <span className="muted">—</span>
                        ) : c.prima * 1000 <= Date.now() ? (
                          <span style={{ color: COLORE.idonea }}>già idonea</span>
                        ) : (
                          data(c.prima)
                        )}
                      </td>
                      <td style={{ ...cell, color: c.ferme ? COLORE.ferma : '#5f6d84' }}>
                        {c.ferme || '·'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                <thead>
                  <tr style={{ textAlign: 'left', color: '#8b96a5' }}>
                    <th style={cellaTesto}>Coin</th>
                    <th style={cellaTesto}>Strategia</th>
                    <th style={cell}>Conferme</th>
                    <th style={cell}>Ultima conferma</th>
                    <th style={cellaTesto}>Stato</th>
                    <th style={cellaTesto}>Quando</th>
                  </tr>
                </thead>
                <tbody>
                  {filtrate.slice(0, quante).map((r) => (
                    <tr key={r.key} style={{ borderTop: '1px solid #1c2740' }}>
                      <td style={cellaTesto}>
                        <b>{r.coin}</b>
                      </td>
                      <td style={{ ...cellaTesto, fontFamily: 'ui-monospace, monospace', fontSize: 12 }}>
                        {r.strategia}
                        {r.generata && (
                          <span className="muted" style={{ fontSize: 11 }}>
                            {' '}
                            (scoperta)
                          </span>
                        )}
                      </td>
                      <td style={cell}>
                        {/* i pallini sono un DOPPIO segnale col numero accanto: il
                            colore da solo non deve mai portare l'informazione */}
                        <span style={{ color: COLORE[r.stato], letterSpacing: 1 }}>
                          {'●'.repeat(Math.min(r.passi, minPasses))}
                        </span>
                        <span style={{ color: '#3a4560', letterSpacing: 1 }}>
                          {'○'.repeat(Math.max(0, minPasses - r.passi))}
                        </span>
                        <span className="muted" style={{ fontSize: 11 }}>
                          {' '}
                          {Math.min(r.passi, minPasses)}/{minPasses}
                        </span>
                      </td>
                      <td style={cell}>{data(r.ultimaConferma)}</td>
                      <td style={{ ...cellaTesto, color: COLORE[r.stato] }}>
                        {ETICHETTA[r.stato]}
                      </td>
                      <td style={cellaTesto}>
                        {r.stato === 'validata' ? (
                          <span className="muted">—</span>
                        ) : r.stato === 'ferma' ? (
                          <span className="muted">nessuna data: non viene più valutata</span>
                        ) : r.stato === 'idonea' ? (
                          <span>
                            idonea da {Math.abs(r.giorni)} giorn{Math.abs(r.giorni) === 1 ? 'o' : 'i'}
                          </span>
                        ) : (
                          <span>
                            idonea il {data(r.finestraChiude)}{' '}
                            <span className="muted">(fra {r.giorni} g)</span>
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>

          {(perCoin ? perCoinRighe.length : filtrate.length) > quante && (
            <button
              onClick={() => setQuante((q) => q + 40)}
              style={{ ...chip(false), marginTop: 10, padding: '5px 14px' }}
            >
              mostra altre ({(perCoin ? perCoinRighe.length : filtrate.length) - quante})
            </button>
          )}
        </>
      )}
    </div>
  );
}
