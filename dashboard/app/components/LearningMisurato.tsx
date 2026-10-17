'use client';

import { type ReactNode } from 'react';
import type { Controllo } from '../lib/controllo';
import { STATO, durata, formatta, numero, quando, quota } from '../lib/viz';
import { Fonte } from './GateCervello';

/**
 * LEARNING «SOLO MISURATO» — cio' che il sistema osserva ma NON usa per decidere
 * (25 set 2026).
 *
 * E' la meta' destra del pannello `LearningAttivoMisurato`: la separazione
 * attivo/misurato e' la stessa del contratto (docs/controllo_schema.md §1.4) ed e'
 * la risposta alla domanda «il learning sta facendo qualcosa?». Qui la risposta
 * e' sempre «guarda, non tocca»: deriva per coppia, calibrazione, verdetti del
 * trailing, referti, selettore, ombra e ipotesi dell'AI, memoria notturna.
 *
 * Il default export rende `null` perche' la colonna vive dentro il pannello a
 * due colonne (un pannello separato le metterebbe una sotto l'altra, e la
 * lettura affiancata «cambia / non cambia» e' il punto). Il file resta perche'
 * lo shell lo monta insieme all'altro.
 */

type Misurato = NonNullable<NonNullable<Controllo['learning']>['misurato']>;

const VERDETTO_DERIVA: Record<string, string> = {
  ok: STATO.buono,
  watch: STATO.attenzione,
  drift: STATO.critico,
};

export function Voce({ titolo, children, nota }: { titolo: string; children: ReactNode; nota?: string }) {
  return (
    <div style={{ padding: '8px 0', borderTop: '1px solid var(--border-soft)' }}>
      <div style={{ fontSize: 12, fontWeight: 650, marginBottom: 3 }}>
        {titolo}
        {nota ? <span className="muted" style={{ fontWeight: 400 }}> · {nota}</span> : null}
      </div>
      <div style={{ fontSize: 12.5, lineHeight: 1.55 }}>{children}</div>
    </div>
  );
}

/** Un valore che manca e' «non misurato», mai zero: la regola del contratto. */
function N({ v, dec = 0 }: { v: number | null | undefined; dec?: number }) {
  return v == null ? <span className="muted">—</span> : <>{dec > 0 ? numero(v, dec) : formatta(v)}</>;
}

