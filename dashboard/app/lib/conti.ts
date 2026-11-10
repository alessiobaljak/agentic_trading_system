'use client';

/**
 * I conti e i formati comuni a tutte le schede (10 nov 2026): crypto e azioni. Niente qui sa dei rami di Firebase: si passa una
 * serie di valori di fine giorno `{AAAA-MM-GG: valore}` con il valore di adesso, e tornano i numeri delle schede. Le schede crypto li
 * usano attraverso lib/strategie.ts (che li riesporta), quella delle azioni attraverso components/comuni.
 */
import { useEffect, useState } from 'react';
import { durata } from './viz';

export type Giorni = Record<string, number>;

/** Un orologio che batte ogni `ogniMs`: per «3 min fa» che si aggiorna da solo. */
export function useAdesso(ogniMs = 15000): number {
  const [adesso, setAdesso] = useState(() => Date.now() / 1000);
  useEffect(() => {
    const t = setInterval(() => setAdesso(Date.now() / 1000), ogniMs);
    return () => clearInterval(t);
  }, [ogniMs]);
  return adesso;
}

/* ------------------------------------------------------------------ date */
/** Il giorno UTC di un istante in secondi (i giorni del bot delle crypto sono giorni UTC). */
export const giornoUtc = (s: number): string => new Date(s * 1000).toISOString().slice(0, 10);

/** Il giorno di un istante in secondi in un fuso orario (per le azioni: il giorno della borsa, per esempio Europe/Zurich). */
export function giornoNelFuso(s: number, fuso: string): string {
  const p = new Intl.DateTimeFormat('en-CA', { timeZone: fuso, year: 'numeric', month: '2-digit', day: '2-digit' }).format(s * 1000);
  return p.slice(0, 10);
}

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

/** Punti percentuali (differenza fra due rendimenti): '+0,12'. */
export function punti(x: number | null | undefined, cifre = 2): string {
  if (x == null || !Number.isFinite(x)) return '—';
  const v = Math.abs(100 * x).toFixed(cifre).replace('.', ',');
  return `${segnoDi(100 * x, cifre)}${v}`;
}

/** Un importo: '$10.765,51' con il dollaro, '993,53 USDT' o '1.250,00 CHF' con le altre valute. */
export function soldi(x: number | null | undefined, unita: string, cifre = 2): string {
  if (x == null || !Number.isFinite(x)) return '—';
  const n = x.toLocaleString('it-IT', { minimumFractionDigits: cifre, maximumFractionDigits: cifre });
  return unita === '$' ? `$${n}` : `${n} ${unita}`;
}

/* ------------------------------------------------------------------ i conti di una strategia */
export interface Metriche {
  valore: number | null;
  base: number | null;
  dallInizio: number | null;
  /** oggi rispetto alla chiusura dell'ultimo giorno prima di oggi */
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

export interface IngressoMetriche {
  /** i valori di fine giorno, con quello di adesso al giorno di oggi */
  serie: Giorni;
  /** il valore di adesso (se manca, l'ultimo della serie) */
  valore: number | null;
  /** il capitale di partenza */
  base: number | null;
  /** quando è stato scritto il valore di adesso (secondi) */
  aggiornato: number | null;
  /** il giorno in corso, nella stessa convenzione delle chiavi della serie (se manca: il giorno UTC di `aggiornato`) */
  giornoDiOggi?: string | null;
  /** vero se il primo giorno della serie parte dal capitale (allora il primo giorno conta) */
  primoGiornoDallaBase: boolean;
  adesso: number;
}

export function metricheDaSerie(i: IngressoMetriche): Metriche {
  const { serie, primoGiornoDallaBase } = i;
  const date = Object.keys(serie).sort();
  const base = i.base != null && i.base > 0 ? i.base : null;
  const valore = i.valore != null ? i.valore : date.length ? serie[date[date.length - 1]] : null;
  const giornoDiOggi = i.giornoDiOggi
    ?? (i.aggiornato ? giornoUtc(i.aggiornato) : date.length ? date[date.length - 1] : giornoUtc(i.adesso));
  const dallInizio = valore != null && base ? valore / base - 1 : null;

  const prima = date.filter((x) => x < giornoDiOggi);
  const ieri = prima.length ? serie[prima[prima.length - 1]] : null;
  const oggi = valore == null ? null : ieri ? valore / ieri - 1 : primoGiornoDallaBase && base ? valore / base - 1 : null;

  const limite = spostaGiorno(giornoDiOggi, -7);
  const finoAlLimite = date.filter((x) => x <= limite);
  let sette: number | null = null;
  let setteEtichetta = '7 giorni';
  if (valore != null && finoAlLimite.length) {
    sette = valore / serie[finoAlLimite[finoAlLimite.length - 1]] - 1;
  } else if (valore != null && date.length) {
    const n = Math.round((Date.parse(`${giornoDiOggi}T00:00:00Z`) - Date.parse(`${date[0]}T00:00:00Z`)) / 86400_000) + 1;
    if (primoGiornoDallaBase && base) {
      sette = valore / base - 1;
      setteEtichetta = `da ${n} ${n === 1 ? 'giorno' : 'giorni'}`;
    } else if (date.length > 1) {
      sette = valore / serie[date[0]] - 1;
      setteEtichetta = `da ${n - 1} ${n - 1 === 1 ? 'giorno' : 'giorni'}`;
    }
  }

  // i giorni chiusi (non quello in corso), sul giorno registrato prima; il primo solo se parte dal capitale di partenza
  let giorniSu = 0;
  let giorniTot = 0;
  prima.forEach((k, j) => {
    const prec = j > 0 ? serie[prima[j - 1]] : primoGiornoDallaBase ? base : null;
    if (prec == null || !(prec > 0)) return;
    giorniTot += 1;
    if (serie[k] > prec) giorniSu += 1;
  });

  return {
    valore, base, dallInizio, oggi, sette, setteEtichetta, giorniSu, giorniTot,
    primoGiorno: date[0] ?? null, giornoDiOggi, aggiornato: i.aggiornato,
  };
}

/* ------------------------------------------------------------------ le curve a 100 alla stessa data */
export interface RisultatoCurve {
  /** il giorno in cui tutte le curve accese valgono 100 (la chiusura di quel giorno) */
  base: string | null;
  righe: Record<string, number | string>[];
  /** le serie accese senza dati */
  senzaDati: string[];
}

/** Ogni serie accesa a 100 alla chiusura del primo giorno in cui ci sono tutte (`serie[chiave] = {giorno: valore}`). */
export function curveA100(serie: Record<string, Giorni>, accese: string[]): RisultatoCurve {
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

/** I rendimenti di ogni giorno di una serie, solo fra due giorni di calendario consecutivi (più il primo dalla base, se data). */
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
