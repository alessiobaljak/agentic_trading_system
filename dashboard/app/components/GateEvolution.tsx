'use client';

import { useEffect, useMemo, useState } from 'react';
import { doc, onSnapshot } from 'firebase/firestore';
import {
  Area,
  AreaChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { getDb } from '../lib/firebase';

/**
 * L'EVOLVERSI DELLE STRATEGIE — il fronte di validazione nel tempo.
 *
 * Il registro dice com'è il mondo adesso: tante coppie tracciate, tante a un
 * passaggio, zero validate. Non dice se ieri erano la metà o il doppio, e quella è
 * l'unica differenza che conta davvero:
 *
 *   * la fascia "1 passaggio" che CRESCE  -> la ricerca sta accumulando evidenza;
 *   * la stessa fascia che resta piatta mentre le coppie tracciate cambiano ->
 *     entrano ed escono senza mai arrivare in fondo, ed è il sintomo con cui si è
 *     scoperto il difetto dei due orologi (il purge cancellava le coppie prima che
 *     la conferma successiva potesse arrivare);
 *   * la fascia "validata" che si stacca da zero -> il gate ha prodotto qualcosa.
 *
 * All'epoca quel sintomo si poteva vedere solo confrontando a mano schermate di
 * giorni diversi. Da qui si legge in un colpo d'occhio.
 *
 * I colori sono una SCALA, non categorie: più il passaggio è avanzato, più il
 * colore è acceso. L'ultima fascia è verde perché "validata" non è "un passaggio in
 * più", è uno stato di arrivo. L'identità non è mai affidata al solo colore —
 * legenda e tooltip riportano sempre l'etichetta.
 */
type Point = {
  at: number;
  src?: string;
  tracked?: number;
  validated?: number;
  evaluated?: number;
  passed?: number;
  dist?: Record<string, number>;
};
type Doc = { points?: Point[]; min_passes?: number; updated_at?: number };

type Row = { t: number; label: string; p0: number; p1: number; p2: number; ok: number; tracked: number };

const SERIE = [
  { key: 'p0', label: '0 passaggi', color: '#2a4a73' },
  { key: 'p1', label: '1 passaggio', color: '#3f7fd0' },
  { key: 'p2', label: '2 passaggi', color: '#4f9cf9' },
  { key: 'ok', label: 'validata', color: '#3fb950' },
] as const;

function label(ts: number): string {
  return new Date(ts * 1000).toLocaleString('it-IT', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
  });
}

export default function GateEvolution() {
  const [d, setD] = useState<Doc | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    try {
      return onSnapshot(
        doc(getDb(), 'gate_history', 'timeline'),
        (s) => {
          setD(s.exists() ? (s.data() as Doc) : null);
          setLoaded(true);
        },
        () => setLoaded(true),
      );
    } catch {
      setLoaded(true);
      return;
    }
  }, []);

  const rows: Row[] = useMemo(() => {
    const pts = (d?.points ?? []).filter((p) => p?.at);
    return pts
      .slice()
      .sort((a, b) => a.at - b.at)
      .map((p) => {
        const dist = p.dist ?? {};
        const n = (k: string) => Number(dist[k] ?? 0);
        return {
          t: p.at,
          label: label(p.at),
          p0: n('0'),
          p1: n('1'),
          p2: n('2'),
          ok: Number(p.validated ?? n('3')),
          tracked: Number(p.tracked ?? 0),
        };
      });
  }, [d]);

  const ultimo = rows[rows.length - 1];
  const primo = rows[0];
  /** La domanda vera: il fronte a un passaggio sta crescendo o si sta rinnovando? */
  const delta1 = ultimo && primo ? ultimo.p1 - primo.p1 : 0;

  return (
    <div className="panel">
      <h2>Evoluzione del GATE 1</h2>
      <p className="subtitle">
        Quante coppie hanno accumulato quante conferme, giorno per giorno. Una conferma
        richiede una settimana di dati nuovi, quindi il movimento è lento per
        costruzione: quello che conta è la <b>direzione</b>.
      </p>

      {!loaded ? (
        <p className="muted">Caricamento…</p>
      ) : rows.length === 0 ? (
        <p className="muted">
          Nessuna storia ancora. Il primo punto viene scritto alla prossima passata
          dell&apos;optimizer (ogni 3 ore); servono qualche giorno di punti perché il
          grafico dica qualcosa.
        </p>
      ) : (
        <>
          <div
            style={{
              display: 'flex',
              gap: 18,
              flexWrap: 'wrap',
              marginBottom: 10,
              fontSize: 13,
            }}
          >
            <span>
              coppie tracciate <b>{ultimo.tracked.toLocaleString('it-IT')}</b>
            </span>
            <span>
              a 1 passaggio <b>{ultimo.p1.toLocaleString('it-IT')}</b>{' '}
              <span className="muted">
                ({delta1 >= 0 ? '+' : ''}
                {delta1} da {primo.label})
              </span>
            </span>
            <span>
              a 2 passaggi <b>{ultimo.p2.toLocaleString('it-IT')}</b>
            </span>
            <span style={{ color: ultimo.ok > 0 ? 'var(--green)' : undefined }}>
              validate <b>{ultimo.ok.toLocaleString('it-IT')}</b>
            </span>
          </div>

          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={rows} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
              <CartesianGrid stroke="#1c2740" strokeDasharray="3 3" />
              <XAxis
                dataKey="label"
                stroke="#5f6d84"
                fontSize={11}
                tickLine={false}
                minTickGap={48}
              />
              <YAxis stroke="#5f6d84" fontSize={11} tickLine={false} width={52} />
              <Tooltip
                contentStyle={{
                  background: 'var(--bg-elev)',
                  border: '1px solid var(--border)',
                  borderRadius: 8,
                  fontSize: 12,
                }}
              />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              {SERIE.map((s) => (
                <Area
                  key={s.key}
                  type="monotone"
                  dataKey={s.key}
                  name={s.label}
                  stackId="1"
                  stroke={s.color}
                  strokeWidth={2}
                  fill={s.color}
                  fillOpacity={0.32}
                />
              ))}
            </AreaChart>
          </ResponsiveContainer>

          <p className="muted" style={{ fontSize: 11, marginTop: 8 }}>
            Le coppie oltre la soglia sono contate come «validata». Il fondo del grafico
            (0 passaggi) è la popolazione che il gate ha visto ma non ha mai promosso: è
            normale che sia la stragrande maggioranza.
          </p>
        </>
      )}
    </div>
  );
}
