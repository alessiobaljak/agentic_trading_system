'use client';

import { useEffect, useState } from 'react';
import { onValue, ref, serverTimestamp, set } from 'firebase/database';
import { getRtdb } from '../lib/firebase';

/**
 * Kill switch. Scrive /commands/kill_switch = true (il bot lo rimette a false
 * dopo aver chiuso tutte le posizioni). C'e' una conferma in mezzo: un click
 * per sbaglio non deve chiudere tutto.
 *
 * Due varianti (25 set 2026): `button` e' il pulsante STOP sempre visibile in
 * alto, con la finestra di conferma; `panel` (Impostazioni) e' UNA riga di
 * stato — prima era un secondo pannello con lo stesso dialogo, e due posti da
 * cui chiudere tutto sono uno di troppo.
 */
export default function KillSwitch({ variant = 'panel' }: { variant?: 'panel' | 'button' }) {
  const [armed, setArmed] = useState(false); // dialog open
  const [sending, setSending] = useState(false);
  const [current, setCurrent] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const db = getRtdb();
    const unsub = onValue(ref(db, 'commands/kill_switch'), (snap) => {
      setCurrent(snap.exists() ? Boolean(snap.val()) : false);
    });
    return () => unsub();
  }, []);

  const trigger = async () => {
    setError(null);
    setSending(true);
    try {
      const db = getRtdb();
      await set(ref(db, 'commands/kill_switch'), true);
      // best-effort audit trail; bot ignores extra keys under /commands
      await set(ref(db, 'commands/kill_switch_meta'), {
        requested_by: 'dashboard',
        requested_at: serverTimestamp(),
      }).catch(() => undefined);
      setArmed(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Invio del kill switch fallito.');
    } finally {
      setSending(false);
    }
  };

  const pending = current === true;

  const confirmDialog = armed && (
    <div className="dialog-overlay" role="dialog" aria-modal="true">
      <div className="dialog">
        <h3>Confermi il kill switch?</h3>
        <p>
          Scrive <code>/commands/kill_switch = true</code>. Il bot chiude{' '}
          <strong>tutte le posizioni aperte</strong> e smette di aprirne. Dalla dashboard non si
          torna indietro.
        </p>
        {error && <div className="warn">{error}</div>}
        <div className="dialog-actions">
          <button className="btn" onClick={() => setArmed(false)} disabled={sending}>
            Annulla
          </button>
          <button className="btn btn-danger" onClick={trigger} disabled={sending}>
            {sending ? 'Invio…' : 'Sì, chiudi tutto'}
          </button>
        </div>
      </div>
    </div>
  );

  // Variante compatta per la top bar: pulsante d'emergenza sempre visibile.
  if (variant === 'button') {
    return (
      <>
        <button
          className={`emergency-btn ${pending ? 'active' : ''}`}
          onClick={() => setArmed(true)}
          disabled={sending || pending}
          title="Kill switch: chiude tutte le posizioni e ferma nuove entrate"
        >
          <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <circle cx="12" cy="12" r="9" />
            <path d="M12 7v6" />
          </svg>
          {pending ? 'KILL ATTIVO' : 'STOP'}
        </button>
        {confirmDialog}
      </>
    );
  }

  // Impostazioni: una riga di stato. Il pulsante e la conferma stanno in alto.
  return (
    <div className="panel">
      <h2>Kill switch</h2>
      <p style={{ margin: 0, fontSize: 13 }}>
        {pending ? (
          <span style={{ color: 'var(--red)', fontWeight: 700 }}>
            ATTIVO — il bot sta chiudendo le posizioni e non ne apre di nuove.
          </span>
        ) : (
          <>
            <span style={{ color: 'var(--green)', fontWeight: 600 }}>spento</span>
            <span className="muted">
              {' '}· il pulsante STOP in alto chiude tutte le posizioni e ferma le entrate
            </span>
          </>
        )}
      </p>
      {error && <div className="warn">{error}</div>}
    </div>
  );
}
