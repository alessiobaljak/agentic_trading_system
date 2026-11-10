'use client';

/**
 * La scheda «Dettagli» (seconda tornata, 10 nov 2026; il proprietario: «la sezione dettagli invece non mi piace per niente troppo
 * testo riesci a farla come la sezione strategia»): i dati di UNA strategia alla volta, letti in diretta solo per quella scelta.
 *
 * Forme (chi le scrive):
 *   - /{ramo}/posizioni   {simbolo: peso} (f5.py, a ogni ribilancio): peso > 0 comprata, < 0 venduta, in frazione del capitale.
 *     Il demo non scrive i suoi pesi: usa la decisione di G1 (demo_binance.py legge data/paper_g1.json), quindi per il demo si
 *     mostrano i pesi di /paper_g1/posizioni come «voluti», accanto alle differenze vere di /demo_binance/confronto.
 *   - /{ramo}/diario/{giorno}  paper: {equity, long, short, costi_totali, funding_totale}; demo: {equity, long, short, entrate:
 *     {funding_incassato (+ incassato), commissioni_pagate (+ pagate)}} (demo_binance.py, `entrate_del_conto`).
 *   - /{ramo}/ribilanciamenti/{chiave}  paper: {entrate, uscite, long, short, costo, ordini_limite, eseguito, limite: {variazioni,
 *     eseguite, costo, costo_a_mercato}}; demo: {ordini, entrate, uscite, rifiutati: [{simbolo, errore}],
 *     monete_mancanti_sul_demo: [simbolo], sotto_il_minimo: {variazioni, valore_in_frazione_del_conto}, piazzati, limite: {ordini,
 *     eseguiti_a_limite, a_mercato}}.
 *   - /paper_eventi/aperte/{id} {tipo, simbolo, entrata (ms), rendimento_ora, uscita_giorno}; /paper_eventi/chiuse/{id} {tipo,
 *     simbolo, uscita (ms), rendimento, dollari, motivo} (eventi.py).
 *   - Il funding del paper: `stato.funding_totale` è quello PAGATO (f5.py, `_funding_regolati`: q × mark × tasso, tolto dal valore);
 *     incassato = −funding_totale.
 */
import { useEffect, useState } from 'react';
import { limitToLast, onValue, orderByKey, query, ref } from 'firebase/database';
import { getRtdb } from './firebase';
import {
  rendimentiGiornalieri, serieConOggi, spostaGiorno, type Confronto, type DatiRamo, type DefStrategia, type Giorni, type StatoRamo,
} from './strategie';

export interface StatoDettaglio extends StatoRamo {
  costi_totali?: number;
  funding_totale?: number;
  limite_variazioni?: number;
  limite_eseguite?: number;
}

export interface RibilancioDettaglio {
  chiave: string;
  entrate?: number;
  uscite?: number;
  long?: number;
  short?: number;
  costo?: number;
  ordini?: number;
  eseguito?: number;
  piazzati?: number;
  rifiutati?: { simbolo?: string; errore?: string }[] | string[];
  monete_mancanti_sul_demo?: string[];
  sotto_il_minimo?: { variazioni?: number; valore_in_frazione_del_conto?: number } | null;
  solo_eventi?: boolean;
  limite?: { variazioni?: number; eseguite?: number; ordini?: number; eseguiti_a_limite?: number; a_mercato?: number } | null;
}

export interface Operazione {
  id: string;
  tipo?: string;
  simbolo?: string;
  entrata?: number;
  uscita?: number;
  rendimento_ora?: number;
  rendimento?: number;
  dollari?: number;
  uscita_giorno?: string;
  motivo?: string;
}

export interface DiarioGiorno {
  equity?: number;
  entrate?: { funding_incassato?: number; commissioni_pagate?: number } | null;
}

export interface Dettaglio {
  stato: StatoDettaglio | null;
  giorni: Giorni | null;
  diario: Record<string, DiarioGiorno | null> | null;
  ribilancio: RibilancioDettaglio | null;
  pesi: Record<string, number> | null;
  confronto: Confronto | null;
  aperte: Operazione[];
  chiuse: Operazione[];
  arrivato: boolean;
}

