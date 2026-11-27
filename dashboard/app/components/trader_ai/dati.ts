'use client';

import { useEffect, useState } from 'react';

/**
 * I dati del trader AI per la plancia (area trader_ai, 27 novembre 2026; il proprietario: «crea un'altra sezione dove posso vedere come
 * va questo agente AI live»). Il trader gira sulla macchina e non scrive su Firebase: la macchina salva stato, diario, conto simulato e
 * resoconti nel repository (`trader_ai/avanti/`, `trader_ai/vps/salva.sh`), che è pubblico. La plancia li legge da lì, dal browser
 * (raw.githubusercontent.com, che permette la lettura da qualunque sito), e legge il prezzo di BTC direttamente da Binance per il
 * risultato aperto di adesso. Niente chiavi, niente scritture.
 */
const BASE = 'https://raw.githubusercontent.com/alessiobaljak/agentic_trading_system/HEAD/trader_ai/avanti';
const PREZZO = 'https://fapi.binance.com/fapi/v1/premiumIndex?symbol=BTCUSDT';
export const TETTO_DOLLARI = 5;
export const QUOTA_OBIETTIVO = 0.03;

export interface Risposta {
  azione?: string;
  margine_usdt?: number | null;
  leva?: number | null;
  stop_prezzo?: number | null;
  obiettivo_prezzo?: number | null;
  tipo_ordine?: string | null;
  prezzo_limite?: number | null;
  motivo?: string;
  approccio?: string;
  diario?: string;
  lezione?: string | null;
}

/** Una riga del diario: una chiamata al modello (con `stato` e `motivo`) o un evento del programma (con `evento`). */
export interface RigaDiario {
  ora: string;
  evento?: string;
  motivo?: string;
  stato?: string;
  prezzo?: number;
  conto?: number;
  guadagno_giorno?: number;
  guadagno_netto?: number;
  costo?: number;
  speso_oggi?: number;
  durata_s?: number;
  risposta?: Risposta | null;
  scarto?: string | null;
  [k: string]: unknown;
}

export interface Operazione {
  n: number;
  aperta?: string;
  eseguita?: string | null;
  chiusa?: string;
  tipo?: string | null;
  lato: 'lungo' | 'corto';
  leva?: number;
  quantita?: number;
  entrata?: number;
  uscita?: number;
  come?: string;
  risultato?: number;
  spese?: number;
  funding?: number;
  R?: number | null;
  r?: number | null;
  rischio_pct?: number | null;
  motivo?: string;
  approccio?: string;
}

export interface Aperta {
  aperta?: string;
  tipo?: string | null;
  lato: 'lungo' | 'corto';
  leva?: number;
  entrata?: number;
  quantita?: number;
  stop?: number | null;
  obiettivo?: number | null;
  in_attesa?: boolean;
  eseguita?: string | null;
  margine?: number | null;
  motivo?: string;
  approccio?: string;
  rischio_pct?: number | null;
}

export interface Stato {
  giorno?: string;
  conto_mezzanotte?: number;
  inizio?: { giorno?: string; conto?: number };
  aperta?: Aperta | null;
  operazioni?: Operazione[];
  note?: string[];
  approccio?: string | null;
  fermo_fino?: string | null;
  obiettivo_ora?: string | null;
  tetto_dalle?: string | null;
  estraneo?: string | null;
  esaurito?: boolean;
  ultima?: string | null;
  ultimo_scarto?: string | null;
  stat_giorno?: { chiamate?: number; costo?: number };
}

export interface ContoSimulato {
  portafoglio?: number;
  posizione?: { lato: 'lungo' | 'corto'; quantita: number; entrata: number; leva: number; margine: number; liquidazione?: number } | null;
}

export interface DatiTrader {
  stato: Stato | null;
  diario: RigaDiario[];
  conto: ContoSimulato | null;
  spesa: Record<string, number>;
  /** quando la plancia li ha letti (secondi) */
  letti: number;
  errore: string | null;
}

async function leggi(nome: string, minuto: number): Promise<string> {
  // il numero del minuto evita la copia vecchia della cache di GitHub (fino a 5 minuti)
  const r = await fetch(`${BASE}/${nome}?m=${minuto}`, { cache: 'no-store' });
  if (!r.ok) throw new Error(`${nome}: ${r.status}`);
  return r.text();
}

export function righeDiario(testo: string): RigaDiario[] {
  const out: RigaDiario[] = [];
  for (const riga of testo.split('\n')) {
    if (!riga.trim()) continue;
    try {
      out.push(JSON.parse(riga) as RigaDiario);
    } catch {
      /* una riga a metà (salvata mentre il programma scriveva): si salta */
    }
  }
  return out;
}

/* Una lettura sola per tutta l'area (la riga di stato in cima e la pagina sotto la usano insieme): un giro ogni minuto finché qualcuno
   guarda, fermo quando nessuno guarda. */
let ultimi: DatiTrader | null = null;
const chi = new Set<(d: DatiTrader) => void>();
let giroAttivo: ReturnType<typeof setInterval> | null = null;

async function giro(): Promise<void> {
  const minuto = Math.floor(Date.now() / 60_000);
  try {
    const [s, d, c, sp] = await Promise.all([
      leggi('stato.json', minuto), leggi('diario.jsonl', minuto), leggi('conto_simulato.json', minuto), leggi('spesa.json', minuto),
    ]);
    ultimi = { stato: JSON.parse(s), diario: righeDiario(d), conto: JSON.parse(c), spesa: JSON.parse(sp), letti: Date.now() / 1000,
      errore: null };
  } catch (e) {
    ultimi = { ...(ultimi ?? { stato: null, diario: [], conto: null, spesa: {} }), letti: Date.now() / 1000,
      errore: e instanceof Error ? e.message : String(e) };
  }
  chi.forEach((f) => f(ultimi as DatiTrader));
}

