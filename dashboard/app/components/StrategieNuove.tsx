'use client';

import { useMemo } from 'react';
import { CartesianGrid, Legend, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { lista } from '../lib/controllo';
import { usePaper6, type EventoN3, type PosizionePaper6, type StrategiaPaper6 } from '../lib/paper6';
import Paper6 from './Paper6';

const pct = (x?: number | null, cifre = 1) =>
  x == null || !Number.isFinite(x) ? '—' : `${x >= 0 ? '+' : ''}${(100 * x).toFixed(cifre)}%`;

function Lato({ titolo, voci }: { titolo: string; voci: PosizionePaper6[] }) {
  return (
    <p style={{ margin: '4px 0', fontSize: 12.5 }}>
      <b>{titolo}</b>{' '}
      {voci.length === 0
        ? 'nessuna'
        : voci.map((v) => `${(v.moneta ?? '').replace('USDT', '')} ${Math.abs(100 * (v.peso ?? 0)).toFixed(1)}%`).join(', ')}
    </p>
  );
}

/**
 * La scheda «Strategie nuove» (21 ott 2026): la prima della dashboard dopo lo stop del vecchio paper del gate. In
 * alto le strategie in parole semplici (stato, monete, regola, risultato sul passato: research/REGISTRO.md), poi le
 * posizioni di adesso della strategia del funding con la banda, le operazioni sulle monete nuove e il paper completo.
 * Si legge, non si opera: il bot non esegue ancora queste strategie.
 */
const SERIE: { chiave: string; nome: string; colore: string }[] = [
  { chiave: 'F5', nome: 'Funding con la banda (dal 2021)', colore: 'var(--accent)' },
  { chiave: 'F5 + M7 + K2', nome: 'Le tre insieme (dal 2022)', colore: 'var(--amber)' },
];

/** Il passato (non il paper): 100 investiti, valore a fine mese, su scala logaritmica. */
function Passato({ passato }: { passato: Record<string, { mese?: string | null; valore?: number | null }[]> }) {
  const dati = useMemo(() => {
    const perMese = new Map<string, Record<string, number | string>>();
    for (const s of SERIE) {
      for (const p of lista<{ mese?: string | null; valore?: number | null }>(passato[s.chiave])) {
        if (!p.mese || p.valore == null) continue;
        const riga = perMese.get(p.mese) ?? { mese: p.mese };
        riga[s.chiave] = p.valore;
        perMese.set(p.mese, riga);
      }
    }
    return Array.from(perMese.values()).sort((a, b) => String(a.mese).localeCompare(String(b.mese)));
  }, [passato]);
  if (dati.length < 2) return null;
  const ultimo = dati[dati.length - 1];
  return (
    <div className="panel">
      <h2>Come sarebbe andata sul passato di Binance</h2>
      <p className="muted" style={{ margin: '0 0 8px', fontSize: 12.5 }}>
        Non è il paper: è la regola applicata agli anni passati, al netto dei costi. 100 investiti all&apos;inizio; scala
        logaritmica. Fine {String(ultimo.mese)}:{' '}
        {SERIE.map((s) => (ultimo[s.chiave] != null ? `${s.nome.split(' (')[0]} ${Number(ultimo[s.chiave]).toFixed(0)}` : null))
          .filter(Boolean)
          .join(' · ')}
        .
      </p>
      <div style={{ width: '100%', height: 240 }}>
        <ResponsiveContainer>
          <LineChart data={dati} margin={{ top: 6, right: 12, bottom: 0, left: 0 }}>
            <CartesianGrid stroke="var(--border)" strokeDasharray="3 3" />
            <XAxis dataKey="mese" stroke="var(--text-dim)" fontSize={11} tickLine={false} minTickGap={40} />
            <YAxis scale="log" domain={['auto', 'auto']} stroke="var(--text-dim)" fontSize={11} tickLine={false} width={48}
                   tickFormatter={(v: number) => v.toFixed(0)} />
            <Tooltip formatter={(v: number) => v.toFixed(0)} labelStyle={{ color: 'var(--text)' }}
                     contentStyle={{ background: 'var(--bg-panel)', border: '1px solid var(--border)', fontSize: 12 }} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            {SERIE.map((s) => (
              <Line key={s.chiave} type="monotone" dataKey={s.chiave} name={s.nome} stroke={s.colore} strokeWidth={2}
                    dot={false} connectNulls />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default function StrategieNuove() {
  const { doc } = usePaper6();
  const strategie = lista<StrategiaPaper6>(doc?.strategie);
  const f5 = doc?.posizioni?.F5;
  const n3 = lista<EventoN3>(doc?.eventi_n3);
  const sett = doc?.settimana_in_corso?.F5;

  return (
    <>
      <div className="panel">
        <h2>Le strategie</h2>
        <p className="muted" style={{ margin: '0 0 8px', fontSize: 12.5 }}>
          Trovate con le regole scritte prima del calcolo e provate sul passato di Binance; nel paper senza soldi veri.
        </p>
        {strategie.length === 0 ? (
          <p className="muted" style={{ margin: 0, fontSize: 12.5 }}>Arrivano al prossimo giro dello snapshot.</p>
        ) : (
          strategie.map((s, i) => (
            <div key={i} style={{ marginTop: i ? 12 : 0 }}>
              <div className="sotto-titolo">
                {s.nome} · <span className="muted">{s.stato}</span>
              </div>
              <p style={{ margin: '2px 0', fontSize: 12.5 }}><b>Monete:</b> {s.monete}</p>
              <p style={{ margin: '2px 0', fontSize: 12.5 }}><b>Regola:</b> {s.regola}</p>
              <p style={{ margin: '2px 0', fontSize: 12.5 }}><b>Sul passato:</b> {s.passato}</p>
            </div>
          ))
        )}
      </div>

      {doc?.passato && <Passato passato={doc.passato} />}

      <div className="panel">
        <h2>Funding con la banda: le posizioni della settimana{f5?.lunedi ? ` dal ${f5.lunedi}` : ''}</h2>
        {sett?.netto_senza_costi != null && (
          <p style={{ margin: '0 0 6px', fontSize: 12.5 }}>
            <b>Settimana in corso</b> (dal {sett.lunedi} al {sett.fino_al}, senza costi, solo informazione):{' '}
            {pct(sett.netto_senza_costi, 2)}
          </p>
        )}
        <Lato titolo="Long" voci={lista<PosizionePaper6>(f5?.long)} />
        <Lato titolo="Short" voci={lista<PosizionePaper6>(f5?.short)} />
      </div>

      <div className="panel">
        <h2>Monete appena quotate: le operazioni</h2>
        {n3.length === 0 ? (
          <p className="muted" style={{ margin: 0, fontSize: 12.5 }}>
            Nessuna ancora: contano le monete quotate dal 21 ottobre 2026, che si aprono a 7 giorni dalla quotazione.
          </p>
        ) : (
          <ul className="lista-grigia">
            {n3.map((x, i) => (
              <li key={i}>
                {x.mercato} <b>{(x.simbolo ?? '').replace('USDT', '').replace('_', '')}</b> dal {x.ingresso}: {x.stato}
                {x.r != null ? ` ${pct(x.r)}${x.fermata ? ' (uscita a +30%)' : ''}` : ''}
              </li>
            ))}
          </ul>
        )}
      </div>

      <Paper6 aperta />
    </>
  );
}
