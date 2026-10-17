'use client';

/**
 * TopVitals — chip di stato "vivo" nella top bar del guscio.
 * SOLO LETTURA: legge gli stessi path RTDB già usati da BotStatus
 * (bot_status, account/equity, positions) per mostrare stato + equity
 * mark-to-market su ogni sezione. Non scrive nulla, non tocca alcuna logica.
 *
 * Dal 25 set 2026 porta anche due chip dal controllo orario: il semaforo di
 * sistema («e' rotto?») e il freno globale, cosi' si vedono da ogni scheda.
 * «Online» usa la soglia scritta dal bot (`salute.soglia_online_s`, 900 s):
 * prima erano 5 minuti qui e 5 in BotStatus, e il market scan ogni 4 h
 * faceva sfarfallare il badge su OFFLINE col bot vivo.
 */
import { useEffect, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { getRtdb } from '../lib/firebase';
import { toMillis, type BotStatus, type Position } from '../lib/types';
import { semaforoColore, useControllo } from '../lib/controllo';

const SOGLIA_ONLINE_DEFAULT_S = 900;

export default function TopVitals() {
  const [status, setStatus] = useState<BotStatus | null>(null);
  const [equity, setEquity] = useState<number | null>(null);
  const [positions, setPositions] = useState<Position[]>([]);
  const [now, setNow] = useState(Date.now());
  const { doc: controllo, stato: statoControllo, caricamento: caricamentoControllo } = useControllo();

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
  const sogliaMs = (controllo?.salute?.soglia_online_s ?? SOGLIA_ONLINE_DEFAULT_S) * 1000;
  const heartbeatMs = toMillis(status?.heartbeat ?? status?.updated_at ?? null);
  const online = heartbeatMs != null && now - heartbeatMs < sogliaMs;
  const running = (status?.state ?? '').toLowerCase() === 'running';
  const live = running && online;
  const usd = (n: number) => `$${n.toLocaleString('it-IT', { maximumFractionDigits: 2 })}`;

  const semaforo = controllo?.meta?.semaforo_sistema ?? null;
  const freno = controllo?.salute?.freno_globale === true;
  const testoSemaforo =
    statoControllo === 'assente' ? 'nessun controllo'
    : semaforo === 'verde' ? 'sistema ok'
    : semaforo === 'giallo' ? 'sistema: avvisi'
    : semaforo === 'rosso' ? 'sistema: grave'
    : 'sistema n/d';

  return (
    <div className="top-vitals">
      <div className="vital-chip">
        <span className={`badge ${live ? 'green' : 'red'}`} style={{ padding: '3px 9px' }}>
          <span className="dot" style={{ background: live ? 'var(--green)' : 'var(--red)' }} />
          {live ? 'VIVO' : online ? (status?.state ?? 'SCONOSCIUTO').toUpperCase() : 'OFFLINE'}
        </span>
      </div>
      {!(caricamentoControllo && !controllo) && (
        <div className="vital-chip" title="semaforo di sistema dell'ultimo controllo orario («e' rotto?»)">
          <span className="badge gray" style={{ padding: '3px 9px' }}>
            <span className="dot" style={{ background: semaforoColore(semaforo) }} />
            {testoSemaforo}
            {statoControllo === 'fermo' && ' (vecchio)'}
          </span>
        </div>
      )}
      {controllo && (
        <div className="vital-chip" title={freno ? 'freno globale acceso: size ridotta' : 'freno globale spento'}>
          <span className={`badge ${freno ? 'amber' : 'gray'}`} style={{ padding: '3px 9px' }}>
            freno {freno ? 'ON' : 'OFF'}
          </span>
        </div>
      )}
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
