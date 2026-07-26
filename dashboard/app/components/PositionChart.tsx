'use client';

import { useEffect, useRef } from 'react';

/**
 * Grafico prezzo professionale (candlestick, tutti i timeframe, indicatori) via
 * widget TradingView. SOLO visualizzazione: nessun dato del bot, nessuna scrittura.
 * Le coin del bot sono perpetual USDT di Binance -> simbolo BINANCE:<SYM>.P.
 */
export default function PositionChart({
  symbol,
  interval = '60',
  height = '100%',
}: {
  symbol: string;
  interval?: string;
  height?: string | number;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    el.innerHTML = '';
    const widget = document.createElement('div');
    widget.className = 'tradingview-widget-container__widget';
    widget.style.height = '100%';
    widget.style.width = '100%';
    el.appendChild(widget);

    const script = document.createElement('script');
    script.src =
      'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
    script.type = 'text/javascript';
    script.async = true;
    script.innerHTML = JSON.stringify({
      autosize: true,
      symbol: `BINANCE:${symbol}.P`,
      interval,
      timezone: 'Etc/UTC',
      theme: 'dark',
      style: '1', // candele
      locale: 'it',
      backgroundColor: 'rgba(14, 21, 36, 1)',
      gridColor: 'rgba(40, 48, 61, 0.5)',
      hide_side_toolbar: false,
      allow_symbol_change: false,
      calendar: false,
      support_host: 'https://www.tradingview.com',
    });
    el.appendChild(script);

    return () => {
      el.innerHTML = '';
    };
  }, [symbol, interval]);

  return (
    <div
      ref={ref}
      className="tradingview-widget-container"
      style={{ height, width: '100%' }}
    />
  );
}
