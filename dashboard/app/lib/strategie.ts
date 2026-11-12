'use client';

/**
 * Le strategie in corso lette dalla dashboard (10 nov 2026, il proprietario: «una Dashboard pulita semplice e veloce da leggere
 * che mi permetta in tempo reale di vedere come stanno andando le diverse strategie paper demo etc»).
 *
 * Chi scrive (la forma dei dati è la loro):
 *   - bot/portafoglio/f5.py      → /paper_g1, /paper_g1n, /paper_g11, /paper_f5: `stato`, `giorni/{AAAA-MM-GG}` (il valore
 *                                  dell'ultima ora del giorno UTC), `ribilanciamenti/{AAAA-MM-GG}`;
 *   - bot/portafoglio/eventi.py  → /paper_eventi: `stato`, `giorni` (scritti dal 3 novembre: il primo giorno registrato non è il
 *                                  primo giorno della strategia);
 *   - bot/portafoglio/demo_binance.py → /demo_binance: `stato`, `giorni` della fase in corso (a 1.000 USDT dall'8 novembre),
 *                                  `fasi/{nome}/giorni` le fasi di prima, `ribilanciamenti`, `allarme`, `allarmi/{tipo}`, `fermo`,
 *                                  `confronto`, `errore`;
 *   - bot/portafoglio/conto_vero.py → /conto_vero: `stato` (spento: «spento: <motivo>», `acceso: false`), `allarmi`, `fermo`,
 *                                  `versione` (il commit in esecuzione, quello approvato letto, se coincidono);
 *   - bot/main.py                → /bot_status/heartbeat (secondi), a ogni giro del ciclo.
 *   - il proprietario, da qui    → /commands/conto_vero_versione_approvata, /commands/conto_vero_riparti e
 *                                  /commands/conto_vero_riparti_conferma (12 nov 2026): si rileggono per mostrare a che punto sono.
 *
 * Qui solo lettura: i comandi del demo («chiudi tutto», «riparti») stanno in components/strategie/ComandiDemo.tsx, quelli del conto
 * vero (approva la versione, chiudi tutto, riparti in due passi) in components/strategie/ComandiContoVero.tsx.
 */
import { useEffect, useMemo, useState } from 'react';
import { limitToLast, onValue, orderByKey, query, ref } from 'firebase/database';
import { giornoUtc, metricheDaSerie, rendimentiGiornalieri, type Giorni, type Metriche } from './conti';
import { getRtdb } from './firebase';

// i conti e i formati comuni (anche alle azioni) stanno in lib/conti.ts; qui si riesportano per le schede crypto
export * from './conti';

export type Tipo = 'paper' | 'demo' | 'vero';

export interface DefStrategia {
  /** il ramo su Firebase, anche chiave stabile della strategia (il colore la segue, non l'ordine) */
  ramo: string;
  nome: string;
  /** il nome corto dei pulsanti (scheda Dettagli) */
  breve: string;
  /** il nome nell'indirizzo della pagina Dettagli (#crypto/dettagli/<pagina>) */
  pagina: string;
  descrizione: string;
  tipo: Tipo;
  /** il campo dello stato con il capitale di partenza */
  base: 'capitale' | 'capitale_iniziale';
  /** il colore della serie (token CSS, validato con lo strumento della skill dataviz: chiaro su #ffffff, scuro su #1a1a19) */
  colore: string;
  /** vero se il primo giorno registrato parte dal capitale di partenza (solo il demo, fase in corso: `parti_da_zero`) */
  primoGiornoDallaBase: boolean;
  unita: '$' | 'USDT';
}

