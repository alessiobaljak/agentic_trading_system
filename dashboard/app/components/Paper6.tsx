'use client';

import { lista } from '../lib/controllo';
import { usePaper6, type CandidataPaper6, type PosizionePaper6 } from '../lib/paper6';
import ControlloSezione from './ControlloSezione';

const pct = (x?: number | null, cifre = 2) =>
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
 * Il paper delle strategie nuove del programma 6 (20 ott 2026): le candidate misurate sui dati dal 20 ottobre 2026,
 * con le posizioni della settimana di F3 e K1. Si legge, non si opera: il bot non le esegue.
 */
export default function Paper6({ aperta = false }: { aperta?: boolean }) {
  const { doc, caricamento, etaS } = usePaper6();
  const candidate = lista<CandidataPaper6>(doc?.candidate);
  const f3 = candidate.find((c) => c.nome === 'F3');

  return (
    <ControlloSezione
      titolo="Strategie nuove in paper (programma 6)"
      aggiornatoS={etaS}
      errore={doc?.meta?.errore ?? null}
      aperta={aperta}
      riassunto={
        caricamento && !doc
          ? 'carico…'
          : !doc
            ? 'non ancora pubblicato'
            : f3 && (f3.periodi ?? 0) > 0
              ? `F3 ${pct(f3.totale)} in ${f3.periodi} settimane`
              : `la misura parte il ${doc.inizio_misura?.settimane ?? '26 ottobre'}`
      }
    >
      {!doc ? (
        <p className="muted" style={{ margin: 0, fontSize: 12.5 }}>
          Il paper arriva qui al prossimo giro dello snapshot (ogni 2 ore).
        </p>
      ) : (
        <>
          <p className="muted" style={{ margin: '0 0 8px', fontSize: 12.5 }}>
            Senza soldi veri e senza ordini: ogni mattina si ricalcolano le regole sui dati pubblici del giorno prima. Dati
            fino al {doc.dati_fino_al ?? '—'}
            {doc.funding_stimato_dal ? `; funding stimato dall'indice del premio dal ${doc.funding_stimato_dal}` : ''}.
            Verdetto {doc.verdetto ?? 'a 52 settimane'}.
          </p>
          <table className="tabella-report" style={{ width: "100%", fontSize: 12.5 }}>
            <thead>
              <tr>
                <th style={{ textAlign: 'left' }}>Candidata</th>
                <th>Periodi</th>
                <th>Totale</th>
                <th>Ultimo</th>
                <th>Sharpe</th>
              </tr>
            </thead>
            <tbody>
              {candidate.map((c, i) => (
                <tr key={i}>
                  <td>
                    <b>{c.nome}</b>
                    {c.descrizione ? <span className="muted"> · {c.descrizione}</span> : null}
                  </td>
                  <td style={{ textAlign: 'center' }}>
                    {c.periodi ?? 0} {c.unita === 'giorni' ? 'g' : 'sett.'}
                  </td>
                  <td style={{ textAlign: 'center' }}>{pct(c.totale)}</td>
                  <td style={{ textAlign: 'center' }}>{c.ultimo ? `${pct(c.ultimo.netto)} (${c.ultimo.data})` : '—'}</td>
                  <td style={{ textAlign: 'center' }}>{c.sharpe == null ? '—' : c.sharpe.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {(['F3', 'K1', 'M1'] as const).map((n) => {
            const p = doc.posizioni?.[n];
            if (!p) return null;
            return (
              <div key={n} style={{ marginTop: 10 }}>
                <div className="sotto-titolo">
                  {n}: posizioni della settimana dal {p.lunedi ?? '—'}
                </div>
                <Lato titolo="Long" voci={lista<PosizionePaper6>(p.long)} />
                <Lato titolo="Short" voci={lista<PosizionePaper6>(p.short)} />
              </div>
            );
          })}
          <p className="muted" style={{ margin: '10px 0 0', fontSize: 12 }}>
            Fonte: research/programma6/paper/PAPER.md (regole in REGOLE.md, scritte prima dei dati nuovi).
          </p>
        </>
      )}
    </ControlloSezione>
  );
}
