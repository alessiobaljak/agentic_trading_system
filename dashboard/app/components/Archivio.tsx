'use client';

import { lista, useControllo, type Manca } from '../lib/controllo';
import { useGateDoc } from '../lib/gate';
import { durata } from '../lib/viz';

import BacklogSi from './BacklogSi';
import ReportGiornaliero from './ReportGiornaliero';
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
 * L'ARCHIVIO (10 nov 2026): le schede del vecchio sistema (gate, ottimizzatore, vecchio bot e il suo paper), fermo dal 13 ottobre
 * 2026 (`ops/gate_fermo`). Spostate qui dalla barra laterale di prima, senza cancellarne nessuna e con gli stessi componenti:
 *
 *   report       — il report giornaliero (fermo dall'11 ottobre);
 *   controllo    — il controllo orario: semafori, anomalie, paper, learning e gate in breve;
 *   operativita  — posizioni aperte e trade chiusi del vecchio bot;
 *   gate         — imbuto, maturazione, cervello, supervisore, evoluzione, autopsia, strategie operate;
 *   learning     — cosa cambiava le decisioni e cosa era solo misurato;
 *   impostazioni — rischio, kill switch, riconciliazione.
 *
 * In cima lo stato del vecchio bot (TopVitals) e il pulsante STOP del vecchio sistema (KillSwitch): prima stavano in alto in ogni
 * scheda. Il kill switch chiude le posizioni del vecchio executor: non ferma il paper delle strategie nuove né il demo (bot/main.py),
 * che hanno i loro interruttori e, per il demo, il pulsante «chiudi tutto» nella prima schermata.
 */
export type SezioneArchivio = 'report' | 'controllo' | 'operativita' | 'gate' | 'learning' | 'impostazioni';

export const SEZIONI_ARCHIVIO: { id: SezioneArchivio; nome: string; intro: string }[] = [
  { id: 'controllo', nome: 'Controllo', intro: 'Il controllo orario scritto dal bot: era rotto? perdeva? cosa era cambiato.' },
  { id: 'report', nome: 'Report', intro: 'Il report giornaliero del vecchio sistema, sempre nella stessa forma (fermo dall\'11 ottobre).' },
  { id: 'operativita', nome: 'Operatività', intro: 'Posizioni aperte e trade chiusi del vecchio bot (con il verdetto sul trailing).' },
  { id: 'gate', nome: 'Gate', intro: 'Dentro il gate: dove morivano le candidate, come maturava il registro, le strategie operate.' },
  { id: 'learning', nome: 'Learning', intro: 'Cosa cambiava le decisioni (attivo) e cosa era solo misurato.' },
  { id: 'impostazioni', nome: 'Impostazioni', intro: 'Leva e rischio del vecchio bot entro i tetti di sicurezza; kill switch; riconciliazione.' },
];

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
      <BacklogSi />
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

export default function Archivio({ sezione, onSezione }: {
  sezione: SezioneArchivio;
  onSezione: (s: SezioneArchivio) => void;
}) {
  const corrente = SEZIONI_ARCHIVIO.find((s) => s.id === sezione) ?? SEZIONI_ARCHIVIO[0];
  return (
    <>
      <div className="cr-archivio-testa">
        <div className="warn" style={{ marginTop: 0 }}>
          <b>Il vecchio sistema è fermo dal 13 ottobre 2026</b> (gate, ottimizzatore, vecchio bot): queste pagine restano da consultare.
          Le strategie in corso sono nella scheda Strategie.
        </div>
        <div className="top-vitals">
          <TopVitals />
          <KillSwitch variant="button" />
        </div>
        <nav className="cr-sottoschede" role="tablist" aria-label="sezioni dell'archivio">
          {SEZIONI_ARCHIVIO.map((s) => (
            <button key={s.id} role="tab" aria-selected={s.id === corrente.id} onClick={() => onSezione(s.id)}>
              {s.nome}
            </button>
          ))}
        </nav>
        <p className="cr-sotto" style={{ margin: 0 }}>{corrente.intro}</p>
      </div>

      <div className="grid" key={corrente.id}>
        {corrente.id === 'report' && <ReportGiornaliero />}

        {corrente.id === 'controllo' && <ControlloTab />}

        {corrente.id === 'operativita' && <OperativitaTab />}

        {corrente.id === 'gate' && (
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

        {corrente.id === 'learning' && (
          <>
            <LearningAttivoMisurato />
            <StrategyWeights />
            <LearningMisurato />
          </>
        )}

        {corrente.id === 'impostazioni' && (
          <>
            <RiskControl />
            <KillSwitch />
            <ReconcilerStatus />
          </>
        )}
      </div>
    </>
  );
}
