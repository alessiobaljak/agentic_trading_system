'use client';

import { useEffect, useState } from 'react';
import { onValue, ref, set } from 'firebase/database';
import { getRtdb } from '../lib/firebase';

/**
 * Cosa crede il bot contro cosa c'è davvero sull'exchange.
 *
 * In paper questo pannello resta vuoto ed è corretto: senza exchange non c'è
 * nulla da riconciliare. Coi soldi veri la divergenza fra stato interno e stato
 * reale è la modalità di fallimento più pericolosa — silenziosa, e te ne accorgi
 * dal saldo. Per questo il banner è rosso e prominente: se compare, il bot ha già
 * smesso di aprire posizioni.
 *
 * Il reset è manuale e volutamente scomodo: azzerare l'allarme senza aver capito
 * la causa significa rimettere a operare un sistema che sta lavorando su numeri
 * che non corrispondono alla realtà.
 */
type Finding = {
  event?: string;
  action?: string;
  symbol?: string | null;
  detail?: Record<string, unknown>;
  critical?: boolean;
};
type Doc = {
  checked_at?: number;
  error?: boolean;
  down_since?: number | null;
  findings?: Finding[];
};

const EVENT_LABEL: Record<string, string> = {
  missing_sl_tp: 'Posizione SENZA protezione',
  ghost_position: 'Posizione fantasma',
  duplicate_order: 'Ordine duplicato',
  exchange_down: 'Exchange irraggiungibile',
  balance_mismatch: 'Saldo discordante',
};
const ACTION_LABEL: Record<string, string> = {
  emergency_close_symbol: 'chiusa a mercato',
  drop_local_state: 'stato locale allineato',
  cancel_order: 'duplicato da cancellare',
  wait: 'in attesa, nessuna azione',
  halt: 'STOP TOTALE',
};

export default function ReconcilerStatus() {
  const [d, setD] = useState<Doc | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    const unsub = onValue(
      ref(getRtdb(), '/reconciliation'),
      (s) => { setD((s.val() as Doc) ?? null); setLoaded(true); },
      () => setLoaded(true),
    );
    return () => unsub();
  }, []);

  const reset = async () => {
    if (!confirm('Azzerare l\'allarme di riconciliazione? Fallo solo dopo aver '
               + 'capito la causa: il bot tornerà ad aprire posizioni.')) return;
    setBusy(true);
    try {
      await set(ref(getRtdb(), '/reconciliation'), { checked_at: Date.now() / 1000,
                                                     error: false, findings: [] });
    } finally {
      setBusy(false);
    }
  };

  const findings = d?.findings ?? [];
  const down = d?.down_since
    ? Math.round((Date.now() / 1000 - Number(d.down_since)) / 60) : null;

  return (
    <div className="panel">
      <h2>Riconciliazione con l&apos;exchange</h2>
      <p className="subtitle">
        Confronto fra le posizioni che il bot crede di avere e quelle davvero aperte su
        Binance. In paper resta vuoto: non c&apos;è un exchange da confrontare.
      </p>

      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : !d ? (
        <p className="muted">
          Nessun controllo eseguito. Il reconciler è attivo solo in live
          (<code>DRY_RUN=false</code>): in paper non avrebbe nulla da confrontare.
        </p>
      ) : (
        <>
          {d.error && (
            <div style={{
              background: 'rgba(248,81,73,.12)', border: '1px solid var(--red)',
              borderRadius: 8, padding: '10px 12px', marginBottom: 12,
            }}>
              <b style={{ color: 'var(--red)' }}>
                DIVERGENZA CON L&apos;EXCHANGE — nuove posizioni bloccate
              </b>
              <div style={{ fontSize: 12, marginTop: 4 }}>
                Il bot non apre più nulla finché l&apos;allarme non viene azzerato a mano.
              </div>
            </div>
          )}

          {down !== null && (
            <p style={{ color: 'var(--amber)', fontSize: 13 }}>
              Exchange irraggiungibile da <b>{down} minuti</b>. Nessuna chiusura tentata:
              senza risposte affidabili una chiusura al buio può duplicare posizioni o
              fallire a metà.
            </p>
          )}

          {!findings.length ? (
            <p style={{ color: 'var(--green)' }}>
              ✓ Stato interno ed exchange coincidono.
            </p>
          ) : (
            <ul style={{ margin: '4px 0 0', paddingLeft: 18, fontSize: 13 }}>
              {findings.map((f, i) => (
                <li key={i} style={{ color: f.critical ? 'var(--red)' : 'var(--amber)' }}>
                  <b>{EVENT_LABEL[f.event ?? ''] ?? f.event}</b>
                  {f.symbol ? ` · ${f.symbol}` : ''} → {ACTION_LABEL[f.action ?? ''] ?? f.action}
                </li>
              ))}
            </ul>
          )}

          <p className="muted" style={{ fontSize: 11, marginTop: 10 }}>
            Ultimo controllo:{' '}
            {d.checked_at ? new Date(d.checked_at * 1000).toLocaleString('it-IT') : '—'}
          </p>

          {d.error && (
            <button className="btn" onClick={reset} disabled={busy}
                    style={{ borderColor: 'var(--red)', color: 'var(--red)' }}>
              {busy ? 'Azzeramento…' : 'Azzera allarme (solo dopo aver capito la causa)'}
            </button>
          )}
        </>
      )}
    </div>
  );
}
