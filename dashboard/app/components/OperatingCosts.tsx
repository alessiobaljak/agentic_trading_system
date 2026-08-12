'use client';

import { useEffect, useMemo, useState } from 'react';
import { collection, limit, onSnapshot, orderBy, query } from 'firebase/firestore';
import { getDb } from '../lib/firebase';

/**
 * Quanto costa operare, e quanto serve rendere solo per pareggiare.
 *
 * Il PnL netto è un numero solo e nasconde il conto: due sistemi con lo stesso
 * risultato possono avere costi molto diversi, e quello coi costi alti è molto
 * più fragile — basta un edge leggermente peggiore e va sotto.
 *
 * Il caso più insidioso è "lordo positivo, netto negativo": il mercato ti ha dato
 * ragione e il conto se l'è mangiato. Senza questa scomposizione sembrerebbe una
 * strategia che non funziona, e si andrebbe a cercare il problema nel posto
 * sbagliato.
 *
 * In DRY_RUN sono STIME dal modello del gate, non misure dai fill di Binance: il
 * pannello lo dichiara, perché al passaggio ai soldi veri la differenza fra i due
 * numeri sarà essa stessa un'informazione.
 */
type Trade = {
  symbol?: string;
  pnl?: number;
  commission_usdt?: number;
  spread_usdt?: number;
  funding_paid_usdt?: number;
  total_cost_usdt?: number;
  gross_pnl_usdt?: number;
  costs_are_estimated?: boolean;
};

const MAX = 500;
const START_EQUITY = 1000;

export default function OperatingCosts() {
  const [rows, setRows] = useState<Trade[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const q = query(collection(getDb(), 'trades'), orderBy('exit_ts', 'desc'), limit(MAX));
    const unsub = onSnapshot(
      q,
      (snap) => { setRows(snap.docs.map((d) => d.data() as Trade)); setLoaded(true); },
      () => setLoaded(true),
    );
    return () => unsub();
  }, []);

  const r = useMemo(() => {
    const withCost = rows.filter((t) => t.total_cost_usdt != null);
    if (!withCost.length) return null;
    const sum = (f: (t: Trade) => number) => withCost.reduce((a, t) => a + f(t), 0);
    const bySymbol = new Map<string, number>();
    withCost.forEach((t) => {
      const k = t.symbol ?? '?';
      bySymbol.set(k, (bySymbol.get(k) ?? 0) + Number(t.total_cost_usdt ?? 0));
    });
    return {
      n: withCost.length,
      commission: sum((t) => Number(t.commission_usdt ?? 0)),
      spread: sum((t) => Number(t.spread_usdt ?? 0)),
      funding: sum((t) => Number(t.funding_paid_usdt ?? 0)),
      total: sum((t) => Number(t.total_cost_usdt ?? 0)),
      gross: sum((t) => Number(t.gross_pnl_usdt ?? 0)),
      net: sum((t) => Number(t.pnl ?? 0)),
      estimated: withCost.every((t) => t.costs_are_estimated !== false),
      top: [...bySymbol.entries()].sort((a, b) => b[1] - a[1]).slice(0, 6),
    };
  }, [rows]);

  if (!loaded) return <div className="panel"><h2>Costi</h2><p className="muted">Loading…</p></div>;
  if (!r) {
    return (
      <div className="panel">
        <h2>Costi operativi</h2>
        <p className="muted">
          Nessun trade con i costi scomposti. Il dettaglio si popola sui trade chiusi
          dopo l&apos;aggiornamento del bot: quelli precedenti hanno solo il PnL netto.
        </p>
      </div>
    );
  }

  const breakEven = (r.total / START_EQUITY) * 100;
  const eaten = r.gross > 0 && r.net <= 0;
  const cellStyle = { padding: '5px 8px' } as const;

  return (
    <div className="panel">
      <h2>Costi operativi</h2>
      <p className="subtitle">
        Quanto è costato operare, voce per voce. Il <b>break-even</b> è quanto il sistema
        deve rendere <i>solo</i> per coprire ciò che spende: se è alto, il problema non è
        la strategia ma il numero di trade o le coin scelte.
      </p>

      {r.estimated && (
        <p className="muted" style={{ fontSize: 12, marginTop: 0 }}>
          ⚪ Valori <b>stimati</b> dal modello di costo del gate (fee, spread per fascia di
          liquidità, funding al tasso reale della coin), non misurati dai fill: in paper
          non esistono fill veri.
        </p>
      )}

      <div style={{ display: 'flex', gap: 22, flexWrap: 'wrap', margin: '8px 0 14px' }}>
        <Stat label="lordo" value={`${r.gross >= 0 ? '+' : ''}${r.gross.toFixed(2)}`}
              color={r.gross >= 0 ? 'var(--green)' : 'var(--red)'} />
        <Stat label="costi totali" value={`−${r.total.toFixed(2)}`} color="var(--amber)" />
        <Stat label="netto" value={`${r.net >= 0 ? '+' : ''}${r.net.toFixed(2)}`}
              color={r.net >= 0 ? 'var(--green)' : 'var(--red)'} />
        <Stat label="break-even" value={`${breakEven.toFixed(2)}%`} />
        <Stat label="costo medio/trade" value={(r.total / r.n).toFixed(3)} />
      </div>

      {eaten && (
        <p style={{ color: 'var(--red)', fontSize: 13, marginTop: 0 }}>
          Il lordo è positivo ma il netto no: il risultato lo mangiano i costi, non il
          mercato. Cercare il problema nella strategia sarebbe cercarlo nel posto sbagliato.
        </p>
      )}

      <div className="grid grid-2">
        <div>
          <div style={{ fontSize: 12, color: 'var(--muted)', fontWeight: 600 }}>
            COMPOSIZIONE
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <tbody>
              {([['commissioni', r.commission], ['spread', r.spread],
                 ['funding', r.funding]] as const).map(([k, v]) => (
                <tr key={k}>
                  <td style={cellStyle}>{k}</td>
                  <td style={{ ...cellStyle, textAlign: 'right' }}>{v.toFixed(2)}</td>
                  <td style={{ ...cellStyle, textAlign: 'right', color: 'var(--muted)' }}>
                    {r.total ? `${Math.round((v / r.total) * 100)}%` : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div>
          <div style={{ fontSize: 12, color: 'var(--muted)', fontWeight: 600 }}>
            COIN PIÙ COSTOSE
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
            <tbody>
              {r.top.map(([sym, v]) => (
                <tr key={sym}>
                  <td style={cellStyle}>{sym}</td>
                  <td style={{ ...cellStyle, textAlign: 'right' }}>{v.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <p className="muted" style={{ fontSize: 11, marginTop: 8 }}>
        Su {r.n} trade con i costi tracciati (ultimi {MAX} chiusi).
      </p>
    </div>
  );
}

function Stat({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div>
      <div style={{ fontSize: 20, fontWeight: 700, color: color ?? 'var(--text)' }}>
        {value}
      </div>
      <div style={{ fontSize: 11, color: 'var(--muted)' }}>{label}</div>
    </div>
  );
}