/** L'ordine dei colori è quello della tavolozza validata (slot 1-6), assegnato alla strategia una volta per tutte. */
export const STRATEGIE: DefStrategia[] = [
  {
    ramo: 'demo_binance', pagina: 'g1demo', breve: 'G1 demo', nome: 'G1 sul conto demo', tipo: 'demo', base: 'capitale_iniziale', colore: 'var(--serie-2)',
    primoGiornoDallaBase: true, unita: 'USDT',
    descrizione: 'G1 con ordini veri sul conto demo di Binance: soldi finti, ordini e prezzi veri.',
  },
  {
    ramo: 'conto_vero', pagina: 'contovero', breve: 'Conto vero', nome: 'G1 sul conto vero', tipo: 'vero', base: 'capitale_iniziale', colore: 'var(--serie-7)',
    primoGiornoDallaBase: true, unita: 'USDT',
    descrizione: 'G1 con soldi veri sul conto di Binance.',
  },
  {
    ramo: 'paper_g1', pagina: 'g1', breve: 'G1', nome: 'G1', tipo: 'paper', base: 'capitale', colore: 'var(--serie-1)', primoGiornoDallaBase: false,
    unita: '$',
    descrizione: 'Il funding fra monete: compra quelle che pagano meno funding e vende quelle che pagano di più. Decide ogni giorno.',
  },
  {
    ramo: 'paper_g1n', pagina: 'g1neutra', breve: 'G1 neutra', nome: 'G1 neutra', tipo: 'paper', base: 'capitale', colore: 'var(--serie-4)', primoGiornoDallaBase: false,
    unita: '$',
    descrizione: 'Come G1, con i due lati pesati perché i movimenti del mercato intero contino poco.',
  },
  {
    ramo: 'paper_g11', pagina: 'g11', breve: 'G11', nome: 'G11', tipo: 'paper', base: 'capitale', colore: 'var(--serie-3)', primoGiornoDallaBase: false,
    unita: '$',
    descrizione: 'Come G1, guardando anche il funding dell\'ultimo giorno.',
  },
  {
    ramo: 'paper_f5', pagina: 'f5', breve: 'F5', nome: 'F5', tipo: 'paper', base: 'capitale', colore: 'var(--serie-5)', primoGiornoDallaBase: false,
    unita: '$',
    descrizione: 'Come G1, ma cambia le posizioni solo il lunedì.',
  },
  {
    ramo: 'paper_eventi', pagina: 'eventi', breve: 'Eventi', nome: 'Eventi', tipo: 'paper', base: 'capitale', colore: 'var(--serie-6)', primoGiornoDallaBase: false,
    unita: '$',
    descrizione: 'Monete appena quotate e funding al tetto: vende la moneta e compra Bitcoin per lo stesso valore, per qualche giorno.',
  },
];

export const defDi = (ramo: string) => STRATEGIE.find((s) => s.ramo === ramo)!;

/* ------------------------------------------------------------------ forme dei dati */
export interface StatoRamo {
  stato?: string;
  acceso?: boolean;
  equity?: number;
  capitale?: number;
  capitale_iniziale?: number;
  rendimento?: number;
  long?: number;
  short?: number;
  ultimo_lunedi?: string;
  aggiornato?: number;
  // eventi
  aperte_n3?: number;
  aperte_e4?: number;
  chiuse?: number;
  rendimento_medio?: number | null;
  // demo
  saldo?: number;
  massimo?: number;
  dal_massimo?: number;
  stop_a?: number;
  limite_eseguiti?: number;
  limite_totali?: number;
  ordini_in_attesa?: number;
  conto_ridotto?: number | null;
}

export interface Ribilancio {
  chiave: string;
  entrate?: number;
  uscite?: number;
  /** paper: l'ora del ribilancio (s) */
  eseguito?: number;
  /** demo: l'ora degli ordini (s) */
  piazzati?: number;
  ordini?: number;
  rifiutati?: unknown[];
  solo_eventi?: boolean;
}

export interface Allarme {
  ora?: number;
  testo?: string;
  posizioni?: string[];
  monete?: string[];
}
export interface Fermo {
  motivo?: string;
  ora?: number;
  chiuse?: number;
  vuoto?: number;
}
export interface Confronto {
  ora?: number;
  differenze?: { simbolo: string; scarto: number }[];
  scarto_totale?: number;
  monete?: number;
}
export interface Errore {
  testo?: string;
  ora?: number;
  dove?: string;
}

export interface DatiRamo {
  stato: StatoRamo | null;
  giorni: Giorni | null;
  ultimoRibilancio: Ribilancio | null;
  /** vero quando lo stato è arrivato (anche vuoto): per distinguere «sto leggendo» da «spento» */
  arrivato: boolean;
}

export interface DatiDemo {
  fasi: Record<string, { giorni?: Giorni | null } | null> | null;
  allarme: Allarme | null;
  allarmi: Record<string, Allarme | null> | null;
  fermo: Fermo | null;
  confronto: Confronto | null;
  errore: Errore | null;
}

