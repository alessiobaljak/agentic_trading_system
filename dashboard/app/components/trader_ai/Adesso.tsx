'use client';

import { useMemo, useState } from 'react';
import { CartesianGrid, Line, LineChart, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Suggerimento, giornoBreve, useAdesso } from '../comuni';
import {
  AZIONE, LATO, TETTO_DOLLARI, coloreDi, eChiamata, numeriDiAdesso, ora, prezzoBtc, secondi, usd, usePrezzoBtc,
  type DatiTrader, type RigaDiario,
} from './dati';

/**
 * La schermata principale del trader AI: il conto di adesso, il giorno contro il 3%, l'operazione aperta con il risultato al prezzo di
 * adesso, il conto del giorno chiamata dopo chiamata e l'ultima decisione del modello. Un solo colore per il trader (slot 7 della
 * tavolozza validata: in quest'area c'è una serie sola), una sola scala.
 */
const COLORE = 'var(--serie-7)';

function Riquadro({ nome, valore, sotto, colore }: { nome: string; valore: string; sotto?: string; colore?: string }) {
  return (
    <div className="cr-riquadro">
      <span>{nome}</span>
      <b style={colore ? { color: colore } : undefined}>{valore}</b>
      {sotto && <span>{sotto}</span>}
    </div>
  );
}

function Barra3({ oggi, obiettivo }: { oggi: number; obiettivo: number }) {
  const quota = Math.max(0, Math.min(1, oggi / obiettivo));
  return (
    <div className="ta-barra" role="img" aria-label={`oggi ${usd(oggi, 2, true)} su ${usd(obiettivo)} USDT del 3%`}>
      <span className="ta-barra-piena" style={{ width: `${quota * 100}%`, background: oggi >= 0 ? COLORE : 'var(--giu-testo)' }} />
    </div>
  );
}

function OperazioneAperta({ d, prezzo }: { d: DatiTrader; prezzo: number | null }) {
  const a = d.stato?.aperta ?? null;
  const n = numeriDiAdesso(d, prezzo);
  if (!a) {
    return <p className="cr-sotto" style={{ margin: 0 }}>Nessuna operazione aperta: il modello aspetta.</p>;
  }
  const lungo = a.lato === 'lungo';
  if (a.in_attesa || !n.pos) {
    const dist = n.prezzoUsato != null && a.entrata ? (a.entrata / n.prezzoUsato - 1) * 100 : null;
    return (
      <>
        <p className="cr-riga">
          <b>Ordine limite in attesa</b>: {lungo ? 'compra' : 'vende'} {a.quantita} BTC a <b>{prezzoBtc(a.entrata)}</b>
          {` (leva ${a.leva}; prezzo adesso ${prezzoBtc(n.prezzoUsato)}`}
          {dist != null ? `, ${Math.abs(dist).toFixed(2)}% ${dist > 0 ? 'sopra' : 'sotto'})` : ')'}.
        </p>
        <p className="cr-riga">Stop {prezzoBtc(a.stop)}{a.obiettivo ? ` · obiettivo ${prezzoBtc(a.obiettivo)}` : ''} · messo alle {ora(a.aperta)}</p>
        {a.motivo && <p className="cr-sotto ta-nota">«{a.motivo}»</p>}
      </>
    );
  }
  const pos = n.pos;
  return (
    <>
      <div className="cr-riquadri">
        <Riquadro nome={LATO[pos.lato]} valore={`${pos.quantita} BTC`} sotto={`leva ${pos.leva} · margine ${usd(pos.margine, 0)}`} />
        <Riquadro nome="Entrata" valore={prezzoBtc(pos.entrata)} sotto={`eseguita alle ${ora(a.eseguita ?? a.aperta)}`} />
        <Riquadro nome="Prezzo adesso" valore={prezzoBtc(n.prezzoUsato)} sotto={prezzo != null ? 'da Binance, in diretta' : 'ultimo salvato'} />
        <Riquadro nome="Risultato aperto" valore={`${usd(n.aperto, 2, true)} USDT`} colore={coloreDi(n.aperto)}
          sotto="prima delle spese di chiusura" />
        <Riquadro nome="Stop" valore={prezzoBtc(a.stop)}
          sotto={a.stop && n.prezzoUsato ? `${(Math.abs(n.prezzoUsato - a.stop) / n.prezzoUsato * 100).toFixed(2)}% dal prezzo` : undefined} />
        <Riquadro nome="Obiettivo" valore={a.obiettivo ? prezzoBtc(a.obiettivo) : 'nessuno'}
          sotto={a.obiettivo && n.prezzoUsato ? `${(Math.abs(a.obiettivo - n.prezzoUsato) / n.prezzoUsato * 100).toFixed(2)}% dal prezzo` : undefined} />
      </div>
      {a.motivo && <p className="cr-sotto ta-nota" style={{ marginTop: 10 }}>«{a.motivo}»</p>}
    </>
  );
}

