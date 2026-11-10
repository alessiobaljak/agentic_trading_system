'use client';

import { Bar, BarChart, CartesianGrid, Cell, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { GiornoRisultato } from '../../lib/dettagli';
import { giornoBreve, pct, soldi, type DefStrategia } from '../../lib/strategie';
import { Colonna } from '../comuni/Colonna';
import { Suggerimento } from '../comuni/Suggerimento';

/**
 * Il risultato di ogni giorno (sul giorno prima), una colonna per giorno nel colore della strategia; il giorno in corso più chiaro.
 * Una sola serie: niente leggenda, il titolo dice cosa è. Al tocco il giorno, il risultato e il valore di fine giorno.
 */
export default function RisultatoGiorni({ def, giorni }: { def: DefStrategia; giorni: GiornoRisultato[] }) {
  const dati = giorni.map((g) => ({ ...g, rPct: 100 * g.r }));
  return (
    <div className="cr-grafico" style={{ height: 200 }}>
      <ResponsiveContainer>
        <BarChart data={dati} margin={{ top: 8, right: 10, bottom: 0, left: 0 }} barCategoryGap="18%">
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
              const g = payload[0].payload as GiornoRisultato;
              return (
                <Suggerimento titolo={`${giornoBreve(g.giorno)}${g.inCorso ? ' · in corso' : ''}`}
                  voci={[{ chiave: 'r', nome: def.breve, colore: def.colore, forma: 'quadro', valore: pct(g.r) }]}
                  nota={`valore ${soldi(g.valore, def.unita)}`} />
              );
            }}
          />
          <Bar dataKey="rPct" fill={def.colore} maxBarSize={24} isAnimationActive={false} shape={<Colonna />}>
            {dati.map((g) => <Cell key={g.giorno} fill={def.colore} fillOpacity={g.inCorso ? 0.45 : 1} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
