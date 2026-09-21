'use client';

import { useEffect, useRef, useState } from 'react';
import {
  createChart,
  ColorType,
  CrosshairMode,
  LineStyle,
  type IChartApi,
  type ISeriesApi,
  type IPriceLine,
  type SeriesMarker,
  type Time,
  type UTCTimestamp,
} from 'lightweight-charts';
import type { Position } from '../lib/types';
import type { Trade } from './ClosedTrades';

/**
 * Grafico a candele NATIVO della dashboard (lightweight-charts). Il canvas non
 * legge il CSS, quindi i colori vengono presi dai token del tema a runtime
 * (`getComputedStyle`): un solo posto decide i colori, anche per il grafico.
 *
 * Overlay: per una POSIZIONE APERTA entry/SL/gradini; per un TRADE CHIUSO entry
 * ed exit come linee E come marker sul tempo, con la finestra temporale centrata
 * sul trade — richiesta del proprietario del 21 set 2026 («voglio vedere il
 * grafico anche delle posizioni chiuse quando ci clicco»).
 */
const TFS: { id: string; label: string; sec: number }[] = [
  { id: '5m', label: '5m', sec: 300 },
  { id: '15m', label: '15m', sec: 900 },
  { id: '1h', label: '1h', sec: 3600 },
  { id: '4h', label: '4h', sec: 14400 },
  { id: '1d', label: '1D', sec: 86400 },
];

type C = { time: UTCTimestamp; open: number; high: number; low: number; close: number };
type V = { time: UTCTimestamp; value: number; color: string };

function token(name: string, fallback: string): string {
  if (typeof window === 'undefined') return fallback;
  const v = getComputedStyle(document.documentElement).getPropertyValue(name).trim();
  return v || fallback;
}

async function fetchKlines(
  symbol: string, interval: string, up: string, down: string,
  endMs?: number,
): Promise<{ c: C[]; v: V[] }> {
  const url =
    `https://fapi.binance.com/fapi/v1/klines?symbol=${encodeURIComponent(symbol)}` +
    `&interval=${interval}&limit=400` + (endMs ? `&endTime=${endMs}` : '');
  const res = await fetch(url);
  if (!res.ok) throw new Error(`klines ${res.status}`);
  const raw = (await res.json()) as unknown[][];
  const c: C[] = [];
  const v: V[] = [];
  for (const k of raw) {
    const time = Math.floor(Number(k[0]) / 1000) as UTCTimestamp;
    const open = Number(k[1]);
    const close = Number(k[4]);
    c.push({ time, open, high: Number(k[2]), low: Number(k[3]), close });
    v.push({ time, value: Number(k[5]), color: close >= open ? up + '59' : down + '59' });
  }
  return { c, v };
}

/** Timeframe che mostra il trade intero con contesto: ~25 candele di durata. */
function tfForTrade(t: Trade): string {
  const entry = t.entry_time ? new Date(t.entry_time).getTime() / 1000 : undefined;
  if (!entry || !t.exit_ts) return '15m';
  const dur = Math.max(60, t.exit_ts - entry);
  const pick = TFS.find((x) => dur / x.sec <= 25) ?? TFS[TFS.length - 1];
  return pick.id;
}

