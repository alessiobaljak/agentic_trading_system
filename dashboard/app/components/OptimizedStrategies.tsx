'use client';

import { useEffect, useMemo, useState } from 'react';
import { collection, doc, limit, onSnapshot, orderBy, query } from 'firebase/firestore';
import { getDb } from '../lib/firebase';

/**
 * Catalogo strategie. Vista PRODUZIONE (default): solo le strategie che hanno
 * davvero tradato in paper, con la loro EQUITY CURVE reale (PnL cumulato) e i
 * risultati veri. Toggle per vedere anche tutte le validate (GATE 1).
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
};
type Feature = { kind: string } & Record<string, unknown>;
type Spec = { features?: Feature[]; volume_mult?: number; min_adx?: number; atr_mult_stop?: number; rr?: number };
type SpecsDoc = { specs?: Record<string, Spec> };
type Prod = { n: number; wins: number; pnl: number; points: Array<[number, number]> }; // [exit_ts, pnl]
type TradeDoc = { strategy?: string; pnl?: number; is_win?: boolean; exit_ts?: number };
type Card = {
  strategy: string;
  generated: boolean;
  desc: string;
  coins: PairRec[];
  avgPf: number;
  totTrades: number;
  validatedNow: boolean;
  simProfit10k: number;   // profitto GATE 1 simulando 10k (media per coin), in $
  bestProfit10k: number;  // miglior coin, in $
};

const GATE_EQUITY = 10_000;
// PnL economico GATE 1 su una equity di 10k: last_pnl_pct e' la somma dei rendimenti
// per-trade OOS, coerente col motore (SimTrade.pnl = pnl_pct * 10k).
const profit10k = (r: PairRec) => (r.last_pnl_pct ?? 0) * GATE_EQUITY;
const fmtMoney = (v: number) => `${v >= 0 ? '+' : ''}$${Math.round(v).toLocaleString()}`;

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
  return tail.length ? `${base} ${tail.join(', ')}.` : base;
}

function robustness(nCoins: number): { label: string; color: string; bg: string } {
  if (nCoins >= 8) return { label: `🛡️ robusta · ${nCoins}`, color: '#8fd18f', bg: '#1c2e1c' };
  if (nCoins >= 3) return { label: `solida · ${nCoins}`, color: '#cdd6e2', bg: '#1d2533' };
  return { label: `${nCoins} crypto`, color: '#c9a24b', bg: '#2e2613' };
}
function hashStr(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) {
    h ^= s.charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

// equity curve REALE dal PnL cumulato dei trade in produzione
function realSpark(points: Array<[number, number]>, w = 100, h = 44) {
  const ordered = [...points].sort((a, b) => a[0] - b[0]);
  const cum: number[] = [0];
  for (const [, pnl] of ordered) cum.push(cum[cum.length - 1] + pnl);
  const min = Math.min(...cum);
  const max = Math.max(...cum);
  const range = max - min || 1;
  const n = cum.length;
  const pts = cum.map((v, i) => {
    const x = n > 1 ? (i / (n - 1)) * w : w / 2;
    const y = h - 6 - ((v - min) / range) * (h - 12);
    return [x, y] as [number, number];
  });
  const line = pts.map((p, i) => `${i ? 'L' : 'M'}${p[0].toFixed(1)} ${p[1].toFixed(1)}`).join(' ');
  return { line, area: `${line} L ${w} ${h} L 0 ${h} Z`, positive: cum[cum.length - 1] >= 0 };
}

const fmtTrades = (n: number) => (n >= 1000 ? `${(n / 1000).toFixed(1)}k` : `${n}`);

export default function OptimizedStrategies() {
  const [reg, setReg] = useState<Reg | null>(null);
  const [specsDoc, setSpecsDoc] = useState<SpecsDoc | null>(null);
  const [prod, setProd] = useState<Record<string, Prod>>({});
  const [view, setView] = useState<'prod' | 'all'>('prod');
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
    const u3 = onSnapshot(
      query(collection(db, 'trades'), orderBy('exit_ts', 'desc'), limit(500)),
      (snap) => {
        const agg: Record<string, Prod> = {};
        snap.forEach((d) => {
          const t = d.data() as TradeDoc;
          const s = t.strategy;
          if (!s) return;
          if (!agg[s]) agg[s] = { n: 0, wins: 0, pnl: 0, points: [] };
          agg[s].n += 1;
          if (t.is_win) agg[s].wins += 1;
          agg[s].pnl += t.pnl ?? 0;
          agg[s].points.push([t.exit_ts ?? 0, t.pnl ?? 0]);
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
      const profits = coins.map(profit10k);
      out.push({
        strategy,
        generated,
        desc: describe(strategy, generated, specs[strategy]),
        coins: coins.sort((a, b) => (b.last_pnl_pct ?? 0) - (a.last_pnl_pct ?? 0)),
        avgPf: pfs.length ? pfs.reduce((s, v) => s + v, 0) / pfs.length : 0,
        totTrades: coins.reduce((s, c) => s + (c.last_trades ?? 0), 0),
        validatedNow: true,
        simProfit10k: profits.length ? profits.reduce((s, v) => s + v, 0) / profits.length : 0,
        bestProfit10k: profits.length ? Math.max(...profits) : 0,
      });
    }
    return out.sort((a, b) => b.coins.length - a.coins.length);
  }, [reg, specsDoc]);

  // vista PRODUZIONE: parte da CHI HA TRADATO (anche se non più validato ora),
  // arricchita coi dati di validazione dove ci sono. Lo storico reale non sparisce.
  const prodCards = useMemo<Card[]>(() => {
    const byStrat = new Map(cards.map((c) => [c.strategy, c]));
    return Object.keys(prod)
      .filter((s) => (prod[s]?.n ?? 0) > 0)
      .map((s) => {
        const c = byStrat.get(s);
        const generated = s.startsWith('gen_');
        return (
          c ?? {
            strategy: s,
            generated,
            desc: describe(s, generated, specsDoc?.specs?.[s]),
            coins: [] as PairRec[],
            avgPf: 0,
            totTrades: 0,
            validatedNow: false,
            simProfit10k: 0,
            bestProfit10k: 0,
          }
        );
      })
      .sort((a, b) => (prod[b.strategy].pnl ?? 0) - (prod[a.strategy].pnl ?? 0));
  }, [cards, prod, specsDoc]);

  const shown = view === 'prod' ? prodCards : cards;

  const cov = reg?.coverage != null ? Math.round(reg.coverage * 100) : null;
  const btn = (active: boolean): React.CSSProperties => ({
    fontSize: 11,
    padding: '3px 10px',
    borderRadius: 6,
    cursor: 'pointer',
    border: '1px solid #28303d',
    background: active ? '#1f2a44' : 'transparent',
    color: active ? '#cfe0ff' : '#8b96a5',
  });

  return (
    <div className="panel">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 8 }}>
        <h2 style={{ margin: 0 }}>Catalogo strategie</h2>
        <div style={{ display: 'flex', gap: 6 }}>
          <button style={btn(view === 'prod')} onClick={() => setView('prod')}>In produzione</button>
          <button style={btn(view === 'all')} onClick={() => setView('all')}>Tutte le validate</button>
        </div>
      </div>
      <p className="subtitle">
        {view === 'prod'
          ? 'Solo strategie che hanno tradato in paper · grafico = equity curve reale'
          : 'Tutte le coppie validate dal GATE 1'}
        {cov != null ? ` · copertura ${reg?.coins_covered}/${reg?.universe_size} (${cov}%)` : ''}
      </p>
      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : shown.length === 0 ? (
        <p className="muted">
          {view === 'prod'
            ? 'Nessuna strategia ancora in produzione: i primi trade paper compariranno qui.'
            : 'Nessuna strategia validata ancora.'}
        </p>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 12 }}>
          {shown.map((c) => {
            const gid = `g-${hashStr(c.strategy)}`;
            const coinNames = c.coins.map((x) => x.symbol.replace('USDT', ''));
            const rob = robustness(c.coins.length);
            const p = prod[c.strategy];
            const curve = p && p.points.length ? realSpark(p.points) : null;
            const stroke = curve ? (curve.positive ? '#3fb950' : '#f85149') : '#2a3340';
            return (
              <div key={c.strategy} style={{ border: '1px solid #28303d', borderRadius: 10, overflow: 'hidden', background: '#0e1420' }}>
                {/* equity curve REALE (o piatta se nessun trade) */}
                <svg viewBox="0 0 100 44" preserveAspectRatio="none" style={{ width: '100%', height: 70, display: 'block', background: '#0a0f18' }}>
                  {curve ? (
                    <>
                      <defs>
                        <linearGradient id={gid} x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor={stroke} stopOpacity="0.5" />
                          <stop offset="100%" stopColor={stroke} stopOpacity="0" />
                        </linearGradient>
                      </defs>
                      <path d={curve.area} fill={`url(#${gid})`} />
                      <path d={curve.line} fill="none" stroke={stroke} strokeWidth="1.4" />
                    </>
                  ) : (
                    <>
                      <line x1="0" y1="36" x2="100" y2="36" stroke="#2a3340" strokeWidth="1" strokeDasharray="2 2" />
                      <text x="50" y="24" fill="#5a6473" fontSize="6" textAnchor="middle">nessun trade ancora</text>
                    </>
                  )}
                </svg>

                <div style={{ padding: 10 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
                    <strong style={{ fontSize: 13 }}>{c.strategy}</strong>
                    <span style={{ fontSize: 9, padding: '1px 5px', borderRadius: 4, background: c.generated ? '#1f2a44' : '#23331f', color: c.generated ? '#8ab4ff' : '#8fd18f' }}>
                      {c.generated ? '🧠 AI' : 'base'}
                    </span>
                    {c.validatedNow ? (
                      <span style={{ fontSize: 9, padding: '1px 5px', borderRadius: 4, background: rob.bg, color: rob.color }}>{rob.label}</span>
                    ) : (
                      <span style={{ fontSize: 9, padding: '1px 5px', borderRadius: 4, background: '#33261b', color: '#c98b4b' }}>storico · non validata ora</span>
                    )}
                  </div>

                  <p style={{ fontSize: 11.5, color: '#aeb7c4', margin: '6px 0 8px', lineHeight: 1.4, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical', overflow: 'hidden', minHeight: 48 }}>
                    {c.desc}
                  </p>

                  {/* PRODUZIONE: i risultati reali in primo piano */}
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 4, textAlign: 'center' }}>
                    {[
                      { l: 'PnL', v: p ? `${p.pnl >= 0 ? '+' : ''}${p.pnl.toFixed(0)}$` : '—', col: p ? (p.pnl >= 0 ? '#3fb950' : '#f85149') : '#7b8696' },
                      { l: 'Win', v: p && p.n ? `${Math.round((p.wins / p.n) * 100)}%` : '—', col: '#cdd6e2' },
                      { l: 'Trade', v: p ? `${p.n}` : '0', col: '#cdd6e2' },
                      { l: 'PF bt', v: c.avgPf ? c.avgPf.toFixed(2) : '—', col: '#8b96a5' },
                    ].map((k) => (
                      <div key={k.l} style={{ background: '#121a28', borderRadius: 6, padding: '4px 2px' }}>
                        <div style={{ fontSize: 13, fontWeight: 700, color: k.col }}>{k.v}</div>
                        <div style={{ fontSize: 9, color: '#7b8696' }}>{k.l}</div>
                      </div>
                    ))}
                  </div>

                  {/* GATE 1: profitto economico simulando 10k di equity di partenza */}
                  {c.validatedNow && c.coins.length > 0 && (
                    <div style={{
                      marginTop: 8, padding: '6px 8px', borderRadius: 6,
                      background: c.simProfit10k >= 0 ? '#11210f' : '#27120f',
                      border: `1px solid ${c.simProfit10k >= 0 ? '#214d1d' : '#5a2620'}`,
                      display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                    }}>
                      <div>
                        <div style={{ fontSize: 14, fontWeight: 700, color: c.simProfit10k >= 0 ? '#3fb950' : '#f85149' }}>
                          {fmtMoney(c.simProfit10k)}
                        </div>
                        <div style={{ fontSize: 9, color: '#7b8696' }}>GATE 1 su $10k · media/coin</div>
                      </div>
                      <div style={{ textAlign: 'right' }}>
                        <div style={{ fontSize: 11, fontWeight: 600, color: '#8fd18f' }}>{fmtMoney(c.bestProfit10k)}</div>
                        <div style={{ fontSize: 9, color: '#7b8696' }}>miglior coin</div>
                      </div>
                    </div>
                  )}

                  <div style={{ fontSize: 10, color: '#7b8696', marginTop: 8 }}>
                    {c.validatedNow ? (
                      <>
                        Validata su {c.coins.length}: {coinNames.slice(0, 5).join(' · ')}
                        {coinNames.length > 5 ? ` +${coinNames.length - 5}` : ''}
                      </>
                    ) : (
                      'Non più nel GATE 1 · qui resta lo storico reale in produzione'
                    )}
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
