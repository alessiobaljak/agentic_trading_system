'use client';

import { useEffect, useMemo, useState } from 'react';
import { collection, limit, onSnapshot, orderBy, query } from 'firebase/firestore';
import { getDb } from '../lib/firebase';

/**
 * Cosa sta imparando il bot sul TRAILING (dati scritti da B1 sui trade paper).
 *
 * Per ogni uscita `trailing_stop` il bot registra:
 *   - trailing_verdict: 'premature' | 'protected' | 'neutral' (controfattuale reale)
 *   - trailing_miss_to_tp: frazione del tragitto entry->TP lasciata sul tavolo (0..1)
 *   - trailing_knockout_atr: profondità del ritracciamento che ci ha buttato fuori, in ATR
 *
 * Il "protected" è corretto (ha fatto il suo lavoro) e non si tocca. Il focus è il
 * "premature": qui aggreghiamo QUANTI sono e soprattutto QUANTI sono RUMORE
 * (knockout < 1 ATR) — quelli recuperabili con un trail consapevole della volatilità
 * senza intaccare i protected. Per-strategia, così si vede DOVE intervenire (B2).
 */
type Trade = {
  strategy?: string;
  exit_reason?: string;
  trailing_verdict?: string;
  trailing_miss_to_tp?: number;
  trailing_knockout_atr?: number | null;
};

const MAX = 500;
const NOISE_ATR = 1.0; // sotto 1 ATR il ritracciamento è "rumore" (fixabile con trail ATR)

const GREEN = '#3fb950';
const RED = '#f85149';
const AMBER = '#d29922';
const MUTED = '#8b96a5';

type Row = {
  strategy: string;
  n: number;          // uscite trailing valutate
  premature: number;
  protected_: number;
  neutral: number;
  noisePrem: number;  // premature da rumore (<1 ATR) = recuperabili
  missSum: number;    // somma miss_to_tp sui premature (per la media)
};

function pct(a: number, b: number): string {
  return b > 0 ? `${Math.round((a / b) * 100)}%` : '—';
}