/** /conto_vero/versione, scritta dal bot (bot/portafoglio/conto_vero.py, `_pubblica_versione`), anche da spento. */
export interface VersioneContoVero {
  /** il commit che il bot sta eseguendo (HEAD del repository all'avvio del processo), 40 caratteri */
  commit?: string;
  /** la data del commit, ISO */
  data?: string;
  titolo?: string;
  /** vero se i file caricati dal bot sono uguali a quel commit; altrimenti `motivo` dice perché */
  pulito?: boolean;
  motivo?: string;
  /** il commit approvato che il bot ha letto all'ultimo controllo (ogni minuto) */
  approvata?: string;
  /** vero se per il bot il codice in esecuzione è quello approvato; altrimenti `blocco` dice perché */
  coincidono?: boolean;
  blocco?: string;
  aggiornato?: number;
}

/** /commands/conto_vero_versione_approvata: fra gli utenti la scrive solo il proprietario, da «Approva questa versione» (la chiave
 *  di amministratore di Firebase ignora le regole: nessun codice del repository la scrive, lo controlla un test). */
export interface VersioneApprovata {
  commit?: string;
  /** millisecondi (l'ora del server di Firebase) */
  ora?: number;
}

export interface DatiContoVero {
  allarmi: Record<string, Allarme | null> | null;
  fermo: Fermo | null;
  versione: VersioneContoVero | null;
  /** vero quando /conto_vero/versione è arrivata (anche vuota) */
  versioneArrivata: boolean;
  approvata: VersioneApprovata | null;
  /** i due passi del «riparti» come sono adesso su Firebase: la richiesta (vero) e la conferma (l'ora del fermo, in testo) */
  riparti: boolean | null;
  ripartiConferma: string | null;
}

export const CONTO_VERO_VUOTO: DatiContoVero = {
  allarmi: null, fermo: null, versione: null, versioneArrivata: false, approvata: null, riparti: null, ripartiConferma: null,
};

export interface DatiStrategie {
  rami: Record<string, DatiRamo>;
  demo: DatiDemo;
  contoVero: DatiContoVero;
  /** l'ultimo battito del ciclo del bot, in secondi */
  battito: number | null;
  battitoArrivato: boolean;
}

const VUOTO_RAMO: DatiRamo = { stato: null, giorni: null, ultimoRibilancio: null, arrivato: false };

