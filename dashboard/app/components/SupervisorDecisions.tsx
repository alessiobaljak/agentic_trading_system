'use client';

import { useEffect, useState } from 'react';
import { doc, onSnapshot } from 'firebase/firestore';
import { getDb } from '../lib/firebase';
import { STATO, quando } from '../lib/viz';

/**
 * LE DECISIONI CHE IL SISTEMA PRENDE DA SOLO.
 *
 * Non i trade — quelli si vedono in Operatività. Qui c'è lo strato sopra: il
 * supervisore gira ogni ora, guarda quante coppie si sono validate, dove muoiono le
 * candidate e quanto margine c'è nel budget di falsi positivi, e decide se toccare
 * una soglia, disfare una propria modifica o non fare niente.
 *
 * «Non fare niente» è un esito normale e viene mostrato come gli altri: un pannello
 * che si accende solo quando succede qualcosa non permette di distinguere «sta
 * valutando e ha deciso di aspettare» da «è fermo».
 *
 * OGNI DECISIONE PORTA IL SUO PERCHÉ, e il dettaglio si apre cliccandola. È l'unico
 * modo di rispondere fra due mesi a «perché questa soglia sta a questo valore?», e
 * serve soprattutto quando la risposta è sbagliata: una decisione senza motivo non si
 * può contestare, si può solo subire.
 *
 * IL BUDGET DI FALSI POSITIVI è il vincolo sopra a tutto, ed è l'unica cosa qui che
 * merita una barra invece di un numero: non interessa il valore, interessa QUANTO
 * SIAMO VICINI AL LIMITE. Con ventimila candidate per passata, allentare una soglia
 * compra sempre qualche passaggio — la domanda non è «passa qualcuno?» ma «quanti di
 * quelli che passano sarebbero passati per caso?».
 */
type Detail = {
  pass_rate?: number;
  expected_lucky_per_day?: number;
  headroom?: number | null;
  evaluated?: number;
  window_days?: number;
  near_misses?: number;
  expected_conversions?: number;
  reverted?: string[];
};
type Dec = {
  kind?: string;
  reason?: string;
  param?: string;
  old?: number | null;
  new?: number | null;
  at?: number;
  detail?: Detail;
};
type State = {
  updated_at?: number;
  validated?: number;
  ready?: boolean;
  pass_rate?: number;
  tuning?: Record<string, string>;
  last_decisions?: Dec[];
  history?: Dec[];
};

const KIND: Record<string, { label: string; color: string; icona: string }> = {
  set_param: { label: 'soglia cambiata', color: 'var(--accent)', icona: '⇄' },
  revert: { label: 'modifica disfatta', color: STATO.attenzione, icona: '↩' },
  tighten: { label: 'si stringe', color: STATO.attenzione, icona: '⊣' },
  fast_gate: { label: 'ri-gioco la storia', color: 'var(--purple)', icona: '⟳' },
  none: { label: 'nessuna azione', color: 'var(--text-faint)', icona: '·' },
};

/** Il margine nel budget, come barra. >1 = c'è spazio; <1 = sforato. La scala è
 *  tagliata a 10× perché oltre non cambia nessuna decisione. */
function Budget({ spazio }: { spazio: number }) {
  const sforato = spazio < 1;
  const quota = Math.max(0.02, Math.min(1, Math.log10(Math.max(spazio, 0.1) * 10) / 2));
  return (
    <div style={{ minWidth: 190 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12 }}>
        <span className="muted">spazio nel budget</span>
        <span style={{ color: sforato ? STATO.critico : 'var(--text)' }}>
          {sforato ? '⚠ ' : ''}
          <b>{spazio.toFixed(1)}×</b>
        </span>
      </div>
      <div
        style={{
          position: 'relative',
          height: 6,
          background: 'var(--border-soft)',
          borderRadius: 3,
          marginTop: 5,
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            width: `${quota * 100}%`,
            height: '100%',
            background: sforato ? STATO.critico : 'var(--accent)',
            borderRadius: 3,
          }}
        />
        {/* il limite: 1× — sotto, ogni allentamento compra fortuna invece che edge */}
        <div
          style={{
            position: 'absolute',
            left: `${(Math.log10(10) / 2) * 100}%`,
            top: -2,
            bottom: -2,
            width: 1,
            background: 'var(--text-faint)',
          }}
          title="il limite: 1×"
        />
      </div>
    </div>
  );
}