/** I file del trader, letti adesso e poi ogni minuto (null finché la prima lettura non è arrivata). */
export function useDatiTrader(): DatiTrader | null {
  const [dati, setDati] = useState<DatiTrader | null>(ultimi);
  useEffect(() => {
    chi.add(setDati);
    if (!giroAttivo) {
      giro();
      giroAttivo = setInterval(giro, 60_000);
    }
    return () => {
      chi.delete(setDati);
      if (!chi.size && giroAttivo) { clearInterval(giroAttivo); giroAttivo = null; }
    };
  }, []);
  return dati;
}

/** Il prezzo mark di BTCUSDT da Binance, ogni `ogniMs` (lo stesso prezzo su cui il conto simulato fa scattare stop e obiettivi). */
export function usePrezzoBtc(ogniMs = 5_000): { prezzo: number | null; ora: number | null } {
  const [p, setP] = useState<{ prezzo: number | null; ora: number | null }>({ prezzo: null, ora: null });
  useEffect(() => {
    let vivo = true;
    const giro = async () => {
      try {
        const r = await fetch(PREZZO, { cache: 'no-store' });
        if (!r.ok) return;
        const j = await r.json();
        const x = Number(j.markPrice);
        if (vivo && Number.isFinite(x) && x > 0) setP({ prezzo: x, ora: Date.now() / 1000 });
      } catch {
        /* senza rete verso Binance resta l'ultimo prezzo salvato dalla macchina */
      }
    };
    giro();
    const t = setInterval(giro, ogniMs);
    return () => { vivo = false; clearInterval(t); };
  }, [ogniMs]);
  return p;
}

/** Il resoconto di un giorno finito (markdown scritto dal trader a mezzanotte UTC); null se non c'è. */
export async function leggiResoconto(giorno: string): Promise<string | null> {
  try {
    const r = await fetch(`${BASE}/resoconti/${giorno}.md?m=${Math.floor(Date.now() / 600_000)}`, { cache: 'no-store' });
    return r.ok ? await r.text() : null;
  } catch {
    return null;
  }
}

export const secondi = (iso?: string | null): number | null => {
  if (!iso) return null;
  const t = Date.parse(iso);
  return Number.isFinite(t) ? t / 1000 : null;
};

export const eChiamata = (r: RigaDiario): boolean => !!r.motivo && typeof r.stato === 'string';

/** Il risultato aperto a un prezzo, come lo conta il conto simulato (la perdita non va oltre il margine). */
export function risultatoAperto(pos: NonNullable<ContoSimulato['posizione']>, prezzo: number): number {
  const segno = pos.lato === 'lungo' ? 1 : -1;
  return Math.max(segno * (prezzo - pos.entrata) * pos.quantita, -pos.margine);
}

/** I numeri di adesso: conto (con il risultato aperto al prezzo di adesso), oggi, il 3%, dall'inizio. */
export function numeriDiAdesso(d: DatiTrader, prezzo: number | null) {
  const st = d.stato ?? {};
  const pos = d.conto?.posizione ?? null;
  const ultimaChiamata = [...d.diario].reverse().find((r) => eChiamata(r) && typeof r.conto === 'number');
  const prezzoUsato = prezzo ?? (typeof ultimaChiamata?.prezzo === 'number' ? ultimaChiamata.prezzo : null);
  const portafoglio = d.conto?.portafoglio ?? null;
  const aperto = pos && prezzoUsato != null ? risultatoAperto(pos, prezzoUsato) : 0;
  const conto = portafoglio != null ? portafoglio + aperto : (ultimaChiamata?.conto ?? null);
  const mezzanotte = st.conto_mezzanotte ?? null;
  const oggi = conto != null && mezzanotte != null ? conto - mezzanotte : null;
  const obiettivo = mezzanotte != null ? mezzanotte * QUOTA_OBIETTIVO : null;
  const inizio = st.inizio?.conto ?? null;
  return { pos, prezzoUsato, portafoglio, aperto, conto, mezzanotte, oggi, obiettivo, inizio,
    dallInizio: conto != null && inizio != null ? conto - inizio : null };
}

export const LATO: Record<string, string> = { lungo: 'Lungo (compra)', corto: 'Corto (vende)' };
export const AZIONE: Record<string, string> = {
  aspetta: 'aspetta', apri_lungo: 'apre lungo', apri_corto: 'apre corto', chiudi: 'chiude', modifica: 'sposta stop o obiettivo',
};

export const ora = (iso?: string | null): string => {
  const s = secondi(iso);
  if (s == null) return '—';
  return new Date(s * 1000).toLocaleTimeString('it-IT', { timeZone: 'Europe/Rome', hour: '2-digit', minute: '2-digit' });
};

export const usd = (x: number | null | undefined, cifre = 2, segno = false): string => {
  if (x == null || !Number.isFinite(x)) return '—';
  const s = Math.abs(x).toLocaleString('it-IT', { minimumFractionDigits: cifre, maximumFractionDigits: cifre });
  const piu = segno ? (x > 0.0049 ? '+' : x < -0.0049 ? '−' : '') : x < 0 ? '−' : '';
  return `${piu}${s}`;
};

export const prezzoBtc = (x: number | null | undefined): string =>
  x == null || !Number.isFinite(x) ? '—' : x.toLocaleString('it-IT', { maximumFractionDigits: 1 });

export const coloreDi = (x?: number | null) => (x == null ? undefined : x > 0.0049 ? 'var(--su-testo)' : x < -0.0049 ? 'var(--giu-testo)' : undefined);
