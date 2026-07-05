'use client';

/**
 * AuthGate — secondo strato di sicurezza (oltre alla protezione Vercel).
 *
 * Le security rules di Firestore/RTDB richiedono un utente autenticato per
 * leggere lo stato e per scrivere kill switch / risk settings. Questo gate fa
 * il login con Google e mostra i contenuti solo a sessione autenticata.
 *
 * Hardening consigliato: in firebase/firestore.rules e database.rules.json
 * blocca l'accesso al TUO solo UID (vedi commenti in quei file).
 */
import { useEffect, useState } from 'react';
import {
  GoogleAuthProvider,
  onAuthStateChanged,
  signInWithPopup,
  type User,
} from 'firebase/auth';
import { getAuthInstance } from '../lib/firebase';

export default function AuthGate({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      const unsub = onAuthStateChanged(getAuthInstance(), (u) => {
        setUser(u);
        setLoading(false);
      });
      return () => unsub();
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
      setLoading(false);
    }
  }, []);

  async function login() {
    setError(null);
    const auth = getAuthInstance();
    const provider = new GoogleAuthProvider();
    try {
      await signInWithPopup(auth, provider);
    } catch (e: unknown) {
      const code = (e as { code?: string })?.code ?? '';
      if (code === 'auth/popup-blocked') {
        setError(
          'Il browser ha bloccato il popup di accesso. Clicca l’icona "popup bloccato" ' +
            'nella barra degli indirizzi e consenti i popup per questo sito, poi riprova.',
        );
      } else if (code === 'auth/popup-closed-by-user' || code === 'auth/cancelled-popup-request') {
        setError('Accesso annullato. Riprova.');
      } else {
        setError(e instanceof Error ? e.message : String(e));
      }
    }
  }

  if (loading) {
    return <div className="notice">Caricamento…</div>;
  }

  if (!user) {
    return (
      <div className="notice">
        <h2 style={{ marginTop: 0 }}>Accesso richiesto</h2>
        <p>Accedi per vedere lo stato del bot e usare i controlli di rischio.</p>
        <button onClick={login} className="btn">
          Accedi con Google
        </button>
        {error && (
          <p className="muted" style={{ marginTop: 12 }}>
            {error}
          </p>
        )}
      </div>
    );
  }

  // La barra utente/logout ora vive nel topbar dello shell (DashboardShell):
  // qui AuthGate resta puro gate d'accesso, senza duplicare l'header.
  return <>{children}</>;
}
