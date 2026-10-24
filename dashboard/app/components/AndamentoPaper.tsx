'use client';

import { useEffect, useMemo, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { CartesianGrid, Legend, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { getRtdb } from '../lib/firebase';

/**
 * L'andamento giorno per giorno del paper del bot e del conto demo di Binance (24 ott 2026, richiesta del proprietario: «aggiungi
 * il grafico paper»). Ogni serie e' il rendimento dal suo capitale di partenza (il paper 10.000 dollari virtuali, il demo il saldo
 * del primo giorno): partono in momenti diversi, quindi si confrontano le pendenze, non il livello del primo giorno. Legge
 * /{ramo}/giorni (il valore dell'ultima ora di ogni giorno UTC, scritto da f5.py e demo_binance.py) e il valore di adesso dallo
 * stato. Colori: la tavolozza di riferimento (slot 1-4, validata sul bianco: due colori sotto 3:1, per questo la legenda, le
 * etichette a fine linea e la tabella sotto).
 */

const SERIE: { ramo: string; nome: string; colore: string; base: 'capitale' | 'capitale_iniziale' }[] = [
  { ramo: 'paper_g1', nome: 'G1 nel paper', colore: '#2a78d6', base: 'capitale' },
  { ramo: 'demo_binance', nome: 'G1 sul conto demo di Binance', colore: '#eb6834', base: 'capitale_iniziale' },
  { ramo: 'paper_g11', nome: 'G11 nel paper', colore: '#1baf7a', base: 'capitale' },
  { ramo: 'paper_f5', nome: 'F5 nel paper (dal 26 ottobre)', colore: '#eda100', base: 'capitale' },
];

type Stato = { equity?: number; capitale?: number; capitale_iniziale?: number; aggiornato?: number };

function pct(x: number | null | undefined): string {
  return x == null || !Number.isFinite(x) ? '—' : `${x >= 0 ? '+' : ''}${(100 * x).toFixed(2)}%`;
}

export default function AndamentoPaper() {
  const [giorni, setGiorni] = useState<Record<string, Record<string, number> | null>>({});
  const [stati, setStati] = useState<Record<string, Stato | null>>({});

  useEffect(() => {
    const db = getRtdb();
    const u = SERIE.flatMap((s) => [
      onValue(ref(db, `${s.ramo}/giorni`), (x) => setGiorni((g) => ({ ...g, [s.ramo]: x.val() }))),
      onValue(ref(db, `${s.ramo}/stato`), (x) => setStati((g) => ({ ...g, [s.ramo]: x.val() }))),
    ]);
    return () => u.forEach((x) => x());
  }, []);

  // una riga per giorno: { giorno, paper_g1: rendimento, ... }; l'ultimo giorno prende il valore di adesso dallo stato
  const dati = useMemo(() => {
    const righe = new Map<string, Record<string, number | string>>();
    for (const s of SERIE) {
      const st = stati[s.ramo];
      const base = Number(st?.[s.base] ?? 0);
      if (!(base > 0)) continue;
      const g = { ...(giorni[s.ramo] ?? {}) };
      if (st?.equity != null && st.aggiornato) g[new Date(st.aggiornato * 1000).toISOString().slice(0, 10)] = st.equity;
      for (const [d, v] of Object.entries(g)) {
        const r = righe.get(d) ?? { giorno: d };
        r[s.ramo] = Number(v) / base - 1;
        righe.set(d, r);
      }
    }
    return Array.from(righe.values()).sort((a, b) => String(a.giorno).localeCompare(String(b.giorno)));
  }, [giorni, stati]);

  return <GraficoAndamento dati={dati} />;
}

/** La parte che disegna, dai rendimenti giorno per giorno gia' calcolati (separata per poterla provare senza il database). */
export function GraficoAndamento({ dati }: { dati: Record<string, number | string>[] }) {
  const presenti = SERIE.filter((s) => dati.some((r) => r[s.ramo] != null));
  const ultima = (ramo: string) => {
    for (let i = dati.length - 1; i >= 0; i--) if (dati[i][ramo] != null) return Number(dati[i][ramo]);
    return null;
  };

  return (
    <>
      <div className="sotto-titolo">Andamento giorno per giorno</div>
      {dati.length === 0 ? (
        <p className="muted" style={{ margin: '2px 0 8px', fontSize: 12.5 }}>Ancora nessun giorno registrato.</p>
      ) : (
        <>
          <p className="muted" style={{ margin: '2px 0 6px', fontSize: 12 }}>
            Rendimento dalla partenza di ciascuno (il paper con 10.000 dollari virtuali, il demo con il saldo del primo giorno, il 24
            ottobre alle 11:11 ora italiana): conta come salgono e scendono insieme, non il punto di partenza.
          </p>
          <div style={{ width: '100%', height: 220 }}>
            <ResponsiveContainer>
              <LineChart data={dati} margin={{ top: 6, right: 12, bottom: 0, left: 0 }}>
                <CartesianGrid stroke="var(--border-soft)" vertical={false} />
                <XAxis dataKey="giorno" stroke="var(--text-faint)" fontSize={11} tickLine={false} minTickGap={30}
                       tickFormatter={(d: string) => d.slice(5)} />
                <YAxis stroke="var(--text-faint)" fontSize={11} tickLine={false} width={52}
                       tickFormatter={(v: number) => `${(100 * v).toFixed(1)}%`} />
                <Tooltip formatter={(v: number) => pct(v)} labelFormatter={(d: string) => `giorno ${d}`}
                         labelStyle={{ color: 'var(--text)' }}
                         contentStyle={{ background: 'var(--bg-panel)', border: '1px solid var(--border)', fontSize: 12 }} />
                <ReferenceLine y={0} stroke="var(--border)" />
                <Legend wrapperStyle={{ fontSize: 12 }}
                        formatter={(v: string) => <span style={{ color: 'var(--text-dim)' }}>{v}</span>} />
                {presenti.map((s) => (
                  <Line key={s.ramo} type="linear" dataKey={s.ramo} name={s.nome} stroke={s.colore} strokeWidth={2}
                        dot={{ r: 4, strokeWidth: 2, stroke: 'var(--bg-panel)', fill: s.colore }} activeDot={{ r: 5 }}
                        connectNulls isAnimationActive={false} />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
          <table className="tabella-report" style={{ marginTop: 6 }}>
            <thead>
              <tr><th>Adesso</th><th>dalla partenza</th></tr>
            </thead>
            <tbody>
              {presenti.map((s) => (
                <tr key={s.ramo}>
                  <td><span style={{ display: 'inline-block', width: 12, height: 2, background: s.colore, marginRight: 6,
                                     verticalAlign: 'middle' }} />{s.nome}</td>
                  <td>{pct(ultima(s.ramo))}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </>
  );
}
