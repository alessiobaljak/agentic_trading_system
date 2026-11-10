'use client';

import type { CSSProperties, ReactNode } from 'react';
import { durataFa, pct, soldi, type Metriche } from '../../lib/conti';

/**
 * La scheda di una strategia, senza sapere da dove arrivano i dati (10 nov 2026, mattone comune a crypto e azioni): nome con il
 * segno del suo colore, l'etichetta del tipo (ordini simulati / conto demo / soldi veri), il valore grande con «dall'inizio», tre
 * riquadri (oggi, 7 giorni, giorni in guadagno) e qualche riga corta. I numeri arrivano già fatti da `metricheDaSerie`
 * (lib/conti.ts). L'aspetto è quello delle schede crypto della prima schermata (classi `cr-` in globals.css).
 */
export type TipoScheda = 'paper' | 'demo' | 'vero';

export const ETICHETTE_TIPO: Record<TipoScheda, string> = {
  paper: 'ordini simulati',
  demo: 'ordini veri · soldi finti',
  vero: 'soldi veri',
};

/** Oltre due ore senza aggiornamento il numero si segna come vecchio. */
const VECCHIO_S = 2 * 3600;

export function Delta({ x, cifre = 2 }: { x: number | null; cifre?: number }) {
  return <span className={x == null ? undefined : x > 0 ? 'cr-su' : x < 0 ? 'cr-giu' : undefined}>{pct(x, cifre)}</span>;
}

export function TestaScheda({ nome, colore, tipo, etichetta, descrizione }: {
  nome: string;
  colore: string;
  tipo: TipoScheda;
  etichetta?: string;
  descrizione?: string;
}) {
  return (
    <>
      <div className="cr-scheda-testa">
        <span className="cr-chiave" style={{ background: colore }} aria-hidden="true" />
        <h3>{nome}</h3>
        <span className={`cr-etichetta ${tipo}`}>{etichetta ?? ETICHETTE_TIPO[tipo]}</span>
      </div>
      {descrizione && <p className="cr-descr">{descrizione}</p>}
    </>
  );
}

/** «24 monete comprate · 23 vendute» (o «azioni», …). */
export function RigaPosizioni({ comprate, vendute, cosa = 'monete', coda }: {
  comprate: number; vendute: number; cosa?: string; coda?: ReactNode;
}) {
  return <span><b>{comprate} {cosa} comprate · {vendute} vendute</b>{coda}</span>;
}

export interface PropsSchedaBase {
  nome: string;
  colore: string;
  tipo: TipoScheda;
  etichetta?: string;
  descrizione?: string;
  linkDettagli?: string | null;
  /** '$' davanti, ogni altra valuta dopo il numero ('USDT', 'CHF', …) */
  unita: string;
  metriche: Metriche;
  adesso: number;
  /** il testo dello stato, mostrato solo se non è «acceso» */
  stato?: string | null;
  /** la riga delle posizioni (per esempio `<RigaPosizioni comprate={24} vendute={23} />`) */
  posizioni?: ReactNode;
  ultimoRibilancio?: { etichetta?: string; testo: string } | null;
  /** «Partito con …» */
  partenza?: ReactNode;
  /** righe corte in più, in fondo alle righe */
  righeExtra?: ReactNode;
  /** comandi o altro sotto la scheda (per esempio i pulsanti del demo) */
  children?: ReactNode;
}

export default function SchedaBase(p: PropsSchedaBase) {
  const m = p.metriche;
  const vecchio = m.aggiornato != null && p.adesso - m.aggiornato > VECCHIO_S;
  return (
    <article className="cr-scheda" data-tipo={p.tipo} style={{ '--colore-scheda': p.colore } as CSSProperties}>
      <TestaScheda nome={p.nome} colore={p.colore} tipo={p.tipo} etichetta={p.etichetta} descrizione={p.descrizione} />

      <div className="cr-valore">
        <span className="cr-valore-num">{soldi(m.valore, p.unita)}</span>
        <span className="cr-valore-delta">
          <Delta x={m.dallInizio} /> <small>dall&apos;inizio</small>
        </span>
      </div>

      <dl className="cr-numeri">
        <div>
          <dt>Oggi</dt>
          <dd><Delta x={m.oggi} /></dd>
        </div>
        <div>
          <dt title={m.setteEtichetta}>{m.setteEtichetta === '7 giorni' ? 'Ultimi 7 giorni' : m.setteEtichetta}</dt>
          <dd><Delta x={m.sette} /></dd>
        </div>
        <div>
          <dt>Giorni in guadagno</dt>
          <dd>{m.giorniTot ? `${m.giorniSu} su ${m.giorniTot}` : '—'}</dd>
        </div>
      </dl>

      <div className="cr-righe">
        {p.stato && p.stato !== 'acceso' && <span className="cr-vecchio">Stato: {p.stato}</span>}
        {p.posizioni}
        {p.ultimoRibilancio && <span>{p.ultimoRibilancio.etichetta ?? 'Ultimo ribilancio'}: {p.ultimoRibilancio.testo}</span>}
        <span>
          {p.partenza}
          {p.partenza ? ' · ' : null}
          <span className={vecchio ? 'cr-vecchio' : undefined}>
            {vecchio ? 'dato vecchio: ' : ''}aggiornato {m.aggiornato ? durataFa(p.adesso, m.aggiornato) : '—'}
          </span>
        </span>
        {p.righeExtra}
        {p.linkDettagli && <a className="cr-vai" href={p.linkDettagli} aria-label={`dettagli di ${p.nome}`}>Dettagli ›</a>}
      </div>

      {p.children}
    </article>
  );
}

/** La scheda di una strategia senza numeri ancora (spenta, in attesa, in lettura): la testa e una riga. */
export function SchedaSenzaNumeri({ nome, colore, tipo, etichetta, descrizione, testo, children }: {
  nome: string; colore: string; tipo: TipoScheda; etichetta?: string; descrizione?: string; testo: string; children?: ReactNode;
}) {
  return (
    <article className="cr-scheda" data-tipo={tipo} style={{ '--colore-scheda': colore } as CSSProperties}>
      <TestaScheda nome={nome} colore={colore} tipo={tipo} etichetta={etichetta} descrizione={descrizione} />
      <p className="cr-riga muted">{testo}</p>
      {children}
    </article>
  );
}
