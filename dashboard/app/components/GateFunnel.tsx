'use client';

import { useEffect, useMemo, useState } from 'react';
import { doc, onSnapshot } from 'firebase/firestore';
import { getDb } from '../lib/firebase';
import { GATE_RAMP, STATO, durata, formatta } from '../lib/viz';
import { RigaUltimoGiro, useOrologio } from './GateCervello';

/**
 * L'IMBUTO DEL GATE — da ventimila tentativi a zero strategie operative.
 *
 * DUE IMBUTI, NON UNO, ed è la cosa importante di questo pannello. La prima versione
 * li aveva messi in fila e fra «passate» (14) e «1 conferma» (324) compariva un tasso
 * di sopravvivenza del 2314%: un numero impossibile, che smascherava l'errore.
 *
 * Le due metà misurano cose di natura diversa:
 *   * a sinistra un FLUSSO — quante candidate sono state provate e quante sono
 *     passate IN QUESTA passata. Si azzera e ricomincia ogni tre ore;
 *   * a destra uno STOCK — quante coppie il registro sta accumulando, con quante
 *     conferme ciascuna. Cresce e cala nell'arco di settimane.
 *
 * Fra le due non c'è un filtro: c'è il TEMPO. Una candidata che passa oggi non è
 * validata, è al primo di tre appuntamenti distanti una settimana di dati nuovi l'uno
 * dall'altro. Dividere i due blocchi e non calcolare percentuali attraverso il
 * confine è l'unico modo di non raccontare una bugia con una freccia.
 *
 * Perché riquadri e non barre: le fasi vanno da ~21.000 a 0, quindi su una scala
 * comune si vedrebbe la prima barra e cinque righe piatte. E il dato che interessa non
 * è il valore assoluto, è quanto ne sopravvive fra una fase e la successiva.
 *
 * DUE AUTOPSIE, NON UNA SOMMA (25 set 2026). Il flusso veniva sommato da
 * `gate_autopsy/discover` (la discovery, ogni 3 ore) e `gate_autopsy/current`
 * (l'optimizer sulle strategie base, che da settimane gira di rado): sommare un
 * numero di stamattina con uno di dieci giorni fa dava un «questa passata» che non
 * era mai esistito. Ora ogni autopsia ha il suo blocco con la sua età, e la riga
 * «ultimo giro» viene dal documento del gate, che dice davvero quando è finito.
 */
type Rep = { updated_at?: number; evaluated?: number; passed?: number; diagnosed?: number; near_miss_count?: number };
type Reg = { pairs?: unknown; validated?: string[]; ready?: boolean };
type Punto = { at: number; tracked?: number; validated?: number; dist?: Record<string, number> };
type Storia = { points?: Punto[] };

type Fase = { id: string; label: string; valore: number; spiega: string; colore?: string };

function Freccia({ da, a }: { da: number; a: number }) {
  const pct = da > 0 ? (a / da) * 100 : 0;
  const testo = da <= 0 ? '—' : pct >= 1 ? `${pct.toFixed(0)}%` : pct > 0 ? `${pct.toFixed(2)}%` : '0%';
  return (
    <div
      style={{
        display: 'flex', alignItems: 'center', gap: 5, padding: '0 2px',
        color: 'var(--text-faint)', fontSize: 11, whiteSpace: 'nowrap',
      }}
      title={`${formatta(a)} su ${formatta(da)} arrivano alla fase successiva`}
    >
      <span aria-hidden="true">▸</span>
      <span>{testo}</span>
    </div>
  );
}

function Riquadro({ f, prec, primo }: { f: Fase; prec: number; primo: boolean }) {
  const quota = prec > 0 ? Math.min(1, f.valore / prec) : 0;
  return (
    <div
      title={f.spiega}
      style={{
        minWidth: 104,
        border: '1px solid var(--border-soft)',
        borderRadius: 10,
        padding: '10px 12px',
      }}
    >
      {/* cifre proporzionali: tabular-nums su un numero grande e isolato lo fa
          sembrare slabbrato */}
      <div
        style={{
          fontSize: 22,
          lineHeight: 1.1,
          color: f.valore > 0 ? 'var(--text)' : 'var(--text-faint)',
        }}
      >
        {formatta(f.valore)}
      </div>
      <div className="muted" style={{ fontSize: 11, marginTop: 2 }}>{f.label}</div>
      {/* la barra è proporzionale alla fase PRECEDENTE: con rapporti di 1 su mille una
          scala comune mostrerebbe solo la prima. Sulla prima fase non c'è barra —
          non essendoci un "prima", una barra piena direbbe qualcosa che non è misurato */}
      {!primo && (
        <div
          style={{
            height: 4, marginTop: 7, borderRadius: 2,
            background: 'var(--border-soft)', overflow: 'hidden',
          }}
        >
          <div
            style={{
              width: `${Math.max(quota * 100, f.valore > 0 ? 3 : 0)}%`,
              height: '100%',
              background: f.colore ?? 'var(--accent)',
              borderRadius: 2,
            }}
          />
        </div>
      )}
    </div>
  );
}

function Blocco({ titolo, sotto, fasi }: { titolo: string; sotto?: string; fasi: Fase[] }) {
  return (
    <div style={{ minWidth: 0 }}>
      <div className="muted" style={{ fontSize: 11, marginBottom: 6, letterSpacing: '.04em' }}>
        {titolo}
        {sotto ? <span style={{ letterSpacing: 0, marginLeft: 6 }}>· {sotto}</span> : null}
      </div>
      <div style={{ display: 'flex', alignItems: 'center', gap: 4, overflowX: 'auto', paddingBottom: 4 }}>
        {fasi.map((f, i) => (
          <div key={f.id} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
            {i > 0 && <Freccia da={fasi[i - 1].valore} a={f.valore} />}
            <Riquadro f={f} prec={i > 0 ? fasi[i - 1].valore : 0} primo={i === 0} />
          </div>
        ))}
      </div>
    </div>
  );
}

