'use client';

import { useMemo, useState } from 'react';
import { Bar, BarChart, CartesianGrid, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import {
  confrontoDemoPaper, defDi, giornoBreve, pct, punti, riassumi,
  type DatiDemo, type DatiRamo, type RigaConfronto,
} from '../../lib/strategie';
import { Suggerimento } from './Suggerimento';

/**
 * G1 sul conto demo contro G1 nel paper, giorno per giorno: il rendimento di ogni giorno UTC (dal valore di fine giorno a quello del
 * giorno dopo, /demo_binance/giorni e /paper_g1/giorni) e la differenza in punti. Il demo ha cambiato capitale (circa 5.000 dal 24
 * ottobre, 280 dal 6 novembre, 1.000 dall'8 novembre): le fasi di prima stanno in /demo_binance/fasi/{nome}/giorni e si contano giorno
 * su giorno dentro la stessa fase; il giorno del cambio non si confronta, tranne il primo giorno della fase in corso, che parte dal
 * suo capitale a mezzanotte. Colori: gli stessi delle curve (G1 nel paper slot 1, il demo slot 2).
 */
const COLORE_PAPER = defDi('paper_g1').colore;
const COLORE_DEMO = defDi('demo_binance').colore;

/** La colonna con l'estremo arrotondato dalla parte del dato e la base dritta (skill dataviz, marks-and-anatomy.md). */
function Colonna(props: { x?: number; y?: number; width?: number; height?: number; fill?: string; value?: unknown }) {
  const { x = 0, y = 0, width = 0, height = 0, fill } = props;
  const v = Array.isArray(props.value) ? Number(props.value[1]) - Number(props.value[0]) : Number(props.value);
  const h = Math.abs(height);
  if (!Number.isFinite(v) || width <= 0 || h < 0.5) return <g />;
  const alto = Math.min(y, y + height);
  const basso = alto + h;
  const r = Math.min(4, h, width / 2);
  const x1 = x + width;
  const d = v >= 0
    ? `M${x},${basso} L${x},${alto + r} Q${x},${alto} ${x + r},${alto} L${x1 - r},${alto} Q${x1},${alto} ${x1},${alto + r} L${x1},${basso} Z`
    : `M${x},${alto} L${x1},${alto} L${x1},${basso - r} Q${x1},${basso} ${x1 - r},${basso} L${x + r},${basso} Q${x},${basso} ${x},${basso - r} Z`;
  return <path d={d} fill={fill} />;
}

function Riassunto({ titolo, righe }: { titolo: string; righe: RigaConfronto[] }) {
  const r = riassumi(righe);
  if (!r.giorni) return null;
  return (
    <p className="cr-riga">
      <b>{titolo}</b> ({r.giorni} {r.giorni === 1 ? 'giorno chiuso' : 'giorni chiusi'}): demo {pct(r.demoComposto)}, paper{' '}
      {pct(r.paperComposto)}. In media il demo fa <b>{punti(r.media)} punti</b> al giorno rispetto al paper; lo scarto tipico, senza
      segno, è di {punti(r.scartoTipico).replace('+', '')} punti.
    </p>
  );
}

export default function DemoControPaper({ paper, demo, fasi }: {
  paper: DatiRamo | undefined;
  demo: DatiRamo | undefined;
  fasi: DatiDemo['fasi'];
}) {
  const [tutti, setTutti] = useState(false);
  const righe = useMemo(
    () => (paper && demo ? confrontoDemoPaper(paper, demo, fasi) : []),
    [paper, demo, fasi],
  );
  const faseInCorso = righe.filter((r) => r.fase === null && r.demo != null);
  const grafico = righe.map((r) => ({ ...r, paperPct: r.paper == null ? null : 100 * r.paper, demoPct: r.demo == null ? null : 100 * r.demo }));
  const visibili = tutti ? [...righe].reverse() : [...righe].reverse().slice(0, 10);
  const capitale = demo?.stato?.capitale_iniziale;

  return (
    <section className="cr-pannello">
      <h2>G1 sul demo contro G1 nel paper, giorno per giorno</h2>
      <p className="cr-sotto">
        Quanto ha fatto ogni giorno la stessa strategia con ordini veri (demo) e con ordini simulati (paper). Conta la differenza: i
        capitali sono diversi (il paper 10.000 dollari virtuali, il demo {capitale ? `${capitale.toLocaleString('it-IT')} USDT` : 'il suo'}
        {' '}dalla fase in corso). La differenza è il demo meno il paper, in punti percentuali. I giorni vanno da mezzanotte a mezzanotte
        UTC (l&apos;una di notte in Italia, d&apos;inverno).
      </p>

      {righe.length === 0 ? (
        <p className="cr-sotto">Ancora nessun giorno con tutti e due.</p>
      ) : (
        <>
          <Riassunto titolo="Fase in corso" righe={faseInCorso} />
          {righe.some((r) => r.fase !== null && r.demo != null) && <Riassunto titolo="Tutte le fasi" righe={righe} />}

          <div className="cr-legenda-fissa" aria-hidden="true">
            <span><span className="cr-quadro" style={{ background: COLORE_PAPER }} />G1 nel paper</span>
            <span><span className="cr-quadro" style={{ background: COLORE_DEMO }} />G1 sul demo</span>
          </div>
          <div className="cr-grafico" style={{ height: 220 }}>
            <ResponsiveContainer>
              <BarChart data={grafico} margin={{ top: 8, right: 10, bottom: 0, left: 0 }} barGap={2} barCategoryGap="22%">
                <CartesianGrid stroke="var(--griglia)" vertical={false} />
                <XAxis dataKey="giorno" stroke="var(--asse)" tick={{ fill: 'var(--text-faint)', fontSize: 11 }} tickLine={false}
                  minTickGap={18} tickFormatter={(g: string) => giornoBreve(g)} />
                <YAxis stroke="var(--asse)" tick={{ fill: 'var(--text-faint)', fontSize: 11 }} tickLine={false} width={44}
                  tickFormatter={(v: number) => `${v.toLocaleString('it-IT', { maximumFractionDigits: 1 })}%`} />
                <ReferenceLine y={0} stroke="var(--asse)" />
                <Tooltip
                  cursor={{ fill: 'var(--velo)' }}
                  isAnimationActive={false}
                  content={({ active, payload }) => {
                    if (!active || !payload?.length) return null;
                    const r = payload[0].payload as RigaConfronto;
                    const voci = [
                      { chiave: 'demo', nome: 'G1 sul demo', colore: COLORE_DEMO, forma: 'quadro' as const, valore: pct(r.demo) },
                      { chiave: 'paper', nome: 'G1 nel paper', colore: COLORE_PAPER, forma: 'quadro' as const, valore: pct(r.paper) },
                    ];
                    const nota = r.differenza != null ? `differenza ${punti(r.differenza)} punti`
                      : r.nota ?? (r.demo == null ? 'il demo non ha questo giorno' : 'il paper non ha questo giorno');
                    return (
                      <Suggerimento
                        titolo={`${giornoBreve(r.giorno)}${r.inCorso ? ' · oggi, in corso' : ''}${r.fase ? ` · demo ${r.fase}` : ''}`}
                        voci={voci} nota={nota} />
                    );
                  }}
                />
                <Bar dataKey="paperPct" name="G1 nel paper" fill={COLORE_PAPER} maxBarSize={24} isAnimationActive={false}
                  shape={<Colonna />} />
                <Bar dataKey="demoPct" name="G1 sul demo" fill={COLORE_DEMO} maxBarSize={24} isAnimationActive={false}
                  shape={<Colonna />} />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="cr-scorre">
            <table className="cr-tabella">
              <thead>
                <tr><th>Giorno</th><th>Demo</th><th>Paper</th><th title="demo meno paper, in punti percentuali">Differenza</th></tr>
              </thead>
              <tbody>
                {visibili.map((r) => (
                  <tr key={r.giorno}>
                    <td>
                      {giornoBreve(r.giorno)}
                      {r.inCorso && <span className="cr-fase">oggi, in corso</span>}
                      {r.nota ? <span className="cr-fase">{r.nota}</span> : r.fase && <span className="cr-fase">demo {r.fase}</span>}
                    </td>
                    <td>{pct(r.demo)}</td>
                    <td>{pct(r.paper)}</td>
                    <td>{punti(r.differenza)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {righe.length > 10 && (
            <button type="button" className="cr-link" onClick={() => setTutti((t) => !t)}>
              {tutti ? 'Mostra solo gli ultimi 10 giorni' : `Mostra tutti i ${righe.length} giorni`}
            </button>
          )}
        </>
      )}
    </section>
  );
}
