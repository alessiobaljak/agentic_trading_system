'use client';

import { useEffect, useMemo, useState } from 'react';
import { doc, onSnapshot } from 'firebase/firestore';
import { getDb } from '../lib/firebase';
import type { StrategyWeightsDoc, StrategyWeight } from '../lib/types';
import { STATO, formatta, numero, quota } from '../lib/viz';

/**
 * Pesi adattivi (0..1) per strategia × regime, letti come DECISIONE e non come
 * voto (25 set 2026).
 *
 * Prima il colore diceva «in forma / sotto osservazione / penalizzata» con soglie
 * 0,9 e 0,7 che non corrispondevano a niente nel bot. La soglia che conta e'
 * UNA: sotto 0,5 il peso moltiplica la convinzione del segnale (60 di base) sotto
 * la soglia dell'orchestratore (30), quindi quella strategia in quel regime NON
 * apre piu' trade: e' in panchina. A 0 e' spenta. E' la stessa regola con cui il
 * controllo orario conta `pesi.in_panchina_n` (docs/controllo_schema.md §1.4),
 * cosi' i due pannelli dicono lo stesso numero.
 *
 * Win rate e campione stanno nel documento e prima non si vedevano: un peso 0,4
 * su 3 trade e un peso 0,4 su 40 trade non sono la stessa informazione.
 */
const SOGLIA_PANCHINA = 0.5;

type Stato = 'attivo' | 'panchina' | 'spenta';

function statoDi(w: number): Stato {
  if (w <= 0) return 'spenta';
  if (w < SOGLIA_PANCHINA) return 'panchina';
  return 'attivo';
}

const STILE: Record<Stato, { label: string; colore: string }> = {
  attivo: { label: 'ATTIVO', colore: STATO.buono },
  panchina: { label: 'in panchina', colore: STATO.attenzione },
  spenta: { label: 'spenta', colore: STATO.critico },
};

export default function StrategyWeights() {
  const [doc_, setDoc] = useState<StrategyWeightsDoc | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const db = getDb();
    const unsub = onSnapshot(
      doc(db, 'strategy_weights', 'current'),
      (snap) => {
        setDoc(snap.exists() ? (snap.data() as StrategyWeightsDoc) : null);
        setLoaded(true);
      },
      () => setLoaded(true),
    );
    return () => unsub();
  }, []);

  // ordinati per peso, i piu' bassi in cima: la domanda e' «chi e' in panchina?»
  const rows = useMemo(() => {
    const weights: StrategyWeight[] = doc_?.weights ?? [];
    return [...weights].sort(
      (a, b) => (a.weight ?? 0) - (b.weight ?? 0) || String(a.strategy).localeCompare(String(b.strategy)),
    );
  }, [doc_]);

  const conta = useMemo(() => {
    const c = { attivo: 0, panchina: 0, spenta: 0 };
    for (const w of rows) c[statoDi(w.weight ?? 0)] += 1;
    return c;
  }, [rows]);

  const cell = { padding: '5px 8px', whiteSpace: 'nowrap' } as const;

  return (
    <div className="panel">
      <h2>Peso appreso · strategia × regime</h2>
      <p className="subtitle">
        Quanto il learning si fida di ogni combinazione (0..1). <b>Peso sotto 0,5 = strategia in
        panchina in quel regime</b>: non apre trade finche&apos; il peso non risale. In cima le piu&apos; basse.
      </p>
      {!loaded ? (
        <p className="muted">Caricamento…</p>
      ) : rows.length === 0 ? (
        <p className="muted">Nessun peso pubblicato ancora.</p>
      ) : (
        <>
          <div className="muted" style={{ fontSize: 12, marginBottom: 8 }}>
            <span style={{ color: STILE.attivo.colore, fontWeight: 600 }}>{formatta(conta.attivo)} attive</span>
            {' '}· <span style={{ color: STILE.panchina.colore, fontWeight: 600 }}>{formatta(conta.panchina)} in panchina</span>
            {' '}· <span style={{ color: STILE.spenta.colore, fontWeight: 600 }}>{formatta(conta.spenta)} spente</span>
            {' '}su {formatta(rows.length)} combinazioni
          </div>
          <div style={{ maxHeight: 420, overflow: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12.5 }}>
              <thead>
                <tr className="muted" style={{ position: 'sticky', top: 0, background: 'var(--bg-panel)' }}>
                  <th style={{ ...cell, textAlign: 'left' }}>strategia · regime</th>
                  <th style={{ ...cell, textAlign: 'left', minWidth: 120 }}>peso</th>
                  <th style={cell} title="quota di trade vinti da cui viene il peso">win rate</th>
                  <th style={cell} title="quanti trade hanno contribuito al peso (0 = in prova, in rientro)">campione</th>
                  <th style={{ ...cell, textAlign: 'left' }}>stato</th>
                </tr>
              </thead>
              <tbody>
                {rows.map((w) => {
                  const wt = w.weight ?? 0;
                  const st = statoDi(wt);
                  const inProva = (w.sample_size ?? 0) === 0 && wt < 1;
                  return (
                    <tr key={`${w.strategy}|${w.regime}`} style={{ borderTop: '1px solid var(--border-soft)' }}>
                      <td className="mono" style={{ ...cell, textAlign: 'left' }}>
                        {w.strategy} <span className="muted">· {w.regime}</span>
                      </td>
                      <td style={{ ...cell, textAlign: 'left' }}>
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                          <span className="bucket-track" style={{ width: 80, display: 'inline-block' }}>
                            <span
                              className="bucket-fill"
                              style={{ width: `${Math.max(0, Math.min(1, wt)) * 100}%`, background: STILE[st].colore, display: 'block' }}
                            />
                          </span>
                          <span className="mono" style={{ color: STILE[st].colore, fontWeight: 700 }}>{numero(wt, 2)}</span>
                        </span>
                      </td>
                      <td style={cell}>{w.win_rate == null ? <span className="muted">—</span> : quota(w.win_rate)}</td>
                      <td style={cell}>{w.sample_size == null ? <span className="muted">—</span> : formatta(w.sample_size)}</td>
                      <td style={{ ...cell, textAlign: 'left' }}>
                        <span style={{ color: STILE[st].colore, fontWeight: 650 }}>{STILE[st].label}</span>
                        {inProva ? (
                          <span className="wtag" style={{ background: 'var(--amber-soft)', color: 'var(--amber)', marginLeft: 6 }}>
                            in prova
                          </span>
                        ) : null}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
