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
import { CHROME, GATE_RAMP, STATO, formatta } from '../lib/viz';

/**
 * L'EVOLVERSI DELLE STRATEGIE — il fronte di validazione nel tempo.
 *
 * Il registro dice com'è il mondo adesso. Non dice se ieri le coppie a un passaggio
 * erano la metà o il doppio, e quella è l'unica differenza che conta:
 *
 *   * il fronte che CRESCE  -> la ricerca sta accumulando evidenza;
 *   * il fronte piatto mentre le coppie tracciate cambiano -> entrano ed escono senza
 *     arrivare in fondo. È il sintomo con cui si è scoperto il difetto dei due
 *     orologi, e all'epoca lo si poteva vedere solo confrontando a mano schermate di
 *     giorni diversi.
 *
 * PERCHÉ TRE GRAFICI E NON UNO. Le tre serie stanno su scale che differiscono di due
 * ordini di grandezza: oggi ~230 coppie a una conferma, 0 a due, 0 validate. Su un
 * asse comune la prima riempie il riquadro e le altre due sono una riga sullo zero —
 * cioè proprio le due che dicono se il sistema sta arrivando in fondo diventano
 * invisibili. Tre riquadri, ognuno con la sua scala, mostrano la DIREZIONE di
 * ciascuna, che è la domanda vera.
 *
 * Il prezzo di questa scelta va detto: i tre riquadri NON sono confrontabili fra loro
 * in altezza. Per questo il numero attuale è scritto grande sopra ogni riquadro — la
 * grandezza la porta la cifra, non il grafico.
 *
 * I colori sono una rampa ordinale validata (vedi lib/viz.ts): più conferme = più
 * chiaro. Non sono tinte scelte a occhio — la prima versione aveva due blu a ΔE 9.5,
 * indistinguibili anche con vista piena.
 */
type Punto = {
  at: number;
  tracked?: number;
  validated?: number;
  /** coppie ferme nel registro ma non piu' valutate: la coin e' uscita
   *  dall'universo. Non avanzano e non falliscono — fuori dai conti. */
  frozen?: number;
  dist?: Record<string, number>;
};
type Doc = { points?: Punto[]; min_passes?: number };
type Riga = { t: number; label: string; uno: number; due: number; ok: number;
              tracked: number; frozen: number };
type SerieKey = 'uno' | 'due' | 'ok';

const PERIODI = [
  { id: '7g', label: '7 giorni', giorni: 7 },
  { id: '30g', label: '30 giorni', giorni: 30 },
  { id: 'tutto', label: 'Tutto', giorni: Infinity },
] as const;
type PeriodoId = (typeof PERIODI)[number]['id'];

type Serie = { key: SerieKey; label: string; color: string; nota: string };
const SERIE: Serie[] = [
  { key: 'uno', label: '1 conferma', color: GATE_RAMP.uno,
    nota: 'hanno passato il gate una volta' },
  { key: 'due', label: '2 conferme', color: GATE_RAMP.due,
    nota: 'a un appuntamento dalla validazione' },
  { key: 'ok', label: 'validate', color: STATO.buono,
    nota: 'operabili dal bot' },
];

function label(ts: number): string {
  return new Date(ts * 1000).toLocaleString('it-IT', {
    day: '2-digit', month: 'short', hour: '2-digit',
  });
}

/** Un riquadro per serie: scala propria, titolo che nomina la serie (quindi niente
 *  legenda da leggere), valore attuale come etichetta diretta. */
