'use client';

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
export default function StrategieNuove() {
  const { doc } = usePaper6();
  const strategie = lista<StrategiaPaper6>(doc?.strategie);
  const f5 = doc?.posizioni?.F5;
  const n3 = lista<EventoN3>(doc?.eventi_n3);

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

      <div className="panel">
        <h2>Funding con la banda: le posizioni della settimana{f5?.lunedi ? ` dal ${f5.lunedi}` : ''}</h2>
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
