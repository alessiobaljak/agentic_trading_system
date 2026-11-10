'use client';

import { useEffect, useMemo, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { Bar, BarChart, CartesianGrid, Cell, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { getRtdb } from '../lib/firebase';
import { defDi, metriche } from '../lib/strategie';

/**
 * Giorno per giorno, paper e demo insieme (il proprietario, 3 nov 2026: «un grafico che ti fa vedere paper e demo come stanno andando
 * giornalmente, sia profitto che win rate che percentuali, posizioni aperte e chiuse, così quando voglio guardo la dashboard»).
 *
 * Per ogni strategia: il valore di fine giorno (/{ramo}/giorni), il profitto di ogni giorno (in dollari e in percentuale sul valore del
 * giorno prima), i giorni in guadagno sul totale (per queste strategie la «percentuale di vincita» è quella dei giorni: tengono decine
 * di posizioni insieme), le posizioni aperte e quelle entrate e uscite a ogni ribilancio (/{ramo}/ribilanciamenti), e per gli eventi
 * le operazioni chiuse e quante in guadagno (/paper_eventi/chiuse). Il paper parte da 10.000 dollari virtuali, il demo dal saldo del
 * conto demo (circa 5.000): per confrontarli contano le percentuali.
 */

type Serie = { ramo: string; nome: string; base: 'capitale' | 'capitale_iniziale' };
const SERIE: Serie[] = [
  { ramo: 'demo_binance', nome: 'G1 sul conto demo di Binance', base: 'capitale_iniziale' },
  { ramo: 'paper_g1', nome: 'G1 nel paper', base: 'capitale' },
  { ramo: 'paper_g1n', nome: 'G1 neutra al mercato (paper)', base: 'capitale' },
  { ramo: 'paper_g11', nome: 'G11 (paper)', base: 'capitale' },
  { ramo: 'paper_f5', nome: 'F5, il lunedì (paper)', base: 'capitale' },
  { ramo: 'paper_eventi', nome: 'Eventi (paper)', base: 'capitale' },
];

type Stato = { equity?: number; capitale?: number; capitale_iniziale?: number; aggiornato?: number; long?: number; short?: number;
  aperte_n3?: number; aperte_e4?: number };
type Rib = { long?: number; short?: number; entrate?: number; uscite?: number };
type Chiusa = { uscita?: number; rendimento?: number; dollari?: number };
type Dati = { giorni?: Record<string, number> | null; stato?: Stato | null; rib?: Record<string, Rib> | null;
  chiuse?: Record<string, Chiusa> | null };
type Giorno = { giorno: string; valore: number; profitto: number; pct: number; dallInizio: number; entrate: number | null;
  uscite: number | null; chiuse: number | null };

const COLORE_SU = '#2a78d6';
const COLORE_GIU = '#eb6834';

function pct(x: number | null | undefined, cifre = 2): string {
  return x == null || !Number.isFinite(x) ? '—' : `${x >= 0 ? '+' : ''}${(100 * x).toFixed(cifre)}%`;
}
function usd(x: number | null | undefined): string {
  if (x == null || !Number.isFinite(x)) return '—';
  return `${x >= 0 ? '+' : '−'}$${Math.abs(x).toLocaleString('it-IT', { maximumFractionDigits: 2, minimumFractionDigits: 2 })}`;
}
function soldi(x: number | null | undefined): string {
  return x == null || !Number.isFinite(x) ? '—' : `$${x.toLocaleString('it-IT', { maximumFractionDigits: 2, minimumFractionDigits: 2 })}`;
}

/** I giorni di una strategia, dal primo valore registrato; l'ultimo giorno prende il valore di adesso dallo stato. */
export function giorniDi(d: Dati, base: number): Giorno[] {
  const g: Record<string, number> = { ...(d.giorni ?? {}) };
  if (d.stato?.equity != null && d.stato.aggiornato) g[new Date(d.stato.aggiornato * 1000).toISOString().slice(0, 10)] = d.stato.equity;
  const date = Object.keys(g).sort();
  const perData = (fn: (k: string, v: Rib) => number | undefined) => {
    const out: Record<string, number> = {};
    for (const [k, v] of Object.entries(d.rib ?? {})) {
      const x = fn(k, v);
      if (x != null) out[k.slice(0, 10)] = (out[k.slice(0, 10)] ?? 0) + x;
    }
    return out;
  };
  const entrate = perData((_, v) => v.entrate);
  const uscite = perData((_, v) => v.uscite);
  const chiusePerGiorno: Record<string, number> = {};
  for (const c of Object.values(d.chiuse ?? {})) {
    if (!c.uscita) continue;
    const k = new Date(c.uscita).toISOString().slice(0, 10);
    chiusePerGiorno[k] = (chiusePerGiorno[k] ?? 0) + 1;
  }
  let prima = base;
  return date.map((k) => {
    const v = Number(g[k]);
    const r: Giorno = { giorno: k, valore: v, profitto: v - prima, pct: prima > 0 ? v / prima - 1 : 0, dallInizio: base > 0 ? v / base - 1 : 0,
      entrate: entrate[k] ?? null, uscite: uscite[k] ?? null, chiuse: d.chiuse ? (chiusePerGiorno[k] ?? 0) : null };
    prima = v;
    return r;
  });
}

export default function DiarioPaper() {
  const [dati, setDati] = useState<Record<string, Dati>>({});
  const [scelta, setScelta] = useState<string>('demo_binance');

  useEffect(() => {
    const db = getRtdb();
    const metti = (ramo: string, campo: keyof Dati) => (x: { val: () => unknown }) =>
      setDati((p) => ({ ...p, [ramo]: { ...(p[ramo] ?? {}), [campo]: x.val() as never } }));
    const u = SERIE.flatMap((s) => [
      onValue(ref(db, `${s.ramo}/giorni`), metti(s.ramo, 'giorni')),
      onValue(ref(db, `${s.ramo}/stato`), metti(s.ramo, 'stato')),
      onValue(ref(db, `${s.ramo}/ribilanciamenti`), metti(s.ramo, 'rib')),
      ...(s.ramo === 'paper_eventi' ? [onValue(ref(db, 'paper_eventi/chiuse'), metti(s.ramo, 'chiuse'))] : []),
    ]);
    return () => u.forEach((x) => x());
  }, []);

  const righe = useMemo(() => SERIE.map((s) => {
    const d = dati[s.ramo] ?? {};
    const base = Number(d.stato?.[s.base] ?? 0);
    const gg = base > 0 ? giorniDi(d, base) : [];
    // i giorni in guadagno contati come nella prima schermata (lib/strategie.ts, `metriche`): solo i giorni chiusi, giorno su giorno
    const m = metriche(defDi(s.ramo), { stato: d.stato ?? null, giorni: d.giorni ?? null, ultimoRibilancio: null, arrivato: true },
      Date.now() / 1000);
    const vinti = m.giorniSu;
    const contati = m.giorniTot;
    const chiuse = Object.values(d.chiuse ?? {});
    const ultimo = gg[gg.length - 1];
    const aperte = s.ramo === 'paper_eventi' ? `${(d.stato?.aperte_n3 ?? 0) + (d.stato?.aperte_e4 ?? 0)} operazioni`
      : d.stato?.long != null ? `${d.stato.long} comprate, ${d.stato.short ?? 0} vendute` : '—';
    return { s, base, gg, vinti, contati, ultimo, aperte,
      migliore: gg.length ? gg.reduce((a, b) => (b.pct > a.pct ? b : a)) : null,
      peggiore: gg.length ? gg.reduce((a, b) => (b.pct < a.pct ? b : a)) : null,
      chiuse: chiuse.length, chiuseVinte: chiuse.filter((c) => (c.rendimento ?? 0) > 0).length,
      entrateTot: gg.reduce((a, b) => a + (b.entrate ?? 0), 0), usciteTot: gg.reduce((a, b) => a + (b.uscite ?? 0), 0) };
  }).filter((r) => r.gg.length > 0), [dati]);

  const sel = righe.find((r) => r.s.ramo === scelta) ?? righe[0];
  const ultimi = sel ? sel.gg.slice(-30) : [];

  return (
    <>
      <div className="sotto-titolo">Giorno per giorno: profitto, giorni in guadagno, posizioni</div>
      {righe.length === 0 ? (
        <p className="muted" style={{ margin: '2px 0 8px', fontSize: 12.5 }}>Ancora nessun giorno registrato.</p>
      ) : (
        <>
          <p className="muted" style={{ margin: '2px 0 6px', fontSize: 12 }}>
            Il paper parte da 10.000 dollari virtuali, il demo dal capitale della sua fase in corso (in USDT): per confrontarli contano le
            percentuali. «Giorni in guadagno» sono i giorni chiusi (non quello in corso) sopra il giorno prima: queste strategie
            tengono decine di posizioni insieme, quindi la vincita si conta a giorni; per gli eventi si contano anche le operazioni
            chiuse.
          </p>
          <div style={{ overflowX: 'auto' }}>
            <table className="tabella-report">
              <thead>
                <tr>
                  <th>Strategia</th><th>Valore</th><th>Dall&apos;inizio</th><th>Profitto</th><th>Giorni in guadagno</th>
                  <th>Giorno migliore</th><th>Giorno peggiore</th><th>Aperte ora</th><th>Entrate / uscite</th>
                </tr>
              </thead>
              <tbody>
                {righe.map((r) => (
                  <tr key={r.s.ramo} onClick={() => setScelta(r.s.ramo)} style={{ cursor: 'pointer',
                    fontWeight: sel && r.s.ramo === sel.s.ramo ? 600 : undefined }}>
                    <td>{r.s.nome}</td>
                    <td>{soldi(r.ultimo?.valore)}</td>
                    <td>{pct(r.ultimo?.dallInizio)}</td>
                    <td>{usd(r.ultimo ? r.ultimo.valore - r.base : null)}</td>
                    <td>{r.vinti} su {r.contati} ({pct(r.contati ? r.vinti / r.contati : null, 0).replace('+', '')})</td>
                    <td>{r.migliore ? `${pct(r.migliore.pct)} (${r.migliore.giorno.slice(5)})` : '—'}</td>
                    <td>{r.peggiore ? `${pct(r.peggiore.pct)} (${r.peggiore.giorno.slice(5)})` : '—'}</td>
                    <td>{r.aperte}</td>
                    <td>{r.s.ramo === 'paper_eventi'
                      ? `${r.chiuse} chiuse, ${r.chiuseVinte} in guadagno`
                      : (r.entrateTot || r.usciteTot) ? `${r.entrateTot} / ${r.usciteTot}` : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {sel && (
            <>
              <p style={{ margin: '10px 0 4px', fontSize: 12.5 }}>
                Scegli la strategia toccando la sua riga. Adesso: <b>{sel.s.nome}</b>, profitto di ogni giorno sul giorno prima.
              </p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6, margin: '0 0 6px' }}>
                {righe.map((r) => (
                  <button key={r.s.ramo} className="btn" onClick={() => setScelta(r.s.ramo)}
                    style={{ fontWeight: r.s.ramo === sel.s.ramo ? 600 : undefined }}>{r.s.nome}</button>
                ))}
              </div>
              <div style={{ width: '100%', height: 200 }}>
                <ResponsiveContainer>
                  <BarChart data={ultimi} margin={{ top: 6, right: 12, bottom: 0, left: 0 }}>
                    <CartesianGrid stroke="var(--border-soft)" vertical={false} />
                    <XAxis dataKey="giorno" stroke="var(--text-faint)" fontSize={11} tickLine={false} minTickGap={20}
                           tickFormatter={(d: string) => d.slice(5)} />
                    <YAxis stroke="var(--text-faint)" fontSize={11} tickLine={false} width={52}
                           tickFormatter={(v: number) => `${(100 * v).toFixed(1)}%`} />
                    <Tooltip formatter={(v: number) => pct(v)} labelFormatter={(d: string) => `giorno ${d}`}
                             labelStyle={{ color: 'var(--text)' }}
                             contentStyle={{ background: 'var(--bg-panel)', border: '1px solid var(--border)', fontSize: 12 }} />
                    <ReferenceLine y={0} stroke="var(--border)" />
                    <Bar dataKey="pct" name="profitto del giorno" isAnimationActive={false} radius={[4, 4, 0, 0]}>
                      {ultimi.map((x) => <Cell key={x.giorno} fill={x.pct >= 0 ? COLORE_SU : COLORE_GIU} />)}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </div>
              <p className="muted" style={{ margin: '2px 0 6px', fontSize: 12 }}>
                <span style={{ color: COLORE_SU }}>■</span> giorno in guadagno · <span style={{ color: COLORE_GIU }}>■</span> giorno in perdita
              </p>
              <div style={{ overflowX: 'auto' }}>
                <table className="tabella-report">
                  <thead>
                    <tr>
                      <th>Giorno</th><th>Valore</th><th>Profitto del giorno</th><th>Dall&apos;inizio</th>
                      <th>{sel.s.ramo === 'paper_eventi' ? 'Operazioni chiuse' : 'Entrate / uscite'}</th>
                    </tr>
                  </thead>
                  <tbody>
                    {[...ultimi].reverse().map((x) => (
                      <tr key={x.giorno}>
                        <td>{x.giorno}</td>
                        <td>{soldi(x.valore)}</td>
                        <td>{usd(x.profitto)} ({pct(x.pct)})</td>
                        <td>{pct(x.dallInizio)}</td>
                        <td>{sel.s.ramo === 'paper_eventi' ? (x.chiuse ?? 0)
                          : x.entrate != null || x.uscite != null ? `${x.entrate ?? 0} / ${x.uscite ?? 0}` : '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </>
          )}
        </>
      )}
    </>
  );
}
