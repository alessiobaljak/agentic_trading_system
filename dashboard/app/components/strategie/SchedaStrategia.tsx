'use client';

import {
  durataFa, giornoBreve, metriche, oraItaliana, pct, soldi,
  type DatiDemo, type DatiRamo, type DefStrategia, type Ribilancio,
} from '../../lib/strategie';
import ComandiDemo from './ComandiDemo';

/** Oltre due ore senza aggiornamento il numero è vecchio (il bot scrive ogni ora: bot/portafoglio/f5.py, OGNI_VALUTAZIONE_S). */
const VECCHIO_S = 2 * 3600;

const ETICHETTA: Record<DefStrategia['tipo'], string> = {
  paper: 'ordini simulati',
  demo: 'ordini veri · soldi finti',
  vero: 'soldi veri',
};

function Delta({ x, cifre = 2 }: { x: number | null; cifre?: number }) {
  return <span className={x == null ? undefined : x > 0 ? 'cr-su' : x < 0 ? 'cr-giu' : undefined}>{pct(x, cifre)}</span>;
}

function testoRibilancio(def: DefStrategia, r: Ribilancio | null, ultimoLunedi?: string): string | null {
  if (!r) return ultimoLunedi ? `${giornoBreve(ultimoLunedi)}` : null;
  const giorno = giornoBreve(r.chiave.slice(0, 10));
  const ora = r.piazzati ?? r.eseguito;
  const pezzi: string[] = [];
  const n = (k: number, uno: string, tanti: string) => `${k} ${k === 1 ? uno : tanti}`;
  if (r.entrate != null || r.uscite != null) {
    pezzi.push(`${n(r.entrate ?? 0, 'entrata', 'entrate')}, ${n(r.uscite ?? 0, 'uscita', 'uscite')}`);
  }
  if (def.tipo !== 'paper' && r.ordini != null) pezzi.push(n(r.ordini, 'ordine', 'ordini'));
  const rifiutati = Array.isArray(r.rifiutati) ? r.rifiutati.length : 0;
  if (rifiutati) pezzi.push(n(rifiutati, 'rifiutato', 'rifiutati'));
  if (r.solo_eventi) pezzi.push('solo eventi');
  return `${ora ? oraItaliana(ora) : giorno}${pezzi.length ? ` (${pezzi.join(', ')})` : ''}`;
}

function Testa({ def }: { def: DefStrategia }) {
  return (
    <>
      <div className="cr-scheda-testa">
        <span className="cr-chiave" style={{ background: def.colore }} aria-hidden="true" />
        <h3>{def.nome}</h3>
        <span className={`cr-etichetta ${def.tipo}`}>{ETICHETTA[def.tipo]}</span>
      </div>
      <p className="cr-descr">{def.descrizione}</p>
    </>
  );
}

/** Spento se non ha mai scritto, se lo dice (`acceso: false`) o se il testo dello stato comincia con «spento». */
export function eSpento(d: DatiRamo | undefined): boolean {
  const s = d?.stato;
  return !s || s.acceso === false || /^spento/i.test(s.stato ?? '');
}

