'use client';

import { useEffect, useMemo, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { collection, limit, onSnapshot, orderBy, query } from 'firebase/firestore';
import { getDb, getRtdb } from '../lib/firebase';
import type { Position } from '../lib/types';
import PositionChart from './PositionChart';
import PositionMetrics from './PositionMetrics';
import Positions from './Positions';
import ClosedTrades from './ClosedTrades';

/**
 * Scheda Operatività: grafico prezzo SEMPRE visibile in cima (con selettore coin),
 * metriche quando la coin selezionata è una posizione aperta, poi le tabelle
 * posizioni aperte e trade chiusi. Cliccando una riga (aperta o chiusa) il grafico
 * si punta su quella coin. SOLO lettura + il comando di chiusura già esistente.
 */
export default function OperativitaTab() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [tradeSyms, setTradeSyms] = useState<string[]>([]);
  const [selected, setSelected] = useState<string>('');

  useEffect(() => {
    const u1 = onValue(ref(getRtdb(), 'positions'), (snap) => {
      const val = snap.val() as Record<string, Position> | null;
      const list = val
        ? Object.entries(val).map(([sym, p]) => ({ ...p, symbol: p.symbol ?? sym }))
        : [];
      list.sort((a, b) => (a.symbol > b.symbol ? 1 : -1));
      setPositions(list);
    });
    // simboli distinti dai trade chiusi recenti, per il selettore del grafico
    const q = query(collection(getDb(), 'trades'), orderBy('exit_ts', 'desc'), limit(200));
    const u2 = onSnapshot(
      q,
      (snap) => {
        const seen: string[] = [];
        snap.forEach((d) => {
          const s = (d.data() as { symbol?: string }).symbol;
          if (s && !seen.includes(s)) seen.push(s);
        });
        setTradeSyms(seen);
      },
      () => undefined,
    );
    return () => {
      u1();
      u2();
    };
  }, []);

  const openSyms = useMemo(() => positions.map((p) => p.symbol), [positions]);
  const otherSyms = useMemo(
    () => tradeSyms.filter((s) => !openSyms.includes(s)),
    [tradeSyms, openSyms],
  );

  // default: prima posizione aperta -> primo trade chiuso -> BTCUSDT
  useEffect(() => {
    if (selected) return;
    const def = openSyms[0] || tradeSyms[0] || 'BTCUSDT';
    if (def) setSelected(def);
  }, [openSyms, tradeSyms, selected]);

  const selectedPos = positions.find((p) => p.symbol === selected) || null;

  return (
    <>
      <div className="panel">
        <div className="detail-head" style={{ marginBottom: 12 }}>
          <div>
            <h2 style={{ margin: 0 }}>Grafico</h2>
            <p className="subtitle" style={{ margin: '4px 0 0' }}>
              Prezzo live (TradingView) · scegli la coin o clicca una riga sotto
            </p>
          </div>
          <select
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
            aria-label="coin del grafico"
          >
            {openSyms.length > 0 && (
              <optgroup label="Posizioni aperte">
                {openSyms.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </optgroup>
            )}
            {otherSyms.length > 0 && (
              <optgroup label="Trade chiusi">
                {otherSyms.map((s) => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </optgroup>
            )}
            {openSyms.length === 0 && otherSyms.length === 0 && (
              <option value="BTCUSDT">BTCUSDT</option>
            )}
          </select>
        </div>

        {selectedPos ? (
          <PositionMetrics position={selectedPos} />
        ) : (
          <p className="muted" style={{ fontSize: 12, marginTop: 0, marginBottom: 10 }}>
            {selected} · nessuna posizione aperta su questa coin (metriche operative solo per le posizioni aperte).
          </p>
        )}

        {selected && (
          <div className="detail-chart" style={{ height: 460 }}>
            <PositionChart symbol={selected} interval="60" />
          </div>
        )}
      </div>

      <Positions onSelect={(p) => setSelected(p.symbol)} />
      <ClosedTrades onSelect={(s) => setSelected(s)} />
    </>
  );
}