/** Legge in diretta tutto ciò che serve alla prima schermata (solo i rami che servono, non /bot_status intero). */
export function useStrategie(): DatiStrategie {
  const [rami, setRami] = useState<Record<string, DatiRamo>>({});
  const [demo, setDemo] = useState<DatiDemo>({ fasi: null, allarme: null, allarmi: null, fermo: null, confronto: null, errore: null });
  const [contoVero, setContoVero] = useState<DatiContoVero>(CONTO_VERO_VUOTO);
  const [battito, setBattito] = useState<number | null>(null);
  const [battitoArrivato, setBattitoArrivato] = useState(false);

  useEffect(() => {
    const db = getRtdb();
    const metti = (ramo: string, campo: keyof DatiRamo, valore: unknown) =>
      setRami((p) => ({ ...p, [ramo]: { ...(p[ramo] ?? VUOTO_RAMO), [campo]: valore, ...(campo === 'stato' ? { arrivato: true } : {}) } }));
    const stop: (() => void)[] = [];
    for (const s of STRATEGIE) {
      stop.push(onValue(ref(db, `${s.ramo}/stato`), (x) => metti(s.ramo, 'stato', x.val())));
      if (s.tipo === 'vero') continue; // spento: niente giorni da leggere finché non parte
      stop.push(onValue(ref(db, `${s.ramo}/giorni`), (x) => metti(s.ramo, 'giorni', x.val())));
      stop.push(onValue(query(ref(db, `${s.ramo}/ribilanciamenti`), orderByKey(), limitToLast(1)), (x) => {
        const v = (x.val() ?? {}) as Record<string, Omit<Ribilancio, 'chiave'>>;
        const chiave = Object.keys(v).sort().pop();
        metti(s.ramo, 'ultimoRibilancio', chiave ? { chiave, ...v[chiave] } : null);
      }));
    }
    const d = (campo: keyof DatiDemo) => (x: { val: () => unknown }) => setDemo((p) => ({ ...p, [campo]: x.val() as never }));
    stop.push(onValue(ref(db, 'demo_binance/fasi'), d('fasi')));
    stop.push(onValue(ref(db, 'demo_binance/allarme'), d('allarme')));
    stop.push(onValue(ref(db, 'demo_binance/allarmi'), d('allarmi')));
    stop.push(onValue(ref(db, 'demo_binance/fermo'), d('fermo')));
    stop.push(onValue(ref(db, 'demo_binance/confronto'), d('confronto')));
    stop.push(onValue(ref(db, 'demo_binance/errore'), d('errore')));
    const v = (campo: keyof DatiContoVero) => (x: { val: () => unknown }) =>
      setContoVero((p) => ({ ...p, [campo]: x.val() as never }));
    stop.push(onValue(ref(db, 'conto_vero/allarmi'), v('allarmi')));
    stop.push(onValue(ref(db, 'conto_vero/fermo'), v('fermo')));
    stop.push(onValue(ref(db, 'conto_vero/versione'), (x) =>
      setContoVero((p) => ({ ...p, versione: x.val() as VersioneContoVero | null, versioneArrivata: true }))));
    stop.push(onValue(ref(db, 'commands/conto_vero_versione_approvata'), v('approvata')));
    stop.push(onValue(ref(db, 'commands/conto_vero_riparti'), (x) =>
      setContoVero((p) => ({ ...p, riparti: x.val() === true }))));
    stop.push(onValue(ref(db, 'commands/conto_vero_riparti_conferma'), (x) =>
      setContoVero((p) => ({ ...p, ripartiConferma: typeof x.val() === 'string' ? (x.val() as string) : null }))));
    stop.push(onValue(ref(db, 'bot_status/heartbeat'), (x) => {
      const n = Number(x.val());
      setBattito(Number.isFinite(n) && n > 0 ? (n > 1e12 ? n / 1000 : n) : null);
      setBattitoArrivato(true);
    }));
    return () => stop.forEach((f) => f());
  }, []);

  return { rami, demo, contoVero, battito, battitoArrivato };
}

/** Quello che serve alla riga di stato in cima a tutte le pagine Crypto: il battito, l'ultimo aggiornamento delle strategie, gli
 *  allarmi e il fermo del demo, gli allarmi del conto vero. Più leggero di `useStrategie` (niente giorni né ribilanciamenti). */
export interface StatoCrypto {
  battito: number | null;
  battitoArrivato: boolean;
  aggiornato: number | null;
  demo: Pick<DatiDemo, 'allarme' | 'allarmi' | 'fermo'>;
  contoVero: Pick<DatiContoVero, 'allarmi' | 'fermo'>;
}

export function useStatoCrypto(): StatoCrypto {
  const [battito, setBattito] = useState<number | null>(null);
  const [battitoArrivato, setBattitoArrivato] = useState(false);
  const [aggiornati, setAggiornati] = useState<Record<string, number>>({});
  const [demo, setDemo] = useState<StatoCrypto['demo']>({ allarme: null, allarmi: null, fermo: null });
  const [contoVero, setContoVero] = useState<StatoCrypto['contoVero']>({ allarmi: null, fermo: null });
  useEffect(() => {
    const db = getRtdb();
    const stop = STRATEGIE.map((s) => onValue(ref(db, `${s.ramo}/stato/aggiornato`), (x) => {
      const n = Number(x.val());
      setAggiornati((p) => ({ ...p, [s.ramo]: Number.isFinite(n) ? n : 0 }));
    }));
    stop.push(onValue(ref(db, 'bot_status/heartbeat'), (x) => {
      const n = Number(x.val());
      setBattito(Number.isFinite(n) && n > 0 ? (n > 1e12 ? n / 1000 : n) : null);
      setBattitoArrivato(true);
    }));
    stop.push(onValue(ref(db, 'demo_binance/allarme'), (x) => setDemo((p) => ({ ...p, allarme: x.val() }))));
    stop.push(onValue(ref(db, 'demo_binance/allarmi'), (x) => setDemo((p) => ({ ...p, allarmi: x.val() }))));
    stop.push(onValue(ref(db, 'demo_binance/fermo'), (x) => setDemo((p) => ({ ...p, fermo: x.val() }))));
    stop.push(onValue(ref(db, 'conto_vero/allarmi'), (x) => setContoVero((p) => ({ ...p, allarmi: x.val() }))));
    stop.push(onValue(ref(db, 'conto_vero/fermo'), (x) => setContoVero((p) => ({ ...p, fermo: x.val() }))));
    return () => stop.forEach((f) => f());
  }, []);
  const valori = Object.values(aggiornati).filter((x) => x > 0);
  return { battito, battitoArrivato, aggiornato: valori.length ? Math.max(...valori) : null, demo, contoVero };
}

