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
  type UTCTimestamp,
} from 'lightweight-charts';
import type { Position } from '../lib/types';

/**
 * Grafico a candele NATIVO della dashboard (lightweight-charts), tematizzato coi
 * token del design system: nessuna chrome/branding esterno. Dati dalle klines
 * Binance futures (come Closed Trades). Overlay entry/SL/TP per la posizione.
 */
const TFS: { id: string; label: string }[] = [
  { id: '5m', label: '5m' },
  { id: '15m', label: '15m' },
  { id: '1h', label: '1h' },
  { id: '4h', label: '4h' },
  { id: '1d', label: '1D' },
];

type C = { time: UTCTimestamp; open: number; high: number; low: number; close: number };
type V = { time: UTCTimestamp; value: number; color: string };

async function fetchKlines(symbol: string, interval: string): Promise<{ c: C[]; v: V[] }> {
  const url =
    `https://fapi.binance.com/fapi/v1/klines?symbol=${encodeURIComponent(symbol)}` +
    `&interval=${interval}&limit=400`;
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
    v.push({ time, value: Number(k[5]), color: close >= open ? 'rgba(63,185,80,0.35)' : 'rgba(248,81,73,0.35)' });
  }
  return { c, v };
}

export default function CandleChart({
  symbol,
  position,
  height = 460,
}: {
  symbol: string;
  position?: Position | null;
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

  // crea il chart UNA volta
  useEffect(() => {
    const el = wrapRef.current;
    if (!el) return;
    const chart = createChart(el, {
      autoSize: true,
      layout: {
        background: { type: ColorType.Solid, color: '#0e1524' },
        textColor: '#93a0b5',
        fontFamily: "ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif",
        fontSize: 11,
      },
      grid: {
        vertLines: { color: 'rgba(40,48,61,0.35)' },
        horzLines: { color: 'rgba(40,48,61,0.35)' },
      },
      crosshair: { mode: CrosshairMode.Normal },
      rightPriceScale: { borderColor: '#26324a' },
      timeScale: { borderColor: '#26324a', timeVisible: true, secondsVisible: false },
    });
    const candle = chart.addCandlestickSeries({
      upColor: '#3fb950',
      downColor: '#f85149',
      wickUpColor: '#3fb950',
      wickDownColor: '#f85149',
      borderVisible: false,
    });
    const vol = chart.addHistogramSeries({
      priceFormat: { type: 'volume' },
      priceScaleId: 'vol',
    });
    chart.priceScale('vol').applyOptions({ scaleMargins: { top: 0.82, bottom: 0 } });

    chart.subscribeCrosshairMove((param) => {
      const leg = legendRef.current;
      if (!leg) return;
      const d = param.seriesData.get(candle) as C | undefined;
      if (!d) {
        leg.textContent = '';
        return;
      }
      const up = d.close >= d.open;
      const col = up ? '#3fb950' : '#f85149';
      leg.innerHTML =
        `<span style="color:#93a0b5">O</span> ${d.open}  ` +
        `<span style="color:#93a0b5">H</span> ${d.high}  ` +
        `<span style="color:#93a0b5">L</span> ${d.low}  ` +
        `<span style="color:#93a0b5">C</span> <span style="color:${col};font-weight:700">${d.close}</span>`;
    });

    chartRef.current = chart;
    candleRef.current = candle;
    volRef.current = vol;
    return () => {
      chart.remove();
      chartRef.current = null;
      candleRef.current = null;
      volRef.current = null;
      linesRef.current = [];
    };
  }, []);

  // carica i dati al cambio symbol/interval
  useEffect(() => {
    let cancelled = false;
    setErr(null);
    setLoading(true);
    fetchKlines(symbol, interval)
      .then(({ c, v }) => {
        if (cancelled || !candleRef.current || !volRef.current) return;
        candleRef.current.setData(c);
        volRef.current.setData(v);
        chartRef.current?.timeScale().fitContent();
        setLoading(false);
      })
      .catch(() => {
        if (cancelled) return;
        setErr('Grafico non disponibile (Binance non raggiungibile dal browser).');
        setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [symbol, interval]);

  // overlay entry/SL/TP della posizione aperta
  useEffect(() => {
    const candle = candleRef.current;
    if (!candle) return;
    for (const l of linesRef.current) candle.removePriceLine(l);
    linesRef.current = [];
    if (!position) return;
    const add = (price: number | undefined, color: string, title: string, dashed: boolean) => {
      if (price == null || !Number.isFinite(price) || price <= 0) return;
      linesRef.current.push(
        candle.createPriceLine({
          price,
          color,
          lineWidth: 1,
          lineStyle: dashed ? LineStyle.Dashed : LineStyle.Solid,
          axisLabelVisible: true,
          title,
        }),
      );
    };
    add(position.entry_price, '#7db6ff', 'Entry', false);
    add(position.stop_price, '#f85149', 'SL', true);
    add(position.take_profit_price, '#3fb950', 'TP', true);
  }, [position, symbol, interval, loading]);

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