const VUOTO: Dettaglio = {
  stato: null, giorni: null, diario: null, ribilancio: null, pesi: null, confronto: null, aperte: [], chiuse: [], arrivato: false,
};

/** I dati della strategia scelta, letti in diretta; si riparte da zero quando cambia la strategia. */
export function useDettaglio(def: DefStrategia): Dettaglio {
  const [d, setD] = useState<Dettaglio>(VUOTO);
  const ramo = def.ramo;
  useEffect(() => {
    setD(VUOTO);
    const db = getRtdb();
    const metti = (campo: keyof Dettaglio, valore: unknown) =>
      setD((p) => ({ ...p, [campo]: valore, ...(campo === 'stato' ? { arrivato: true } : {}) }));
    const lista = (v: unknown): Operazione[] =>
      Object.entries((v ?? {}) as Record<string, Omit<Operazione, 'id'>>).map(([id, x]) => ({ id, ...x }));
    const stop = [
      onValue(ref(db, `${ramo}/stato`), (x) => metti('stato', x.val())),
      onValue(ref(db, `${ramo}/giorni`), (x) => metti('giorni', x.val())),
      onValue(ref(db, `${ramo}/diario`), (x) => metti('diario', x.val())),
      onValue(query(ref(db, `${ramo}/ribilanciamenti`), orderByKey(), limitToLast(1)), (x) => {
        const v = (x.val() ?? {}) as Record<string, Omit<RibilancioDettaglio, 'chiave'>>;
        const chiave = Object.keys(v).sort().pop();
        metti('ribilancio', chiave ? { chiave, ...v[chiave] } : null);
      }),
    ];
    if (def.tipo === 'demo') {
      stop.push(onValue(ref(db, 'paper_g1/posizioni'), (x) => metti('pesi', x.val())));
      stop.push(onValue(ref(db, 'demo_binance/confronto'), (x) => metti('confronto', x.val())));
    } else if (ramo !== 'paper_eventi') {
      stop.push(onValue(ref(db, `${ramo}/posizioni`), (x) => metti('pesi', x.val())));
    } else {
      stop.push(onValue(ref(db, 'paper_eventi/aperte'), (x) => metti('aperte', lista(x.val()))));
      stop.push(onValue(query(ref(db, 'paper_eventi/chiuse'), orderByKey(), limitToLast(30)), (x) => metti('chiuse', lista(x.val()))));
    }
    return () => stop.forEach((f) => f());
  }, [ramo, def.tipo]);
  return d;
}

/** La discesa più grande dal massimo, sui valori di fine giorno (e su quello di adesso); il massimo parte dal capitale se la serie
 *  comincia dal capitale. Negativa (−0,12 = −12%), 0 se non è mai scesa; null senza dati. */
export function discesaMassima(def: DefStrategia, d: DatiRamo): number | null {
  const serie = serieConOggi(d);
  const date = Object.keys(serie).sort();
  if (!date.length) return null;
  const base = Number(d.stato?.[def.base] ?? 0);
  let massimo = def.primoGiornoDallaBase && base > 0 ? base : serie[date[0]];
  let peggiore = 0;
  for (const k of date) {
    massimo = Math.max(massimo, serie[k]);
    if (massimo > 0) peggiore = Math.min(peggiore, serie[k] / massimo - 1);
  }
  return peggiore;
}

/** Spese pagate e funding incassato: il paper dallo stato, il demo dalla somma delle entrate vere del diario (fase in corso). */
export function speseEFunding(def: DefStrategia, d: Dettaglio): { spese: number | null; funding: number | null } {
  if (def.tipo === 'demo') {
    const voci = Object.values(d.diario ?? {}).map((x) => x?.entrate).filter((x): x is NonNullable<typeof x> => !!x);
    if (!voci.length) return { spese: null, funding: null };
    return {
      spese: voci.reduce((a, x) => a + Number(x.commissioni_pagate ?? 0), 0),
      funding: voci.reduce((a, x) => a + Number(x.funding_incassato ?? 0), 0),
    };
  }
  return {
    spese: d.stato?.costi_totali != null ? Number(d.stato.costi_totali) : null,
    funding: d.stato?.funding_totale != null ? -Number(d.stato.funding_totale) : null,
  };
}

