'use client';

import { useEffect, useMemo, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { getRtdb } from '../../lib/firebase';
import { giornoBreve, pct, soldi } from '../comuni';
import type { DatiAzioni, StrategiaAzioni } from './Azioni';

/**
 * Le operazioni giorno per giorno della misura in avanti (sessione «trading stock», stock/avanti/): una tabella per giorno, il più
 * recente in cima. Legge /azioni/strategie/<id>/operazioni, scritto da stock/avanti/plancia.py (ultimi 30 giorni di borsa).
 */
export interface Operazione {
  simbolo: string;
  lato?: string;
  quantita?: number;
  ingresso?: number;
  uscita_prezzo?: number;
  uscita?: string;
  guadagno?: number;
  proporzione?: number;
  commissione_ib?: number;
  nota?: string;
  ora_ingresso?: string;
}

type ConOperazioni = StrategiaAzioni & { operazioni?: Record<string, Operazione[] | null> | null };

const LATO: Record<string, string> = { buy: 'Acquisto', sell: 'Vendita' };
const USCITA: Record<string, string> = { stop: 'stop', obiettivo: 'obiettivo', chiusura: 'fine giornata', aperta: 'ancora aperta' };
const coloreDi = (x?: number) => (x == null ? undefined : x >= 0 ? 'var(--giorno-su)' : 'var(--giorno-giu)');
const oraNy = (iso?: string) => (iso ? new Date(iso).toLocaleTimeString('it-CH', { timeZone: 'America/New_York', hour: '2-digit', minute: '2-digit' }) : '');

export default function Operazioni() {
  const [dati, setDati] = useState<DatiAzioni | null>(null);
  const [arrivato, setArrivato] = useState(false);
  useEffect(() => onValue(ref(getRtdb(), 'azioni'), (x) => { setDati(x.val()); setArrivato(true); }), []);

  const strategie = useMemo(
    () => Object.entries((dati?.strategie ?? {}) as Record<string, ConOperazioni | null>)
      .filter((e): e is [string, ConOperazioni] => !!e[1]?.operazioni)
      .sort((a, b) => (a[1].ordine ?? 99) - (b[1].ordine ?? 99)),
    [dati],
  );

  if (!arrivato) return <p className="cr-sotto">Lettura…</p>;
  if (!strategie.length) {
    return <section className="cr-pannello cr-vuoto"><p className="cr-sotto" style={{ margin: 0 }}>Nessuna operazione ancora su Firebase.</p></section>;
  }

  return (
    <>
      {strategie.map(([id, s]) => {
        const valuta = s.valuta ?? 'USD';
        const giorni = Object.entries(s.operazioni ?? {}).filter((e): e is [string, Operazione[]] => !!e[1]?.length)
          .sort((a, b) => b[0].localeCompare(a[0]));
        return giorni.map(([g, ops]) => {
          const fatte = ops.filter((o) => o.guadagno != null);
          const totale = fatte.reduce((t, o) => t + (o.guadagno ?? 0), 0);
          const vinte = fatte.filter((o) => (o.guadagno ?? 0) > 0).length;
          return (
            <section className="cr-pannello" key={`${id}-${g}`}>
              <div className="cr-pannello-testa"><h2>{s.nome ?? id}: {giornoBreve(g)}</h2></div>
              <p className="cr-sotto">
                {fatte.length} operazioni, {vinte} in guadagno, totale{' '}
                <b style={{ color: coloreDi(totale) }}>{soldi(totale, valuta)}</b>
                {ops.length > fatte.length ? ` · ${ops.length - fatte.length} saltate o non eseguite` : ''}
              </p>
              <div className="cr-scorre">
                <table className="cr-tabella">
                  <thead>
                    <tr><th>Titolo</th><th style={{ textAlign: 'left' }}>Lato</th><th>Ingresso</th><th>Uscita</th><th>Come</th><th>Guadagno</th><th>%</th></tr>
                  </thead>
                  <tbody>
                    {ops.map((o, i) => (
                      <tr key={`${o.simbolo}-${i}`}>
                        <td>{o.simbolo.replace(/_/g, '.')}</td>
                        <td style={{ textAlign: 'left' }}>{LATO[o.lato ?? ''] ?? (o.nota || '—')}</td>
                        <td>{o.ingresso != null ? <>{o.ingresso.toFixed(2)}<span className="cr-fase">{oraNy(o.ora_ingresso)} NY</span></> : '—'}</td>
                        <td>{o.uscita_prezzo != null ? o.uscita_prezzo.toFixed(2) : '—'}</td>
                        <td>{USCITA[o.uscita ?? ''] ?? o.uscita ?? '—'}</td>
                        <td style={{ color: coloreDi(o.guadagno) }}>{o.guadagno != null ? soldi(o.guadagno, valuta) : '—'}</td>
                        <td style={{ color: coloreDi(o.proporzione) }}>{o.proporzione != null ? pct(o.proporzione) : '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>
          );
        });
      })}
    </>
  );
}
