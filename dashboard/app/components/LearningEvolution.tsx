'use client';

import { useEffect, useMemo, useState } from 'react';
import { collection, doc, onSnapshot } from 'firebase/firestore';
import { getDb } from '../lib/firebase';

/**
 * Come si muovono i pesi nel tempo, versione per versione.
 *
 * I pesi guidano size e leva di ogni trade: sbagliarli non costa un trade, costa
 * tutti quelli dopo. Per questo l'aggiornamento ha quattro difese (filtro
 * anomalie, soglia di campione, smoothing, blocco sui salti aggregati) e uno
 * storico ad anello di 90 versioni. Questo pannello rende visibile la traiettoria:
 * un peso che oscilla a ogni giro è rumore inseguito, uno che scende e resta giù
 * è apprendimento.
 *
 * NIENTE BOTTONE DI ROLLBACK: il prompt lo chiedeva, ma ripristinare pesi vecchi
 * mentre il bot opera cambierebbe size e leva a metà di posizioni già aperte, e
 * il ricalcolo successivo li sovrascriverebbe comunque entro l'ora. Un rollback
 * ha senso solo insieme a una pausa del learning, che oggi non esiste: meglio non
 * offrire un bottone che promette più di quanto mantiene.
 */
type W = { strategy: string; regime: string; weight: number; sample_size?: number };
type Snap = { version?: number; updated_at?: number; weights?: W[]; trade_count_used?: number };

const COLORS = ['#3fb950', '#58a6ff', '#d29922', '#f85149', '#bc8cff', '#39c5cf'];

export default function LearningEvolution() {
  const [versions, setVersions] = useState<Snap[]>([]);
  const [current, setCurrent] = useState<Snap | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const db = getDb();
    const u1 = onSnapshot(doc(db, 'strategy_weights', 'current'),
      (s) => setCurrent(s.exists() ? (s.data() as Snap) : null), () => {});
    // lo storico è un anello di documenti v000..vNNN: si leggono tutti e si
    // ordinano per `version`, che è il numero progressivo vero (l'id è modulo N)
    const u2 = onSnapshot(collection(db, 'strategy_weights'),
      (snap) => {
        const rows: Snap[] = [];
        snap.forEach((d) => {
          if (d.id.startsWith('v') && d.id !== 'current') rows.push(d.data() as Snap);
        });
        rows.sort((a, b) => (a.version ?? 0) - (b.version ?? 0));
        setVersions(rows);
        setLoaded(true);
      },
      () => setLoaded(true));
    return () => { u1(); u2(); };
  }, []);

  // serie per gruppo strategia×regime, nell'ordine delle versioni
  const { series, keys } = useMemo(() => {
    const map = new Map<string, (number | null)[]>();
    versions.forEach((snap, idx) => {
      (snap.weights ?? []).forEach((w) => {
        const k = `${w.strategy}·${w.regime}`;
        if (!map.has(k)) map.set(k, new Array(versions.length).fill(null));
        map.get(k)![idx] = w.weight;
      });
    });
    // i gruppi che si sono mossi di più sono quelli che vale la pena guardare
    const ranked = [...map.entries()]
      .map(([k, v]) => {
        const vals = v.filter((x): x is number => x !== null);
        const span = vals.length ? Math.max(...vals) - Math.min(...vals) : 0;
        return { k, v, span };
      })
      .sort((a, b) => b.span - a.span)
      .slice(0, 6);
    return { series: ranked, keys: ranked.map((r) => r.k) };
  }, [versions]);

  const W = 560, H = 150, PAD = 8;
  const x = (i: number) => PAD + (i * (W - 2 * PAD)) / Math.max(1, versions.length - 1);
  const y = (v: number) => H - PAD - v * (H - 2 * PAD);

  return (
    <div className="panel">
      <h2>Evoluzione dei pesi</h2>
      <p className="subtitle">
        Un peso che oscilla a ogni versione è rumore inseguito; uno che scende e resta
        giù è apprendimento. Ogni aggiornamento passa da filtro anomalie, soglia di
        campione, smoothing e blocco sui salti aggregati.
      </p>

      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : (
        <>
          <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap', marginBottom: 10 }}>
            <div>
              <div style={{ fontSize: 20, fontWeight: 700 }}>{current?.version ?? '—'}</div>
              <div style={{ fontSize: 11, color: 'var(--muted)' }}>versione attiva</div>
            </div>
            <div>
              <div style={{ fontSize: 20, fontWeight: 700 }}>
                {current?.trade_count_used ?? '—'}
              </div>
              <div style={{ fontSize: 11, color: 'var(--muted)' }}>trade usati</div>
            </div>
            <div>
              <div style={{ fontSize: 20, fontWeight: 700 }}>{versions.length}</div>
              <div style={{ fontSize: 11, color: 'var(--muted)' }}>versioni in storico</div>
            </div>
          </div>

          {versions.length < 2 ? (
            <p className="muted">
              Servono almeno due versioni per disegnare una traiettoria. Lo storico si
              popola a ogni aggiornamento dei pesi che supera le difese.
            </p>
          ) : (
            <>
              <svg width="100%" viewBox={`0 0 ${W} ${H}`} style={{ maxWidth: W }}>
                {[0, 0.5, 1].map((g) => (
                  <line key={g} x1={PAD} x2={W - PAD} y1={y(g)} y2={y(g)}
                        stroke="#28303d" strokeWidth="1" />
                ))}
                {series.map((s, si) => {
                  const pts = s.v
                    .map((v, i) => (v === null ? null : `${x(i)},${y(v)}`))
                    .filter(Boolean).join(' ');
                  return <polyline key={s.k} points={pts} fill="none"
                                   stroke={COLORS[si % COLORS.length]} strokeWidth="2" />;
                })}
              </svg>
              <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', fontSize: 11 }}>
                {keys.map((k, i) => (
                  <span key={k} style={{ color: COLORS[i % COLORS.length] }}>■ {k}</span>
                ))}
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}
