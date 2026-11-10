'use client';

import { useEffect, useState } from 'react';
import { onAuthStateChanged, signOut, type User } from 'firebase/auth';
import { getAuthInstance } from '../lib/firebase';
import { STRATEGIE } from '../lib/strategie';
import { SEZIONI_ARCHIVIO } from './Archivio';
import { AREE, type Area } from './aree';

/**
 * Il guscio della PLANCIA (terza tornata, 10 nov 2026; il proprietario: «la dashboard si chiama Trading Bot (magari trova un altro
 * nome). In alto vedrei solo Crypto e Stock o altre che magari creiamo in futuro, quando clicchi su una si apre la schermata
 * principale e sulla sinistra hai il menu con i diversi entry point per la singola dashboard»).
 *
 *   in alto    — il nome, le aree (components/aree.ts: Crypto, Azioni), il tema, l'uscita;
 *   a sinistra — il menu delle pagine dell'area scelta; il pulsante ☰ lo nasconde e lo rimette (sul computer la scelta si ricorda
 *                in questo browser; sul telefono è un cassetto che si apre sopra la pagina);
 *   al centro  — la testata dell'area (per Crypto: bot vivo e allarmi del demo) e la pagina.
 *
 * Gli indirizzi sono `#<area>/<pagina>/<resto…>` (#crypto/strategie, #crypto/dettagli/g1demo, #crypto/archivio/gate,
 * #azioni/strategie). I vecchi segnalibri (#strategie, #dettagli, #dettagli-paper_g1, #archivio-gate, #gate, #controllo, #report,
 * #azioni…) aprono la pagina giusta e l'indirizzo si riscrive. Il tema chiaro resta quello di sempre (21 set 2026); lo scuro si accende
 * dal pulsante in alto e si ricorda su questo dispositivo.
 */

