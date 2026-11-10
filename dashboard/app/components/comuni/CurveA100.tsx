'use client';

import { useMemo, useState } from 'react';
import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { curveA100, giornoBreve, type Giorni } from '../../lib/conti';
import { Suggerimento } from './Suggerimento';

/**
 * Le curve di tutte le strategie messe a 100 alla stessa data (mattone comune a crypto e azioni: ogni serie è `{giorno: valore di
 * fine giorno}`, con quello di adesso per oggi; la scheda crypto passa /{ramo}/giorni, quella delle azioni /azioni/strategie/*). La data è il primo giorno in cui ci sono tutte quelle accese: si tocca un nome per toglierlo o rimetterlo, e la partenza
 * si sposta. Una sola scala (nessun doppio asse); colori per strategia, sempre gli stessi (skill dataviz: slot 1-6 validati);
 * leggenda sempre presente con il valore di adesso, che fa anche da tabella; il riquadro al tocco mostra tutte le curve del giorno.
 */
const num = (v: number, cifre = 1) => v.toLocaleString('it-IT', { minimumFractionDigits: cifre, maximumFractionDigits: cifre });

/** Una curva: la chiave stabile (il colore la segue, non l'ordine), il nome, il colore validato e i valori di fine giorno. */
export interface SerieCurva {
  chiave: string;
  nome: string;
  colore: string;
  giorni: Giorni;
}

