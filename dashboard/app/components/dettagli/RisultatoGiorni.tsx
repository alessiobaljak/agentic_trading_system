'use client';

import { Bar, BarChart, CartesianGrid, Cell, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import type { GiornoRisultato } from '../../lib/dettagli';
import { giornoBreve, pct, soldi, type DefStrategia } from '../../lib/strategie';
import { Colonna } from '../comuni/Colonna';
import { Suggerimento } from '../comuni/Suggerimento';

/**
 * Il risultato di ogni giorno (sul giorno prima), una colonna per giorno: verde se in guadagno, arancione se in perdita, per tutte le
 * strategie (terza tornata, 10 nov 2026, il proprietario: «se è negativa dovrebbe essere arancione»); il giorno in corso più chiaro.
 * La coppia è validata con lo strumento della skill dataviz (chiaro #00661a / #eb6834 su #ffffff, scuro #22b14c / #c2410c su #1a1a19,
 * anche per chi vede male rosso e verde); il segno si legge anche dalla direzione della colonna e dalla leggenda sopra.
 * Al tocco il giorno, il risultato e il valore di fine giorno.
 */
const SU = 'var(--giorno-su)';
const GIU = 'var(--giorno-giu)';
export default function RisultatoGiorni({ def, giorni }: { def: DefStrategia; giorni: GiornoRisultato[] }) {
  const dati = giorni.map((g) => ({ ...g, rPct: 100 * g.r }));
  return (
    <>
    <div className="cr-legenda-fissa">
      <span><span className="cr-quadro" style={{ background: SU }} aria-hidden="true" />giorno in guadagno</span>
      <span><span className="cr-quadro" style={{ background: GIU }} aria-hidden="true" />giorno in perdita</span>
    </div>
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
                  voci={[{ chiave: 'r', nome: def.breve, colore: g.r >= 0 ? SU : GIU, forma: 'quadro', valore: pct(g.r) }]}
                  nota={`valore ${soldi(g.valore, def.unita)}`} />
              );
            }}
          />
          <Bar dataKey="rPct" fill={SU} maxBarSize={24} isAnimationActive={false} shape={<Colonna />}>
            {dati.map((g) => <Cell key={g.giorno} fill={g.r >= 0 ? SU : GIU} fillOpacity={g.inCorso ? 0.45 : 1} />)}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
    </>
  );
}
