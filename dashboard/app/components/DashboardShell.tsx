'use client';

import { useEffect, useState } from 'react';
import { onAuthStateChanged, signOut, type User } from 'firebase/auth';
import { getAuthInstance } from '../lib/firebase';

import Archivio, { SEZIONI_ARCHIVIO, type SezioneArchivio } from './Archivio';
import Dettagli, { SCELTE } from './dettagli/Dettagli';
import Azioni from './stock/Azioni';
import Strategie from './strategie/Strategie';

/**
 * Il guscio della dashboard, rifatto il 10 nov 2026 (il proprietario: «mi serve una Dashboard pulita semplice e veloce da leggere
 * che mi permetta in tempo reale di vedere come stanno andando le diverse strategie paper demo etc»; la legge soprattutto dal
 * telefono). Quattro schede in alto, al posto della barra laterale:
 *
 *   strategie — la prima schermata: bot vivo e allarmi, una scheda per strategia (demo e conto vero separati dal paper), le curve
 *               a 100 e G1 demo contro G1 paper giorno per giorno (components/strategie/);
 *   dettagli  — una strategia alla volta, scelta con i pulsanti in cima: riquadri, giorno per giorno, pesi, ultimo ribilancio, il
 *               conto demo, le operazioni degli eventi, G1 demo contro paper giorno per giorno (components/dettagli/; seconda
 *               tornata del 10 nov 2026: «troppo testo», ora numeri e grafici);
 *   azioni    — le azioni, della sessione «trading stock» (components/stock/; la guida è dashboard/GUIDA_SCHEDA_AZIONI.md);
 *   archivio  — il vecchio sistema, fermo dal 13 ottobre 2026: report, controllo, operatività, gate, learning, impostazioni.
 *
 * L'indirizzo ricorda la scheda (#strategie, #dettagli-paper_g1, #archivio-gate…); i vecchi segnalibri (#controllo, #gate, #report…)
 * aprono la loro sezione nell'archivio. Il tema chiaro resta quello di sempre (21 set 2026); lo scuro si accende dal pulsante in
 * alto e si ricorda su questo dispositivo.
 */
type Scheda = 'strategie' | 'dettagli' | 'azioni' | 'archivio';

/** Le schede in alto. «Azioni» è della sessione «trading stock» (components/stock/, dashboard/GUIDA_SCHEDA_AZIONI.md). */
const SCHEDE: { id: Scheda; nome: string }[] = [
  { id: 'strategie', nome: 'Strategie' },
  { id: 'dettagli', nome: 'Dettagli' },
  { id: 'azioni', nome: 'Azioni' },
  { id: 'archivio', nome: 'Archivio' },
];

/** I vecchi hash (segnalibri, link nelle issue) → la sezione dell'archivio. */
const VECCHI_HASH: Record<string, SezioneArchivio> = {
  report: 'report',
  controllo: 'controllo',
  operativita: 'operativita',
  gate: 'gate',
  learning: 'learning',
  impostazioni: 'impostazioni',
  panoramica: 'controllo',
  sentiment: 'controllo',
  ricerca: 'gate',
  apprendimento: 'learning',
};

function leggiHash(h: string): { scheda: Scheda; sezione: SezioneArchivio | null; ramo?: string } {
  if (h === 'dettagli') return { scheda: 'dettagli', sezione: null };
  if (h.startsWith('dettagli-')) {
    const r = h.slice('dettagli-'.length);
    if (SCELTE.some((x) => x.ramo === r)) return { scheda: 'dettagli', sezione: null, ramo: r };
  }
  if (h === 'archivio') return { scheda: 'archivio', sezione: null };
  if (h === 'azioni') return { scheda: 'azioni', sezione: null };
  if (h.startsWith('archivio-')) {
    const s = h.slice('archivio-'.length);
    if (SEZIONI_ARCHIVIO.some((x) => x.id === s)) return { scheda: 'archivio', sezione: s as SezioneArchivio };
  }
  if (h in VECCHI_HASH) return { scheda: 'archivio', sezione: VECCHI_HASH[h] };
  return { scheda: 'strategie', sezione: null };
}

