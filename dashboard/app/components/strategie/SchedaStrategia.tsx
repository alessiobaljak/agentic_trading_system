'use client';

import {
  durataFa, giornoBreve, metriche, oraItaliana, pct, soldi,
  type DatiContoVero, type DatiDemo, type DatiRamo, type DefStrategia, type Ribilancio,
} from '../../lib/strategie';
import SchedaBase, { RigaPosizioni, SchedaSenzaNumeri, TestaScheda } from '../comuni/SchedaBase';
import ComandiContoVero from './ComandiContoVero';
import ComandiDemo from './ComandiDemo';

/**
 * La scheda di una strategia crypto nella prima schermata: legge i rami del bot (lib/strategie.ts) e li passa alla scheda comune
 * (components/comuni/SchedaBase.tsx), con in più il conto vero spento e, per il demo, i comandi «chiudi tutto» e «riparti»; per
 * il conto vero la versione del codice da approvare e i suoi comandi (ComandiContoVero.tsx), visibili anche da spento.
 * «Aggiornato» diventa vecchio oltre due ore: il bot scrive ogni ora (bot/portafoglio/f5.py, OGNI_VALUTAZIONE_S).
 */
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

/** Spento se non ha mai scritto, se lo dice (`acceso: false`) o se il testo dello stato comincia con «spento». */
export function eSpento(d: DatiRamo | undefined): boolean {
  const s = d?.stato;
  return !s || s.acceso === false || /^spento/i.test(s.stato ?? '');
}

export default function SchedaStrategia({ def, dati, adesso, demo, contoVero }: {
  def: DefStrategia;
  dati: DatiRamo | undefined;
  adesso: number;
  /** solo per la scheda del demo: allarmi, fermo, confronto, errore */
  demo?: DatiDemo;
  /** solo per la scheda del conto vero: la versione del codice, l'approvazione, il fermo e i due passi del «riparti» */
  contoVero?: DatiContoVero;
}) {
  const d: DatiRamo = dati ?? { stato: null, giorni: null, ultimoRibilancio: null, arrivato: false };
  const link = def.tipo !== 'vero' ? `#crypto/dettagli/${def.pagina}` : null;
  const comandiVero = def.tipo === 'vero' && contoVero
    ? <ComandiContoVero stato={d.stato} spento={eSpento(d)} dati={contoVero} /> : null;

  // il conto vero: spento finché il proprietario non lo chiede (bot/portafoglio/conto_vero.py)
  if (def.tipo === 'vero' && eSpento(d)) {
    const motivo = (d.stato?.stato ?? '').replace(/^spento:\s*/i, '');
    return (
      <article className="cr-scheda" data-tipo="vero">
        <TestaScheda nome={def.nome} colore={def.colore} tipo={def.tipo} descrizione={def.descrizione} />
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
        {comandiVero}
      </article>
    );
  }

  const s = d.stato;
  const comandi = def.tipo === 'demo' && demo ? <ComandiDemo stato={s} fermo={demo.fermo} confronto={demo.confronto} />
    : comandiVero;
  if (!s || s.equity == null) {
    return (
      <SchedaSenzaNumeri nome={def.nome} colore={def.colore} tipo={def.tipo} descrizione={def.descrizione}
        testo={!d.arrivato ? 'Lettura in corso…' : s?.stato ? `${s.stato}${s.aggiornato ? ` (${durataFa(adesso, s.aggiornato)})` : ''}.`
          : 'Spento o non ancora partito.'}>
        {comandi}
      </SchedaSenzaNumeri>
    );
  }

  const m = metriche(def, d, adesso);
  const eventi = def.ramo === 'paper_eventi';
  const rib = testoRibilancio(def, d.ultimoRibilancio, s.ultimo_lunedi);
  const capitale = Number(s[def.base] ?? 0);
  const errore = demo?.errore;
  const erroreRecente = errore?.testo && errore.ora && adesso - errore.ora < 24 * 3600;

  return (
    <SchedaBase
      nome={def.nome} colore={def.colore} tipo={def.tipo} descrizione={def.descrizione} linkDettagli={link}
      unita={def.unita} metriche={m} adesso={adesso} stato={s.stato}
      posizioni={eventi ? (
        <span>
          <b>{(s.aperte_n3 ?? 0) + (s.aperte_e4 ?? 0)} operazioni aperte</b> · {s.chiuse ?? 0} chiuse
          {s.rendimento_medio != null ? ` (in media ${pct(s.rendimento_medio)})` : ''}
        </span>
      ) : s.long == null && s.short == null ? null : (
        <RigaPosizioni comprate={s.long ?? 0} vendute={s.short ?? 0}
          coda={def.tipo === 'demo' && (s.ordini_in_attesa ?? 0) > 0 ? ` · ${s.ordini_in_attesa} ordini limite in attesa` : null} />
      )}
      ultimoRibilancio={rib ? {
        etichetta: def.ramo === 'paper_f5' ? 'Ultimo cambio (il lunedì)' : eventi ? 'Ultimo giro' : 'Ultimo ribilancio', testo: rib,
      } : null}
      partenza={def.unita === 'USDT'
        ? <>Partito con <b>{soldi(capitale, 'USDT', 0)}</b>{m.primoGiorno ? ` il ${giornoBreve(m.primoGiorno)}` : ''}</>
        : <>Partito con <b>{soldi(capitale, '$', 0)}</b> virtuali</>}
      righeExtra={<>
        {def.tipo === 'demo' && s.limite_totali ? (
          <span>Ordini limite eseguiti {s.limite_eseguiti ?? 0} su {s.limite_totali} (il resto a mercato).</span>
        ) : null}
        {def.tipo === 'demo' && erroreRecente && (
          <span>Ultimo errore registrato ({oraItaliana(errore!.ora)}): {errore!.testo}</span>
        )}
      </>}
    >
      {comandi}
    </SchedaBase>
  );
}
