'use client';

import { useEffect, useState } from 'react';
import { doc, onSnapshot } from 'firebase/firestore';
import { getDb } from '../lib/firebase';

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
 * OGNI DECISIONE PORTA IL SUO PERCHÉ. È l'unico modo di rispondere fra due mesi a
 * «perché questa soglia sta a questo valore?», e serve soprattutto quando la
 * risposta è sbagliata: una decisione senza motivo non si può contestare, si può
 * solo subire.
 *
 * IL BUDGET DI FALSI POSITIVI è il vincolo che sta sopra a tutto. Con ventimila
 * candidate valutate per passata, allentare una soglia compra sempre qualche
 * passaggio: la domanda non è «passa qualcuno?» ma «quanti di quelli che passano
 * sarebbero passati per caso?». Finché lo spazio è > 1 il supervisore può muoversi;
 * sotto, disfa le proprie modifiche invece di continuare.
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

const KIND: Record<string, { label: string; color: string }> = {
  set_param: { label: 'soglia cambiata', color: 'var(--accent)' },
  revert: { label: 'modifica disfatta', color: 'var(--amber)' },
  tighten: { label: 'si stringe', color: 'var(--amber)' },
  fast_gate: { label: 'ri-gioco la storia', color: 'var(--purple)' },
  none: { label: 'nessuna azione', color: 'var(--text-faint)' },
};

function quando(ts?: number): string {
  if (!ts) return '—';
  return new Date(ts * 1000).toLocaleString('it-IT', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export default function SupervisorDecisions() {
  const [s, setS] = useState<State | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    try {
      return onSnapshot(
        doc(getDb(), 'supervisor', 'state'),
        (snap) => {
          setS(snap.exists() ? (snap.data() as State) : null);
          setLoaded(true);
        },
        () => setLoaded(true),
      );
    } catch {
      setLoaded(true);
      return;
    }
  }, []);

  const storia = [...(s?.history ?? [])].reverse().slice(0, 20);
  const tuning = Object.entries(s?.tuning ?? {}).filter(([k]) => !k.startsWith('#'));
  const ultimo = storia[0]?.detail;
  const spazio = ultimo?.headroom;

  return (
    <div className="panel">
      <h2>Decisioni del supervisore</h2>
      <p className="subtitle">
        Lo strato che si tara da solo: ogni ora guarda la validazione, l&apos;autopsia
        delle candidate e il budget di falsi positivi, e decide. «Nessuna azione» è un
        esito, non un silenzio.
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
          <div style={{ display: 'flex', gap: 18, flexWrap: 'wrap', fontSize: 13, marginBottom: 12 }}>
            <span>
              coppie validate <b>{s.validated ?? 0}</b>
            </span>
            <span>
              tasso di passaggio <b>{((s.pass_rate ?? 0) * 100).toFixed(3)}%</b>
            </span>
            {spazio != null && (
              <span style={{ color: spazio < 1 ? 'var(--red)' : undefined }}>
                spazio nel budget <b>{spazio.toFixed(1)}×</b>
                {spazio < 1 && ' — sforato'}
              </span>
            )}
            <span className="muted">aggiornato {quando(s.updated_at)}</span>
          </div>

          <div style={{ marginBottom: 14 }}>
            <div className="muted" style={{ fontSize: 12, marginBottom: 6 }}>
              PARAMETRI CHE IL SUPERVISORE HA CAMBIATO
            </div>
            {tuning.length === 0 ? (
              <p className="muted" style={{ fontSize: 13, margin: 0 }}>
                Nessuno: il sistema sta girando sui valori validati a mano. È lo stato di
                riposo giusto — ogni modifica automatica è un debito da rimisurare.
              </p>
            ) : (
              <div className="chip-row" style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
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

          <div className="muted" style={{ fontSize: 12, marginBottom: 6 }}>
            ULTIME DECISIONI
          </div>
          {storia.length === 0 ? (
            <p className="muted" style={{ fontSize: 13 }}>
              Nessuna decisione registrata.
            </p>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
              {storia.map((d, i) => {
                const k = KIND[d.kind ?? 'none'] ?? KIND.none;
                return (
                  <div
                    key={`${d.at ?? i}-${i}`}
                    style={{
                      border: '1px solid var(--border-soft)',
                      borderLeft: `3px solid ${k.color}`,
                      borderRadius: 8,
                      padding: '8px 11px',
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
                      <b style={{ color: k.color, fontSize: 12 }}>{k.label}</b>
                      {d.param && (
                        <span style={{ fontSize: 12 }}>
                          {d.param}
                          {d.old != null && d.new != null && (
                            <>
                              : {d.old} → <b>{d.new}</b>
                            </>
                          )}
                        </span>
                      )}
                      <span className="muted" style={{ fontSize: 11 }}>
                        {quando(d.at)}
                      </span>
                    </div>
                    <div style={{ fontSize: 13 }}>{d.reason}</div>
                    {d.detail?.near_misses != null && (
                      <div className="muted" style={{ fontSize: 11, marginTop: 4 }}>
                        quasi-passaggi coinvolti: {d.detail.near_misses}
                        {d.detail.expected_conversions != null &&
                          ` · conversioni previste: ~${d.detail.expected_conversions}`}
                      </div>
                    )}
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
