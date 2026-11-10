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
 *   - bot/portafoglio/conto_vero.py → /conto_vero: `stato` (spento: «spento: <motivo>», `acceso: false`), `allarmi`, `fermo`.
 *   - bot/main.py                → /bot_status/heartbeat (secondi), a ogni giro del ciclo.
 *
 * Qui solo lettura: i comandi del demo («chiudi tutto», «riparti») stanno in components/strategie/ComandiDemo.tsx.
 */
import { useEffect, useMemo, useState } from 'react';
import { limitToLast, onValue, orderByKey, query, ref } from 'firebase/database';
import { getRtdb } from './firebase';
import { durata } from './viz';

export type Tipo = 'paper' | 'demo' | 'vero';

export interface DefStrategia {
  /** il ramo su Firebase, anche chiave stabile della strategia (il colore la segue, non l'ordine) */
  ramo: string;
  nome: string;
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
    ramo: 'demo_binance', nome: 'G1 sul conto demo', tipo: 'demo', base: 'capitale_iniziale', colore: 'var(--serie-2)',
    primoGiornoDallaBase: true, unita: 'USDT',
    descrizione: 'G1 con ordini veri sul conto demo di Binance: soldi finti, ordini e prezzi veri.',
  },
  {
    ramo: 'conto_vero', nome: 'G1 sul conto vero', tipo: 'vero', base: 'capitale_iniziale', colore: 'var(--serie-7)',
    primoGiornoDallaBase: true, unita: 'USDT',
    descrizione: 'G1 con soldi veri sul conto di Binance.',
  },
  {
    ramo: 'paper_g1', nome: 'G1', tipo: 'paper', base: 'capitale', colore: 'var(--serie-1)', primoGiornoDallaBase: false,
    unita: '$',
    descrizione: 'Il funding fra monete: compra quelle che pagano meno funding e vende quelle che pagano di più. Decide ogni giorno.',
  },
  {
    ramo: 'paper_g1n', nome: 'G1 neutra', tipo: 'paper', base: 'capitale', colore: 'var(--serie-4)', primoGiornoDallaBase: false,
    unita: '$',
    descrizione: 'Come G1, con i due lati pesati perché i movimenti del mercato intero contino poco.',
  },
  {
    ramo: 'paper_g11', nome: 'G11', tipo: 'paper', base: 'capitale', colore: 'var(--serie-3)', primoGiornoDallaBase: false,
    unita: '$',
    descrizione: 'Come G1, guardando anche il funding dell\'ultimo giorno.',
  },
  {
    ramo: 'paper_f5', nome: 'F5', tipo: 'paper', base: 'capitale', colore: 'var(--serie-5)', primoGiornoDallaBase: false,
    unita: '$',
    descrizione: 'Come G1, ma cambia le posizioni solo il lunedì.',
  },
  {
    ramo: 'paper_eventi', nome: 'Eventi', tipo: 'paper', base: 'capitale', colore: 'var(--serie-6)', primoGiornoDallaBase: false,
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

export type Giorni = Record<string, number>;

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

export interface DatiContoVero {
  allarmi: Record<string, Allarme | null> | null;
  fermo: Fermo | null;
}

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
  const [contoVero, setContoVero] = useState<DatiContoVero>({ allarmi: null, fermo: null });
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
    stop.push(onValue(ref(db, 'bot_status/heartbeat'), (x) => {
      const n = Number(x.val());
      setBattito(Number.isFinite(n) && n > 0 ? (n > 1e12 ? n / 1000 : n) : null);
      setBattitoArrivato(true);
    }));
    return () => stop.forEach((f) => f());
  }, []);

  return { rami, demo, contoVero, battito, battitoArrivato };
}

/** Un orologio che batte ogni `ogniMs`: per «3 min fa» che si aggiorna da solo. */
export function useAdesso(ogniMs = 15000): number {
  const [adesso, setAdesso] = useState(() => Date.now() / 1000);
  useEffect(() => {
    const t = setInterval(() => setAdesso(Date.now() / 1000), ogniMs);
    return () => clearInterval(t);
  }, [ogniMs]);
  return adesso;
}

/* ------------------------------------------------------------------ date (i giorni del bot sono giorni UTC) */
export const giornoUtc = (s: number): string => new Date(s * 1000).toISOString().slice(0, 10);

