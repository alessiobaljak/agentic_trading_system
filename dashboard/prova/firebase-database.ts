/**
 * SOLO PER LA PROVA IN LOCALE: prende il posto di `firebase/database` quando la dashboard parte con `DASHBOARD_PROVA=1`
 * (next.config.mjs). Legge e scrive sull'albero finto di ./dati.ts, nella memoria del browser; non parla con nessun server.
 */
import { creaDati } from './dati';

type Valore = unknown;
type Vincolo = { tipo: 'orderByKey' } | { tipo: 'limitToLast'; n: number };
export type Database = { prova: true };
export type DatabaseReference = { percorso: string; vincoli: Vincolo[] };
export type Unsubscribe = () => void;
export type DataSnapshot = { key: string | null; val: () => Valore; exists: () => boolean };

let albero: Record<string, unknown> | null = null;
const ascoltatori = new Set<{ r: DatabaseReference; cb: (s: DataSnapshot) => void }>();

function radice(): Record<string, unknown> {
  if (!albero) {
    const scenario = typeof window !== 'undefined' ? new URLSearchParams(window.location.search).get('prova') : null;
    albero = creaDati(scenario);
  }
  return albero;
}

const pezzi = (p: string) => p.split('/').filter(Boolean);

function leggi(percorso: string): Valore {
  let v: unknown = radice();
  for (const k of pezzi(percorso)) {
    if (v == null || typeof v !== 'object') return null;
    v = (v as Record<string, unknown>)[k];
  }
  return v ?? null;
}

function istantanea(r: DatabaseReference): DataSnapshot {
  let v = leggi(r.percorso);
  const ultimo = r.vincoli.find((x) => x.tipo === 'limitToLast') as { n: number } | undefined;
  if (ultimo && v && typeof v === 'object') {
    const chiavi = Object.keys(v as object).sort().slice(-ultimo.n);
    v = Object.fromEntries(chiavi.map((k) => [k, (v as Record<string, unknown>)[k]]));
  }
  const copia = v == null ? null : JSON.parse(JSON.stringify(v));
  return { key: pezzi(r.percorso).pop() ?? null, val: () => copia, exists: () => copia != null };
}

export function getDatabase(): Database {
  return { prova: true };
}

export function ref(_db: Database, percorso = ''): DatabaseReference {
  return { percorso, vincoli: [] };
}

export function orderByKey(): Vincolo {
  return { tipo: 'orderByKey' };
}

export function limitToLast(n: number): Vincolo {
  return { tipo: 'limitToLast', n };
}

export function query(r: DatabaseReference, ...vincoli: Vincolo[]): DatabaseReference {
  return { percorso: r.percorso, vincoli: [...r.vincoli, ...vincoli] };
}

export function onValue(r: DatabaseReference, cb: (s: DataSnapshot) => void): Unsubscribe {
  const voce = { r, cb };
  ascoltatori.add(voce);
  const t = setTimeout(() => cb(istantanea(r)), 40);
  return () => {
    clearTimeout(t);
    ascoltatori.delete(voce);
  };
}

export async function get(r: DatabaseReference): Promise<DataSnapshot> {
  return istantanea(r);
}

export function serverTimestamp(): object {
  return { '.sv': 'timestamp' };
}

export async function set(r: DatabaseReference, valore: Valore): Promise<void> {
  const p = pezzi(r.percorso);
  let nodo = radice() as Record<string, unknown>;
  for (const k of p.slice(0, -1)) {
    if (nodo[k] == null || typeof nodo[k] !== 'object') nodo[k] = {};
    nodo = nodo[k] as Record<string, unknown>;
  }
  const ultima = p[p.length - 1];
  const v = valore && typeof valore === 'object' && '.sv' in (valore as object) ? Date.now() : valore;
  if (v == null) delete nodo[ultima];
  else nodo[ultima] = v;
  console.info('[prova] scrittura finta', r.percorso, v);
  ascoltatori.forEach(({ r: a, cb }) => cb(istantanea(a)));
}
