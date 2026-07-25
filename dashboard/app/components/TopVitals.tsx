'use client';

/**
 * TopVitals — chip di stato "vivo" nella top bar del guscio.
 * SOLO LETTURA: legge gli stessi path RTDB già usati da BotStatus
 * (bot_status, account/equity, positions) per mostrare stato + equity
 * mark-to-market su ogni sezione. Non scrive nulla, non tocca alcuna logica.
 */
import { useEffect, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { getRtdb } from '../lib/firebase';
import { toMillis, type BotStatus, type Position } from '../lib/types';

const HEARTBEAT_STALE_MS = 5 * 60 * 1000;

export default function TopVitals() {
  const [status, setStatus] = useState<BotStatus | null>(null);
  const [equity, setEquity] = useState<number | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [now, setNow] = useState(Date.now());

  useEffect(() => {
    const db = getRtdb();
    const u1 = onValue(ref(db, 'bot_status'), (s) =>
      setStatus(s.exists() ? (s.val() as BotStatus) : null),
    );
    const u2 = onValue(ref(db, 'account/equity'), (s) =>
      setEquity(s.exists() ? Number(s.val()) : null),
    );
    const u3 = onValue(ref(db, 'positions'), (s) => {
      const val = s.val() as Record<string, Position> | null;
      setPositions(val ? Object.values(val) : []);
    });
    const tick = setInterval(() => setNow(Date.now()), 15000);
    return () => {
      u1();
      u2();
      u3();
      clearInterval(tick);
    };
  }, []);

  const uPnl = positions.reduce((s, p) => s + (p.unrealized_pnl ?? 0), 0);
  const equityMtm = equity != null ? equity + uPnl : null;
  const heartbeatMs = toMillis(status?.heartbeat ?? status?.updated_at ?? null);
  const online = heartbeatMs != null && now - heartbeatMs < HEARTBEAT_STALE_MS;
  const running = (status?.state ?? '').toLowerCase() === 'running';
  const live = running && online;
  const usd = (n: number) => `$${n.toLocaleString(undefined, { maximumFractionDigits: 2 })}`;

  return (
    <div className="top-vitals">
      <div className="vital-chip">
        <span className={`badge ${live ? 'green' : 'red'}`} style={{ padding: '3px 9px' }}>
          <span className="dot" style={{ background: live ? 'var(--green)' : 'var(--red)' }} />
          {live ? 'LIVE' : online ? (status?.state ?? 'UNKNOWN').toUpperCase() : 'OFFLINE'}
        </span>
      </div>
      {equityMtm != null && (
        <div className="vital-chip">
          <span>
            <span className="vc-label">Equity</span>
            <span className="vc-value">{usd(equityMtm)}</span>
          </span>
        </div>
      )}
      {positions.length > 0 && (
        <div className="vital-chip">
          <span>
            <span className="vc-label">uPnL aperto</span>
            <span className={`vc-value ${uPnl >= 0 ? 'pos' : 'neg'}`}>
              {uPnl >= 0 ? '+' : ''}
              {usd(uPnl).replace('$', '')}
            </span>
          </span>
        </div>
      )}
    </div>
  );
}