export default function TrailingLearning() {
  const [rows, setRows] = useState<Trade[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const q = query(collection(getDb(), 'trades'), orderBy('exit_ts', 'desc'), limit(MAX));
    const unsub = onSnapshot(
      q,
      (snap) => {
        setRows(snap.docs.map((d) => d.data() as Trade));
        setLoaded(true);
      },
      () => setLoaded(true),
    );
    return () => unsub();
  }, []);

  const { perStrat, tot } = useMemo(() => {
    const map = new Map<string, Row>();
    const tot: Row = { strategy: 'TOTALE', n: 0, premature: 0, protected_: 0, neutral: 0, noisePrem: 0, missSum: 0 };
    for (const t of rows) {
      // trailing_stop e scale_out: entrambi tagliano il runner -> stesso verdetto controfattuale
      if ((t.exit_reason !== 'trailing_stop' && t.exit_reason !== 'scale_out') || !t.trailing_verdict) continue;
      const key = t.strategy ?? '—';
      let r = map.get(key);
      if (!r) {
        r = { strategy: key, n: 0, premature: 0, protected_: 0, neutral: 0, noisePrem: 0, missSum: 0 };
        map.set(key, r);
      }
      const add = (x: Row) => {
        x.n += 1;
        if (t.trailing_verdict === 'premature') {
          x.premature += 1;
          x.missSum += t.trailing_miss_to_tp ?? 0;
          if (t.trailing_knockout_atr != null && t.trailing_knockout_atr < NOISE_ATR) x.noisePrem += 1;
        } else if (t.trailing_verdict === 'protected') {
          x.protected_ += 1;
        } else {
          x.neutral += 1;
        }
      };
      add(r);
      add(tot);
    }
    const perStrat = Array.from(map.values()).sort((a, b) => b.premature - a.premature);
    return { perStrat, tot };
  }, [rows]);

  const cell = { padding: '6px 8px' } as const;

  return (
    <div className="panel">
      <h2>Trailing — perché usciamo prima</h2>
      <p className="subtitle">
        Il <span style={{ color: GREEN }}>protected</span> ha protetto da una perdita (corretto, non si tocca).
        Il <span style={{ color: RED }}>premature</span> è dove siamo usciti prima del TP: la colonna
        chiave è <b>rumore</b> — i premature con ritracciamento &lt; 1 ATR, recuperabili con un trail
        consapevole della volatilità senza intaccare i protected.
      </p>

      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : tot.n === 0 ? (
        <p className="muted">
          Nessuna uscita trailing ancora valutata. Il bot scrive questi dati (B1) circa un&apos;ora dopo
          l&apos;uscita, e solo se ha girato con il codice aggiornato sul VPS. Si popola da solo col tempo.
        </p>
      ) : (
        <>
          <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', margin: '4px 0 14px' }}>
            <Stat label="uscite trailing" value={String(tot.n)} />
            <Stat label="prematuri" value={`${tot.premature} · ${pct(tot.premature, tot.n)}`} color={RED} />
            <Stat label="protetti" value={`${tot.protected_} · ${pct(tot.protected_, tot.n)}`} color={GREEN} />
            <Stat
              label="prematuri = rumore (<1 ATR)"
              value={`${tot.noisePrem} · ${pct(tot.noisePrem, tot.premature)} dei prematuri`}
              color={AMBER}
            />
            <Stat
              label="miss medio dal TP"
              value={tot.premature > 0 ? `${Math.round((tot.missSum / tot.premature) * 100)}%` : '—'}
            />
          </div>

          <p className="muted" style={{ fontSize: 12, marginTop: 0, marginBottom: 12 }}>
            {tot.noisePrem / Math.max(1, tot.premature) >= 0.5
              ? 'La maggior parte dei prematuri è rumore: un trail ATR li recupererebbe. Candidato reale per B2.'
              : 'Pochi prematuri sono rumore: allargare il trail rischierebbe di rovinare i protected. Meglio non toccare.'}
          </p>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
              <thead>
                <tr style={{ textAlign: 'left', color: MUTED }}>
                  <th style={cell}>Strategia</th>
                  <th style={{ ...cell, textAlign: 'right' }}>Trailing</th>
                  <th style={{ ...cell, textAlign: 'right' }}>Prematuri</th>
                  <th style={{ ...cell, textAlign: 'right' }}>Protetti</th>
                  <th style={{ ...cell, textAlign: 'right' }}>Prem. = rumore</th>
                  <th style={{ ...cell, textAlign: 'right' }}>Miss medio</th>
                </tr>
              </thead>
              <tbody>
                {perStrat.map((r) => (
                  <tr key={r.strategy} style={{ borderTop: '1px solid #28303d' }}>
                    <td style={{ ...cell, fontWeight: 600 }}>{r.strategy}</td>
                    <td style={{ ...cell, textAlign: 'right' }}>{r.n}</td>
                    <td style={{ ...cell, textAlign: 'right', color: RED }}>
                      {r.premature} <span style={{ color: MUTED }}>({pct(r.premature, r.n)})</span>
                    </td>
                    <td style={{ ...cell, textAlign: 'right', color: GREEN }}>
                      {r.protected_} <span style={{ color: MUTED }}>({pct(r.protected_, r.n)})</span>
                    </td>
                    <td style={{ ...cell, textAlign: 'right', color: AMBER }}>
                      {r.noisePrem} <span style={{ color: MUTED }}>({pct(r.noisePrem, r.premature)})</span>
                    </td>
                    <td style={{ ...cell, textAlign: 'right' }}>
                      {r.premature > 0 ? `${Math.round((r.missSum / r.premature) * 100)}%` : '—'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}

function Stat({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div>
      <div style={{ fontSize: 20, fontWeight: 700, color: color ?? '#e6edf3' }}>{value}</div>
      <div style={{ fontSize: 11, color: MUTED }}>{label}</div>
    </div>
  );
}
