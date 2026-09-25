'use client';

import { useEffect, useMemo, useState, type ReactNode } from 'react';
import { onAuthStateChanged, signOut, type User } from 'firebase/auth';
import { getAuthInstance } from '../lib/firebase';
import { lista, useControllo, type Manca } from '../lib/controllo';
import { useGateDoc } from '../lib/gate';
import { durata } from '../lib/viz';

import BotStatus from './BotStatus';
import ControlloAnomalie from './ControlloAnomalie';
import ControlloHero from './ControlloHero';
import ControlloLettura from './ControlloLettura';
import ControlloPaper from './ControlloPaper';
import ControlloSezione from './ControlloSezione';
import OperativitaTab from './OperativitaTab';
import StrategyWeights from './StrategyWeights';
import GateMaturazione from './GateMaturazione';
import RiskControl from './RiskControl';
import KillSwitch from './KillSwitch';
import TopVitals from './TopVitals';
import ReconcilerStatus from './ReconcilerStatus';
import SupervisorDecisions from './SupervisorDecisions';
import GateAutopsy from './GateAutopsy';
import GateFunnel from './GateFunnel';
import GateEvolution from './GateEvolution';
import GateCervello from './GateCervello';
import StrategieOperate from './StrategieOperate';
import LearningAttivoMisurato from './LearningAttivoMisurato';
import LearningMisurato from './LearningMisurato';

/**
 * Il guscio della dashboard (25 set 2026): cinque schede, e la prima e' il
 * CONTROLLO — quello che il proprietario apre dal telefono la mattina.
 *
 *   controllo    — «e' rotto? perde?»: semafori, anomalie, paper, learning e
 *                  gate in breve, tutto dal documento orario del bot;
 *   operativita  — grafico, posizioni aperte, trade chiusi (tempo reale);
 *   gate         — dentro il gate: imbuto, maturazione, cervello, supervisore,
 *                  evoluzione, autopsia, le strategie operate;
 *   learning     — cosa cambia le decisioni ORA e cosa e' solo misurato;
 *   impostazioni — rischio, kill switch, riconciliazione (solo live).
 *
 * Sono sparite panoramica, ricerca, strategie, sentiment e apprendimento: i
 * loro pannelli o vivono nel controllo (calcolati dal bot una volta, non da
 * dieci componenti ognuno a modo suo) o stanno nelle schede gate/learning. I
 * vecchi hash nei segnalibri vengono girati sulla scheda nuova.
 */
type TabId = 'controllo' | 'operativita' | 'gate' | 'learning' | 'impostazioni';
type NavId = Exclude<TabId, 'impostazioni'>;

/** I vecchi hash (segnalibri, link nelle issue) → scheda nuova. */
const VECCHI_HASH: Record<string, TabId> = {
  panoramica: 'controllo',
  sentiment: 'controllo',
  ricerca: 'gate',
  strategie: 'gate',
  apprendimento: 'learning',
};

/* --- icone (inline SVG, stroke = currentColor) ---------------------------- */
function Icon({ id }: { id: TabId }) {
  const p: Record<TabId, ReactNode> = {
    // controllo: uno scudo con la spunta — «e' tutto a posto?»
    controllo: (
      <>
        <path d="M12 3l7 3v5c0 4.5-3 8.5-7 10-4-1.5-7-5.5-7-10V6l7-3z" />
        <path d="M9 12l2 2 4-4" />
      </>
    ),
    operativita: <path d="M3 12h4l3 7 4-14 3 7h4" />,
    // gate: un imbuto — le candidate entrano larghe ed escono strette
    gate: (
      <>
        <path d="M4 5h16l-6 7v6l-4 2v-8L4 5z" />
      </>
    ),
    learning: (
      <>
        <path d="M12 3l9 5-9 5-9-5 9-5z" />
        <path d="M21 8v5" />
        <path d="M7 10.5V15c0 1.5 2.5 3 5 3s5-1.5 5-3v-4.5" />
      </>
    ),
    impostazioni: (
      <>
        <circle cx="12" cy="12" r="3" />
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
      </>
    ),
  };
  return (
    <svg
      className="nav-ico"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.9"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {p[id]}
    </svg>
  );
}

const META: Record<TabId, { label: string; title: string; intro: string }> = {
  controllo: {
    label: 'Controllo',
    title: 'Controllo',
    intro: 'Il controllo orario scritto dal bot: e\' rotto? perde? cosa e\' cambiato.',
  },
  operativita: {
    label: 'Operatività',
    title: 'Operatività',
    intro: 'Posizioni aperte e trade chiusi (con verdetto sul trailing), in tempo reale.',
  },
  gate: {
    label: 'Gate',
    title: 'Gate',
    intro:
      'Dentro il gate: dove muoiono le candidate, come matura il registro e quali '
      + 'strategie stanno operando davvero.',
  },
  learning: {
    label: 'Learning',
    title: 'Learning',
    intro: 'Cosa cambia le decisioni adesso (attivo) e cosa e\' solo misurato.',
  },
  impostazioni: {
    label: 'Impostazioni',
    title: 'Impostazioni · Rischio',
    intro: 'Leva e rischio entro i tetti di sicurezza applicati dal bot; kill switch.',
  },
};