export default function SupervisorDecisions() {
  const [s, setS] = useState<State | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [aperta, setAperta] = useState<number | null>(null);

  useEffect(() => {
    try {
      return onSnapshot(
        doc(getDb(), 'supervisor', 'state'),
        (snap) => { setS(snap.exists() ? (snap.data() as State) : null); setLoaded(true); },
        () => setLoaded(true),
      );
    } catch {
      setLoaded(true);
      return;
    }
  }, []);

  const storia = [...(s?.history ?? [])].reverse().slice(0, 20);
  const tuning = Object.entries(s?.tuning ?? {}).filter(([k]) => !k.startsWith('#'));
  const spazio = storia.find((d) => d.detail?.headroom != null)?.detail?.headroom;

  return (
    <div className="panel">
      <h2>Decisioni del supervisore</h2>
      <p className="subtitle">
        Lo strato che si tara da solo: ogni ora guarda la validazione, l&apos;autopsia
        delle candidate e il budget di falsi positivi, e decide. Clicca una decisione
        per il dettaglio.
      </p>

      {!loaded ? (
        <p className="muted">Caricamento…</p>
      ) : !s ? (
        <p className="muted">
          Il supervisore non ha ancora scritto nulla. Gira su timer sulla VPS
          (<code>trading-supervisor.timer</code>): se questo pannello resta vuoto per
          più di un&apos;ora, il timer è fermo.
        </p>
      ) : (
        <>
          <div
            style={{
              display: 'flex',
              gap: 24,
              flexWrap: 'wrap',
              alignItems: 'flex-end',
              marginBottom: 16,
            }}
          >
            <div>
              <div className="muted" style={{ fontSize: 12 }}>coppie validate</div>
              <div style={{ fontSize: 24, lineHeight: 1.15 }}>{s.validated ?? 0}</div>
            </div>
            <div>
              <div className="muted" style={{ fontSize: 12 }}>tasso di passaggio</div>
              <div style={{ fontSize: 24, lineHeight: 1.15 }}>
                {((s.pass_rate ?? 0) * 100).toFixed(3)}<span style={{ fontSize: 14 }}>%</span>
              </div>
            </div>
            {spazio != null && <Budget spazio={spazio} />}
            <span style={{ flex: 1 }} />
            <span className="muted" style={{ fontSize: 11 }}>
              aggiornato {quando(s.updated_at)}
            </span>
          </div>

          <div style={{ marginBottom: 16 }}>
            <div className="muted" style={{ fontSize: 12, marginBottom: 6 }}>
              PARAMETRI CHE IL SUPERVISORE HA CAMBIATO
            </div>
            {tuning.length === 0 ? (
              <p className="muted" style={{ fontSize: 13, margin: 0 }}>
                Nessuno: il sistema gira sui valori validati a mano. È lo stato di riposo
                giusto — ogni modifica automatica è un debito da rimisurare.
              </p>
            ) : (
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                {tuning.map(([k, v]) => (
                  <span
                    key={k}
                    style={{
                      border: '1px solid var(--border)',
                      borderRadius: 999,
                      padding: '3px 10px',
                      fontSize: 12,
                    }}
                  >
                    {k} = <b>{v}</b>
                  </span>
                ))}
              </div>
            )}
          </div>

          <div className="muted" style={{ fontSize: 12, marginBottom: 8 }}>
            LINEA DEL TEMPO
          </div>
          {storia.length === 0 ? (
            <p className="muted" style={{ fontSize: 13 }}>Nessuna decisione registrata.</p>
          ) : (
            <div style={{ position: 'relative', paddingLeft: 22 }}>
              {/* il filo della linea del tempo */}
              <div
                aria-hidden="true"
                style={{
                  position: 'absolute',
                  left: 6,
                  top: 6,
                  bottom: 6,
                  width: 1,
                  background: 'var(--border-soft)',
                }}
              />
              {storia.map((d, i) => {
                const k = KIND[d.kind ?? 'none'] ?? KIND.none;
                const id = d.at ?? -i;
                const apri = aperta === id;
                return (
                  <div key={`${id}-${i}`} style={{ position: 'relative', marginBottom: 4 }}>
                    <span
                      aria-hidden="true"
                      style={{
                        position: 'absolute',
                        left: -19,
                        top: 12,
                        width: 9,
                        height: 9,
                        borderRadius: '50%',
                        background: k.color,
                        // anello della superficie: stacca il punto dal filo
                        boxShadow: '0 0 0 2px var(--bg-panel)',
                      }}
                    />
                    <button
                      onClick={() => setAperta(apri ? null : id)}
                      aria-expanded={apri}
                      style={{
                        display: 'block',
                        width: '100%',
                        textAlign: 'left',
                        background: apri ? 'rgba(79,156,249,.07)' : 'transparent',
                        border: '1px solid var(--border-soft)',
                        borderRadius: 8,
                        padding: '8px 11px',
                        cursor: 'pointer',
                        color: 'inherit',
                        font: 'inherit',
                      }}
                    >
                      <div
                        style={{
                          display: 'flex',
                          gap: 10,
                          alignItems: 'baseline',
                          flexWrap: 'wrap',
                          marginBottom: 3,
                        }}
                      >
                        <b style={{ color: k.color, fontSize: 12 }}>
                          <span aria-hidden="true">{k.icona}</span> {k.label}
                        </b>
                        {d.param && (
                          <span style={{ fontSize: 12 }}>
                            {d.param}
                            {d.old != null && d.new != null && (
                              <> : {d.old} → <b>{d.new}</b></>
                            )}
                          </span>
                        )}
                        <span className="muted" style={{ fontSize: 11 }}>{quando(d.at)}</span>
                      </div>
                      <div style={{ fontSize: 13 }}>{d.reason}</div>

                      {apri && d.detail && (
                        <div
                          style={{
                            marginTop: 8,
                            paddingTop: 8,
                            borderTop: '1px solid var(--border-soft)',
                            display: 'flex',
                            gap: 16,
                            flexWrap: 'wrap',
                            fontSize: 11,
                          }}
                          className="muted"
                        >
                          {d.detail.evaluated != null && (
                            <span>valutate: {d.detail.evaluated.toLocaleString('it-IT')}</span>
                          )}
                          {d.detail.pass_rate != null && (
                            <span>tasso: {(d.detail.pass_rate * 100).toFixed(3)}%</span>
                          )}
                          {d.detail.expected_lucky_per_day != null && (
                            <span>fortunate attese/giorno: {d.detail.expected_lucky_per_day}</span>
                          )}
                          {d.detail.headroom != null && (
                            <span>spazio: {d.detail.headroom}×</span>
                          )}
                          {d.detail.window_days != null && (
                            <span>finestra: {d.detail.window_days}g</span>
                          )}
                          {d.detail.near_misses != null && (
                            <span>quasi-passaggi: {d.detail.near_misses}</span>
                          )}
                          {d.detail.expected_conversions != null && (
                            <span>conversioni previste: ~{d.detail.expected_conversions}</span>
                          )}
                          {d.detail.reverted?.length ? (
                            <span>disfatti: {d.detail.reverted.join(', ')}</span>
                          ) : null}
                        </div>
                      )}
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </>
      )}
    </div>
  );
}
