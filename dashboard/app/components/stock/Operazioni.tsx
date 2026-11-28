'use client';

import { useEffect, useMemo, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { getRtdb } from '../../lib/firebase';
import { giornoBreve, pct, soldi } from '../comuni';
import type { DatiAzioni, StrategiaAzioni } from './Azioni';

/**
 * Le operazioni giorno per giorno della misura in avanti (sessione «trading stock», stock/avanti/), per TUTTE le strategie del demo
 * (richiesta del proprietario del 28 novembre 2026: «rivedi la scheda operations per far vedere tutte le strategie»). Legge
 * /azioni/strategie/<id>/operazioni, scritto da stock/avanti/plancia.py (prima candela), gamma.py (prova 45, anche i giorni senza
 * ingresso con il perché) e miscela.py (gli ordini della sera e della banca centrale, con «genere: ordine»). Ultimi 30 giorni.
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
  /** «ordine»: un ordine della miscela (comprato o venduto, senza guadagno a sé) */
  genere?: string;
}

type ConOperazioni = StrategiaAzioni & { operazioni?: Record<string, Operazione[] | null> | null };

const LATO: Record<string, string> = { buy: 'Acquisto', sell: 'Vendita' };
const USCITA: Record<string, string> = {
  stop: 'stop', obiettivo: 'obiettivo', chiusura: 'fine giornata', aperta: 'ancora aperta', asta: 'asta di chiusura',
  'giorno dopo': 'il giorno dopo', mercato: 'a mercato', 'fuori orario': 'fuori orario',
};
const GIORNI_VISIBILI = 7;
const coloreDi = (x?: number) => (x == null ? undefined : x >= 0 ? 'var(--giorno-su)' : 'var(--giorno-giu)');
const oraNy = (iso?: string) => (iso ? new Date(iso).toLocaleTimeString('it-CH', { timeZone: 'America/New_York', hour: '2-digit', minute: '2-digit' }) : '');
const titolo = (s: string) => s.replace(/_/g, '.');

/** I giorni con almeno una riga, dal più recente. */
function giorniDi(s: ConOperazioni): [string, Operazione[]][] {
  return Object.entries(s.operazioni ?? {}).filter((e): e is [string, Operazione[]] => !!e[1]?.length)
    .sort((a, b) => b[0].localeCompare(a[0]));
}

/** Le righe di un giorno divise in operazioni (con l'ingresso), ordini della miscela e note (giorni senza ingresso, saltati). */
function dividi(ops: Operazione[]) {
  const ordini = ops.filter((o) => o.genere === 'ordine');
  const operazioni = ops.filter((o) => o.genere !== 'ordine' && o.quantita != null);
  const note = ops.filter((o) => o.genere !== 'ordine' && o.quantita == null);
  return { ordini, operazioni, note };
}

/** Una frase sul giorno: quante operazioni, quanti ordini, o il perché non si è entrati. */
function sintesi(ops: Operazione[], valuta: string): string {
  const { ordini, operazioni, note } = dividi(ops);
  const parti: string[] = [];
  if (operazioni.length) {
    const chiuse = operazioni.filter((o) => o.guadagno != null);
    const totale = chiuse.reduce((t, o) => t + (o.guadagno ?? 0), 0);
    parti.push(`${operazioni.length} ${operazioni.length === 1 ? 'operazione' : 'operazioni'}, totale ${soldi(totale, valuta)}`);
  }
  if (ordini.length) {
    const eseguiti = ordini.filter((o) => o.ingresso != null).length;
    parti.push(`${eseguiti} ${eseguiti === 1 ? 'ordine eseguito' : 'ordini eseguiti'}` + (ordini.length > eseguiti ? `, ${ordini.length - eseguiti} in attesa o non eseguiti` : ''));
  }
  if (!parti.length && note.length) parti.push(note[0].nota || 'nessuna operazione');
  return parti.join(' · ') || '—';
}

