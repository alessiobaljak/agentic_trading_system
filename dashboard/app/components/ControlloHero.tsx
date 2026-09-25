'use client';

import { etaTesto, semaforoColore, useControllo, type Semaforo } from '../lib/controllo';
import { useGateDoc } from '../lib/gate';
import { durata, numero, pct, quota, segno } from '../lib/viz';
import ControlloLettura from './ControlloLettura';

/**
 * La testa della scheda Controllo (25 set 2026): quello che il proprietario
 * deve vedere in tre secondi dal telefono.
 *
 *   1. una riga di chip: «e' rotto?» (semaforo sistema), «perde?» (semaforo
 *      paper), quanto e' vecchio il controllo, freno globale, DRY_RUN, e chi ha
 *      scritto il documento se non e' stato il bot (il ripiego GitHub/ops vale,
 *      ma i `settings.*` che porta sono quelli del repo, non della VPS);
 *   2. quattro numeri: equity e rendimento · PF vissuto 30 g contro promesso ·
 *      rischio aperto e posizioni col tetto · validate e copertura;
 *   3. la lettura di `salute`, una frase scritta dal bot da regole.
 *
 * Tutto viene dal documento orario `dashboard/controllo` (§1 del contratto),
 * tranne la copertura del registro, che sta nel documento del gate (§2.3):
 * il bot non ricalcola il registro ogni ora, porta solo le validate.
 *
 * Se il documento non c'e' ancora, lo si dice invece di mostrare zeri: il bot
 * lo scrive al primo giro orario dopo il deploy. Se e' fermo da piu' di due
 * ore, il banner rosso rimanda a `ops/heartbeat.md` e al comando ops `stato`:
 * un controllo vecchio non e' «tutto ok», e' «non sappiamo».
 */
function Chip({
  colore,
  etichetta,
  title,
  className = '',
}: {
  colore: string;
  etichetta: string;
  title?: string;
  className?: string;
}) {
  return (
    <span className={`mini-chip chip-semaforo ${className}`} title={title}>
      <span className="dot" style={{ background: colore }} />
      {etichetta}
    </span>
  );
}

function testoSemaforo(s: Semaforo | null | undefined): string {
  if (s === 'verde') return 'ok';
  if (s === 'giallo') return 'avvisi';
  if (s === 'rosso') return 'grave';
  return 'n/d';
}

