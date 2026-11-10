/**
 * SOLO PER LA PROVA IN LOCALE (`DASHBOARD_PROVA=1`, next.config.mjs): prende il posto di `firebase/firestore`. Ogni documento e
 * ogni raccolta risultano vuoti: la prima schermata legge solo il Realtime Database (prova/firebase-database.ts).
 */
export type Firestore = { prova: true };
type Rif = { percorso: string };
type Istantanea = {
  exists: () => boolean;
  data: () => undefined;
  docs: never[];
  empty: boolean;
  size: number;
  forEach: (cb: (d: never) => void) => void;
};

const vuota: Istantanea = { exists: () => false, data: () => undefined, docs: [], empty: true, size: 0, forEach: () => undefined };

export function getFirestore(): Firestore {
  return { prova: true };
}

export function doc(_db: Firestore, ...pezzi: string[]): Rif {
  return { percorso: pezzi.join('/') };
}

export function collection(_db: Firestore, ...pezzi: string[]): Rif {
  return { percorso: pezzi.join('/') };
}

export function query(r: Rif): Rif {
  return r;
}

export function orderBy(): null {
  return null;
}

export function limit(): null {
  return null;
}

export function onSnapshot(_r: Rif, next: (s: Istantanea) => void): () => void {
  const t = setTimeout(() => next(vuota), 40);
  return () => clearTimeout(t);
}

export async function setDoc(): Promise<void> {
  /* niente da scrivere nella prova */
}

export function serverTimestamp(): object {
  return { prova: 'ora del server' };
}
