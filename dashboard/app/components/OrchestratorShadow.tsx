'use client';

import { useEffect, useMemo, useState } from 'react';
import { collection, limit, onSnapshot, query } from 'firebase/firestore';
import { getDb } from '../lib/firebase';

/**
 * Cosa avrebbe deciso il modello, accanto a cosa ha fatto il bot.
 *
 * L'LLM gira in modalità OMBRA: riceve lo stesso contesto che avrebbe se
 * comandasse — segnali, regime, rischio aperto, allarmi — e la sua scelta viene
 * registrata. Non tocca nulla.
 *
 * Serve perché una decisione di un modello non è riproducibile, quindi non è
 * backtestabile: non potrebbe mai passare dal GATE 1, e l'unico modo di sapere se
 * aggiunge o distrugge valore sarebbe farla girare per mesi coi soldi. L'ombra
 * scioglie il nodo senza correre il rischio.
 *
 * Il numero da guardare è la riga VETO: sono i trade che il modello avrebbe
 * evitato. Quando ce ne saranno abbastanza si potrà verificare se hanno perso —
 * ed è quella verifica, non un'impressione, che sblocca il passo 2.
 */
type Shadow = {
  choice?: string | null;
  direction?: string | null;
  conviction?: number | null;
  reason?: string;
  primary_risk?: string;
  rejected?: string[];
  actual?: string | null;
  verdict?: string;
  regime?: string | null;
  signals_available?: number;
  at?: number;
};

const VERDICT: Record<string, { label: string; color: string; help: string }> = {
  agree: { label: 'stesso trade', color: 'var(--green)',
           help: 'il modello avrebbe scelto quello che il bot ha aperto' },
  different_pick: { label: 'trade diverso', color: 'var(--amber)',
                    help: 'avrebbe preso un altro segnale fra quelli disponibili' },
  shadow_only: { label: 'avrebbe operato', color: 'var(--amber)',
                 help: 'il bot è rimasto fermo, il modello avrebbe aperto' },
  shadow_veto: { label: 'VETO', color: 'var(--red)',
                 help: 'il bot ha aperto, il modello avrebbe evitato — è la riga che conta' },
  both_flat: { label: 'entrambi fermi', color: 'var(--muted)',
               help: 'nessuno dei due avrebbe operato' },
};

export default function OrchestratorShadow() {
  const [rows, setRows] = useState<Shadow[]>([]);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    const unsub = onSnapshot(
      query(collection(getDb(), 'ai_shadow'), limit(200)),
      (snap) => {
        const out: Shadow[] = [];
        snap.forEach((d) => out.push(d.data() as Shadow));
        out.sort((a, b) => (b.at ?? 0) - (a.at ?? 0));
        setRows(out);
        setLoaded(true);
      },
      () => setLoaded(true),
    );
    return () => unsub();
  }, []);

  const counts = useMemo(() => {
    const c: Record<string, number> = {};
    rows.forEach((r) => { c[r.verdict ?? '?'] = (c[r.verdict ?? '?'] ?? 0) + 1; });
    return c;
  }, [rows]);

  const last = rows[0];
  const cellStyle = { padding: '5px 8px' } as const;

  return (
    <div className="panel">
      <h2>Orchestratore — l&apos;LLM in ombra</h2>
      <p className="subtitle">
        Il modello riceve lo stesso contesto che avrebbe se comandasse e dice cosa
        farebbe. <b>Non tocca nulla</b>: una decisione di un modello non è riproducibile,
        quindi non è backtestabile — l&apos;ombra è l&apos;unico modo di misurarla senza rischiare.
      </p>

      {!loaded ? (
        <p className="muted">Loading…</p>
      ) : !rows.length ? (
        <>
          <p className="muted">
            Nessuna decisione in ombra ancora registrata. Si popola a ogni ciclo di
            decisione quando il bot opera con <code>ANTHROPIC_API_KEY</code> configurata
            e <code>AI_SHADOW_ENABLED=true</code>.
          </p>
          <p className="muted" style={{ fontSize: 12 }}>
            Finché il registro GATE 1 è vuoto e il kill switch è attivo il bot non
            decide, quindi non c&apos;è nulla da mettere in ombra: è corretto che resti vuoto.
          </p>
        </>
      ) : (
        <>
          <div style={{ display: 'flex', gap: 18, flexWrap: 'wrap', marginBottom: 12 }}>
            {Object.entries(VERDICT).map(([k, v]) => (
              <div key={k} title={v.help}>
                <div style={{ fontSize: 20, fontWeight: 700, color: v.color }}>
                  {counts[k] ?? 0}
                </div>
                <div style={{ fontSize: 11, color: 'var(--muted)' }}>{v.label}</div>
              </div>
            ))}
          </div>

          <p className="muted" style={{ fontSize: 12, marginTop: 0 }}>
            La riga da guardare è <b style={{ color: 'var(--red)' }}>VETO</b>: i trade che
            il modello avrebbe evitato. Quando saranno abbastanza si potrà verificare se
            hanno perso — ed è quella verifica, non un&apos;impressione, che sblocca il
            passo successivo.
          </p>

          {last && (
            <div style={{ border: '1px solid #28303d', borderRadius: 8,
                          padding: '10px 12px', margin: '10px 0' }}>
              <div style={{ fontSize: 12, color: 'var(--muted)' }}>ULTIMA DECISIONE</div>
              <div style={{ marginTop: 4 }}>
                <b>modello:</b>{' '}
                {last.choice
                  ? `${last.choice} ${last.direction ?? ''} (convinzione ${last.conviction ?? '—'})`
                  : 'nessun trade'}
                {' · '}
                <b>bot:</b> {last.actual ?? 'fermo'}
              </div>
              {last.reason && (
                <div style={{ fontSize: 13, marginTop: 6 }}>
                  <span style={{ color: 'var(--muted)' }}>motivo: </span>{last.reason}
                </div>
              )}
              {last.primary_risk && (
                <div style={{ fontSize: 13, marginTop: 4 }}>
                  <span style={{ color: 'var(--muted)' }}>rischio principale: </span>
                  {last.primary_risk}
                </div>
              )}
              {!!(last.rejected ?? []).length && (
                <div style={{ fontSize: 12, marginTop: 6, color: 'var(--muted)' }}>
                  scartati: {(last.rejected ?? []).join(' · ')}
                </div>
              )}
            </div>
          )}

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
              <thead>
                <tr style={{ textAlign: 'left', color: 'var(--muted)' }}>
                  <th style={cellStyle}>Quando</th>
                  <th style={cellStyle}>Modello</th>
                  <th style={cellStyle}>Bot</th>
                  <th style={cellStyle}>Esito</th>
                </tr>
              </thead>
              <tbody>
                {rows.slice(0, 20).map((r, i) => {
                  const v = VERDICT[r.verdict ?? ''] ?? { label: r.verdict ?? '—',
                                                          color: 'var(--muted)', help: '' };
                  return (
                    <tr key={i} style={{ borderTop: '1px solid #28303d' }}>
                      <td style={{ ...cellStyle, color: 'var(--muted)' }}>
                        {r.at ? new Date(r.at * 1000).toLocaleString('it-IT') : '—'}
                      </td>
                      <td style={cellStyle}>{r.choice ?? '—'}</td>
                      <td style={cellStyle}>{r.actual ?? '—'}</td>
                      <td style={{ ...cellStyle, color: v.color }} title={v.help}>
                        {v.label}
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