export default function ControlloHero() {
  const { doc, caricamento, etaS, stato } = useControllo();
  const gate = useGateDoc();

  if (caricamento && !doc) {
    return (
      <div className="panel">
        <p className="muted" style={{ margin: 0 }}>Caricamento del controllo…</p>
      </div>
    );
  }

  if (stato === 'assente' || !doc) {
    return (
      <div className="panel">
        <h2>Controllo</h2>
        <p style={{ margin: 0, fontSize: 13.5 }}>
          Nessun controllo ancora pubblicato: il bot lo scrive al primo giro orario dopo il
          deploy. Se il bot e&apos; vivo da piu&apos; di un&apos;ora e questo avviso resta,
          controlla <code>ops/heartbeat.md</code> e chiedi <code>controllo</code> dalla coda ops.
        </p>
      </div>
    );
  }

  const meta = doc.meta ?? {};
  const salute = doc.salute ?? {};
  const paper = doc.paper ?? {};
  const attivo = doc.learning?.attivo ?? null;
  const registro = gate.doc?.registro ?? null;

  const freno = salute.freno_globale === true;
  const dryRun = salute.dry_run;
  const ripiego = meta.generato_da != null && meta.generato_da !== 'bot';

  // --- tile 1: equity e rendimento ---
  const rend = paper.rendimento_pct ?? null;
  const classeRend = rend == null ? '' : rend >= 0 ? 'good' : 'bad';

  // --- tile 2: PF vissuto 30 g contro promesso ---
  const pf30 = paper.ultimi_30g?.pf ?? null;
  const trade30 = paper.ultimi_30g?.trades ?? null;
  // promesso = media dei last_pf del registro (la stessa che usa il freno);
  // se il controllo non la porta, la stessa media sta nel documento del gate
  const pfPromesso =
    attivo?.freno_globale?.pf_atteso
    ?? gate.doc?.strategie?.promessa_vs_vissuto?.pf_atteso_media_registro
    ?? null;
  const pfPromessoNota = attivo?.freno_globale?.pf_atteso_nota ?? 'media semplice dei last_pf del registro';
  const numeriPiccoli = trade30 != null && trade30 < 20;
  const classePf =
    pf30 == null || pfPromesso == null ? '' : pf30 >= pfPromesso ? 'good' : pf30 >= 1 ? 'warnb' : 'bad';

  // --- tile 3: rischio aperto e posizioni ---
  const rischio = salute.rischio_aperto_pct ?? null;
  const posizioni = salute.posizioni_aperte ?? null;
  const tetto = salute.tetto_posizioni ?? null;
  const tettoAttivo = salute.tetto_posizioni_attivo === true;
  const classeRischio = rischio == null ? '' : rischio > 6 ? 'bad' : rischio > 3 ? 'warnb' : 'good';

  // --- tile 4: validate e copertura ---
  const validate = attivo?.impronta?.validate ?? registro?.validate ?? null;
  const copertura = registro?.copertura ?? null;
  const obiettivo = registro?.obiettivo_copertura ?? null;
  const gateEta = salute.gate_ultimo_giro_eta_s ?? null;
  const classeValidate =
    salute.gate_pronto === false ? 'bad' : salute.gate_stato === 'errore' ? 'bad' : 'accent';

  return (
    <>
      {stato === 'fermo' && (
        <div className="avviso-rosso" role="alert">
          <b>Controllo fermo da {durata(etaS)}.</b> Il bot avrebbe dovuto scriverlo ogni ora e
          il ripiego GitHub ogni due: i numeri qui sotto sono vecchi. Guarda il battito in{' '}
          <code>ops/heartbeat.md</code> e chiedi <code>stato</code> dalla coda ops.
        </div>
      )}

      <div className="panel hero-controllo">
        <div className="chip-row" style={{ marginTop: 0 }}>
          <Chip
            colore={semaforoColore(meta.semaforo_sistema)}
            etichetta={`sistema: ${testoSemaforo(meta.semaforo_sistema)}`}
            title="«E' rotto?»: la peggiore anomalia di famiglia sistema"
          />
          <Chip
            colore={semaforoColore(meta.semaforo_paper)}
            etichetta={`paper: ${testoSemaforo(meta.semaforo_paper)}`}
            title="«Perde?»: la peggiore anomalia di famiglia paper"
          />
          <Chip
            colore={stato === 'ok' ? 'var(--green)' : stato === 'ritardo' ? 'var(--amber)' : 'var(--red)'}
            etichetta={etaTesto(etaS)}
            title={
              meta.generato_at
                ? `scritto ${new Date(Number(meta.generato_at) * 1000).toLocaleString('it-IT')} in ${meta.durata_ms ?? '?'} ms`
                : undefined
            }
          />
          <Chip
            colore={freno ? 'var(--amber)' : 'var(--text-faint)'}
            etichetta={`freno ${freno ? 'ON' : 'OFF'}`}
            title={
              freno
                ? `freno globale acceso${salute.freno_globale_dal ? ` dal ${new Date(Number(salute.freno_globale_dal) * 1000).toLocaleDateString('it-IT')}` : ''}: size ridotta`
                : 'freno globale spento: il paper non e\' in deriva rispetto al promesso'
            }
          />
          <Chip
            colore={dryRun === false ? 'var(--red)' : 'var(--amber)'}
            etichetta={dryRun === false ? 'LIVE' : dryRun == null ? 'DRY_RUN ?' : 'DRY_RUN'}
            title={dryRun == null ? 'il bot non ha pubblicato dry_run' : 'paper trading: nessun denaro vero'}
          />
          {ripiego && (
            <Chip
              colore="var(--purple)"
              etichetta={`scritto dal ripiego (${meta.generato_da})`}
              title={`fonte impostazioni: ${meta.fonte_impostazioni ?? 'n/d'} — i settings letti non sono quelli della VPS`}
            />
          )}
          {(meta.errori ?? []).length > 0 && (
            <Chip
              colore="var(--amber)"
              etichetta={`${(meta.errori ?? []).length} sezioni fallite`}
              title={(meta.errori ?? []).join('\n')}
            />
          )}
        </div>

        <div className="stat-grid" style={{ marginTop: 14 }}>
          <div className={`stat-tile ${classeRend}`}>
            <div className="stat-label">Equity e rendimento</div>
            <div className="stat-value">{numero(paper.equity, 2)}</div>
            <div className="stat-sub">
              {rend != null ? `${segno(rend, 2)}%` : 'rendimento n/d'}
              {paper.equity_iniziale != null && ` da ${numero(paper.equity_iniziale, 0)}`}
              {paper.giorni_paper != null && ` · ${paper.giorni_paper} g di paper`}
            </div>
          </div>

          <div className={`stat-tile ${classePf}`} title={`PF promesso: ${pfPromessoNota}`}>
            <div className="stat-label">PF vissuto 30 g vs promesso</div>
            <div className="stat-value">
              {pf30 != null ? numero(pf30, 2) : trade30 ? 'senza perdite' : '—'}
              <span className="muted" style={{ fontSize: 14, fontWeight: 500 }}>
                {' '}vs {pfPromesso != null ? numero(pfPromesso, 2) : '—'}
              </span>
            </div>
            <div className="stat-sub">
              {trade30 != null ? `${trade30} trade in 30 g` : 'trade 30 g n/d'}
              {numeriPiccoli && ' · numeri piccoli'}
            </div>
          </div>

          <div className={`stat-tile ${classeRischio}`}>
            <div className="stat-label">Rischio aperto e posizioni</div>
            <div className="stat-value">
              {pct(rischio, 1)}
              <span className="muted" style={{ fontSize: 14, fontWeight: 500 }}>
                {' '}· {posizioni ?? '—'}
                {tetto != null && tettoAttivo ? `/${tetto}` : ''} pos.
              </span>
            </div>
            <div className="stat-sub">
              long {pct(salute.rischio_long_pct, 1)} · short {pct(salute.rischio_short_pct, 1)}
              {salute.tetto_direzione_pct != null && ` · tetto ${pct(salute.tetto_direzione_pct, 0)}`}
              {tetto != null && !tettoAttivo && ' · tetto posizioni spento (parita\')'}
            </div>
          </div>

          <div className={`stat-tile ${classeValidate}`}>
            <div className="stat-label">Validate e copertura</div>
            <div className="stat-value">
              {validate ?? '—'}
              <span className="muted" style={{ fontSize: 14, fontWeight: 500 }}>
                {' '}· copertura {quota(copertura, 0)}
                {obiettivo != null && ` su ${quota(obiettivo, 0)}`}
              </span>
            </div>
            <div className="stat-sub">
              gate {salute.gate_stato ?? 'n/d'}
              {salute.gate_modalita && ` (${salute.gate_modalita})`}
              {gateEta != null && ` · ${durata(gateEta)} fa`}
              {salute.gate_pronto === false && ' · NON PRONTO: bot flat'}
            </div>
          </div>
        </div>

        <ControlloLettura sezione={salute} style={{ marginTop: 14 }} />
      </div>
    </>
  );
}