function ContoDelGiorno({ d, conto }: { d: DatiTrader; conto: number | null }) {
  const st = d.stato ?? {};
  const giorno = st.giorno ?? '';
  const mezzanotte = st.conto_mezzanotte ?? null;
  const punti = useMemo(() => {
    const out = d.diario
      .filter((r: RigaDiario) => eChiamata(r) && typeof r.conto === 'number' && r.ora.startsWith(giorno))
      .map((r) => ({ t: secondi(r.ora) ?? 0, conto: r.conto as number }));
    if (conto != null) out.push({ t: Date.now() / 1000, conto });
    return out;
  }, [d.diario, giorno, conto]);
  if (mezzanotte == null || punti.length < 2) {
    return <p className="cr-sotto" style={{ margin: 0 }}>La curva del giorno si disegna dalla seconda chiamata.</p>;
  }
  const traguardo = mezzanotte * 1.03;
  const valori = punti.map((p) => p.conto).concat([mezzanotte]);
  const basso = Math.min(...valori);
  const alto = Math.max(...valori, Math.min(traguardo, Math.max(...valori) + (traguardo - mezzanotte) * 0.35));
  const margine = Math.max(1, (alto - basso) * 0.12);
  const dominio: [number, number] = [Math.floor(basso - margine), Math.ceil(alto + margine)];
  const mostraTraguardo = traguardo <= dominio[1];
  return (
    <>
      <div className="cr-grafico">
        <ResponsiveContainer>
          <LineChart data={punti} margin={{ top: 8, right: 14, bottom: 0, left: 0 }}>
            <CartesianGrid stroke="var(--griglia)" vertical={false} />
            <XAxis dataKey="t" type="number" domain={['dataMin', 'dataMax']} stroke="var(--asse)" tickLine={false} minTickGap={36}
              tick={{ fill: 'var(--text-faint)', fontSize: 11 }}
              tickFormatter={(s: number) => ora(new Date(s * 1000).toISOString())} />
            <YAxis stroke="var(--asse)" tick={{ fill: 'var(--text-faint)', fontSize: 11 }} tickLine={false} width={48} domain={dominio}
              tickFormatter={(v: number) => usd(v, 0)} allowDecimals={false} />
            <ReferenceLine y={mezzanotte} stroke="var(--asse)" strokeDasharray="4 4"
              label={{ value: 'mezzanotte', position: 'insideBottomLeft', fill: 'var(--text-faint)', fontSize: 11 }} />
            {mostraTraguardo && (
              <ReferenceLine y={traguardo} stroke="var(--text-faint)" strokeDasharray="2 4"
                label={{ value: '+3%', position: 'insideTopLeft', fill: 'var(--text-faint)', fontSize: 11 }} />
            )}
            <Tooltip
              cursor={{ stroke: 'var(--text-faint)', strokeWidth: 1 }}
              isAnimationActive={false}
              content={({ active, payload }) => {
                if (!active || !payload?.length) return null;
                const p = payload[0].payload as { t: number; conto: number };
                return (
                  <Suggerimento titolo={ora(new Date(p.t * 1000).toISOString())}
                    voci={[{ chiave: 'conto', nome: `conto · oggi ${usd(p.conto - mezzanotte, 2, true)}`, colore: COLORE, forma: 'linea',
                      valore: usd(p.conto) }]} />
                );
              }}
            />
            <Line dataKey="conto" type="linear" stroke={COLORE} strokeWidth={2} strokeLinecap="round" strokeLinejoin="round"
              isAnimationActive={false} activeDot={{ r: 5, stroke: 'var(--bg-panel)', strokeWidth: 2, fill: COLORE }}
              dot={(p: { index: number; cx?: number; cy?: number }) =>
                p.index === punti.length - 1 && p.cx != null && p.cy != null
                  ? <circle key="fine" cx={p.cx} cy={p.cy} r={4} fill={COLORE} stroke="var(--bg-panel)" strokeWidth={2} />
                  : <g key={`p-${p.index}`} />} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p className="cr-sotto" style={{ margin: '6px 0 0' }}>
        Il conto (USDT) a ogni chiamata al modello da mezzanotte UTC; l&apos;ultimo punto è adesso. Tratteggio: il conto di mezzanotte e
        il 3%{mostraTraguardo ? '' : ' (fuori scala)'}.
      </p>
    </>
  );
}

function descriviRisposta(r: RigaDiario): string {
  const x = r.risposta;
  if (!x?.azione) return r.stato === 'ok' ? 'nessuna risposta letta' : `risposta non letta (${r.stato})`;
  const pezzi = [AZIONE[x.azione] ?? x.azione];
  if (x.azione === 'apri_lungo' || x.azione === 'apri_corto') {
    pezzi.push(`margine ${usd(x.margine_usdt, 0)}, leva ${x.leva}`);
    if (x.tipo_ordine === 'limite' && x.prezzo_limite) pezzi.push(`limite a ${prezzoBtc(x.prezzo_limite)}`);
    if (x.stop_prezzo) pezzi.push(`stop ${prezzoBtc(x.stop_prezzo)}`);
    if (x.obiettivo_prezzo) pezzi.push(`obiettivo ${prezzoBtc(x.obiettivo_prezzo)}`);
  } else if (x.azione === 'modifica') {
    if (x.stop_prezzo) pezzi.push(`stop a ${prezzoBtc(x.stop_prezzo)}`);
    if (x.obiettivo_prezzo) pezzi.push(`obiettivo a ${prezzoBtc(x.obiettivo_prezzo)}`);
  }
  return pezzi.join(' · ');
}

