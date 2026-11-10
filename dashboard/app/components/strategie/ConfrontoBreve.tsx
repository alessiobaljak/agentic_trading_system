'use client';

import { Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, YAxis } from 'recharts';
import { confrontoFase, type ConfrontoFase } from '../../lib/dettagli';
import { defDi, giornoBreve, pct, punti, type DatiRamo } from '../../lib/strategie';
import { Suggerimento } from '../comuni/Suggerimento';

/**
 * G1 sul demo contro G1 nel paper, in breve (seconda tornata, 10 nov 2026; il proprietario: «forse rimuovere o migliorerei questa G1
 * sul demo contro G1 nel paper, giorno per giorno»): dalla partenza della fase in corso del demo, i due risultati, la differenza e una
 * piccola curva per ciascuno, sulla stessa scala. Il giorno per giorno con le fasi passate sta nella scheda Dettagli.
 */
const DEMO = defDi('demo_binance');
const PAPER = defDi('paper_g1');

function Curva({ c, chiave, colore, nome, dominio }: {
  c: ConfrontoFase; chiave: 'demo' | 'paper'; colore: string; nome: string; dominio: [number, number];
}) {
  const ultimo = c.curva.reduce((i, r, k) => (r[chiave] != null ? k : i), -1);
  return (
    <div className="cr-curvina" aria-hidden="true">
      <ResponsiveContainer>
        <LineChart data={c.curva} margin={{ top: 6, right: 6, bottom: 4, left: 6 }}>
          <YAxis hide domain={dominio} />
          <ReferenceLine y={0} stroke="var(--asse)" />
          <Tooltip
            cursor={{ stroke: 'var(--text-faint)', strokeWidth: 1 }}
            isAnimationActive={false}
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null;
              const r = payload[0].payload as ConfrontoFase['curva'][number];
              return (
                <Suggerimento titolo={r.giorno < c.partenza ? 'partenza' : giornoBreve(r.giorno)}
                  voci={[{ chiave, nome, colore, forma: 'linea', valore: pct(r[chiave]) }]} />
              );
            }}
          />
          <Line dataKey={chiave} stroke={colore} strokeWidth={2} strokeLinecap="round" isAnimationActive={false} connectNulls
            activeDot={{ r: 4, stroke: 'var(--bg-panel)', strokeWidth: 2, fill: colore }}
            dot={(p: { index: number; cx?: number; cy?: number }) =>
              p.index === ultimo && p.cx != null && p.cy != null
                ? <circle key="fine" cx={p.cx} cy={p.cy} r={4} fill={colore} stroke="var(--bg-panel)" strokeWidth={2} />
                : <g key={p.index} />} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function ConfrontoBreve({ paper, demo }: { paper: DatiRamo | undefined; demo: DatiRamo | undefined }) {
  const c = confrontoFase(paper, demo);
  if (!c) {
    return (
      <section className="cr-pannello">
        <h2>G1 demo contro G1 paper</h2>
        <p className="cr-sotto" style={{ margin: 0 }}>Servono almeno un giorno del demo e il giorno prima del paper.</p>
      </section>
    );
  }
  const valori = c.curva.flatMap((r) => [r.demo, r.paper]).filter((x): x is number => x != null);
  const dominio: [number, number] = [Math.min(0, ...valori), Math.max(0, ...valori)];
  const cls = (x: number) => (Math.abs(x) < 0.00005 ? undefined : x > 0 ? 'cr-su' : 'cr-giu');

  return (
    <section className="cr-pannello">
      <h2>G1 demo contro G1 paper</h2>
      <p className="cr-sotto">
        Dal {giornoBreve(c.partenza)}, partenza del demo a {c.capitale.toLocaleString('it-IT')} USDT · {c.giorni}{' '}
        {c.giorni === 1 ? 'giorno' : 'giorni'}
      </p>
      <div className="cr-confronto">
        <div className="cr-confronto-voce">
          <div className="cr-confronto-nome"><span className="cr-chiave" style={{ background: DEMO.colore }} />G1 demo</div>
          <div className={`cr-confronto-num ${cls(c.demo) ?? ''}`}>{pct(c.demo)}</div>
          <Curva c={c} chiave="demo" colore={DEMO.colore} nome="G1 demo" dominio={dominio} />
        </div>
        <div className="cr-confronto-voce">
          <div className="cr-confronto-nome"><span className="cr-chiave" style={{ background: PAPER.colore }} />G1 paper</div>
          <div className={`cr-confronto-num ${cls(c.paper) ?? ''}`}>{pct(c.paper)}</div>
          <Curva c={c} chiave="paper" colore={PAPER.colore} nome="G1 paper" dominio={dominio} />
        </div>
        <div className="cr-confronto-voce cr-confronto-diff">
          <div className="cr-confronto-nome">Differenza</div>
          <div className={`cr-confronto-num ${cls(c.differenza) ?? ''}`}>{punti(c.differenza)} <small>punti</small></div>
        </div>
      </div>
    </section>
  );
}