export default function CurveA100({ curve, oggi, titolo = 'Le strategie a confronto, tutte a 100' }: {
  curve: SerieCurva[];
  /** il giorno in corso, nella convenzione delle chiavi delle serie */
  oggi: string | null;
  titolo?: string;
}) {
  const [spente, setSpente] = useState<string[]>([]);
  const serie = useMemo(() => Object.fromEntries(curve.map((c) => [c.chiave, c.giorni])) as Record<string, Giorni>, [curve]);
  const defDi = (k: string) => curve.find((c) => c.chiave === k) ?? { chiave: k, nome: k, colore: 'var(--text-faint)', giorni: {} };
  const disponibili = curve.filter((s) => Object.keys(s.giorni ?? {}).length > 0).map((s) => ({ ...s, ramo: s.chiave }));
  const chiaveAccese = disponibili.filter((s) => !spente.includes(s.ramo)).map((s) => s.ramo).join(',');
  const accese = useMemo(() => (chiaveAccese ? chiaveAccese.split(',') : []), [chiaveAccese]);
  const { base, righe } = useMemo(() => curveA100(serie, accese), [serie, accese]);

  // la strategia che fissa la partenza: quella accesa che comincia per ultima
  const ultimaAPartire = useMemo(() => {
    let r: string | null = null;
    let primo = '';
    for (const x of accese) {
      const p = Object.keys(serie[x] ?? {}).sort()[0] ?? '';
      if (p >= primo) { primo = p; r = x; }
    }
    return r;
  }, [serie, accese]);

  const ultimoIndice = useMemo(() => {
    const out: Record<string, number> = {};
    righe.forEach((r, i) => { for (const k of accese) if (r[k] != null) out[k] = i; });
    return out;
  }, [righe, accese]);

  const valoreFinale = (ramo: string): number | null => {
    const i = ultimoIndice[ramo];
    return i == null ? null : Number(righe[i][ramo]);
  };

  const cambia = (ramo: string) =>
    setSpente((p) => (p.includes(ramo) ? p.filter((x) => x !== ramo) : [...p, ramo]));

  // le partenze possibili: il primo giorno di ogni strategia; scegliendone una si tolgono quelle partite dopo
  const primoDi = (ramo: string) => Object.keys(serie[ramo] ?? {}).sort()[0] ?? '';
  const partenze = Array.from(new Set(disponibili.map((s) => primoDi(s.ramo)))).sort().reverse();
  const dopo = (g: string) => disponibili.filter((s) => primoDi(s.ramo) > g).map((s) => s.ramo);
  const scelta = (g: string) => {
    const via = dopo(g);
    return base === g && via.length === spente.length && via.every((r) => spente.includes(r));
  };

  if (disponibili.length === 0) {
    return (
      <section className="cr-pannello">
        <h2>{titolo}</h2>
        <p className="cr-sotto">Ancora nessun giorno registrato su Firebase.</p>
      </section>
    );
  }

  return (
    <section className="cr-pannello">
      <h2>{titolo}</h2>
      <p className="cr-sotto">
        {base ? (
          <>
            Tutte valgono 100 alla chiusura del <b>{giornoBreve(base)}</b>
            {ultimaAPartire ? <>, il primo giorno registrato di {defDi(ultimaAPartire).nome}</> : null}: 104 vuol dire +4% da
            quel giorno. Per vedere più giorni scegli una partenza più vecchia (fra parentesi quante strategie ci sono); un nome si
            toglie o si rimette toccandolo.
          </>
        ) : 'Accendi almeno una strategia toccando il suo nome.'}
      </p>

      {partenze.length > 1 && (
        <div className="cr-sottoschede cr-partenze" role="group" aria-label="da quale giorno">
          <span className="cr-partenze-nome">Da quando:</span>
          {partenze.map((g, i) => (
            <button key={g} type="button" aria-pressed={scelta(g)} onClick={() => setSpente(dopo(g))}>
              {giornoBreve(g)}{i === 0 ? ' (tutte)' : ` (${disponibili.length - dopo(g).length})`}
            </button>
          ))}
        </div>
      )}

      <ul className="cr-legenda" aria-label="strategie nel grafico">
        {disponibili.map((s) => {
          const accesa = !spente.includes(s.ramo);
          const v = accesa ? valoreFinale(s.ramo) : null;
          return (
            <li key={s.ramo}>
              <button type="button" aria-pressed={accesa} onClick={() => cambia(s.ramo)}
                title={accesa ? `Togli ${s.nome} dal grafico` : `Rimetti ${s.nome} nel grafico`}>
                <span className="cr-chiave" style={{ background: s.colore }} aria-hidden="true" />
                {s.nome}
                {v != null && <span className="cr-num">{num(v)}</span>}
              </button>
            </li>
          );
        })}
      </ul>

      {righe.length < 2 ? (
        <p className="cr-sotto">
          C&apos;è un solo giorno da quella partenza: la curva si disegna da domani. Togli una strategia partita da poco per vedere più
          giorni.
        </p>
      ) : (
        <div className="cr-grafico">
          <ResponsiveContainer>
            <LineChart data={righe} margin={{ top: 8, right: 14, bottom: 0, left: 0 }}>
              <CartesianGrid stroke="var(--griglia)" vertical={false} />
              <XAxis dataKey="giorno" stroke="var(--asse)" tick={{ fill: 'var(--text-faint)', fontSize: 11 }} tickLine={false}
                minTickGap={24} tickFormatter={(g: string) => giornoBreve(g)} padding={{ left: 4, right: 18 }} />
              <YAxis stroke="var(--asse)" tick={{ fill: 'var(--text-faint)', fontSize: 11 }} tickLine={false} width={44}
                domain={['auto', 'auto']} tickFormatter={(v: number) => num(v, 0)} allowDecimals={false} />
              <ReferenceLine y={100} stroke="var(--asse)" />
              <Tooltip
                cursor={{ stroke: 'var(--text-faint)', strokeWidth: 1 }}
                isAnimationActive={false}
                content={({ active, payload, label }) => {
                  if (!active || !payload?.length) return null;
                  const g = String(label);
                  const voci = payload
                    .filter((p) => p.value != null)
                    .sort((a, b) => Number(b.value) - Number(a.value))
                    .map((p) => {
                      const d = defDi(String(p.dataKey));
                      const v = Number(p.value);
                      return { chiave: d.chiave, nome: d.nome, colore: d.colore, forma: 'linea' as const,
                        valore: `${num(v)} (${v >= 100 ? '+' : '−'}${num(Math.abs(v - 100))}%)` };
                    });
                  return <Suggerimento titolo={`${giornoBreve(g)}${g === oggi ? ' · oggi, in corso' : ''}`} voci={voci} />;
                }}
              />
              {accese.map((ramo) => {
                const d = defDi(ramo);
                return (
                  <Line key={ramo} dataKey={ramo} name={d.nome} type="linear" stroke={d.colore} strokeWidth={2}
                    strokeLinecap="round" strokeLinejoin="round" connectNulls isAnimationActive={false}
                    activeDot={{ r: 5, stroke: 'var(--bg-panel)', strokeWidth: 2, fill: d.colore }}
                    dot={(p: { index: number; cx?: number; cy?: number }) =>
                      p.index === ultimoIndice[ramo] && p.cx != null && p.cy != null
                        ? <circle key={`${ramo}-fine`} cx={p.cx} cy={p.cy} r={4} fill={d.colore} stroke="var(--bg-panel)" strokeWidth={2} />
                        : <g key={`${ramo}-${p.index}`} />} />
                );
              })}
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {righe.length >= 2 && (
        <details>
          <summary className="cr-link">I numeri del grafico</summary>
          <div className="cr-scorre">
            <table className="cr-tabella">
              <thead>
                <tr>
                  <th>Giorno</th>
                  {accese.map((r) => <th key={r}>{defDi(r).nome}</th>)}
                </tr>
              </thead>
              <tbody>
                {[...righe].reverse().map((r) => (
                  <tr key={String(r.giorno)}>
                    <td>{giornoBreve(String(r.giorno))}{r.giorno === oggi ? ' (oggi)' : ''}</td>
                    {accese.map((k) => <td key={k}>{r[k] != null ? num(Number(r[k])) : '—'}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </details>
      )}
    </section>
  );
}