export default function CandleChart({
  symbol,
  position,
  trade,
  height = 460,
}: {
  symbol: string;
  position?: Position | null;
  trade?: Trade | null;
  height?: number;
}) {
  const wrapRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleRef = useRef<ISeriesApi<'Candlestick'> | null>(null);
  const volRef = useRef<ISeriesApi<'Histogram'> | null>(null);
  const linesRef = useRef<IPriceLine[]>([]);
  const legendRef = useRef<HTMLDivElement>(null);
  const [interval, setInterval] = useState('1h');
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const colors = useRef({
    up: token('--green', '#16a34a'), down: token('--red', '#dc2626'),
    text: token('--text-dim', '#475569'), border: token('--border', '#c7d1de'),
    panel: token('--bg-panel', '#ffffff'), accent: token('--accent', '#2563eb'),
  });

  // un trade chiuso sceglie il timeframe che lo mostra intero
  const tradeKey = trade ? `${trade.trade_id ?? ''}|${trade.exit_ts ?? ''}` : '';
  useEffect(() => {
    if (trade) setInterval(tfForTrade(trade));
  }, [tradeKey]); // eslint-disable-line react-hooks/exhaustive-deps

  // crea il chart UNA volta
  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const k = colors.current;
    const chart = createChart(el, {
      autoSize: true,
      layout: {
        background: { type: ColorType.Solid, color: k.panel },
        textColor: k.text,
        fontFamily: "ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
        fontSize: 11,
      },
      grid: {
        vertLines: { color: 'rgba(15,23,42,0.06)' },
        horzLines: { color: 'rgba(15,23,42,0.06)' },
      },
      crosshair: { mode: CrosshairMode.Normal },
      rightPriceScale: { borderColor: k.border },
      timeScale: { borderColor: k.border, timeVisible: true, secondsVisible: false },
    });
    const candle = chart.addCandlestickSeries({
      upColor: k.up, downColor: k.down, wickUpColor: k.up, wickDownColor: k.down,
      borderVisible: false,
    });
    const vol = chart.addHistogramSeries({ priceFormat: { type: 'volume' }, priceScaleId: 'vol' });
    chart.priceScale('vol').applyOptions({ scaleMargins: { top: 0.82, bottom: 0 } });

    chart.subscribeCrosshairMove((param) => {
      const leg = legendRef.current;
      if (!leg) return;
      const d = param.seriesData.get(candle) as C | undefined;
      if (!d) { leg.textContent = ''; return; }
      const col = d.close >= d.open ? k.up : k.down;
      leg.innerHTML =
        `<span style="color:${k.text}">O</span> ${d.open}  ` +
        `<span style="color:${k.text}">H</span> ${d.high}  ` +
        `<span style="color:${k.text}">L</span> ${d.low}  ` +
        `<span style="color:${k.text}">C</span> <span style="color:${col};font-weight:700">${d.close}</span>`;
    });

    chartRef.current = chart; candleRef.current = candle; volRef.current = vol;
    return () => {
      chart.remove();
      chartRef.current = null; candleRef.current = null; volRef.current = null; linesRef.current = [];
    };
  }, []);

  // carica i dati al cambio symbol/interval/trade: per un trade chiuso le
  // candele finiscono un po' DOPO l'uscita, cosi' si vede anche cosa e' successo poi
  useEffect(() => {
    let cancelled = false;
    setErr(null); setLoading(true);
    const tf = TFS.find((x) => x.id === interval)?.sec ?? 3600;
    const endMs = trade?.exit_ts ? (trade.exit_ts + tf * 40) * 1000 : undefined;
    fetchKlines(symbol, interval, colors.current.up, colors.current.down, endMs)
      .then(({ c, v }) => {
        if (cancelled || !candleRef.current || !volRef.current) return;
        candleRef.current.setData(c);
        volRef.current.setData(v);
        const ts = chartRef.current?.timeScale();
        const entry = trade?.entry_time ? new Date(trade.entry_time).getTime() / 1000 : undefined;
        if (ts && trade?.exit_ts && entry) {
          const pad = Math.max((trade.exit_ts - entry) * 0.6, tf * 8);
          ts.setVisibleRange({ from: (entry - pad) as UTCTimestamp, to: (trade.exit_ts + pad) as UTCTimestamp });
        } else {
          ts?.fitContent();
        }
        setLoading(false);
      })
      .catch(() => {
        if (cancelled) return;
        setErr('Grafico non disponibile (Binance non raggiungibile dal browser).');
        setLoading(false);
      });
    return () => { cancelled = true; };
  }, [symbol, interval, tradeKey]); // eslint-disable-line react-hooks/exhaustive-deps

  // overlay: posizione aperta (entry/SL/gradini) oppure trade chiuso (entry/exit)
  useEffect(() => {
    const candle = candleRef.current;
    if (!candle) return;
    for (const l of linesRef.current) candle.removePriceLine(l);
    linesRef.current = [];
    candle.setMarkers([]);
    const k = colors.current;
    const add = (price: number | undefined, color: string, title: string, dashed: boolean) => {
      if (price == null || !Number.isFinite(price) || price <= 0) return;
      linesRef.current.push(candle.createPriceLine({
        price, color, lineWidth: 1,
        lineStyle: dashed ? LineStyle.Dashed : LineStyle.Solid,
        axisLabelVisible: true, title,
      }));
    };
    if (position) {
      add(position.entry_price, k.accent, 'Entry', false);
      add(position.stop_price, k.down, 'SL', true);
      const ladder = position.tp_ladder;
      if (ladder && ladder.length > 0) ladder.forEach((t, i) => add(t.price, k.up, `TP${i + 1}`, !t.hit));
      else add(position.take_profit_price, k.up, 'TP', true);
      return;
    }
    if (trade) {
      const long = trade.direction?.toLowerCase() === 'long';
      const win = (trade.pnl ?? 0) >= 0;
      add(trade.entry_price, k.accent, `Entry ${long ? 'long' : 'short'}`, false);
      add(trade.exit_price, win ? k.up : k.down, `Exit ${win ? '+' : ''}${(trade.pnl ?? 0).toFixed(2)}`, false);
      add(trade.stop_price, k.down, 'SL', true);
      add(trade.take_profit_price, k.up, 'TP', true);
      const entryTs = trade.entry_time ? Math.floor(new Date(trade.entry_time).getTime() / 1000) : undefined;
      const tf = TFS.find((x) => x.id === interval)?.sec ?? 3600;
      const snap = (t: number) => (Math.floor(t / tf) * tf) as UTCTimestamp;
      const markers: SeriesMarker<Time>[] = [];
      if (entryTs) markers.push({
        time: snap(entryTs), position: long ? 'belowBar' : 'aboveBar',
        color: k.accent, shape: long ? 'arrowUp' : 'arrowDown', text: 'IN',
      });
      if (trade.exit_ts) markers.push({
        time: snap(trade.exit_ts), position: long ? 'aboveBar' : 'belowBar',
        color: win ? k.up : k.down, shape: 'circle', text: 'OUT',
      });
      markers.sort((a, b) => Number(a.time) - Number(b.time));
      candle.setMarkers(markers);
    }
  }, [position, trade, tradeKey, symbol, interval, loading]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div>
      <div className="chart-toolbar">
        <div className="seg" role="tablist" aria-label="timeframe">
          {TFS.map((t) => (
            <button key={t.id} className={interval === t.id ? 'on' : ''} onClick={() => setInterval(t.id)}>
              {t.label}
            </button>
          ))}
        </div>
        <div ref={legendRef} className="chart-legend mono" />
      </div>
      <div className="chart-canvas" style={{ height }}>
        <div ref={wrapRef} style={{ position: 'absolute', inset: 0 }} />
        {loading && !err && <div className="chart-overlay muted">Caricamento grafico…</div>}
        {err && <div className="chart-overlay muted">{err}</div>}
      </div>
    </div>
  );
}
