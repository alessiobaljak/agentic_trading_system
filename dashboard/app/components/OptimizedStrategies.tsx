'use client';

import { useEffect, useMemo, useState } from 'react';
import { doc, onSnapshot } from 'firebase/firestore';
import { getDb } from '../lib/firebase';

/**
 * GATE 1 — vista PER STRATEGIA. Una scheda per strategia (base o generata),
 * con la sua logica/parametri e l'elenco delle crypto su cui ha dato esito
 * positivo (PF, PnL OOS, win rate, trade, pass). Legge il registro validato
 * (strategy_registry/validated, `pairs` come stringa JSON) e, per le strategie
 * generate, la loro spec da discovered_strategies/specs.
 */
type PairRec = {
  symbol: string;
  strategy: string;
  pass_count?: number;
  last_pf?: number;
  last_pnl_pct?: number;
  last_trades?: number;
  last_win_rate?: number;
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
type Feature = { kind: string } & Record<string, unknown>;
type Spec = {
  features?: Feature[];
  volume_mult?: number;
  min_adx?: number;
  atr_mult_stop?: number;
  rr?: number;
};
type SpecsDoc = { specs?: Record<string, Spec> };

type Group = { strategy: string; generated: boolean; spec?: Spec; coins: PairRec[] };

function describeSpec(spec?: Spec): string {
  if (!spec) return '—';
  const parts = (spec.features ?? []).map((f) => {
    const extra = Object.entries(f)
      .filter(([k]) => k !== 'kind')
      .map(([k, v]) => `${k}=${v}`)
      .join(' ');
    return extra ? `${f.kind} ${extra}` : f.kind;
  });
  let s = parts.join(' AND ') || '—';
  const tail: string[] = [];
  if (spec.min_adx) tail.push(`ADX≥${spec.min_adx}`);
  if (spec.volume_mult) tail.push(`vol×${spec.volume_mult}`);
  if (spec.atr_mult_stop) tail.push(`stop ${spec.atr_mult_stop} ATR`);
  if (spec.rr) tail.push(`RR ${spec.rr}`);
  if (tail.length) s += ` · ${tail.join(' · ')}`;
  return s;
}

const pct = (v?: number) => (v != null ? `${(v * 100).toFixed(0)}%` : '—');

export default function OptimizedStrategies() {
  const [reg, setReg] = useState<Reg | null>(null);
  const [specsDoc, setSpecsDoc] = useState<SpecsDoc | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const db = getDb();
    const u1 = onSnapshot(
      doc(db, 'strategy_registry', 'validated'),
      (snap) => {
        setReg(snap.exists() ? (snap.data() as Reg) : null);
        setLoaded(true);
      },
      () => setLoaded(true),
    );
    const u2 = onSnapshot(doc(db, 'discovered_strategies', 'specs'), (snap) => {
      setSpecsDoc(snap.exists() ? (snap.data() as SpecsDoc) : null);
    });
    return () => {
      u1();
      u2();
    };
  }, []);

  const groups = useMemo<Group[]>(() => {
    if (!reg) return [];
    let pairs: Record<string, PairRec> = {};
    try {
      pairs = typeof reg.pairs === 'string' ? JSON.parse(reg.pairs) : (reg.pairs ?? {});
    } catch {
      pairs = {};
    }
    const specs = specsDoc?.specs ?? {};
    const byStrat = new Map<string, Group>();
    for (const key of reg.validated ?? []) {
      const rec = pairs[key];
      if (!rec) continue;
      const name = rec.strategy;
      if (!byStrat.has(name)) {
        const generated = name.startsWith('gen_');
        byStrat.set(name, { strategy: name, generated, spec: generated ? specs[name] : undefined, coins: [] });
      }
      byStrat.get(name)!.coins.push(rec);
    }
    const out = Array.from(byStrat.values());
    for (const g of out) g.coins.sort((a, b) => (b.last_pnl_pct ?? 0) - (a.last_pnl_pct ?? 0));
    // strategie più "robuste" prima: più crypto validate, poi PnL medio
    out.sort((a, b) => b.coins.length - a.coins.length);
    return out;
  }, [reg, specsDoc]);

  const updated = reg?.updated_at ? new Date(reg.updated_at * 1000).toLocaleString() : null;
  const cov = reg?.coverage != null ? Math.round(reg.coverage * 100) : null;

  return (
    <div className="panel">
      <h2>GATE 1 — Strategie validate (per strategia)</h2>
      <p className="subtitle">
        Una scheda per strategia · logica/parametri + crypto con esito positivo.
        {cov != null ? ` · copertura ${reg?.coins_covered}/${reg?.universe_size} (${cov}%)` : ''}
        {reg?.ready ? ' · ✅ SUPERATO' : ''}
        {updated ? ` · agg. ${updated}` : ''}
      </p>
      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : groups.length === 0 ? (
        <p className="muted">Nessuna strategia validata ancora.</p>
      ) : (
        <div style={{ display: 'grid', gap: 12 }}>
          {groups.map((g) => (
            <div
              key={g.strategy}
              style={{ border: '1px solid #28303d', borderRadius: 8, padding: 12, background: '#0e1420' }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                <strong style={{ fontSize: 14 }}>{g.strategy}</strong>
                <span
                  style={{
                    fontSize: 10,
                    padding: '2px 6px',
                    borderRadius: 4,
                    background: g.generated ? '#1f2a44' : '#23331f',
                    color: g.generated ? '#8ab4ff' : '#8fd18f',
                  }}
                >
                  {g.generated ? '🧠 generata' : 'base'}
                </span>
                <span className="muted" style={{ fontSize: 12 }}>
                  {g.coins.length} crypto validate
                </span>
              </div>

              <div style={{ fontSize: 12, color: '#aeb7c4', marginTop: 6 }}>
                {g.generated ? (
                  <>Logica: <span style={{ color: '#cdd6e2' }}>{describeSpec(g.spec)}</span></>
                ) : (
                  <span className="muted">Parametri ottimizzati per ogni crypto (vedi sotto)</span>
                )}
              </div>

              <div style={{ overflowX: 'auto', marginTop: 8 }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
                  <thead>
                    <tr style={{ textAlign: 'left', color: '#8b96a5' }}>
                      <th style={{ padding: '4px 6px' }}>Coin</th>
                      <th style={{ padding: '4px 6px' }}>PF</th>
                      <th style={{ padding: '4px 6px' }}>PnL OOS</th>
                      <th style={{ padding: '4px 6px' }}>Win</th>
                      <th style={{ padding: '4px 6px' }}>Trade</th>
                      <th style={{ padding: '4px 6px' }}>Pass</th>
                      {!g.generated && <th style={{ padding: '4px 6px' }}>Parametri</th>}
                    </tr>
                  </thead>
                  <tbody>
                    {g.coins.map((c) => (
                      <tr key={c.symbol} style={{ borderTop: '1px solid #1c2430' }}>
                        <td style={{ padding: '4px 6px', fontWeight: 600 }}>{c.symbol}</td>
                        <td style={{ padding: '4px 6px' }}>{c.last_pf?.toFixed(2) ?? '—'}</td>
                        <td
                          style={{ padding: '4px 6px', color: (c.last_pnl_pct ?? 0) >= 0 ? '#3fb950' : '#f85149' }}
                        >
                          {pct(c.last_pnl_pct)}
                        </td>
                        <td style={{ padding: '4px 6px' }}>{pct(c.last_win_rate)}</td>
                        <td style={{ padding: '4px 6px' }}>{c.last_trades ?? '—'}</td>
                        <td style={{ padding: '4px 6px' }}>{c.pass_count ?? '—'}</td>
                        {!g.generated && (
                          <td style={{ padding: '4px 6px', color: '#8b96a5', fontSize: 11 }}>
                            {Object.entries(c.last_params ?? {})
                              .map(([k, v]) => `${k}=${v}`)
                              .join(', ')}
                          </td>
                        )}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
