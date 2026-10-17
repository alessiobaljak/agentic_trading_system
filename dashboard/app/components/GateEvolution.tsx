'use client';

import { useEffect, useMemo, useState } from 'react';
import { doc, onSnapshot } from 'firebase/firestore';
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { getDb } from '../lib/firebase';
import { CHROME, STATO, formatta } from '../lib/viz';

/**
 * L'EVOLVERSI DELLE VALIDATE — il fronte di validazione nel tempo.
 *
 * Il registro dice com'è il mondo adesso. Non dice se ieri le validate erano la
 * metà o il doppio, e quella è la differenza che conta: il fronte che CRESCE vuol
 * dire che la ricerca accumula evidenza; piatto mentre le coppie tracciate cambiano
 * vuol dire che entrano ed escono senza arrivare in fondo (il sintomo con cui si
 * è scoperto il difetto dei due orologi).
 *
 * RIDOTTO A UNA SERIE (25 set 2026). Le tre serie (1 conferma, 2 conferme,
 * validate) stavano su scale diverse di due ordini di grandezza e servivano tre
 * riquadri; con 160 validate la sola serie che risponde alla domanda «sta
 * arrivando in fondo?» è questa. Le altre due fasce vivono nell'imbuto qui sopra
 * (che le mostra come stock) e nella maturazione della scheda Strategie.
 */
type Punto = {
  at: number;
  tracked?: number;
  validated?: number;
  frozen?: number;
  dist?: Record<string, number>;
};
type Doc = { points?: Punto[]; min_passes?: number };
type Riga = { t: number; label: string; ok: number; tracked: number; frozen: number };

const PERIODI = [
  { id: '7g', label: '7 giorni', giorni: 7 },
  { id: '30g', label: '30 giorni', giorni: 30 },
  { id: 'tutto', label: 'Tutto', giorni: Infinity },
] as const;
type PeriodoId = (typeof PERIODI)[number]['id'];

function label(ts: number): string {
  return new Date(ts * 1000).toLocaleString('it-IT', {
    day: '2-digit', month: 'short', hour: '2-digit',
  });
}

export default function GateEvolution() {
  const [d, setD] = useState<Doc | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [periodo, setPeriodo] = useState<PeriodoId>('30g');

  useEffect(() => {
    try {
      return onSnapshot(
        doc(getDb(), 'gate_history', 'timeline'),
        (s) => { setD(s.exists() ? (s.data() as Doc) : null); setLoaded(true); },
        () => setLoaded(true),
      );
    } catch {
      setLoaded(true);
      return;
    }
  }, []);

  const tutte: Riga[] = useMemo(() => {
    return [...(d?.points ?? [])]
      .filter((p) => p?.at)
      .sort((a, b) => a.at - b.at)
      .map((p) => ({
        t: p.at, label: label(p.at),
        ok: Number(p.validated ?? p.dist?.['3'] ?? 0),
        tracked: Number(p.tracked ?? 0),
        frozen: Number(p.frozen ?? 0),
      }));
  }, [d]);

  const righe = useMemo(() => {
    const g = PERIODI.find((p) => p.id === periodo)?.giorni ?? Infinity;
    if (!Number.isFinite(g) || tutte.length === 0) return tutte;
    const taglio = tutte[tutte.length - 1].t - g * 86400;
    return tutte.filter((r) => r.t >= taglio);
  }, [tutte, periodo]);

  const ultimo = righe[righe.length - 1];
  const primo = righe[0];
  const delta = ultimo && primo ? ultimo.ok - primo.ok : 0;
  const piatta = righe.every((r) => r.ok === 0);

  return (
    <div className="panel">
      <h2>Validate nel tempo</h2>
      <p className="subtitle">
        Quante coppie hanno le tre conferme, giorno per giorno. Una conferma richiede una
        settimana di dati nuovi: il movimento è lento per costruzione, conta la <b>direzione</b>.
      </p>

      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center', marginBottom: 8 }}>
        {PERIODI.map((p) => (
          <button
            key={p.id}
            onClick={() => setPeriodo(p.id)}
            className={`btn ${periodo === p.id ? 'btn-primary' : 'btn-ghost'}`}
            style={{ padding: '4px 12px', fontSize: 12 }}
            aria-pressed={periodo === p.id}
          >
            {p.label}
          </button>
        ))}
        <span style={{ flex: 1 }} />
        {ultimo && (
          <span style={{ fontSize: 12 }}>
            <span aria-hidden="true" style={{ width: 8, height: 8, borderRadius: 2, background: STATO.buono, display: 'inline-block', marginRight: 6 }} />
            <b style={{ fontSize: 18, lineHeight: 1 }}>{formatta(ultimo.ok)}</b>
            <span className="muted"> validate · {delta >= 0 ? '+' : ''}{delta} nel periodo · {formatta(ultimo.tracked)} tracciate</span>
            {ultimo.frozen > 0 && (
              <span className="muted" title="coppie ferme: la coin è uscita dall'universo, non avanzano e non falliscono">
                {' '}· {formatta(ultimo.frozen)} congelate
              </span>
            )}
          </span>
        )}
      </div>

      {!loaded ? (
        <p className="muted">Caricamento…</p>
      ) : tutte.length === 0 ? (
        <p className="muted">
          Nessuna storia ancora. Il primo punto lo scrive il supervisore al prossimo giro
          (ogni ora); optimizer e discovery ne aggiungono altri ogni 3 ore.
        </p>
      ) : (
        <ResponsiveContainer width="100%" height={90}>
          <LineChart data={righe} margin={{ top: 4, right: 6, left: 0, bottom: 0 }}>
            <CartesianGrid stroke={CHROME.griglia} vertical={false} />
            <XAxis dataKey="label" stroke={CHROME.asse} fontSize={10} tickLine={false} minTickGap={64} />
            <YAxis
              stroke={CHROME.asse}
              fontSize={10}
              tickLine={false}
              width={34}
              allowDecimals={false}
              // una serie ferma a zero, con dominio automatico, disegna una riga a metà
              // riquadro: sembra un valore. Ancorarla a 0..1 la tiene sul fondo, dov'è.
              domain={piatta ? [0, 1] : ['auto', 'auto']}
            />
            <Tooltip
              cursor={{ stroke: CHROME.asse, strokeWidth: 1 }}
              contentStyle={{
                background: 'var(--bg-elev)',
                border: '1px solid var(--border)',
                borderRadius: 8,
                fontSize: 12,
              }}
              formatter={(v: number) => [formatta(v), 'validate']}
            />
            <Line
              type="monotone"
              dataKey="ok"
              name="validate"
              stroke={STATO.buono}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, strokeWidth: 2, stroke: CHROME.superficie }}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
