'use client';

import { useEffect, useState } from 'react';
import { onValue, ref, serverTimestamp, set } from 'firebase/database';
import { getRtdb } from '../lib/firebase';

/**
 * Kill switch. Sets /commands/kill_switch = true (the bot resets it to false
 * after flattening all positions). Confirmation-guarded so it can't be tripped
 * by an accidental click.
 */
export default function KillSwitch() {
  const [armed, setArmed] = useState(false); // dialog open
  const [sending, setSending] = useState(false);
  const [current, setCurrent] = useState<boolean | null>(null);
  const [lastSent, setLastSent] = useState<number | null>(null);
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
      setLastSent(Date.now());
      setArmed(false);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to trigger kill switch.');
    } finally {
      setSending(false);
    }
  };

  const pending = current === true;

  return (
    <div className="panel" style={{ borderColor: 'var(--red)' }}>
      <h2 style={{ color: 'var(--red)' }}>Kill Switch</h2>
      <p className="subtitle">
        Immediately flatten all positions and halt new entries. Use only in an emergency.
      </p>

      {pending ? (
        <div className="badge red" style={{ marginBottom: 12 }}>
          KILL SWITCH ACTIVE — bot is flattening positions
        </div>
      ) : (
        <div className="muted" style={{ fontSize: 12, marginBottom: 12 }}>
          Status: idle
          {lastSent != null && ` · last sent ${new Date(lastSent).toLocaleTimeString()}`}
        </div>
      )}

      <button
        className="btn btn-danger"
        onClick={() => setArmed(true)}
        disabled={sending || pending}
      >
        {pending ? 'Kill switch sent' : 'KILL SWITCH'}
      </button>

      {error && <div className="warn">{error}</div>}

      {armed && (
        <div className="dialog-overlay" role="dialog" aria-modal="true">
          <div className="dialog">
            <h3>Confirm kill switch</h3>
            <p>
              This sets <code>/commands/kill_switch = true</code>. The bot will close{' '}
              <strong>all open positions</strong> and stop opening new ones. This action cannot be
              undone from the dashboard.
            </p>
            <div className="dialog-actions">
              <button className="btn" onClick={() => setArmed(false)} disabled={sending}>
                Cancel
              </button>
              <button className="btn btn-danger" onClick={trigger} disabled={sending}>
                {sending ? 'Sending…' : 'Yes, kill everything'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