const NAV: NavId[] = ['controllo', 'operativita', 'gate', 'learning'];

function isTab(v: string): v is TabId {
  return v in META;
}

/* ------------------------------------------------ la scheda Controllo ---- */
function ControlloTab() {
  const { doc, stato } = useControllo();
  const gate = useGateDoc();
  const learning = doc?.learning ?? null;
  const attivo = learning?.attivo ?? null;
  const cambiamenti = lista<string>(attivo?.cambiamenti_24h);
  const manca = lista<Manca>(doc?.manca);
  const salute = doc?.salute ?? null;

  return (
    <>
      <ControlloHero />
      <BotStatus />
      <ControlloAnomalie />
      {stato !== 'assente' && doc && (
        <>
          <ControlloPaper />

          <ControlloSezione
            titolo="Learning in breve"
            computedAt={learning?.computed_at}
            errore={learning?.errore}
            riassunto={
              cambiamenti.length
                ? `${cambiamenti.length} cambiamenti in 24 h`
                : 'nessun cambiamento in 24 h'
            }
          >
            <ControlloLettura sezione={learning} style={{ marginTop: 0 }} />
            <div className="sotto-titolo" style={{ marginTop: 12 }}>
              Cosa ha cambiato decisione nelle ultime 24 h
            </div>
            {cambiamenti.length === 0 ? (
              <p className="muted" style={{ margin: 0, fontSize: 12.5 }}>
                Nessun pezzo del learning ha cambiato decisione: freno, panchina, cooldown, keep e
                validate sono come nel controllo precedente.
              </p>
            ) : (
              <ul className="lista-grigia">
                {cambiamenti.map((c, i) => (
                  <li key={i}>{c}</li>
                ))}
              </ul>
            )}
            <p className="muted" style={{ margin: '10px 0 0', fontSize: 12 }}>
              Il dettaglio (freno, panchina, deriva, calibrazione, referti) sta nella scheda
              Learning.
            </p>
          </ControlloSezione>

          <ControlloSezione
            titolo="Gate in breve"
            aggiornatoS={salute?.gate_ultimo_giro_eta_s ?? gate.etaS}
            riassunto={salute?.gate_stato ?? gate.doc?.meta?.stato ?? 'n/d'}
          >
            <p className="riga-paper" style={{ marginTop: 0 }}>
              ultimo giro{' '}
              {salute?.gate_ultimo_giro_eta_s != null
                ? `${durata(salute.gate_ultimo_giro_eta_s)} fa`
                : gate.etaS != null
                  ? `${durata(gate.etaS)} fa`
                  : 'mai visto'}
              {' '}· modalità <b>{salute?.gate_modalita ?? gate.doc?.meta?.modalita ?? 'n/d'}</b>
              {' '}· stato <b>{salute?.gate_stato ?? gate.doc?.meta?.stato ?? 'n/d'}</b>
              {gate.doc?.meta?.fase && gate.doc.meta.stato === 'in_corso' && ` (fase ${gate.doc.meta.fase})`}
              {' '}· validate{' '}
              <b>{attivo?.impronta?.validate ?? gate.doc?.registro?.validate ?? '—'}</b>
              {gate.doc?.registro?.validate_delta_giro != null
                && gate.doc.registro.validate_delta_giro !== 0
                && ` (${gate.doc.registro.validate_delta_giro > 0 ? '+' : ''}${gate.doc.registro.validate_delta_giro} nel giro)`}
              {salute?.gate_pronto === false && (
                <span style={{ color: 'var(--red)' }}> · NON PRONTO: il bot resta flat</span>
              )}
              {gate.doc?.meta?.stato === 'errore' && gate.doc.meta.errore && (
                <span style={{ color: 'var(--red)' }}> · errore: {gate.doc.meta.errore}</span>
              )}
            </p>
            <p className="muted" style={{ margin: '8px 0 0', fontSize: 12 }}>
              Imbuto, maturazione, cervello e strategie operate stanno nella scheda Gate.
            </p>
          </ControlloSezione>

          <ControlloSezione
            titolo="Cosa manca"
            computedAt={doc.meta?.generato_at}
            riassunto={manca.length ? `${manca.length} evidenze non disponibili qui` : undefined}
          >
            {manca.length === 0 ? (
              <p className="muted" style={{ margin: 0, fontSize: 12.5 }}>
                Il controllo non dichiara evidenze mancanti.
              </p>
            ) : (
              <ul className="lista-grigia">
                {manca.map((m, i) => (
                  <li key={i}>
                    <b>{m.evidenza}</b>
                    {m.perche && <> — {m.perche}</>}
                    {m.come_avere && <span className="muted"> · come averla: {m.come_avere}</span>}
                  </li>
                ))}
              </ul>
            )}
          </ControlloSezione>
        </>
      )}
    </>
  );
}