export function ColonnaMisurato({ m, now }: { m: Misurato | null | undefined; now: number }) {
  if (!m) return <p className="muted" style={{ fontSize: 12 }}>sezione «misurato» assente</p>;
  if (m.errore) return <p className="muted" style={{ fontSize: 12 }}>sezione non calcolata: {m.errore}</p>;
  const d = m.deriva;
  const cal = m.calibrazione;
  const tr = m.trailing;
  const ref = m.referti;
  return (
    <>
      {m.lettura ? <p style={{ fontSize: 13, margin: '0 0 6px' }}>{m.lettura}</p> : null}

      <Voce titolo="Deriva per coppia" nota={d?.at ? quando(d.at) : undefined}>
        {d ? (
          <>
            <span style={{ color: STATO.buono }}>{formatta(d.coppie_ok ?? 0)} ok</span>
            {' '}· <span style={{ color: STATO.attenzione }}>{formatta(d.coppie_watch ?? 0)} sotto osservazione</span>
            {' '}· <span style={{ color: STATO.critico }}>{formatta(d.coppie_drift ?? 0)} in deriva</span>
            <div className="muted" style={{ fontSize: 11 }}>
              verdetto per coppia da {formatta(d.soglia_coppia ?? 0)} trade (per strategia {formatta(d.soglia_strategia ?? 0)}); la coppia
              piu&apos; tradata ne ha <N v={d.max_trades_coppia} />
            </div>
            {d.top && d.top.length > 0 ? (
              <div style={{ overflowX: 'auto', marginTop: 4 }}>
                <table style={{ borderCollapse: 'collapse', fontSize: 12, width: '100%' }}>
                  <thead>
                    <tr className="muted" style={{ textAlign: 'left' }}>
                      <th style={{ padding: '2px 6px 2px 0', textAlign: 'left' }}>coppia</th>
                      <th style={{ padding: '2px 6px', textAlign: 'left' }}>verdetto</th>
                      <th style={{ padding: '2px 6px' }}>trade</th>
                      <th style={{ padding: '2px 6px' }}>PF vissuto</th>
                      <th style={{ padding: '2px 6px' }}>atteso</th>
                    </tr>
                  </thead>
                  <tbody>
                    {d.top.map((r) => (
                      <tr key={r.coppia} style={{ borderTop: '1px solid var(--border-soft)' }} title={r.motivo ?? undefined}>
                        <td className="mono" style={{ padding: '2px 6px 2px 0', textAlign: 'left', whiteSpace: 'nowrap' }}>{r.coppia}</td>
                        <td style={{ padding: '2px 6px', textAlign: 'left', color: VERDETTO_DERIVA[r.verdetto ?? ''] ?? 'var(--text-dim)', fontWeight: 600 }}>
                          {r.verdetto ?? '—'}
                        </td>
                        <td style={{ padding: '2px 6px' }}><N v={r.trades} /></td>
                        <td style={{ padding: '2px 6px' }}><N v={r.pf_vissuto} dec={2} /></td>
                        <td style={{ padding: '2px 6px' }}><N v={r.pf_atteso} dec={2} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : null}
          </>
        ) : (
          <span className="muted">non misurata</span>
        )}
      </Voce>

      <Voce titolo="Calibrazione della convinzione" nota={cal?.at ? quando(cal.at) : undefined}>
        {cal ? (
          <>
            verdetto <b>{cal.verdetto ?? '—'}</b> su <N v={cal.trades} /> trade · correlazione <N v={cal.correlazione} dec={2} />
            {' '}· fiducia <N v={cal.trust} dec={2} />
            {cal.nota ? <div className="muted" style={{ fontSize: 11 }}>{cal.nota}</div> : null}
          </>
        ) : (
          <span className="muted">non misurata</span>
        )}
      </Voce>

      <Voce titolo="Verdetti del trailing">
        {tr ? (
          <>
            <N v={tr.verdetti_totali} /> verdetti: <span style={{ color: STATO.critico }}>{formatta(tr.prematuri ?? 0)} prematuri</span>,{' '}
            <span style={{ color: STATO.buono }}>{formatta(tr.protetti ?? 0)} protetti</span>, {formatta(tr.neutri ?? 0)} neutri
            <div className="muted" style={{ fontSize: 11 }}>
              per la proposta contano solo i trailing sul timeframe del bot: {formatta(tr.verdetti_per_proposta ?? 0)}{' '}
              ({formatta(tr.prematuri_tf ?? 0)} prematuri, {formatta(tr.protetti_tf ?? 0)} protetti; ne servono {formatta(tr.soglia ?? 0)})
              {' '}→ il paper propone keep {tr.proposta_paper == null ? 'nessuno' : numero(tr.proposta_paper, 2)}
            </div>
          </>
        ) : (
          <span className="muted">non misurati</span>
        )}
      </Voce>

      <Voce titolo="Referti dei trade chiusi">
        {ref ? (
          <>
            <N v={ref.n_con_referto} /> con referto (<N v={ref.persi_con_referto} /> persi) · morti all&apos;ingresso {formatta(ref.ingresso ?? 0)},
            {' '}in uscita {formatta(ref.uscita ?? 0)}, in protezione {formatta(ref.protezione ?? 0)}
            <div className="muted" style={{ fontSize: 11 }}>
              stop largo {formatta(ref.stop_largo ?? 0)} · lock mai armato {formatta(ref.lock_mai ?? 0)} · controtrend {formatta(ref.controtrend ?? 0)}
            </div>
            {ref.ipotesi && ref.ipotesi.length > 0 ? (
              <ul style={{ margin: '4px 0 0', paddingLeft: 18, fontSize: 12 }}>
                {ref.ipotesi.map((h, i) => <li key={i}>{h}</li>)}
              </ul>
            ) : (
              <div className="muted" style={{ fontSize: 11 }}>nessuna ipotesi per il gate</div>
            )}
          </>
        ) : (
          <span className="muted">non misurati</span>
        )}
      </Voce>

      <Voce titolo="Selettore per famiglia" nota={m.selettore?.at ? quando(m.selettore.at) : undefined}>
        {m.selettore ? (
          <>
            {Object.entries(m.selettore.verdetti ?? {}).length === 0 ? (
              <span className="muted">nessun verdetto</span>
            ) : (
              <div className="chip-row" style={{ marginTop: 0 }}>
                {Object.entries(m.selettore.verdetti ?? {}).map(([f, v]) => (
                  <span key={f} className="mini-chip">{f} <span className="mono">{v}</span></span>
                ))}
              </div>
            )}
            {m.selettore.nota ? <div className="muted" style={{ fontSize: 11 }}>{m.selettore.nota}</div> : null}
          </>
        ) : (
          <span className="muted">nessun rapporto del selettore</span>
        )}
      </Voce>

      <Voce titolo="AI in ombra e ipotesi">
        {m.ombra_ai ? (
          <>
            ombra: <N v={m.ombra_ai.n} /> confronti, d&apos;accordo col bot <N v={m.ombra_ai.agree} />
            {m.ombra_ai.n ? <> ({quota((m.ombra_ai.agree ?? 0) / m.ombra_ai.n)})</> : null}
            {' '}· ultimo {quando(m.ombra_ai.ultimo_at)}
          </>
        ) : (
          <span className="muted">ombra AI: nessun confronto</span>
        )}
        <div>
          {m.ipotesi_ai ? (
            <>ipotesi AI: <N v={m.ipotesi_ai.proposte} /> proposte, <N v={m.ipotesi_ai.accettate} /> accettate · {quando(m.ipotesi_ai.at)}</>
          ) : (
            <span className="muted">ipotesi AI: nessuna</span>
          )}
        </div>
      </Voce>

      <Voce titolo="Memoria notturna">
        {m.notturno_at != null ? (
          <>
            aggiornata {durata(now - m.notturno_at)} fa ({quando(m.notturno_at)})
            {now - m.notturno_at > 2 * 86400 ? <span style={{ color: STATO.attenzione }}> · piu&apos; di due giorni</span> : null}
          </>
        ) : (
          <span className="muted">mai scritta</span>
        )}
      </Voce>

      <Fonte sez={m} />
    </>
  );
}

/** Vedi il commento in testa: la colonna e' montata da `LearningAttivoMisurato`. */
export default function LearningMisurato() {
  return null;
}