/* ------------------------------------------------------------------ i conti di una strategia */
/** I valori di fine giorno con, per il giorno in corso, il valore di adesso dallo stato. */
export function serieConOggi(d: DatiRamo): Giorni {
  const g: Giorni = {};
  for (const [k, v] of Object.entries(d.giorni ?? {})) if (Number.isFinite(Number(v))) g[k] = Number(v);
  if (d.stato?.equity != null && d.stato.aggiornato) g[giornoUtc(d.stato.aggiornato)] = Number(d.stato.equity);
  return g;
}

export function metriche(def: DefStrategia, d: DatiRamo, adesso: number): Metriche {
  const base = Number(d.stato?.[def.base] ?? 0);
  return metricheDaSerie({
    serie: serieConOggi(d),
    valore: d.stato?.equity != null ? Number(d.stato.equity) : null,
    base: base > 0 ? base : null,
    aggiornato: d.stato?.aggiornato ?? null,
    primoGiornoDallaBase: def.primoGiornoDallaBase,
    adesso,
  });
}

/* ------------------------------------------------------------------ G1 sul demo contro G1 nel paper, giorno per giorno */
export interface RigaConfronto {
  giorno: string;
  paper: number | null;
  demo: number | null;
  differenza: number | null;
  /** la fase del demo: null = quella in corso */
  fase: string | null;
  nota: string | null;
  inCorso: boolean;
}

/** «capitale_280_fino_al_2026-11-08» → «a 280 USDT»; un nome che non si riconosce si mostra pulito. */
export function nomeFase(nome: string): string {
  const m = /capitale_(\d+)(?:_(\d+))?/.exec(nome);
  if (m) return `fase a ${Number(m[1]).toLocaleString('it-IT')}${m[2] ? `,${m[2]}` : ''}`;
  if (nome.includes('conto_intero')) return 'fase a circa 5.000';
  return nome.replace(/_fino_al_.*/, '').replace(/_/g, ' ');
}

export function confrontoDemoPaper(
  paper: DatiRamo,
  demo: DatiRamo,
  fasi: DatiDemo['fasi'],
): RigaConfronto[] {
  const oggi = paper.stato?.aggiornato ? giornoUtc(paper.stato.aggiornato) : null;
  const rPaper = rendimentiGiornalieri(serieConOggi(paper), null);

  // le fasi del demo dalla più vecchia; quella in corso parte dal suo capitale (parti_da_zero apre da zero alla mezzanotte)
  const archiviate = Object.entries(fasi ?? {})
    .map(([nome, f]) => ({ nome, giorni: (f?.giorni ?? {}) as Giorni }))
    .filter((f) => Object.keys(f.giorni).length > 0)
    .sort((a, b) => (Object.keys(a.giorni).sort().pop() ?? '').localeCompare(Object.keys(b.giorni).sort().pop() ?? ''));
  const capitale = Number(demo.stato?.capitale_iniziale ?? 0) || null;
  const fasiTutte = [
    ...archiviate.map((f) => ({ fase: nomeFase(f.nome), r: rendimentiGiornalieri(f.giorni, null), date: Object.keys(f.giorni) })),
    { fase: null as string | null, r: rendimentiGiornalieri(serieConOggi(demo), capitale), date: Object.keys(serieConOggi(demo)) },
  ];
  const quante: Record<string, number> = {};
  for (const f of fasiTutte) for (const k of f.date) quante[k] = (quante[k] ?? 0) + 1;

  const rDemo: Record<string, { r: number | null; fase: string | null; nota: string | null }> = {};
  for (const f of fasiTutte) {
    for (const k of f.date) {
      const r = f.r[k];
      if (quante[k] > 1) {
        // giorno del cambio di capitale: vale solo il primo giorno della fase in corso (parte dal capitale, di notte)
        if (f.fase === null && r != null) rDemo[k] = { r, fase: null, nota: null };
        else if (!rDemo[k]) rDemo[k] = { r: null, fase: f.fase, nota: 'cambio di capitale' };
      } else if (r != null) {
        rDemo[k] = { r, fase: f.fase, nota: null };
      }
    }
  }

  const giorni = Array.from(new Set([...Object.keys(rPaper), ...Object.keys(rDemo)])).sort();
  const primoDemo = Object.keys(rDemo).sort()[0];
  return giorni
    .filter((k) => primoDemo && k >= primoDemo)
    .map((k) => {
      const p = rPaper[k] ?? null;
      const d = rDemo[k]?.r ?? null;
      return {
        giorno: k, paper: p, demo: d, differenza: p != null && d != null ? d - p : null,
        fase: rDemo[k]?.fase ?? null, nota: rDemo[k]?.nota ?? null, inCorso: k === oggi,
      };
    });
}