/** I vecchi hash del vecchio sistema → la sezione dell'archivio. */
const VECCHI_ARCHIVIO: Record<string, string> = {
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

/** Un vecchio indirizzo (prima delle aree) → il percorso nuovo; null se non è un vecchio indirizzo. */
function daVecchio(h: string): string[] | null {
  if (!h || h === 'strategie') return ['crypto', 'strategie'];
  if (h === 'dettagli') return ['crypto', 'dettagli'];
  if (h.startsWith('dettagli-')) {
    const def = STRATEGIE.find((s) => s.ramo === h.slice('dettagli-'.length));
    return ['crypto', 'dettagli', ...(def ? [def.pagina] : [])];
  }
  if (h === 'archivio') return ['crypto', 'archivio'];
  if (h.startsWith('archivio-') && SEZIONI_ARCHIVIO.some((s) => s.id === h.slice('archivio-'.length))) {
    return ['crypto', 'archivio', h.slice('archivio-'.length)];
  }
  if (h in VECCHI_ARCHIVIO) return ['crypto', 'archivio', VECCHI_ARCHIVIO[h]];
  return null;
}

/** L'indirizzo → area, pagina e resto (con l'area e la pagina di partenza se mancano o non esistono). */
function leggi(hash: string): { area: Area; pagina: string; resto: string[]; riscrivi: boolean } {
  const h = decodeURIComponent(hash.replace(/^#\/?/, ''));
  const vecchio = h.includes('/') ? null : AREE.some((a) => a.id === h) ? null : daVecchio(h);
  const parti = (vecchio ?? h.split('/')).filter(Boolean);
  const area = AREE.find((a) => a.id === parti[0]) ?? AREE[0];
  const pagina = area.pagine.find((p) => p.id === parti[1]) ?? area.pagine[0];
  const resto = pagina.id === parti[1] ? parti.slice(2) : [];
  const giusto = [area.id, pagina.id, ...resto].join('/');
  return { area, pagina: pagina.id, resto, riscrivi: giusto !== h };
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

function IconaMenu({ aperto }: { aperto: boolean }) {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"
      aria-hidden="true">
      {aperto ? <path d="M6 6l12 12M18 6L6 18" /> : <path d="M4 7h16M4 12h16M4 17h16" />}
    </svg>
  );
}

export default function DashboardShell() {
  const [percorso, setPercorso] = useState(() => leggi(''));
  const [menuAperto, setMenuAperto] = useState(false);       // il cassetto del telefono
  const [menuNascosto, setMenuNascosto] = useState(false);   // il menu a sinistra del computer (il proprietario: «a scomparsa»)
  const [user, setUser] = useState<User | null>(null);
  const [tema, cambiaTema] = useTema();

  useEffect(() => {
    const sync = () => {
      const p = leggi(window.location.hash);
      setPercorso(p);
      if (p.riscrivi) window.history.replaceState(null, '', `#${[p.area.id, p.pagina, ...p.resto].join('/')}`);
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

  // il menu del computer nascosto o no: si ricorda in questo browser
  useEffect(() => {
    try {
      setMenuNascosto(localStorage.getItem('menu_nascosto') === '1');
    } catch {
      /* senza memoria del browser il menu parte aperto */
    }
  }, []);
  const telefono = () => typeof window !== 'undefined' && window.matchMedia('(max-width: 760px)').matches;
  const cambiaMenu = () => {
    if (telefono()) {
      setMenuAperto((a) => !a);
      return;
    }
    setMenuNascosto((n) => {
      try {
        localStorage.setItem('menu_nascosto', n ? '0' : '1');
      } catch {
        /* vale solo per questa visita */
      }
      return !n;
    });
  };

  // il menu del telefono si chiude con Esc
  useEffect(() => {
    if (!menuAperto) return undefined;
    const esc = (e: KeyboardEvent) => { if (e.key === 'Escape') setMenuAperto(false); };
    window.addEventListener('keydown', esc);
    return () => window.removeEventListener('keydown', esc);
  }, [menuAperto]);

  const { area, pagina, resto } = percorso;
  const corrente = area.pagine.find((p) => p.id === pagina) ?? area.pagine[0];
  const Contenuto = corrente.Contenuto;
  const Testata = area.Testata;

  const apri = (parti: string[]) => {
    setMenuAperto(false);
    window.location.hash = parti.join('/');
    window.scrollTo({ top: 0 });
  };
  const vai = (nuovoResto: string[], opzioni?: { sostituisci?: boolean }) => {
    const parti = [area.id, corrente.id, ...nuovoResto.filter(Boolean)];
    if (opzioni?.sostituisci) {
      window.history.replaceState(null, '', `#${parti.join('/')}`);
      setPercorso(leggi(`#${parti.join('/')}`));
    } else {
      window.location.hash = parti.join('/');
    }
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
            Plancia
            <small>crypto e azioni · niente soldi veri</small>
          </div>
        </div>

        <button type="button" className="cr-menu-pulsante" aria-controls="menu-pagine" onClick={cambiaMenu}
          aria-label={menuNascosto ? 'mostra il menu delle pagine' : 'nascondi o mostra il menu delle pagine'}
          title={menuNascosto ? 'Mostra il menu' : 'Nascondi il menu'}>
          <IconaMenu aperto={menuAperto} />
          <span>{corrente.nome}</span>
        </button>

        <nav className="cr-schede cr-aree" role="tablist" aria-label="aree">
          {AREE.map((a) => (
            <button key={a.id} role="tab" aria-selected={a.id === area.id} onClick={() => apri([a.id, a.pagine[0].id])}>
              {a.nome}
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

      <div className={`cr-telaio${menuNascosto ? ' senza-menu' : ''}`}>
        {menuAperto && <div className="cr-velo" onClick={() => setMenuAperto(false)} aria-hidden="true" />}
        <nav id="menu-pagine" className={`cr-menu${menuAperto ? ' aperto' : ''}`} aria-label={`pagine di ${area.nome}`}>
          <div className="cr-menu-titolo">
            {area.nome}
            <button type="button" className="cr-menu-chiudi" onClick={() => setMenuAperto(false)} aria-label="chiudi il menu">
              <IconaMenu aperto />
            </button>
          </div>
          {area.pagine.map((p) => (
            <a key={p.id} href={`#${area.id}/${p.id}`} className="cr-menu-voce" aria-current={p.id === corrente.id ? 'page' : undefined}
              onClick={(e) => { e.preventDefault(); apri([area.id, p.id]); }}>
              {p.icona}
              <span>{p.nome}</span>
            </a>
          ))}
        </nav>

        <main className="cr-corpo" key={`${area.id}/${corrente.id}`}>
          {Testata && <Testata />}
          <Contenuto resto={resto} vai={vai} />
        </main>
      </div>
    </div>
  );
}