export default function SchedaStrategia({ def, dati, adesso, demo }: {
  def: DefStrategia;
  dati: DatiRamo | undefined;
  adesso: number;
  /** solo per la scheda del demo: allarmi, fermo, confronto, errore */
  demo?: DatiDemo;
}) {
  const d: DatiRamo = dati ?? { stato: null, giorni: null, ultimoRibilancio: null, arrivato: false };

  // il conto vero: spento finché il proprietario non lo chiede (bot/portafoglio/conto_vero.py)
  if (def.tipo === 'vero' && eSpento(d)) {
    const motivo = (d.stato?.stato ?? '').replace(/^spento:\s*/i, '');
    return (
      <article className="cr-scheda" data-tipo="vero">
        <Testa def={def} />
        <div className="cr-spento"><span className="dot" aria-hidden="true" />Spento</div>
        <div className="cr-righe">
          <span>
            <b>Perché:</b>{' '}
            {!d.arrivato ? 'lettura in corso…' : motivo || 'non ha ancora scritto niente su Firebase (nessun ordine, nessuna richiesta a Binance).'}
          </span>
          <span>
            Parte solo se lo chiedi tu, in modo esplicito: servono l&apos;interruttore, DRY_RUN spento, il codice approvato e un
            capitale fino a 300 USDT. Niente eventi.
          </span>
          {d.stato?.aggiornato && <span>Ultimo controllo {durataFa(adesso, d.stato.aggiornato)}.</span>}
        </div>
      </article>
    );
  }

  const s = d.stato;
  if (!s || s.equity == null) {
    return (
      <article className="cr-scheda" data-tipo={def.tipo}>
        <Testa def={def} />
        <p className="cr-riga muted">
          {!d.arrivato ? 'Lettura in corso…' : s?.stato ? `${s.stato}${s.aggiornato ? ` (${durataFa(adesso, s.aggiornato)})` : ''}.`
            : 'Spento o non ancora partito.'}
        </p>
        {def.tipo === 'demo' && demo && <ComandiDemo stato={s} fermo={demo.fermo} confronto={demo.confronto} />}
      </article>
    );
  }

  const m = metriche(def, d, adesso);
  const vecchio = m.aggiornato != null && adesso - m.aggiornato > VECCHIO_S;
  const eventi = def.ramo === 'paper_eventi';
  const rib = testoRibilancio(def, d.ultimoRibilancio, s.ultimo_lunedi);
  const capitale = Number(s[def.base] ?? 0);
  const errore = demo?.errore;
  const erroreRecente = errore?.testo && errore.ora && adesso - errore.ora < 24 * 3600;

  return (
    <article className="cr-scheda" data-tipo={def.tipo}>
      <Testa def={def} />

      <div className="cr-valore">
        <span className="cr-valore-num">{soldi(m.valore, def.unita)}</span>
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
        {s.stato && s.stato !== 'acceso' && <span className="cr-vecchio">Stato: {s.stato}</span>}
        {eventi ? (
          <span>
            <b>{(s.aperte_n3 ?? 0) + (s.aperte_e4 ?? 0)} operazioni aperte</b> · {s.chiuse ?? 0} chiuse
            {s.rendimento_medio != null ? ` (in media ${pct(s.rendimento_medio)})` : ''}
          </span>
        ) : s.long == null && s.short == null ? null : (
          <span>
            <b>{s.long ?? 0} monete comprate · {s.short ?? 0} vendute</b>
            {def.tipo === 'demo' && (s.ordini_in_attesa ?? 0) > 0 ? ` · ${s.ordini_in_attesa} ordini limite in attesa` : ''}
          </span>
        )}
        {rib && (
          <span>
            {def.ramo === 'paper_f5' ? 'Ultimo cambio (il lunedì)' : eventi ? 'Ultimo giro' : 'Ultimo ribilancio'}: {rib}
          </span>
        )}
        <span>
          {def.unita === 'USDT'
            ? <>Partito con <b>{soldi(capitale, 'USDT', 0)}</b>{m.primoGiorno ? ` il ${giornoBreve(m.primoGiorno)}` : ''}</>
            : <>Partito con <b>{soldi(capitale, '$', 0)}</b> virtuali</>}
          {' · '}
          <span className={vecchio ? 'cr-vecchio' : undefined}>
            {vecchio ? 'dato vecchio: ' : ''}aggiornato {m.aggiornato ? durataFa(adesso, m.aggiornato) : '—'}
          </span>
        </span>
        {def.tipo === 'demo' && s.limite_totali ? (
          <span>Ordini limite eseguiti {s.limite_eseguiti ?? 0} su {s.limite_totali} (il resto a mercato).</span>
        ) : null}
        {def.tipo === 'demo' && erroreRecente && (
          <span>Ultimo errore registrato ({oraItaliana(errore!.ora)}): {errore!.testo}</span>
        )}
      </div>

      {def.tipo === 'demo' && demo && <ComandiDemo stato={s} fermo={demo.fermo} confronto={demo.confronto} />}
    </article>
  );
}