function NotaBreve({ testo }: { testo: string }) {
  const [tutta, setTutta] = useState(false);
  return (
    <button type="button" className={`ta-nota ta-nota-breve${tutta ? ' ta-tutta' : ''}`} onClick={() => setTutta(!tutta)}
      aria-expanded={tutta} title={tutta ? 'tocca per accorciare' : 'tocca per leggere tutto'}>
      «{testo}»
    </button>
  );
}

export function UltimaDecisione({ r, breve = false }: { r: RigaDiario; breve?: boolean }) {
  const nota = r.risposta?.diario;
  return (
    <div className="ta-decisione">
      <p className="cr-riga"><b>{ora(r.ora)}</b> · {r.motivo} · <b>{descriviRisposta(r)}</b></p>
      {nota && (breve ? <NotaBreve testo={nota} /> : <p className="cr-sotto ta-nota">«{nota}»</p>)}
      {r.scarto && <p className="cr-sotto">Scartata dal programma: {r.scarto}</p>}
    </div>
  );
}

export default function Adesso({ d }: { d: DatiTrader }) {
  const { prezzo } = usePrezzoBtc();
  useAdesso(5_000);
  const st = d.stato ?? {};
  const n = numeriDiAdesso(d, prezzo);
  const chiamate = d.diario.filter((r) => eChiamata(r) && r.ora.startsWith(st.giorno ?? '-'));
  const ultima = [...d.diario].reverse().find(eChiamata) ?? null;
  const speso = (st.giorno && d.spesa[st.giorno]) || 0;
  const raggiunto = !!st.obiettivo_ora;
  return (
    <>
      <section className="cr-pannello">
        <div className="cr-pannello-testa">
          <h2>Oggi</h2>
          <span className="cr-pannello-destra">dalla mezzanotte UTC (le 01:00 da noi)</span>
        </div>
        <div className="cr-riquadri">
          <Riquadro nome="Conto adesso" valore={`${usd(n.conto)} USDT`}
            sotto={n.pos ? 'con l\'operazione aperta al prezzo di adesso' : 'niente di aperto'} />
          <Riquadro nome="Oggi" valore={`${usd(n.oggi, 2, true)} USDT`} colore={coloreDi(n.oggi)}
            sotto={n.oggi != null && n.mezzanotte ? `${usd((n.oggi / n.mezzanotte) * 100, 2, true)}% · a mezzanotte ${usd(n.mezzanotte)}` : undefined} />
          <Riquadro nome="Obiettivo del 3%" valore={raggiunto ? 'raggiunto' : `${usd(n.obiettivo)} USDT`}
            sotto={raggiunto ? `alle ${ora(st.obiettivo_ora)}: fermo fino a mezzanotte UTC`
              : n.oggi != null && n.obiettivo != null ? `mancano ${usd(Math.max(0, n.obiettivo - n.oggi))}` : undefined} />
          <Riquadro nome="Dall'inizio della prova" valore={`${usd(n.dallInizio, 2, true)} USDT`} colore={coloreDi(n.dallInizio)}
            sotto={n.inizio ? `partito con ${usd(n.inizio, 0)} il ${giornoBreve(st.inizio?.giorno)}` : undefined} />
          <Riquadro nome="Chiamate al modello oggi" valore={String(chiamate.length)}
            sotto={`spesa ${usd(speso)} di ${TETTO_DOLLARI} dollari${st.tetto_dalle ? ` · tetto finito alle ${ora(st.tetto_dalle)}` : ''}`} />
        </div>
        {n.oggi != null && n.obiettivo ? <Barra3 oggi={n.oggi} obiettivo={n.obiettivo} /> : null}
      </section>

      <section className="cr-pannello">
        <div className="cr-pannello-testa"><h2>Operazione aperta</h2></div>
        <OperazioneAperta d={d} prezzo={prezzo} />
      </section>

      <section className="cr-pannello">
        <div className="cr-pannello-testa"><h2>Il conto di oggi</h2></div>
        <ContoDelGiorno d={d} conto={n.conto} />
      </section>

      {ultima && (
        <section className="cr-pannello">
          <div className="cr-pannello-testa"><h2>L&apos;ultima decisione del modello</h2></div>
          <UltimaDecisione r={ultima} />
          {st.approccio && <p className="cr-sotto" style={{ marginTop: 8 }}>Il suo metodo di adesso: «{st.approccio}»</p>}
        </section>
      )}
    </>
  );
}
