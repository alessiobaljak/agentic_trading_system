'use client';

import { useEffect, useMemo, useState } from 'react';
import { doc, onSnapshot } from 'firebase/firestore';
import { getDb } from '../lib/firebase';

/**
 * GATE 1 — il registro VALIDATO (strategy_registry/validated): ESATTAMENTE le
 * coppie (coin · strategia) che il bot è autorizzato a operare, incluse le
 * strategie GENERATE (gen_*). La mappa `pairs` è salvata come stringa JSON
 * (per non sforare i limiti di Firestore), quindi va decodificata.
 */
type PairRec = {
  symbol: string;
  strategy: string;
  pass_count?: number;
  last_pf?: number;
  last_pnl_pct?: number;
  last_trades?: number;
  last_params?: Record<string, unknown>;
};
type Reg = {
  validated?: string[];
  pairs?: string | Record<string, PairRec>;
  coverage?: number;
  coins_covered?: number;
  universe_size?: number;
  ready?: boolean;
  updated_at?: number;
};

export default function OptimizedStrategies() {
  const [reg, setReg] = useState<Reg | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const unsub = onSnapshot(
      doc(getDb(), 'strategy_registry', 'validated'),
      (snap) => {
        setReg(snap.exists() ? (snap.data() as Reg) : null);
        setLoaded(true);
      },
      () => setLoaded(true),
    );
    return () => unsub();
  }, []);

  const rows = useMemo(() => {
    if (!reg) return [];
    let pairs: Record<string, PairRec> = {};
    try {
      pairs = typeof reg.pairs === 'string' ? JSON.parse(reg.pairs) : (reg.pairs ?? {});
    } catch {
      pairs = {};
    }
    return (reg.validated ?? [])
      .map((k) => pairs[k])
      .filter((e): e is PairRec => Boolean(e))
      .sort((a, b) => (b.last_pnl_pct ?? 0) - (a.last_pnl_pct ?? 0));
  }, [reg]);

  const updated = reg?.updated_at ? new Date(reg.updated_at * 1000).toLocaleString() : null;
  const cov = reg?.coverage != null ? Math.round(reg.coverage * 100) : null;

  return (
    <div className="panel">
      <h2>GATE 1 — Strategie validate (operate dal bot)</h2>
      <p className="subtitle">
        Coppie coin × strategia validate out-of-sample (netto fee), base + generate (gen_*).
        {cov != null ? ` · copertura ${reg?.coins_covered}/${reg?.universe_size} (${cov}%)` : ''}
        {reg?.ready ? ' · ✅ SUPERATO' : ''}
        {updated ? ` · agg. ${updated}` : ''}
      </p>
      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : rows.length === 0 ? (
        <p className="muted">Nessuna strategia validata ancora.</p>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <thead>
              <tr style={{ textAlign: 'left', color: '#8b96a5' }}>
                <th style={{ padding: '6px 8px' }}>Coin</th>
                <th style={{ padding: '6px 8px' }}>Strategia</th>
                <th style={{ padding: '6px 8px' }}>Pass</th>
                <th style={{ padding: '6px 8px' }}>PF</th>
                <th style={{ padding: '6px 8px' }}>PnL OOS</th>
                <th style={{ padding: '6px 8px' }}>Trade</th>
                <th style={{ padding: '6px 8px' }}>Parametri</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((e) => (
                <tr key={`${e.symbol}|${e.strategy}`} style={{ borderTop: '1px solid #28303d' }}>
                  <td style={{ padding: '6px 8px', fontWeight: 600 }}>{e.symbol}</td>
                  <td style={{ padding: '6px 8px' }}>{e.strategy}</td>
                  <td style={{ padding: '6px 8px' }}>{e.pass_count ?? '—'}</td>
                  <td style={{ padding: '6px 8px' }}>{e.last_pf?.toFixed(2) ?? '—'}</td>
                  <td
                    style={{ padding: '6px 8px', color: (e.last_pnl_pct ?? 0) >= 0 ? '#3fb950' : '#f85149' }}
                  >
                    {e.last_pnl_pct != null ? `${(e.last_pnl_pct * 100).toFixed(0)}%` : '—'}
                  </td>
                  <td style={{ padding: '6px 8px' }}>{e.last_trades ?? '—'}</td>
                  <td style={{ padding: '6px 8px', color: '#8b96a5', fontSize: 11 }}>
                    {Object.entries(e.last_params ?? {})
                      .map(([k, v]) => `${k}=${v}`)
                      .join(', ')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