function Mini({ righe, serie }: { righe: Riga[]; serie: Serie }) {
  const ultimo = righe[righe.length - 1];
  const primo = righe[0];
  const val = Number(ultimo?.[serie.key] ?? 0);
  const delta = ultimo && primo ? val - Number(primo[serie.key] ?? 0) : 0;
  const piatta = righe.every((r) => Number(r[serie.key] ?? 0) === 0);
  return (
    <div style={{ flex: '1 1 220px', minWidth: 0 }}>
      <div style={{ display: 'flex', alignItems: 'baseline', gap: 8, flexWrap: 'wrap' }}>
        <span
          aria-hidden="true"
          style={{
            width: 8, height: 8, borderRadius: 2,
            background: serie.color, display: 'inline-block',
          }}
        />
        <span style={{ fontSize: 12 }}>{serie.label}</span>
        <b style={{ fontSize: 20, lineHeight: 1.1 }}>{formatta(val)}</b>
        <span className="muted" style={{ fontSize: 11 }}>
          {delta >= 0 ? '+' : ''}{delta} nel periodo
        </span>
      </div>
      <div className="muted" style={{ fontSize: 11, marginBottom: 4 }}>{serie.nota}</div>
      <ResponsiveContainer width="100%" height={130}>
        <LineChart data={righe} margin={{ top: 6, right: 6, left: 0, bottom: 0 }}>
          <CartesianGrid stroke={CHROME.griglia} vertical={false} />
          <XAxis
            dataKey="label"
            stroke={CHROME.asse}
            fontSize={10}
            tickLine={false}
            minTickGap={64}
          />
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
          />
          <Line
            type="monotone"
            dataKey={serie.key}
            name={serie.label}
            stroke={serie.color}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 4, strokeWidth: 2, stroke: CHROME.superficie }}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function GateEvolution() {
  const [d, setD] = useState<Doc | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [periodo, setPeriodo] = useState<PeriodoId>('30g');
  const [tabella, setTabella] = useState(false);

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
      .map((p) => {
        const dist = p.dist ?? {};
        const n = (k: string) => Number(dist[k] ?? 0);
        return {
          t: p.at, label: label(p.at),
          uno: n('1'), due: n('2'),
          ok: Number(p.validated ?? n('3')),
          tracked: Number(p.tracked ?? 0),
          frozen: Number(p.frozen ?? 0),
        };
      });
  }, [d]);

  const righe = useMemo(() => {
    const g = PERIODI.find((p) => p.id === periodo)?.giorni ?? Infinity;
    if (!Number.isFinite(g) || tutte.length === 0) return tutte;
    const taglio = tutte[tutte.length - 1].t - g * 86400;
    return tutte.filter((r) => r.t >= taglio);
  }, [tutte, periodo]);

  const ultimo = righe[righe.length - 1];

  return (
    <div className="panel">
      <h2>Evoluzione del GATE 1</h2>
      <p className="subtitle">
        Quante coppie hanno accumulato quante conferme, nel tempo. Una conferma richiede
        una settimana di dati nuovi: il movimento è lento per costruzione, quello che
        conta è la <b>direzione</b>.
      </p>

      <div
        style={{
          display: 'flex', gap: 6, flexWrap: 'wrap',
          alignItems: 'center', marginBottom: 12,
        }}
      >
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
          <span className="muted" style={{ fontSize: 12 }}>
            coppie tracciate <b style={{ color: 'var(--text)' }}>{formatta(ultimo.tracked)}</b>
            {ultimo.frozen > 0 && (
              <span
                title={'Coppie ferme nel registro: la loro coin e\u2019 uscita '
                  + 'dall\u2019universo (storia insufficiente o delisting), quindi '
                  + 'l\u2019optimizer non le valuta piu\u2019. Non avanzano e non '
                  + 'falliscono: sono escluse da tutti i conti.'}
              >
                {' '}· {formatta(ultimo.frozen)} congelate
              </span>
            )}
          </span>
        )}
        <button
          onClick={() => setTabella((v) => !v)}
          className="btn btn-ghost"
          style={{ padding: '4px 12px', fontSize: 12 }}
          aria-pressed={tabella}
        >
          {tabella ? 'Grafico' : 'Tabella'}
        </button>
      </div>

      {!loaded ? (
        <p className="muted">Caricamento…</p>
      ) : tutte.length === 0 ? (
        <p className="muted">
          Nessuna storia ancora. Il primo punto lo scrive il supervisore al prossimo giro
          (ogni ora); optimizer e discovery ne aggiungono altri ogni 3 ore. Servono un
          paio di giorni di punti perché la direzione si legga.
        </p>
      ) : tabella ? (
        <div style={{ overflowX: 'auto', maxHeight: 320, overflowY: 'auto' }}>
          <table style={{ width: '100%', fontSize: 12, borderCollapse: 'collapse' }}>
            <thead>
              <tr className="muted" style={{ textAlign: 'left' }}>
                <th style={{ padding: '4px 8px 4px 0' }}>quando</th>
                <th style={{ padding: '4px 8px' }}>tracciate</th>
                {SERIE.map((s) => (
                  <th key={s.key} style={{ padding: '4px 8px' }}>{s.label}</th>
                ))}
              </tr>
            </thead>
            <tbody style={{ fontVariantNumeric: 'tabular-nums' }}>
              {[...righe].reverse().map((r) => (
                <tr key={r.t} style={{ borderTop: '1px solid var(--border-soft)' }}>
                  <td style={{ padding: '4px 8px 4px 0', whiteSpace: 'nowrap' }}>{r.label}</td>
                  <td style={{ padding: '4px 8px' }}>{formatta(r.tracked)}</td>
                  <td style={{ padding: '4px 8px' }}>{formatta(r.uno)}</td>
                  <td style={{ padding: '4px 8px' }}>{formatta(r.due)}</td>
                  <td style={{ padding: '4px 8px' }}>{formatta(r.ok)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <>
          <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
            {SERIE.map((s) => (
              <Mini key={s.key} righe={righe} serie={s} />
            ))}
          </div>
          <p className="muted" style={{ fontSize: 11, marginTop: 10 }}>
            Ogni riquadro ha la <b>sua</b> scala verticale: serve a leggere la direzione,
            non a confrontare le altezze fra loro — la grandezza la porta la cifra sopra
            il grafico. Le coppie a zero passaggi non sono qui: sono la stragrande
            maggioranza e schiaccerebbero tutto il resto.
          </p>
        </>
      )}
    </div>
  );
}