function Giorno({ g, ops, valuta }: { g: string; ops: Operazione[]; valuta: string }) {
  const { ordini, operazioni, note } = dividi(ops);
  const chiuse = operazioni.filter((o) => o.guadagno != null);
  const totale = chiuse.reduce((t, o) => t + (o.guadagno ?? 0), 0);
  const vinte = chiuse.filter((o) => (o.guadagno ?? 0) > 0).length;
  return (
    <div style={{ marginTop: 14 }}>
      <h3 style={{ margin: '0 0 4px', fontSize: 14 }}>{giornoBreve(g)}</h3>
      {operazioni.length > 0 && (
        <>
          <p className="cr-sotto">
            {chiuse.length} {chiuse.length === 1 ? 'operazione chiusa' : 'operazioni chiuse'}, {vinte} in guadagno, totale{' '}
            <b style={{ color: coloreDi(totale) }}>{soldi(totale, valuta)}</b>
            {operazioni.length > chiuse.length ? ` · ${operazioni.length - chiuse.length} ancora aperte` : ''}
          </p>
          <div className="cr-scorre">
            <table className="cr-tabella">
              <thead>
                <tr><th>Titolo</th><th style={{ textAlign: 'left' }}>Lato</th><th>Ingresso</th><th>Uscita</th><th>Come</th><th>Guadagno</th><th>%</th></tr>
              </thead>
              <tbody>
                {operazioni.map((o, i) => (
                  <tr key={`${o.simbolo}-${i}`}>
                    <td>{titolo(o.simbolo)}</td>
                    <td style={{ textAlign: 'left' }}>{LATO[o.lato ?? ''] ?? '—'}</td>
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
        </>
      )}
      {ordini.length > 0 && (
        <div className="cr-scorre">
          <table className="cr-tabella">
            <thead>
              <tr><th>Titolo</th><th style={{ textAlign: 'left' }}>Lato</th><th>Quantità</th><th>Prezzo eseguito</th><th style={{ textAlign: 'left' }}>Perché</th></tr>
            </thead>
            <tbody>
              {ordini.map((o, i) => (
                <tr key={`${o.simbolo}-${i}`}>
                  <td>{titolo(o.simbolo)}</td>
                  <td style={{ textAlign: 'left' }}>{LATO[o.lato ?? ''] ?? '—'}</td>
                  <td>{o.quantita != null ? o.quantita.toLocaleString('it-CH') : '—'}</td>
                  <td>{o.ingresso != null ? <>{o.ingresso.toFixed(2)}<span className="cr-fase">{oraNy(o.ora_ingresso)} NY</span></> : '—'}</td>
                  <td style={{ textAlign: 'left' }}>{o.nota || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      {note.length > 0 && (
        <ul className="cr-sotto" style={{ margin: '4px 0 0', paddingLeft: 18 }}>
          {note.map((o, i) => <li key={`${o.simbolo}-${i}`}>{titolo(o.simbolo)}: {o.nota || 'nessuna operazione'}</li>)}
        </ul>
      )}
    </div>
  );
}

function Strategia({ id, s }: { id: string; s: ConOperazioni }) {
  const [tutti, setTutti] = useState(false);
  const valuta = s.valuta ?? 'USD';
  const giorni = giorniDi(s);
  const visibili = tutti ? giorni : giorni.slice(0, GIORNI_VISIBILI);
  return (
    <section className="cr-pannello" id={`operazioni-${id}`}>
      <div className="cr-pannello-testa"><h2>{s.nome ?? id}</h2></div>
      {!giorni.length && <p className="cr-sotto" style={{ margin: 0 }}>Nessuna operazione negli ultimi 30 giorni di borsa.</p>}
      {visibili.map(([g, ops]) => <Giorno key={g} g={g} ops={ops} valuta={valuta} />)}
      {giorni.length > GIORNI_VISIBILI && (
        <button type="button" className="cr-link" onClick={() => setTutti((x) => !x)}>
          {tutti ? `Mostra solo gli ultimi ${GIORNI_VISIBILI} giorni` : `Mostra tutti i ${giorni.length} giorni`}
        </button>
      )}
    </section>
  );
}

export default function Operazioni() {
  const [dati, setDati] = useState<DatiAzioni | null>(null);
  const [arrivato, setArrivato] = useState(false);
  const [scelta, setScelta] = useState<string | null>(null);
  useEffect(() => onValue(ref(getRtdb(), 'azioni'), (x) => { setDati(x.val()); setArrivato(true); }), []);

  // tutte le strategie pubblicate, anche quelle senza operazioni: si vede che ci sono e che oggi non sono entrate
  const strategie = useMemo(
    () => Object.entries((dati?.strategie ?? {}) as Record<string, ConOperazioni | null>)
      .filter((e): e is [string, ConOperazioni] => !!e[1])
      .sort((a, b) => (a[1].ordine ?? 99) - (b[1].ordine ?? 99)),
    [dati],
  );

  if (!arrivato) return <p className="cr-sotto">Lettura…</p>;
  if (!strategie.length) {
    return <section className="cr-pannello cr-vuoto"><p className="cr-sotto" style={{ margin: 0 }}>Nessuna strategia ancora su Firebase.</p></section>;
  }
  const mostrate = strategie.filter(([id]) => !scelta || id === scelta);

  return (
    <>
      <section className="cr-pannello">
        <div className="cr-pannello-testa"><h2>Tutte le strategie</h2></div>
        <div className="cr-sottoschede" role="group" aria-label="Quali strategie mostrare">
          <button type="button" aria-pressed={!scelta} onClick={() => setScelta(null)}>Tutte</button>
          {strategie.map(([id, s]) => (
            <button key={id} type="button" aria-pressed={scelta === id} onClick={() => setScelta(id)}>{s.nome ?? id}</button>
          ))}
        </div>
        <div className="cr-scorre" style={{ marginTop: 10 }}>
          <table className="cr-tabella">
            <thead>
              <tr><th style={{ textAlign: 'left' }}>Strategia</th><th>Ultimo giorno</th><th>Giorni con operazioni</th><th style={{ textAlign: 'left' }}>L&apos;ultimo giorno</th></tr>
            </thead>
            <tbody>
              {strategie.map(([id, s]) => {
                const giorni = giorniDi(s);
                const conOperazioni = giorni.filter(([, ops]) => { const d = dividi(ops); return d.operazioni.length + d.ordini.length > 0; }).length;
                return (
                  <tr key={id}>
                    <td style={{ textAlign: 'left' }}>{s.nome ?? id}</td>
                    <td>{giorni.length ? giornoBreve(giorni[0][0]) : '—'}</td>
                    <td>{conOperazioni}</td>
                    <td style={{ textAlign: 'left' }}>{giorni.length ? sintesi(giorni[0][1], s.valuta ?? 'USD') : 'nessuna operazione negli ultimi 30 giorni'}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>
      {mostrate.map(([id, s]) => <Strategia key={id} id={id} s={s} />)}
    </>
  );
}