function useTema(): [string, () => void] {
  const [tema, setTema] = useState('chiaro');
  useEffect(() => {
    setTema(document.documentElement.dataset.theme === 'dark' ? 'scuro' : 'chiaro');
  }, []);
  const cambia = () => {
    const nuovo = tema === 'scuro' ? 'chiaro' : 'scuro';
    setTema(nuovo);
    if (nuovo === 'scuro') document.documentElement.dataset.theme = 'dark';
    else delete document.documentElement.dataset.theme;
    try {
      localStorage.setItem('tema', nuovo);
    } catch {
      /* senza memoria del browser il tema vale solo per questa visita */
    }
  };
  return [tema, cambia];
}

export default function DashboardShell() {
  const [scheda, setScheda] = useState<Scheda>('strategie');
  const [sezione, setSezione] = useState<SezioneArchivio>('controllo');
  const [ramo, setRamo] = useState<string>('demo_binance');
  const [user, setUser] = useState<User | null>(null);
  const [tema, cambiaTema] = useTema();

  useEffect(() => {
    const sync = () => {
      const h = window.location.hash.replace('#', '');
      const letto = leggiHash(h);
      setScheda(letto.scheda);
      if (letto.sezione) setSezione(letto.sezione);
      if (letto.ramo) setRamo(letto.ramo);
      if (letto.ramo || letto.scheda !== 'strategie') window.scrollTo({ top: 0 });
      // un vecchio segnalibro si riscrive con il nome nuovo
      if (h in VECCHI_HASH) window.history.replaceState(null, '', `#archivio-${VECCHI_HASH[h]}`);
    };
    sync();
    window.addEventListener('hashchange', sync);
    return () => window.removeEventListener('hashchange', sync);
  }, []);

  useEffect(() => {
    try {
      const unsub = onAuthStateChanged(getAuthInstance(), (u) => setUser(u));
      return () => unsub();
    } catch {
      /* auth non inizializzata: ignora, il gate lo gestisce a monte */
    }
  }, []);

  const vai = (s: Scheda) => {
    setScheda(s);
    window.location.hash = s === 'archivio' ? `archivio-${sezione}` : s === 'dettagli' ? `dettagli-${ramo}` : s;
    window.scrollTo({ top: 0 });
  };
  const vaiRamo = (r: string) => {
    setRamo(r);
    window.history.replaceState(null, '', `#dettagli-${r}`);
  };
  const vaiSezione = (s: SezioneArchivio) => {
    setSezione(s);
    window.location.hash = `archivio-${s}`;
  };

  return (
    <div className="cr-guscio">
      <header className="cr-testa">
        <div className="cr-marchio">
          <span className="cr-logo" aria-hidden="true">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"
              strokeLinejoin="round">
              <path d="M3 15c3 0 3-6 6-6s3 6 6 6 3-4 6-4" />
            </svg>
          </span>
          <div>
            Trading bot
            <small>crypto · Binance futures · niente soldi veri</small>
          </div>
        </div>

        <nav className="cr-schede" role="tablist" aria-label="schede">
          {SCHEDE.map((s) => (
            <button key={s.id} role="tab" aria-selected={scheda === s.id} onClick={() => vai(s.id)}>
              {s.nome}
            </button>
          ))}
        </nav>

        <div className="cr-utente">
          <button className="btn btn-ghost" onClick={cambiaTema} aria-label="cambia tema chiaro o scuro">
            {tema === 'scuro' ? 'Chiaro' : 'Scuro'}
          </button>
          {user && (
            <>
              <span className="cr-email" title={user.email ?? user.uid}>{user.email ?? user.uid}</span>
              <button className="btn btn-ghost" onClick={() => signOut(getAuthInstance())}>Esci</button>
            </>
          )}
        </div>
      </header>

      <main className="cr-corpo" key={scheda}>
        {scheda === 'strategie' && <Strategie />}
        {scheda === 'dettagli' && <Dettagli ramo={ramo} onRamo={vaiRamo} />}
        {scheda === 'azioni' && <Azioni />}
        {scheda === 'archivio' && <Archivio sezione={sezione} onSezione={vaiSezione} />}
      </main>
    </div>
  );
}