/** Ordini limite eseguiti su quelli piazzati, dall'inizio (paper: variazioni; demo: ordini). */
export function ordiniLimite(def: DefStrategia, s: StatoDettaglio | null): { eseguiti: number; totali: number } | null {
  if (!s) return null;
  const e = def.tipo === 'demo' ? s.limite_eseguiti : s.limite_eseguite;
  const t = def.tipo === 'demo' ? s.limite_totali : s.limite_variazioni;
  return t ? { eseguiti: Number(e ?? 0), totali: Number(t) } : null;
}

export interface GiornoRisultato {
  giorno: string;
  r: number;
  valore: number;
  inCorso: boolean;
}

/** Il risultato di ogni giorno (sul giorno prima; il primo dal capitale se la serie parte dal capitale), gli ultimi `n`. */
export function risultatiGiornalieri(def: DefStrategia, d: DatiRamo, oggi: string | null, n = 30): GiornoRisultato[] {
  const serie = serieConOggi(d);
  const base = Number(d.stato?.[def.base] ?? 0);
  const r = rendimentiGiornalieri(serie, def.primoGiornoDallaBase && base > 0 ? base : null);
  return Object.keys(r).sort().slice(-n).map((g) => ({ giorno: g, r: r[g], valore: serie[g], inCorso: g === oggi }));
}

/* ------------------------------------------------------------------ G1 demo contro G1 paper dalla fase in corso */
export interface ConfrontoFase {
  partenza: string;
  capitale: number;
  demo: number;
  paper: number;
  differenza: number;
  giorni: number;
  /** le due curve, in frazione dalla partenza (0 alla partenza) */
  curva: { giorno: string; demo: number | null; paper: number | null }[];
}

/**
 * Dalla partenza della fase in corso del demo (il primo giorno di /demo_binance/giorni: `parti_da_zero` apre da zero alla decisione
 * di G1 della mezzanotte, con il capitale `capitale_iniziale`): il demo dal capitale, il paper dalla chiusura del giorno prima.
 */
export function confrontoFase(paper: DatiRamo | undefined, demo: DatiRamo | undefined): ConfrontoFase | null {
  if (!paper || !demo) return null;
  const sd = serieConOggi(demo);
  const sp = serieConOggi(paper);
  const dd = Object.keys(sd).sort();
  const capitale = Number(demo.stato?.capitale_iniziale ?? 0);
  if (!dd.length || !(capitale > 0)) return null;
  const partenza = dd[0];
  const prima = Object.keys(sp).filter((k) => k < partenza).sort().pop();
  if (!prima) return null;
  const basePaper = sp[prima];
  const ultimoD = sd[dd[dd.length - 1]];
  const dp = Object.keys(sp).filter((k) => k >= partenza).sort();
  if (!dp.length || !(basePaper > 0)) return null;
  const ultimoP = sp[dp[dp.length - 1]];
  const giorniCurva = Array.from(new Set([...dd, ...dp])).sort();
  const curva = [
    { giorno: spostaGiorno(partenza, -1), demo: 0, paper: 0 },
    ...giorniCurva.map((g) => ({
      giorno: g,
      demo: sd[g] != null ? sd[g] / capitale - 1 : null,
      paper: sp[g] != null ? sp[g] / basePaper - 1 : null,
    })),
  ];
  const demoR = ultimoD / capitale - 1;
  const paperR = ultimoP / basePaper - 1;
  return { partenza, capitale, demo: demoR, paper: paperR, differenza: demoR - paperR, giorni: dd.length, curva };
}
