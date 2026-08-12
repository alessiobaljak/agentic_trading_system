'use client';

import { useEffect, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { getRtdb } from '../lib/firebase';

/**
 * Il regime con QUANTO E' NETTO, non solo l'etichetta.
 *
 * Quattro etichette secche non distinguono un trend conclamato da uno che sta per
 * girare: la stessa parola descrive due situazioni opposte per rischio. La
 * confidenza misura la distanza dalle soglie di decisione — vicino al confine
 * basta poco per cambiare regime, quindi l'etichetta vale poco.
 *
 * IMPORTANTE: questi numeri NON influenzano ancora size né leva. Prima va
 * verificato che predicano l'esito (il valore viaggia su ogni trade chiuso
 * proprio per rendere quella misura possibile). Il pannello lo dichiara, così
 * nessuno legge una confidenza alta come "il bot sta rischiando di più".
 */
type Detail = {
  primary_regime?: string;
  confidence?: number;
  secondary_regime?: string | null;
  supporting_signals?: string[];
  conflicting_signals?: string[];
  regime_duration_readings?: number;
  regime_change_probability?: number;
};

const LABEL: Record<string, string> = {
  bull_trending: 'Rialzo in trend',
  bear_trending: 'Ribasso in trend',
  sideways: 'Laterale',
  high_uncertainty: 'Alta incertezza',
};

function confColor(c: number): string {
  if (c >= 0.7) return 'var(--green)';
  if (c >= 0.45) return 'var(--amber)';
  return 'var(--red)';
}

/** Arco di gauge 0..100%: mezza circonferenza, riempita in proporzione. */
function Gauge({ value, color }: { value: number; color: string }) {
  const R = 52;
  const len = Math.PI * R; // lunghezza della semicirconferenza
  return (
    <svg width="140" height="82" viewBox="0 0 140 82" aria-hidden>
      <path d="M 18 70 A 52 52 0 0 1 122 70" fill="none" stroke="#28303d" strokeWidth="12"
            strokeLinecap="round" />
      <path
        d="M 18 70 A 52 52 0 0 1 122 70"
        fill="none" stroke={color} strokeWidth="12" strokeLinecap="round"
        strokeDasharray={`${len * Math.max(0, Math.min(1, value))} ${len}`}
      />
      <text x="70" y="62" textAnchor="middle" fontSize="26" fontWeight="700" fill={color}>
        {Math.round(value * 100)}%
      </text>
    </svg>
  );
}

export default function RegimeIntelligence() {
  const [d, setD] = useState<Detail | null>(null);
  const [regime, setRegime] = useState<string>('');
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const unsub = onValue(
      ref(getRtdb(), '/bot_status'),
      (snap) => {
        const v = snap.val() || {};
        setRegime(String(v.regime ?? ''));
        setD((v.regime_detail as Detail) ?? null);
        setLoaded(true);
      },
      () => setLoaded(true),
    );
    return () => unsub();
  }, []);

  if (!loaded) return <div className="panel"><h2>Regime</h2><p className="muted">Loading…</p></div>;

  const conf = Number(d?.confidence ?? 0);
  const change = Number(d?.regime_change_probability ?? 0);
  const name = LABEL[d?.primary_regime ?? regime] ?? (d?.primary_regime || regime || '—');

  return (
    <div className="panel">
      <h2>Regime — quanto è netto</h2>
      <p className="subtitle">
        La confidenza misura la <b>distanza dalle soglie</b> che decidono l&apos;etichetta:
        vicino al confine basta poco per cambiare regime. Non influenza ancora size né
        leva — prima va verificato che predica l&apos;esito.
      </p>

      {!d ? (
        <p className="muted">
          Nessuna lettura ancora pubblicata. Si popola al primo aggiornamento del regime
          (ogni ora) con il bot aggiornato sul VPS.
        </p>
      ) : (
        <>
          <div style={{ display: 'flex', gap: 24, alignItems: 'center', flexWrap: 'wrap' }}>
            <Gauge value={conf} color={confColor(conf)} />
            <div>
              <div style={{ fontSize: 22, fontWeight: 700 }}>{name}</div>
              {d.secondary_regime && (
                <div style={{ fontSize: 13, color: 'var(--amber)' }}>
                  sovrapposto: {LABEL[d.secondary_regime] ?? d.secondary_regime}
                </div>
              )}
              <div className="muted" style={{ fontSize: 12, marginTop: 6 }}>
                stabile da <b>{d.regime_duration_readings ?? 0}</b> letture ·
                instabilità <b style={{ color: change > 0.5 ? 'var(--red)' : undefined }}>
                  {Math.round(change * 100)}%
                </b>
              </div>
              <div className="muted" style={{ fontSize: 11 }}>
                l&apos;instabilità è la frazione di letture recenti in disaccordo, smorzata
                dalla durata: un indicatore, non una probabilità calibrata
              </div>
            </div>
          </div>

          <div className="grid grid-2" style={{ marginTop: 14 }}>
            <div>
              <div style={{ fontSize: 12, color: 'var(--green)', fontWeight: 600 }}>
                A FAVORE
              </div>
              <ul style={{ margin: '6px 0 0', paddingLeft: 18, fontSize: 13 }}>
                {(d.supporting_signals ?? []).map((s) => <li key={s}>{s}</li>)}
                {!(d.supporting_signals ?? []).length && <li className="muted">—</li>}
              </ul>
            </div>
            <div>
              <div style={{ fontSize: 12, color: 'var(--red)', fontWeight: 600 }}>
                IN CONFLITTO
              </div>
              <ul style={{ margin: '6px 0 0', paddingLeft: 18, fontSize: 13 }}>
                {(d.conflicting_signals ?? []).map((s) => <li key={s}>{s}</li>)}
                {!(d.conflicting_signals ?? []).length && <li className="muted">nessuno</li>}
              </ul>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