export function spostaGiorno(g: string, n: number): string {
  const t = Date.parse(`${g}T00:00:00Z`) + n * 86400_000;
  return new Date(t).toISOString().slice(0, 10);
}

const MESI = ['gen', 'feb', 'mar', 'apr', 'mag', 'giu', 'lug', 'ago', 'set', 'ott', 'nov', 'dic'];
/** '2026-11-10' → '10 nov' */
export function giornoBreve(g: string | null | undefined): string {
  if (!g || g.length < 10) return g ?? '—';
  return `${Number(g.slice(8, 10))} ${MESI[Number(g.slice(5, 7)) - 1] ?? ''}`;
}

/** Ora italiana di un istante in secondi: '10 nov, 01:05'. */
export function oraItaliana(s: number | null | undefined): string {
  if (!s) return '—';
  const d = new Date(s * 1000);
  const parti = new Intl.DateTimeFormat('it-IT', {
    timeZone: 'Europe/Rome', day: 'numeric', month: 'short', hour: '2-digit', minute: '2-digit',
  }).formatToParts(d);
  const p = (t: string) => parti.find((x) => x.type === t)?.value ?? '';
  return `${p('day')} ${p('month').replace('.', '')}, ${p('hour')}:${p('minute')}`;
}

/** «3 min fa», «2 h 05 fa». */
export const durataFa = (adesso: number, t: number): string => `${durata(Math.max(0, adesso - t))} fa`;

/* ------------------------------------------------------------------ numeri */
/** Il segno solo se il numero arrotondato non è zero: «−0,00» non si scrive. */
function segnoDi(x: number, cifre: number): string {
  if (Math.abs(x) < 0.5 * 10 ** -cifre) return '';
  return x > 0 ? '+' : '−';
}

export function pct(x: number | null | undefined, cifre = 2): string {
  if (x == null || !Number.isFinite(x)) return '—';
  const v = Math.abs(100 * x).toFixed(cifre).replace('.', ',');
  return `${segnoDi(100 * x, cifre)}${v}%`;
}

/** Punti percentuali (differenza fra due rendimenti): '+0,12 punti'. */
export function punti(x: number | null | undefined, cifre = 2): string {
  if (x == null || !Number.isFinite(x)) return '—';
  const v = Math.abs(100 * x).toFixed(cifre).replace('.', ',');
  return `${segnoDi(100 * x, cifre)}${v}`;
}

export function soldi(x: number | null | undefined, unita: '$' | 'USDT', cifre = 2): string {
  if (x == null || !Number.isFinite(x)) return '—';
  const n = x.toLocaleString('it-IT', { minimumFractionDigits: cifre, maximumFractionDigits: cifre });
  return unita === '$' ? `$${n}` : `${n} USDT`;
}

/* ------------------------------------------------------------------ i conti di una strategia */
export interface Metriche {
  valore: number | null;
  base: number | null;
  dallInizio: number | null;
  /** oggi rispetto alla chiusura di ieri (il giorno UTC in corso) */
  oggi: number | null;
  sette: number | null;
  /** '7 giorni' o, se la serie è più corta, 'da N giorni' */
  setteEtichetta: string;
  giorniSu: number;
  giorniTot: number;
  primoGiorno: string | null;
  giornoDiOggi: string | null;
  aggiornato: number | null;
}

/** I valori di fine giorno con, per il giorno in corso, il valore di adesso dallo stato. */
export function serieConOggi(d: DatiRamo): Giorni {
  const g: Giorni = {};
  for (const [k, v] of Object.entries(d.giorni ?? {})) if (Number.isFinite(Number(v))) g[k] = Number(v);
  if (d.stato?.equity != null && d.stato.aggiornato) g[giornoUtc(d.stato.aggiornato)] = Number(d.stato.equity);
  return g;
}