export interface RiassuntoConfronto {
  giorni: number;
  media: number | null;
  scartoTipico: number | null;
  demoComposto: number | null;
  paperComposto: number | null;
}

/** Sui giorni chiusi con tutti e due: la differenza media, quella senza segno e i due rendimenti composti. */
export function riassumi(righe: RigaConfronto[]): RiassuntoConfronto {
  const ok = righe.filter((r) => !r.inCorso && r.differenza != null && r.demo != null && r.paper != null);
  if (!ok.length) return { giorni: 0, media: null, scartoTipico: null, demoComposto: null, paperComposto: null };
  const somma = (f: (r: RigaConfronto) => number) => ok.reduce((a, r) => a + f(r), 0);
  return {
    giorni: ok.length,
    media: somma((r) => r.differenza!) / ok.length,
    scartoTipico: somma((r) => Math.abs(r.differenza!)) / ok.length,
    demoComposto: ok.reduce((a, r) => a * (1 + r.demo!), 1) - 1,
    paperComposto: ok.reduce((a, r) => a * (1 + r.paper!), 1) - 1,
  };
}

/** Gli allarmi accesi del demo (e del conto vero), dal più recente. */
export interface AllarmeVisibile {
  dove: 'demo' | 'conto vero';
  tipo: string;
  ora: number | null;
  testo: string;
  monete: string[];
}

export function allarmiAccesi(demo: Pick<DatiDemo, 'allarme' | 'allarmi'>, contoVero: Pick<DatiContoVero, 'allarmi'>): AllarmeVisibile[] {
  const out: AllarmeVisibile[] = [];
  if (demo.allarme?.testo) {
    out.push({ dove: 'demo', tipo: 'conto non vuoto da fermo', ora: demo.allarme.ora ?? null, testo: demo.allarme.testo,
      monete: demo.allarme.posizioni ?? [] });
  }
  for (const [tipo, a] of Object.entries(demo.allarmi ?? {})) {
    if (a?.testo) out.push({ dove: 'demo', tipo, ora: a.ora ?? null, testo: a.testo, monete: a.monete ?? [] });
  }
  for (const [tipo, a] of Object.entries(contoVero.allarmi ?? {})) {
    if (a?.testo) out.push({ dove: 'conto vero', tipo, ora: a.ora ?? null, testo: a.testo, monete: a.monete ?? [] });
  }
  return out.sort((a, b) => (b.ora ?? 0) - (a.ora ?? 0));
}

export const nomeMoneta = (s?: string) => (s ?? '').replace('USDT', '');

/** Le curve di tutte le strategie con i giorni (il conto vero no: è spento). */
export function useSerie(rami: Record<string, DatiRamo>): Record<string, Giorni> {
  return useMemo(() => {
    const out: Record<string, Giorni> = {};
    for (const s of STRATEGIE) {
      if (s.tipo === 'vero') continue;
      const d = rami[s.ramo];
      if (d) out[s.ramo] = serieConOggi(d);
    }
    return out;
  }, [rami]);
}
