'use client';

import { useEffect, useMemo, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { Bar, BarChart, CartesianGrid, Cell, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { getRtdb } from '../../lib/firebase';
import {
  Colonna, Info, Pesi, Suggerimento, giornoBreve, giornoNelFuso, metricheDaSerie, pct, soldi, useAdesso, type Giorni,
} from '../comuni';
import type { DatiAzioni, StrategiaAzioni } from './Azioni';

/**
 * La scheda «Dettagli» delle azioni, speculare a quella delle crypto (components/dettagli/Dettagli.tsx; il proprietario, 28 novembre
 * 2026: «usa la stessa visualizzazione della sessione crypto, devono essere speculari [...] soprattutto la sezione dettagli che deve
 * rimpiazzare quella operazioni»). In cima si sceglie la strategia; sotto i suoi numeri, il giorno per giorno, le posizioni e le
 * operazioni. Legge /azioni/strategie/<id> (stock/avanti/plancia.py, miscela.py, gamma.py); le spiegazioni stanno nelle «i».
 */
export interface Operazione {
  simbolo: string;
  lato?: string;
  quantita?: number;
  ingresso?: number;
  uscita_prezzo?: number;
  uscita?: string;
  guadagno?: number;
  proporzione?: number;
  commissione_ib?: number;
  nota?: string;
  ora_ingresso?: string;
  /** «ordine»: un ordine della miscela (comprato o venduto, senza guadagno a sé) */
  genere?: string;
}

type ConOperazioni = StrategiaAzioni & { operazioni?: Record<string, Operazione[] | null> | null };

/** Le strategie del demo, con il nome corto delle linguette e il nome nell'indirizzo (#azioni/dettagli/<pagina>). */
export const SCELTE_AZIONI: { id: string; pagina: string; breve: string }[] = [
  { id: 'prima_candela_15m', pagina: 'candela', breve: 'Prima candela' },
  { id: 'miscela', pagina: 'miscela', breve: 'Miscela' },
  { id: 'gamma', pagina: 'prova45', breve: 'Ultima mezz\'ora' },
];

// i giorni delle azioni sono i giorni di borsa di New York (come la scheda Strategie)
const FUSO = 'America/New_York';
const SU = 'var(--giorno-su)';
const GIU = 'var(--giorno-giu)';
const coloreDi = (ordine?: number) => `var(--serie-${Math.min(7, Math.max(1, Math.round(ordine ?? 1)))})`;
const titolo = (s: string) => s.replace(/_/g, '.');
const unitaDi = (s: StrategiaAzioni) => ((s.valuta ?? 'USD') === 'USD' ? '$' : (s.valuta ?? 'USD'));
const classe = (x: number | null | undefined) => (x == null || Math.abs(x) < 0.00005 ? undefined : x > 0 ? 'cr-su' : 'cr-giu');
const LATO: Record<string, string> = { buy: 'acquisto', sell: 'vendita' };
/** I soldi con il segno davanti (come le crypto): +$115,70, −$217,30. */
function soldiConSegno(x: number | null | undefined, unita: string): string {
  if (x == null || !Number.isFinite(x)) return '—';
  const n = soldi(Math.abs(x), unita);
  return Math.abs(x) < 0.005 ? n : `${x > 0 ? '+' : '−'}${n}`;
}
/** Le date scritte dai programmi (2026-11-27) come le altre della scheda (27 nov). */
const conDate = (t?: string) => (t ?? '').replace(/\d{4}-\d{2}-\d{2}/g, (g) => giornoBreve(g));
const USCITA: Record<string, string> = {
  stop: 'stop', obiettivo: 'obiettivo', chiusura: 'fine giornata', aperta: 'ancora aperta', asta: 'asta di chiusura',
  'giorno dopo': 'il giorno dopo', mercato: 'a mercato', 'fuori orario': 'fuori orario', parziale: 'in parte',
};

function Riquadro({ nome, valore, cls, info }: { nome: string; valore: React.ReactNode; cls?: string; info?: React.ReactNode }) {
  return (
    <div className="cr-riquadro">
      <span>{nome}{info && <Info etichetta={`che cos'è: ${nome}`}>{info}</Info>}</span>
      <b className={cls}>{valore}</b>
    </div>
  );
}

function Pannello({ titolo: t, info, destra, children }: {
  titolo: string; info?: React.ReactNode; destra?: React.ReactNode; children: React.ReactNode;
}) {
  return (
    <section className="cr-pannello">
      <div className="cr-pannello-testa">
        <h2>{t}</h2>
        {info && <Info etichetta={`che cos'è: ${t}`}>{info}</Info>}
        {destra && <span className="cr-pannello-destra">{destra}</span>}
      </div>
      {children}
    </section>
  );
}

/** La serie dei valori di fine giorno con quello di adesso al giorno di oggi (come la scheda Strategie). */
function serieDi(s: StrategiaAzioni): Giorni {
  const g: Giorni = { ...(s.giorni ?? {}) };
  if (s.valore != null && s.aggiornato) g[giornoNelFuso(s.aggiornato, FUSO)] = Number(s.valore);
  return g;
}

interface GiornoRisultato { giorno: string; r: number; valore: number; inCorso: boolean }

/** Il risultato di ogni giorno di borsa sul giorno di borsa prima (i fine settimana e le feste non ci sono); il primo dal capitale. */
function risultati(serie: Giorni, s: StrategiaAzioni, oggi: string | null, n = 30): GiornoRisultato[] {
  const date = Object.keys(serie).sort();
  const out: GiornoRisultato[] = [];
  date.forEach((k, i) => {
    const v = Number(serie[k]);
    const prima = i > 0 ? Number(serie[date[i - 1]]) : s.primo_giorno_dal_capitale ? Number(s.capitale ?? 0) : 0;
    if (prima > 0) out.push({ giorno: k, r: v / prima - 1, valore: v, inCorso: k === oggi });
  });
  return out.slice(-n);
}

function discesaMassima(serie: Giorni, s: StrategiaAzioni): number | null {
  const date = Object.keys(serie).sort();
  if (!date.length) return null;
  let massimo = s.primo_giorno_dal_capitale && (s.capitale ?? 0) > 0 ? Number(s.capitale) : Number(serie[date[0]]);
  let peggiore = 0;
  for (const k of date) {
    massimo = Math.max(massimo, Number(serie[k]));
    if (massimo > 0) peggiore = Math.min(peggiore, Number(serie[k]) / massimo - 1);
  }
  return peggiore;
}

/** Il giorno per giorno: una colonna per giorno, verde in guadagno, arancione in perdita (come le crypto); il giorno in corso più chiaro. */
function RisultatoGiorni({ breve, unita, giorni }: { breve: string; unita: string; giorni: GiornoRisultato[] }) {
  const dati = giorni.map((g) => ({ ...g, rPct: 100 * g.r }));
  return (
    <>
      <div className="cr-legenda-fissa">
        <span><span className="cr-quadro" style={{ background: SU }} aria-hidden="true" />giorno in guadagno</span>
        <span><span className="cr-quadro" style={{ background: GIU }} aria-hidden="true" />giorno in perdita</span>
      </div>
      <div className="cr-grafico" style={{ height: 200 }}>
        <ResponsiveContainer>
          <BarChart data={dati} margin={{ top: 8, right: 10, bottom: 0, left: 0 }} barCategoryGap="18%">
            <CartesianGrid stroke="var(--griglia)" vertical={false} />
            <XAxis dataKey="giorno" stroke="var(--asse)" tick={{ fill: 'var(--text-faint)', fontSize: 11 }} tickLine={false}
              minTickGap={18} tickFormatter={(g: string) => giornoBreve(g)} />
            <YAxis stroke="var(--asse)" tick={{ fill: 'var(--text-faint)', fontSize: 11 }} tickLine={false} width={44}
              tickFormatter={(v: number) => `${v.toLocaleString('it-IT', { maximumFractionDigits: 1 })}%`} />
            <ReferenceLine y={0} stroke="var(--asse)" />
            <Tooltip
              cursor={{ fill: 'var(--velo)' }}
              isAnimationActive={false}
              content={({ active, payload }) => {
                if (!active || !payload?.length) return null;
                const g = payload[0].payload as GiornoRisultato;
                return (
                  <Suggerimento titolo={`${giornoBreve(g.giorno)}${g.inCorso ? ' · in corso' : ''}`}
                    voci={[{ chiave: 'r', nome: breve, colore: g.r >= 0 ? SU : GIU, forma: 'quadro', valore: pct(g.r) }]}
                    nota={`valore ${soldi(g.valore, unita)}`} />
                );
              }}
            />
            <Bar dataKey="rPct" fill={SU} maxBarSize={24} isAnimationActive={false} shape={<Colonna />}>
              {dati.map((g) => <Cell key={g.giorno} fill={g.r >= 0 ? SU : GIU} fillOpacity={g.inCorso ? 0.45 : 1} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </>
  );
}

/** Le righe di tutti i giorni, dal giorno più recente, con il giorno attaccato. */
function righe(s: ConOperazioni): (Operazione & { giorno: string })[] {
  return Object.entries(s.operazioni ?? {})
    .sort((a, b) => b[0].localeCompare(a[0]))
    .flatMap(([g, ops]) => (ops ?? []).map((o) => ({ ...o, giorno: g })));
}

/** Le operazioni della prima candela e della prova 45: aperte, chiuse (le ultime 15), e i giorni senza operazione. */
function Operazioni({ s, unita }: { s: ConOperazioni; unita: string }) {
  const tutte = righe(s);
  const fatte = tutte.filter((o) => o.genere !== 'ordine' && o.quantita != null);
  const aperte = fatte.filter((o) => o.guadagno == null || o.uscita === 'aperta' || o.uscita === 'parziale');
  const chiuse = fatte.filter((o) => o.guadagno != null && o.uscita !== 'aperta').slice(0, 15);
  const conOperazione = new Set(fatte.map((o) => o.giorno));
  const senza = tutte.filter((o) => o.genere !== 'ordine' && o.quantita == null && !conOperazione.has(o.giorno));
  const giorniSenza = Object.entries(senza.reduce<Record<string, string[]>>((acc, o) => {
    (acc[o.giorno] ??= []).push(o.nota || 'nessuna operazione');
    return acc;
  }, {})).slice(0, 5);
  return (
    <Pannello titolo="Le operazioni" info="Ogni riga è un'operazione del conto demo: ingresso, uscita e risultato; il risultato in % è sul valore entrato.">
      <div className="cr-etichetta-riga">Aperte <b>{aperte.length}</b></div>
      {aperte.length === 0 ? <p className="cr-sotto" style={{ margin: 0 }}>nessuna</p> : (
        <table className="cr-tabella">
          <thead><tr><th>Titolo</th><th>Ingresso</th><th>Entrata il</th></tr></thead>
          <tbody>
            {aperte.map((x, i) => (
              <tr key={`${x.giorno}-${x.simbolo}-${i}`}>
                <td>{titolo(x.simbolo)}<span className="cr-fase">{LATO[x.lato ?? ''] ?? x.lato}</span></td>
                <td>{x.ingresso != null ? soldi(x.ingresso, unita) : '—'}</td>
                <td>{giornoBreve(x.giorno)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <div className="cr-etichetta-riga">Chiuse, le ultime <b>{chiuse.length}</b></div>
      {chiuse.length === 0 ? <p className="cr-sotto" style={{ margin: 0 }}>nessuna</p> : (
        <table className="cr-tabella">
          <thead><tr><th>Titolo</th><th>Risultato</th><th>Guadagno</th><th>Chiusa il</th></tr></thead>
          <tbody>
            {chiuse.map((x, i) => (
              <tr key={`${x.giorno}-${x.simbolo}-${i}`}>
                <td>{titolo(x.simbolo)}<span className="cr-fase">{LATO[x.lato ?? ''] ?? x.lato} · {USCITA[x.uscita ?? ''] ?? x.uscita}</span></td>
                <td className={classe(x.proporzione)}>{pct(x.proporzione)}</td>
                <td className={classe(x.guadagno)}>{soldiConSegno(x.guadagno, unita)}</td>
                <td>{giornoBreve(x.giorno)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      {giorniSenza.length > 0 && (
        <>
          <div className="cr-etichetta-riga">
            Giorni senza operazione, gli ultimi <b>{giorniSenza.length}</b>
            <Info>I giorni in cui la regola non è entrata, con il perché (per esempio la copertura delle opzioni sopra zero).</Info>
          </div>
          <table className="cr-tabella">
            <thead><tr><th>Giorno</th><th style={{ textAlign: 'left' }}>Perché</th></tr></thead>
            <tbody>
              {giorniSenza.map(([g, note]) => (
                <tr key={g}><td>{giornoBreve(g)}</td><td style={{ textAlign: 'left' }}>{conDate([...new Set(note)].join('; '))}</td></tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </Pannello>
  );
}

/** Gli ordini della miscela: gli ultimi 15, eseguiti o in attesa, con il perché. */
function Ordini({ s, unita }: { s: ConOperazioni; unita: string }) {
  const ordini = righe(s).filter((o) => o.genere === 'ordine').slice(0, 15);
  const eseguiti = ordini.filter((o) => o.ingresso != null);
  return (
    <Pannello titolo="Gli ordini" info="La miscela non fa operazioni chiuse una per una: ogni sera (e prima della banca centrale) porta SPY e QQQ ai pesi voluti con ordini all'apertura.">
      <div className="cr-riquadri">
        <Riquadro nome="Ordini" valore={ordini.length} />
        <Riquadro nome="Eseguiti" valore={eseguiti.length} />
        <Riquadro nome="Non eseguiti" valore={ordini.length - eseguiti.length}
          info="In attesa dell'apertura (gli ordini della sera si eseguono all'apertura dopo), oppure scaduti o rifiutati: lo dice il perché." />
      </div>
      {ordini.length === 0 ? <p className="cr-sotto" style={{ margin: 0 }}>nessuno negli ultimi 30 giorni</p> : (
        <table className="cr-tabella">
          <thead><tr><th>Titolo</th><th>Quantità</th><th>Prezzo</th><th>Giorno</th><th style={{ textAlign: 'left' }}>Perché</th></tr></thead>
          <tbody>
            {ordini.map((x, i) => (
              <tr key={`${x.giorno}-${x.simbolo}-${i}`}>
                <td>{titolo(x.simbolo)}<span className="cr-fase">{LATO[x.lato ?? ''] ?? x.lato}</span></td>
                <td>{x.quantita != null ? x.quantita.toLocaleString('it-IT') : '—'}</td>
                <td>{x.ingresso != null ? soldi(x.ingresso, unita) : '—'}</td>
                <td>{giornoBreve(x.giorno)}</td>
                <td style={{ textAlign: 'left' }}>{conDate(x.nota) || '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Pannello>
  );
}

export default function Dettagli({ pagina, onPagina }: { pagina: string; onPagina: (p: string) => void }) {
  const [dati, setDati] = useState<DatiAzioni | null>(null);
  const [arrivato, setArrivato] = useState(false);
  const adesso = useAdesso();
  useEffect(() => onValue(ref(getRtdb(), 'azioni'), (x) => { setDati(x.val()); setArrivato(true); }), []);
  return <DettagliVista dati={dati} arrivato={arrivato} adesso={adesso} pagina={pagina} onPagina={onPagina} />;
}

/** La scheda senza Firebase: riceve i dati (così si prova anche con dati finti). */
export function DettagliVista({ dati, arrivato, adesso, pagina, onPagina }: {
  dati: DatiAzioni | null; arrivato: boolean; adesso: number; pagina: string; onPagina: (p: string) => void;
}) {
  const tutte = (dati?.strategie ?? {}) as Record<string, ConOperazioni | null>;
  // le linguette: le strategie note, poi quelle nuove pubblicate dopo (con il loro nome)
  const scelte = useMemo(() => {
    const note = SCELTE_AZIONI.filter((x) => tutte[x.id]);
    const nuove = Object.keys(tutte).filter((id) => tutte[id] && !SCELTE_AZIONI.some((x) => x.id === id))
      .map((id) => ({ id, pagina: id, breve: tutte[id]?.nome ?? id }));
    return [...note, ...nuove].sort((a, b) => (tutte[a.id]?.ordine ?? 99) - (tutte[b.id]?.ordine ?? 99));
  }, [tutte]);

  if (!arrivato) return <p className="cr-sotto">Lettura…</p>;
  if (!scelte.length) {
    return <section className="cr-pannello cr-vuoto"><p className="cr-sotto" style={{ margin: 0 }}>Nessuna strategia ancora su Firebase.</p></section>;
  }
  const scelta = scelte.find((x) => x.pagina === pagina) ?? scelte[0];
  const s = tutte[scelta.id]!;
  const unita = unitaDi(s);
  const serie = serieDi(s);
  const oggi = s.aggiornato ? giornoNelFuso(s.aggiornato, FUSO) : null;
  const m = metricheDaSerie({
    serie, valore: s.valore ?? null, base: s.capitale ?? null, aggiornato: s.aggiornato ?? null, giornoDiOggi: oggi,
    primoGiornoDallaBase: s.primo_giorno_dal_capitale === true, adesso,
  });
  const dd = discesaMassima(serie, s);
  const giorni = risultati(serie, s, oggi);
  const su = giorni.filter((g) => !g.inCorso && g.r > 0).length;
  const chiusi = giorni.filter((g) => !g.inCorso).length;
  const ordini = righe(s).some((o) => o.genere === 'ordine') || scelta.id === 'miscela';

  return (
    <>
      <nav className="cr-scelta" role="tablist" aria-label="strategia">
        {scelte.map((x) => (
          <button key={x.id} role="tab" aria-selected={x.id === scelta.id} onClick={() => onPagina(x.pagina)}>
            <span className="cr-chiave" style={{ background: coloreDi(tutte[x.id]?.ordine) }} aria-hidden="true" />
            {x.breve}
          </button>
        ))}
      </nav>

      <section className="cr-pannello">
        <div className="cr-pannello-testa">
          <span className="cr-chiave" style={{ background: coloreDi(s.ordine) }} aria-hidden="true" />
          <h2>{s.nome ?? scelta.breve}</h2>
          {s.descrizione && <Info etichetta={`che cos'è ${s.nome ?? scelta.breve}`}>{s.descrizione}</Info>}
          <span className={`cr-etichetta ${s.tipo === 'demo' ? 'demo' : 'paper'}`}>
            {s.tipo === 'demo' ? 'ordini veri · soldi finti' : 'ordini simulati'}
          </span>
        </div>
        {s.valore == null ? <p className="cr-sotto">Spento o non ancora partito</p> : (
          <div className="cr-riquadri">
            <Riquadro nome="Valore" valore={soldi(m.valore, unita)} />
            <Riquadro nome="Oggi" valore={pct(m.oggi)} cls={classe(m.oggi)} />
            <Riquadro nome={m.setteEtichetta} valore={pct(m.sette)} cls={classe(m.sette)} />
            <Riquadro nome="Dall'inizio" valore={pct(m.dallInizio)} cls={classe(m.dallInizio)}
              info={`Da ${soldi(m.base, unita, 0)} virtuali (il conto demo è uno solo: ogni strategia ha il suo capitale virtuale).`} />
            <Riquadro nome="Discesa massima" valore={pct(dd)} cls={classe(dd)}
              info="La caduta più grande da un massimo, sui valori di fine giorno." />
            <Riquadro nome="Comprate · vendute" valore={`${s.comprate ?? 0} · ${s.vendute ?? 0}`} />
          </div>
        )}
      </section>

      {giorni.length > 0 && (
        <Pannello titolo="Giorno per giorno" destra={chiusi ? <>in guadagno <b>{su} su {chiusi}</b></> : null}
          info="Il risultato di ogni giorno di borsa di New York sul giorno di borsa prima; il giorno in corso è più chiaro.">
          <RisultatoGiorni breve={scelta.breve} unita={unita} giorni={giorni} />
        </Pannello>
      )}

      {s.pesi && Object.keys(s.pesi).length > 0 && (
        <Pannello titolo="Le posizioni" info="Il peso di ogni titolo, in percentuale del capitale virtuale della strategia.">
          <Pesi pesi={s.pesi} nomeDi={titolo} />
        </Pannello>
      )}

      {ordini ? <Ordini s={s} unita={unita} /> : <Operazioni s={s} unita={unita} />}
    </>
  );
}