export default function DashboardShell() {
  const [tab, setTab] = useState<TabId>('controllo');
  const [user, setUser] = useState<User | null>(null);
  const [collapsed, setCollapsed] = useState(false);

  // deep-link + persistenza al refresh via hash (#gate); i vecchi hash vengono
  // girati sulla scheda nuova e riscritti nella barra degli indirizzi
  useEffect(() => {
    const sync = () => {
      const h = window.location.hash.replace('#', '');
      if (isTab(h)) {
        setTab(h);
      } else if (h in VECCHI_HASH) {
        const nuovo = VECCHI_HASH[h];
        setTab(nuovo);
        window.history.replaceState(null, '', `#${nuovo}`);
      } else if (!h) {
        setTab('controllo');
      }
    };
    sync();
    window.addEventListener('hashchange', sync);
    return () => window.removeEventListener('hashchange', sync);
  }, []);

  // preferenza sidebar compressa
  useEffect(() => {
    try {
      setCollapsed(localStorage.getItem('sidebar_collapsed') === '1');
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    try {
      const unsub = onAuthStateChanged(getAuthInstance(), (u) => setUser(u));
      return () => unsub();
    } catch {
      /* auth non inizializzata: ignora, il gate lo gestisce a monte */
    }
  }, []);

  const select = (id: TabId) => {
    setTab(id);
    if (typeof window !== 'undefined') window.location.hash = id;
  };

  const toggleCollapse = () => {
    setCollapsed((c) => {
      const next = !c;
      try {
        localStorage.setItem('sidebar_collapsed', next ? '1' : '0');
      } catch {
        /* ignore */
      }
      return next;
    });
  };

  const current = useMemo(() => META[tab], [tab]);

  return (
    <div className="app-shell">
      <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
        <div className="sidebar-brand">
          <span className="logo" aria-hidden="true">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M3 15c3 0 3-6 6-6s3 6 6 6 3-4 6-4" />
            </svg>
          </span>
          <span className="brand-text">
            Trading bot
            <span className="brand-sub">crypto futures · paper</span>
          </span>
        </div>

        <button className="sidebar-toggle" onClick={toggleCollapse} title={collapsed ? 'Espandi' : 'Comprimi'} aria-label="comprimi/espandi menu">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ transform: collapsed ? 'rotate(180deg)' : 'none' }}>
            <path d="M15 18l-6-6 6-6" />
          </svg>
          <span className="toggle-label">Comprimi</span>
        </button>

        <div className="nav-section-label">Navigazione</div>
        <nav className="sidebar-nav" role="tablist">
          {NAV.map((id) => (
            <button
              key={id}
              role="tab"
              aria-selected={tab === id}
              title={META[id].label}
              className={`nav-item ${tab === id ? 'active' : ''}`}
              onClick={() => select(id)}
            >
              <Icon id={id} />
              <span className="nav-label">{META[id].label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button
            role="tab"
            aria-selected={tab === 'impostazioni'}
            title="Impostazioni"
            className={`nav-item ${tab === 'impostazioni' ? 'active' : ''}`}
            onClick={() => select('impostazioni')}
          >
            <Icon id="impostazioni" />
            <span className="nav-label">Impostazioni</span>
          </button>

          <span className="dry-pill" title="Paper trading (DRY_RUN): nessun denaro vero">
            <span className="dot" style={{ background: 'var(--amber)' }} />
            <span className="dry-text">DRY_RUN · paper</span>
          </span>
          {user && (
            <>
              <span className="sidebar-user" title={user.email ?? user.uid}>
                {user.email ?? user.uid}
              </span>
              <button
                onClick={() => signOut(getAuthInstance())}
                className="btn btn-ghost"
                style={{ padding: '6px 12px', fontSize: 12 }}
              >
                <span className="nav-label">Esci</span>
                <span aria-hidden="true" style={{ display: collapsed ? 'inline' : 'none' }}>⎋</span>
              </button>
            </>
          )}
        </div>
      </aside>

      <main className="main">
        <header className="main-top">
          <div>
            <div className="page-title">{current.title}</div>
            <span className="page-sub">{current.intro}</span>
          </div>
          <div className="top-vitals">
            <TopVitals />
            <KillSwitch variant="button" />
          </div>
        </header>

        <div className="grid" key={tab} style={{ marginTop: 16 }}>
          {tab === 'controllo' && <ControlloTab />}

          {tab === 'operativita' && <OperativitaTab />}

          {tab === 'gate' && (
            <>
              <GateFunnel />
              <GateMaturazione />
              <GateCervello />
              <SupervisorDecisions />
              <GateEvolution />
              <GateAutopsy />
              <StrategieOperate />
            </>
          )}

          {tab === 'learning' && (
            <>
              <LearningAttivoMisurato />
              <StrategyWeights />
              <LearningMisurato />
            </>
          )}

          {tab === 'impostazioni' && (
            <>
              <RiskControl />
              <KillSwitch />
              <ReconcilerStatus />
            </>
          )}
        </div>
      </main>
    </div>
  );
}
