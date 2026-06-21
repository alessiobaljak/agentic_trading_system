'use client';

import { useEffect, useMemo, useState } from 'react';
import { collection, doc, limit, onSnapshot, orderBy, query } from 'firebase/firestore';
import { getDb } from '../lib/firebase';

/**
 * GATE 1 — vetrina PER STRATEGIA, a schede (card grid). Ogni strategia (base o
 * generata) ha: un mini-grafico generato, una descrizione di cosa fa, e i KPI
 * aggregati sulle crypto validate (success rate, PF, n. crypto, trade).
 * Dati: strategy_registry/validated (+ discovered_strategies/specs per le gen_*).
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
type Spec = { features?: Feature[]; volume_mult?: number; min_adx?: number; atr_mult_stop?: number; rr?: number };
type SpecsDoc = { specs?: Record<string, Spec> };
type Card = {
  strategy: string;
  generated: boolean;
  desc: string;
  coins: PairRec[];
  avgPf: number;
  avgWin: number | null;
  totTrades: number;
};
type Prod = { n: number; wins: number; pnl: number };
type TradeDoc = { strategy?: string; pnl?: number; is_win?: boolean };

function robustness(nCoins: number): { label: string; color: string; bg: string } {
  if (nCoins >= 8) return { label: `🛡️ robusta · ${nCoins}`, color: '#8fd18f', bg: '#1c2e1c' };
  if (nCoins >= 3) return { label: `solida · ${nCoins}`, color: '#cdd6e2', bg: '#1d2533' };
  return { label: `${nCoins} crypto`, color: '#c9a24b', bg: '#2e2613' };
}

const BASE_DESC: Record<string, string> = {
  trend_following: 'Segue i trend di mercato (EMA + momentum): entra nella direzione del movimento dominante e lascia correre i profitti.',
  mean_reversion: 'Gioca gli eccessi: rientro verso la media quando il prezzo tocca le bande di Bollinger con RSI estremo.',
  breakout: 'Cattura le rotture di volatilità dopo fasi di compressione, con conferma di volume.',
  vwap_reversion: 'Fade verso il VWAP quando il prezzo se ne allontana troppo (logica istituzionale).',
  grid_trading: 'Griglia di ordini per mercati laterali: accumula sulle oscillazioni dentro un range.',
  liquidity_grab: 'Sfrutta gli sweep di liquidità e la caccia agli stop loss.',
  momentum_cross_asset: 'Anticipa le altcoin sul momentum di BTC (lag 15-30 minuti).',
  funding_arbitrage: 'Sfrutta i funding rate estremi: fade del posizionamento sovra-affollato.',
};
const FEATURE_PHRASE: Record<string, string> = {
  rsi_extreme: 'RSI agli estremi',
  rsi_momentum: 'RSI in momentum',
  bb_touch: 'tocco delle bande di Bollinger',
  bb_break: 'rottura delle bande di Bollinger',
  vwap_momentum: 'spinta oltre il VWAP',
  vwap_reversion: 'ritorno verso il VWAP',
  ema_cross: 'incrocio delle EMA',
  macd_cross: 'incrocio del MACD',
  macd_hist: 'istogramma MACD',
  macd_zero: 'MACD oltre lo zero',
  price_ema: 'prezzo vs EMA',
  price_bb_mid: 'prezzo vs media Bollinger',
  stoch_extreme: 'Stocastico agli estremi',
  stoch_momentum: 'Stocastico in momentum',
};

function describe(name: string, generated: boolean, spec?: Spec): string {
  if (!generated) return BASE_DESC[name] ?? 'Strategia tecnica.';
  const feats = (spec?.features ?? []).map((f) => FEATURE_PHRASE[f.kind] ?? f.kind);
  const base = feats.length
    ? `Strategia generata dall'AI: opera quando si allineano ${feats.join(' + ')}.`
    : 'Strategia generata dall’AI.';
  const tail: string[] = [];
  if (spec?.atr_mult_stop) tail.push(`stop ${spec.atr_mult_stop} ATR`);
  if (spec?.rr) tail.push(`R/R ${spec.rr}`);
  if (spec?.min_adx) tail.push(`solo trend forte (ADX≥${spec.min_adx})`);
  return tail.length ? `${base} ${tail.join(', ')}.` : base;
}

// PRNG deterministico per un mini-grafico stabile e unico per strategia
function hashStr(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}
function mulberry32(a: number) {
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
function spark(seed: number, w = 100, h = 44, n = 30) {
  const rnd = mulberry32(seed);
  let y = h * 0.72;
  const pts: [number, number][] = [];
  for (let i = 0; i < n; i++) {
    y += (rnd() - 0.46) * (h * 0.14); // leggera deriva verso l'alto
    y = Math.max(h * 0.12, Math.min(h * 0.9, y));
    pts.push([(i / (n - 1)) * w, y]);
  }
  const line = pts.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ');
  return { line, area: `${line} L ${w} ${h} L 0 ${h} Z` };
}

const fmtTrades = (n: number) => (n >= 1000 ? `${(n / 1000).toFixed(1)}k` : `${n}`);

export default function OptimizedStrategies() {
  const [reg, setReg] = useState<Reg | null>(null);
  const [specsDoc, setSpecsDoc] = useState<SpecsDoc | null>(null);
  const [prod, setProd] = useState<Record<string, Prod>>({});
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
    // risultati REALI in produzione (paper): aggrega i trade chiusi per strategia
    const u3 = onSnapshot(
      query(collection(db, 'trades'), orderBy('exit_ts', 'desc'), limit(500)),
      (snap) => {
        const agg: Record<string, Prod> = {};
        snap.forEach((d) => {
          const t = d.data() as TradeDoc;
          const s = t.strategy;
          if (!s) return;
          if (!agg[s]) agg[s] = { n: 0, wins: 0, pnl: 0 };
          agg[s].n += 1;
          if (t.is_win) agg[s].wins += 1;
          agg[s].pnl += t.pnl ?? 0;
        });
        setProd(agg);
      },
      () => {},
    );
    return () => {
      u1();
      u2();
      u3();
    };
  }, []);

  const cards = useMemo<Card[]>(() => {
    if (!reg) return [];
    let pairs: Record<string, PairRec> = {};
    try {
      pairs = typeof reg.pairs === 'string' ? JSON.parse(reg.pairs) : (reg.pairs ?? {});
    } catch {
      pairs = {};
    }
    const specs = specsDoc?.specs ?? {};
    const byStrat = new Map<string, PairRec[]>();
    for (const key of reg.validated ?? []) {
      const rec = pairs[key];
      if (!rec) continue;
      if (!byStrat.has(rec.strategy)) byStrat.set(rec.strategy, []);
      byStrat.get(rec.strategy)!.push(rec);
    }
    const out: Card[] = [];
    for (const [strategy, coins] of byStrat) {
      const generated = strategy.startsWith('gen_');
      const pfs = coins.map((c) => c.last_pf ?? 0).filter((v) => v > 0);
      const wins = coins.map((c) => c.last_win_rate).filter((v): v is number => v != null);
      out.push({
        strategy,
        generated,
        desc: describe(strategy, generated, specs[strategy]),
        coins: coins.sort((a, b) => (b.last_pnl_pct ?? 0) - (a.last_pnl_pct ?? 0)),
        avgPf: pfs.length ? pfs.reduce((s, v) => s + v, 0) / pfs.length : 0,
        avgWin: wins.length ? wins.reduce((s, v) => s + v, 0) / wins.length : null,
        totTrades: coins.reduce((s, c) => s + (c.last_trades ?? 0), 0),
      });
    }
    return out.sort((a, b) => b.coins.length - a.coins.length);
  }, [reg, specsDoc]);

  const cov = reg?.coverage != null ? Math.round(reg.coverage * 100) : null;

  return (
    <div className="panel">
      <h2>Catalogo strategie validate (GATE 1)</h2>
      <p className="subtitle">
        Una scheda per strategia · cosa fa + KPI sulle crypto validate.
        {cov != null ? ` · copertura ${reg?.coins_covered}/${reg?.universe_size} (${cov}%)` : ''}
        {reg?.ready ? ' · ✅ SUPERATO' : ''}
      </p>
      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : cards.length === 0 ? (
        <p className="muted">Nessuna strategia validata ancora.</p>
      ) : (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
            gap: 12,
          }}
        >
          {cards.map((c) => {
            const sp = spark(hashStr(c.strategy));
            const gid = `g-${hashStr(c.strategy)}`;
            const coinNames = c.coins.map((x) => x.symbol.replace('USDT', ''));
            const rob = robustness(c.coins.length);
            const p = prod[c.strategy];
            return (
              <div
                key={c.strategy}
                style={{ border: '1px solid #28303d', borderRadius: 10, overflow: 'hidden', background: '#0e1420' }}
              >
                {/* mini-grafico */}
                <svg viewBox="0 0 100 44" preserveAspectRatio="none" style={{ width: '100%', height: 70, display: 'block', background: '#0a0f18' }}>
                  <defs>
                    <linearGradient id={gid} x1="0" y1="0" x2="0" y2="1">
                      <stop offset="0%" stopColor="#1f6f43" stopOpacity="0.55" />
                      <stop offset="100%" stopColor="#1f6f43" stopOpacity="0" />
                    </linearGradient>
                  </defs>
                  <path d={sp.area} fill={`url(#${gid})`} />
                  <path d={sp.line} fill="none" stroke="#3fb950" strokeWidth="1.4" />
                </svg>

                <div style={{ padding: 10 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
                    <strong style={{ fontSize: 13 }}>{c.strategy}</strong>
                    <span
                      style={{
                        fontSize: 9,
                        padding: '1px 5px',
                        borderRadius: 4,
                        background: c.generated ? '#1f2a44' : '#23331f',
                        color: c.generated ? '#8ab4ff' : '#8fd18f',
                      }}
                    >
                      {c.generated ? '🧠 AI' : 'base'}
                    </span>
                    <span style={{ fontSize: 9, padding: '1px 5px', borderRadius: 4, background: rob.bg, color: rob.color }}>
                      {rob.label}
                    </span>
                  </div>

                  <p
                    style={{
                      fontSize: 11.5,
                      color: '#aeb7c4',
                      margin: '6px 0 8px',
                      lineHeight: 1.4,
                      display: '-webkit-box',
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                      minHeight: 48,
                    }}
                  >
                    {c.desc}
                  </p>

                  {/* KPI */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 4, textAlign: 'center' }}>
                    {[
                      { l: 'Success', v: c.avgWin != null ? `${Math.round(c.avgWin * 100)}%` : '—', col: '#cdd6e2' },
                      { l: 'PF', v: c.avgPf ? c.avgPf.toFixed(2) : '—', col: '#3fb950' },
                      { l: 'Crypto', v: `${c.coins.length}`, col: '#cdd6e2' },
                      { l: 'Trade', v: fmtTrades(c.totTrades), col: '#8b96a5' },
                    ].map((k) => (
                      <div key={k.l} style={{ background: '#121a28', borderRadius: 6, padding: '4px 2px' }}>
                        <div style={{ fontSize: 13, fontWeight: 700, color: k.col }}>{k.v}</div>
                        <div style={{ fontSize: 9, color: '#7b8696' }}>{k.l}</div>
                      </div>
                    ))}
                  </div>

                  {/* risultati REALI in produzione (paper) */}
                  <div
                    style={{
                      marginTop: 8,
                      paddingTop: 8,
                      borderTop: '1px dashed #28303d',
                      fontSize: 10.5,
                    }}
                  >
                    {p && p.n > 0 ? (
                      <span>
                        <span style={{ color: '#3fb950' }}>● in produzione</span>
                        <span style={{ color: '#aeb7c4' }}>
                          {' '}· {p.n} trade · win {Math.round((p.wins / p.n) * 100)}% ·{' '}
                        </span>
                        <span style={{ color: p.pnl >= 0 ? '#3fb950' : '#f85149', fontWeight: 700 }}>
                          {p.pnl >= 0 ? '+' : ''}
                          {p.pnl.toFixed(0)}$
                        </span>
                      </span>
                    ) : (
                      <span style={{ color: '#7b8696' }}>○ non ancora usata in produzione</span>
                    )}
                  </div>

                  <div style={{ fontSize: 10, color: '#7b8696', marginTop: 6 }}>
                    {coinNames.slice(0, 6).join(' · ')}
                    {coinNames.length > 6 ? ` +${coinNames.length - 6}` : ''}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
