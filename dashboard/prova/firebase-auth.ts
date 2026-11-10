/**
 * SOLO PER LA PROVA IN LOCALE (`DASHBOARD_PROVA=1`, next.config.mjs): prende il posto di `firebase/auth`. Un utente finto già
 * dentro, così la pagina si vede senza il login con Google; nessuna rete.
 */
export type User = { uid: string; email: string | null };
export type Auth = { prova: true };

const utente: User = { uid: 'prova', email: 'prova@locale' };

export function getAuth(): Auth {
  return { prova: true };
}

export function onAuthStateChanged(_auth: Auth, cb: (u: User | null) => void): () => void {
  const t = setTimeout(() => cb(utente), 10);
  return () => clearTimeout(t);
}

export async function signOut(): Promise<void> {
  /* niente da fare nella prova */
}

export async function signInWithPopup(): Promise<{ user: User }> {
  return { user: utente };
}

export class GoogleAuthProvider {}