export function metriche(def: DefStrategia, d: DatiRamo, adesso: number): Metriche {
  const serie = serieConOggi(d);
  const date = Object.keys(serie).sort();
  const base = Number(d.stato?.[def.base] ?? 0) > 0 ? Number(d.stato?.[def.base]) : null;
  const valore = d.stato?.equity != null ? Number(d.stato.equity) : date.length ? serie[date[date.length - 1]] : null;
  const giornoDiOggi = d.stato?.aggiornato ? giornoUtc(d.stato.aggiornato) : date.length ? date[date.length - 1] : giornoUtc(adesso);
  const dallInizio = valore != null && base ? valore / base - 1 : null;

  const prima = date.filter((x) => x < giornoDiOggi);
  const ieri = prima.length ? serie[prima[prima.length - 1]] : null;
  const oggi = valore == null ? null : ieri ? valore / ieri - 1 : def.primoGiornoDallaBase && base ? valore / base - 1 : null;

  const limite = spostaGiorno(giornoDiOggi, -7);
  const finoAlLimite = date.filter((x) => x <= limite);
  let sette: number | null = null;
  let setteEtichetta = '7 giorni';
  if (valore != null && finoAlLimite.length) {
    sette = valore / serie[finoAlLimite[finoAlLimite.length - 1]] - 1;
  } else if (valore != null && date.length) {
    const n = Math.round((Date.parse(`${giornoDiOggi}T00:00:00Z`) - Date.parse(`${date[0]}T00:00:00Z`)) / 86400_000) + 1;
    if (def.primoGiornoDallaBase && base) {
      sette = valore / base - 1;
      setteEtichetta = `da ${n} ${n === 1 ? 'giorno' : 'giorni'}`;
    } else if (date.length > 1) {
      sette = valore / serie[date[0]] - 1;
      setteEtichetta = `da ${n - 1} ${n - 1 === 1 ? 'giorno' : 'giorni'}`;
    }
  }

  // i giorni chiusi (non quello in corso), giorno su giorno; il primo solo se parte dal capitale di partenza
  let giorniSu = 0;
  let giorniTot = 0;
  prima.forEach((k, i) => {
    const prec = i > 0 ? serie[prima[i - 1]] : def.primoGiornoDallaBase ? base : null;
    if (prec == null || !(prec > 0)) return;
    giorniTot += 1;
    if (serie[k] > prec) giorniSu += 1;
  });

  return {
    valore, base, dallInizio, oggi, sette, setteEtichetta, giorniSu, giorniTot,
    primoGiorno: date[0] ?? null, giornoDiOggi, aggiornato: d.stato?.aggiornato ?? null,
  };
}

/* ------------------------------------------------------------------ le curve a 100 alla stessa data */
export interface CurveA100 {
  /** il giorno in cui tutte le curve accese valgono 100 (la chiusura di quel giorno) */
  base: string | null;
  righe: Record<string, number | string>[];
  /** le strategie accese senza dati */
  senzaDati: string[];
}

export function curveA100(serie: Record<string, Giorni>, accese: string[]): CurveA100 {
  const conDati = accese.filter((r) => Object.keys(serie[r] ?? {}).length > 0);
  const senzaDati = accese.filter((r) => !conDati.includes(r));
  if (!conDati.length) return { base: null, righe: [], senzaDati };
  const primi = conDati.map((r) => Object.keys(serie[r]).sort()[0]);
  const base = primi.sort().pop()!;
  const valoreBase: Record<string, number> = {};
  for (const r of conDati) {
    const finoAllaBase = Object.keys(serie[r]).filter((k) => k <= base).sort();
    valoreBase[r] = serie[r][finoAllaBase[finoAllaBase.length - 1]];
  }
  const tutte = new Set<string>();
  for (const r of conDati) for (const k of Object.keys(serie[r])) if (k >= base) tutte.add(k);
  const righe = Array.from(tutte).sort().map((g) => {
    const riga: Record<string, number | string> = { giorno: g };
    for (const r of conDati) {
      const v = serie[r][g];
      if (v != null && valoreBase[r] > 0) riga[r] = (100 * v) / valoreBase[r];
    }
    return riga;
  });
  return { base, righe, senzaDati };
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

/** I rendimenti di ogni giorno di una serie, solo fra due giorni consecutivi (più il primo dalla base, se data). */
export function rendimentiGiornalieri(g: Giorni, basePrimoGiorno: number | null): Record<string, number> {
  const date = Object.keys(g).sort();
  const out: Record<string, number> = {};
  date.forEach((k, i) => {
    const v = Number(g[k]);
    if (i === 0) {
      if (basePrimoGiorno && basePrimoGiorno > 0) out[k] = v / basePrimoGiorno - 1;
      return;
    }
    const p = date[i - 1];
    if (p === spostaGiorno(k, -1) && Number(g[p]) > 0) out[k] = v / Number(g[p]) - 1;
  });
  return out;
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

export function allarmiAccesi(demo: DatiDemo, contoVero: DatiContoVero): AllarmeVisibile[] {
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
