'use client';

import { useEffect, useState } from 'react';
import { collection, limit, onSnapshot, orderBy, query } from 'firebase/firestore';
import { getDb } from '../lib/firebase';
import { toMillis, type Insight } from '../lib/types';

/**
 * Weekly insights feed from the `insights` collection, newest first.
 * Each doc is a narrative the orchestrator produced from the learning loop.
 */
export default function Insights() {
  const [items, setItems] = useState<Insight[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const db = getDb();
    const q = query(collection(db, 'insights'), orderBy('created_at', 'desc'), limit(20));
    const unsub = onSnapshot(
      q,
      (snap) => {
        setItems(snap.docs.map((d) => d.data() as Insight));
        setLoaded(true);
      },
      () => setLoaded(true),
    );
    return () => unsub();
  }, []);

  // Diario del learning: mostrato SOLO quando ci sono voci (scelta UX).
  if (loaded && items.length === 0) return null;

  return (
    <div className="panel">
      <h2>Diario del learning</h2>
      <p className="subtitle">Narrative settimanali generate dal loop di apprendimento, dalla più recente</p>
      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          {items.map((it, i) => {
            const ms = toMillis(it.created_at);
            return (
              <div
                key={it.week_id ?? i}
                style={{
                  border: '1px solid var(--border)',
                  borderRadius: 8,
                  padding: 12,
                  background: 'var(--bg-panel-2)',
                }}
              >
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'baseline',
                    gap: 8,
                    marginBottom: 6,
                  }}
                >
                  <strong>Week {it.week_id ?? '—'}</strong>
                  <span className="muted" style={{ fontSize: 12 }}>
                    {ms ? new Date(ms).toLocaleDateString() : ''}
                  </span>
                </div>
                <div className="muted" style={{ fontSize: 12, marginBottom: 8 }}>
                  {it.total_trades != null && <span>{it.total_trades} trades</span>}
                  {it.overall_win_rate != null && (
                    <span> · win rate {(it.overall_win_rate * 100).toFixed(1)}%</span>
                  )}
                </div>
                <p style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{it.narrative}</p>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
