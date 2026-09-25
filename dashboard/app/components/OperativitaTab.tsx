'use client';

import { useEffect, useMemo, useRef, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { collection, limit, onSnapshot, orderBy, query } from 'firebase/firestore';
import { getDb, getRtdb } from '../lib/firebase';
import type { Position } from '../lib/types';
import CandleChart from './CandleChart';
import PositionMetrics from './PositionMetrics';
import Positions from './Positions';
import ClosedTrades, { type Trade } from './ClosedTrades';

/**
 * Scheda Operatività: PRIMA le posizioni aperte, poi i trade chiusi, e in fondo
 * il grafico, chiuso di default (25 set 2026).
 *
 * Il grafico stava in cima e apriva la scheda con 460 px di candele scaricate
 * da Binance — un dato ESTERNO, che dalla rete della VPS spesso non arriva (22
 * set: riquadro bianco) e che sul telefono spinge le tabelle sotto la piega. Le
 * domande che si fanno aprendo la scheda sono «cosa e' aperto» e «com'e' andata»:
 * stanno nelle tabelle. Il grafico si apre a richiesta, e le righe delle tabelle
 * lo aprono e lo puntano sulla loro coin.
 *
 * IL DIFETTO DEL «SEMPRE BTC» (21 set 2026) resta risolto come prima: la scelta
 * automatica segue la prima posizione aperta (o l'ultimo trade chiuso) finche'
 * l'utente non ne fa una sua.
 */
export default function OperativitaTab() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [lastTrades, setLastTrades] = useState<Trade[]>([]);
  const [selected, setSelected] = useState<string>('');
  const [userChose, setUserChose] = useState(false);
  const [trade, setTrade] = useState<Trade | null>(null);
  const [grafico, setGrafico] = useState(false);
  const graficoRef = useRef<HTMLDetailsElement>(null);

  useEffect(() => {
    const u1 = onValue(ref(getRtdb(), 'positions'), (snap) => {
      const val = snap.val() as Record<string, Position> | null;
      const list = val
        ? Object.entries(val).map(([sym, p]) => ({ ...p, symbol: p.symbol ?? sym }))
        : [];
      list.sort((a, b) => (a.symbol > b.symbol ? 1 : -1));
      setPositions(list);
    });
    const q = query(collection(getDb(), 'trades'), orderBy('exit_ts', 'desc'), limit(200));
    const u2 = onSnapshot(q, (snap) => {
      setLastTrades(snap.docs.map((d) => d.data() as Trade));
    }, () => undefined);
    return () => { u1(); u2(); };
  }, []);

  const openSyms = useMemo(() => positions.map((p) => p.symbol), [positions]);
  const tradeSyms = useMemo(() => {
    const seen: string[] = [];
    for (const t of lastTrades) if (t.symbol && !seen.includes(t.symbol)) seen.push(t.symbol);
    return seen;
  }, [lastTrades]);
  const otherSyms = useMemo(() => tradeSyms.filter((s) => !openSyms.includes(s)), [tradeSyms, openSyms]);

  // scelta automatica: segue i dati finche' l'utente non sceglie lui
  useEffect(() => {
    if (userChose) return;
    if (openSyms.length > 0) { setSelected(openSyms[0]); setTrade(null); return; }
    if (lastTrades.length > 0) { setSelected(lastTrades[0].symbol); setTrade(lastTrades[0]); return; }
  }, [openSyms, lastTrades, userChose]);

  const choose = (sym: string, t: Trade | null) => {
    setUserChose(true);
    setSelected(sym);
    setTrade(t);
  };

  /** Dalle tabelle: sceglie la coin, apre il grafico e ci scorre sopra. */
  const mostra = (sym: string, t: Trade | null) => {
    choose(sym, t);
    setGrafico(true);
    window.setTimeout(() => graficoRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' }), 50);
  };

  const selectedPos = positions.find((p) => p.symbol === selected) || null;
  // se la coin scelta ha una posizione aperta, il grafico mostra quella (piu' utile
  // del trade chiuso); altrimenti il trade chiuso cliccato
  const shownTrade = selectedPos ? null : trade && trade.symbol === selected ? trade : null;

  return (
    <>
      <Positions onSelect={(p) => mostra(p.symbol, null)} />
      <ClosedTrades onSelect={(t) => mostra(t.symbol, t)} />

      <details
        ref={graficoRef}
        className="panel"
        open={grafico}
        onToggle={(e) => setGrafico((e.currentTarget as HTMLDetailsElement).open)}
      >
        <summary style={{ cursor: 'pointer' }}>
          <span style={{ fontSize: 15, fontWeight: 650 }}>Grafico</span>
          <span className="muted" style={{ fontSize: 12, marginLeft: 8 }}>
            {selected || 'BTCUSDT'} · candele da Binance (dato esterno, si carica solo se apri)
          </span>
        </summary>

        {/* il contenuto vive solo da aperto: niente fetch a Binance finche' non serve */}
        {grafico ? (
          <div style={{ marginTop: 12 }}>
            <div className="detail-head" style={{ marginBottom: 12 }}>
              <p className="subtitle" style={{ margin: 0 }}>
                {shownTrade
                  ? `${shownTrade.symbol} · ${shownTrade.strategy} · ${shownTrade.direction} · trade chiuso, entry e uscita sul grafico`
                  : 'Prezzo live · scegli la coin o clicca una riga sopra (aperta o chiusa)'}
              </p>
              <select value={selected || 'BTCUSDT'} onChange={(e) => choose(e.target.value, null)} aria-label="coin del grafico">
                {openSyms.length > 0 && (
                  <optgroup label="Posizioni aperte">
                    {openSyms.map((s) => <option key={s} value={s}>{s}</option>)}
                  </optgroup>
                )}
                {otherSyms.length > 0 && (
                  <optgroup label="Trade chiusi">
                    {otherSyms.map((s) => <option key={s} value={s}>{s}</option>)}
                  </optgroup>
                )}
                {openSyms.length === 0 && otherSyms.length === 0 && <option value="BTCUSDT">BTCUSDT</option>}
              </select>
            </div>

            {selectedPos ? (
              <PositionMetrics position={selectedPos} />
            ) : shownTrade ? (
              <p className="muted" style={{ fontSize: 12, marginTop: 0, marginBottom: 10 }}>
                Ingresso {shownTrade.entry_price ?? '—'} · Uscita {shownTrade.exit_price ?? '—'} ·{' '}
                <span className={(shownTrade.pnl ?? 0) >= 0 ? 'pos' : 'neg'} style={{ fontWeight: 700 }}>
                  {(shownTrade.pnl ?? 0) >= 0 ? '+' : ''}{(shownTrade.pnl ?? 0).toFixed(2)}
                </span>
                {' '}· {shownTrade.exit_reason}
              </p>
            ) : (
              <p className="muted" style={{ fontSize: 12, marginTop: 0, marginBottom: 10 }}>
                {selected || 'BTCUSDT'} · nessuna posizione aperta su questa coin.
              </p>
            )}

            <CandleChart symbol={selected || 'BTCUSDT'} position={selectedPos} trade={shownTrade} height={400} />
          </div>
        ) : null}
      </details>
    </>
  );
}