export default function GateFunnel() {
  const [cur, setCur] = useState<Rep | null>(null);
  const [dis, setDis] = useState<Rep | null>(null);
  const [reg, setReg] = useState<Reg | null>(null);
  const [storia, setStoria] = useState<Storia | null>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    try {
      const db = getDb();
      const subs = [
        onSnapshot(doc(db, 'gate_autopsy', 'current'),
          (s) => { setCur(s.exists() ? (s.data() as Rep) : null); setLoaded(true); },
          () => setLoaded(true)),
        onSnapshot(doc(db, 'gate_autopsy', 'discover'),
          (s) => setDis(s.exists() ? (s.data() as Rep) : null), () => {}),
        onSnapshot(doc(db, 'strategy_registry', 'validated'),
          (s) => setReg(s.exists() ? (s.data() as Reg) : null), () => {}),
        onSnapshot(doc(db, 'gate_history', 'timeline'),
          (s) => setStoria(s.exists() ? (s.data() as Storia) : null), () => {}),
      ];
      return () => subs.forEach((u) => u());
    } catch {
      setLoaded(true);
      return;
    }
  }, []);

  const now = useOrologio();

  const { flussi, registro, vuoto } = useMemo(() => {
    const flusso = (r: Rep | null): Fase[] => [
      { id: 'valutate', label: 'valutate', valore: Number(r?.evaluated ?? 0),
        spiega: 'combinazioni coppia × strategia provate in questa passata' },
      { id: 'quasi', label: 'a un passo', valore: Number(r?.near_miss_count ?? 0),
        spiega: 'fermate da UN SOLO criterio, e per poco: i semi da cui si muta al giro dopo' },
      { id: 'passate', label: 'passate', valore: Number(r?.passed ?? 0),
        spiega: 'hanno superato tutti i criteri in questa passata' },
    ];
    // ogni autopsia col suo orologio: l'età è quella del SUO documento
    const eta = (r: Rep | null) => (r?.updated_at ? `${durata(now - r.updated_at)} fa` : 'età ignota');
    const flussi = [
      { id: 'dis', titolo: 'DISCOVERY · ultima passata', sotto: dis ? eta(dis) : 'nessuna', fasi: flusso(dis), c_e: Boolean(dis) },
      { id: 'cur', titolo: 'OPTIMIZER · strategie base', sotto: cur ? eta(cur) : 'nessuna', fasi: flusso(cur), c_e: Boolean(cur) },
    ];
    const punti = [...(storia?.points ?? [])].sort((a, b) => a.at - b.at);
    const u = punti[punti.length - 1];
    const registro: Fase[] = [
      { id: 'uno', label: '1 conferma', valore: Number(u?.dist?.['1'] ?? 0), colore: GATE_RAMP.uno,
        spiega: 'nel registro con un passaggio: aspettano una settimana di dati nuovi' },
      { id: 'due', label: '2 conferme', valore: Number(u?.dist?.['2'] ?? 0), colore: GATE_RAMP.due,
        spiega: 'a un appuntamento dalla validazione' },
      { id: 'validate', label: 'validate', valore: (reg?.validated ?? []).length, colore: STATO.buono,
        spiega: 'tre conferme distanziate: il bot può operarle' },
    ];
    return {
      flussi, registro,
      vuoto: [...flussi.flatMap((f) => f.fasi), ...registro].every((f) => f.valore === 0),
    };
  }, [cur, dis, reg, storia, now]);

  return (
    <div className="panel">
      <h2>L&apos;imbuto del GATE 1</h2>
      <p className="subtitle">
        Da quante strategie si provano a quante il bot può davvero operare. Fra un
        riquadro e l&apos;altro c&apos;è quanto ne sopravvive.
      </p>
      <div style={{ marginBottom: 12 }}>
        <RigaUltimoGiro />
      </div>

      {!loaded ? (
        <p className="muted">Caricamento…</p>
      ) : vuoto ? (
        <p className="muted">
          Nessuna passata registrata. L&apos;imbuto si riempie al primo giro
          dell&apos;optimizer (ogni 3 ore).
        </p>
      ) : (
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', alignItems: 'flex-start' }}>
          {/* un blocco per autopsia, ognuno con la sua età: NON si sommano */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12, minWidth: 0 }}>
            {flussi.map((f) => (
              f.c_e ? (
                <Blocco key={f.id} titolo={f.titolo} sotto={f.sotto} fasi={f.fasi} />
              ) : (
                <div key={f.id} className="muted" style={{ fontSize: 11 }}>
                  {f.titolo} · nessuna autopsia scritta
                </div>
              )
            ))}
          </div>

          {/* il confine, dichiarato. Nessuna percentuale lo attraversa */}
          <div
            style={{
              alignSelf: 'stretch',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              maxWidth: 150,
              paddingTop: 18,
              borderLeft: '1px dashed var(--border)',
              paddingLeft: 14,
            }}
          >
            <div style={{ fontSize: 11, color: 'var(--text-faint)', lineHeight: 1.45 }}>
              qui in mezzo non c&apos;è un filtro:<br />
              <b style={{ color: 'var(--text-dim)' }}>c&apos;è il tempo</b><br />
              tre conferme, una settimana l&apos;una dall&apos;altra
            </div>
          </div>

          <Blocco titolo="NEL REGISTRO · si accumula in settimane" fasi={registro} />
        </div>
      )}
    </div>
  );
}
