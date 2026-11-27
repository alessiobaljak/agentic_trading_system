'use client';

import { useEffect, useMemo, useState } from 'react';
import { RigaStatoBase, giornoBreve, useAdesso, type AvvisoStato } from '../comuni';
import Adesso, { UltimaDecisione } from './Adesso';
import {
  LATO, coloreDi, eChiamata, leggiResoconto, ora, prezzoBtc, secondi, usd, useDatiTrader, type DatiTrader, type Operazione,
} from './dati';

/**
 * Le pagine dell'area «Trader AI» della plancia e la riga di stato in cima. I dati arrivano dalla macchina attraverso il repository
 * (dati.ts): stato, diario, conto simulato e spesa; i resoconti di ogni giorno a mezzanotte UTC.
 */
function Attesa({ d }: { d: DatiTrader | null }) {
  if (!d) return <p className="cr-sotto">Lettura…</p>;
  return (
    <section className="cr-pannello cr-vuoto">
      <p className="cr-sotto" style={{ margin: 0 }}>Non riesco a leggere i dati del trader ({d.errore ?? 'nessun dato'}). Riprovo ogni minuto.</p>
    </section>
  );
}

/** In cima a ogni pagina: il trader è vivo? (l'ultima riga del diario), quando sono arrivati i dati, e gli avvisi. */
export function StatoTrader() {
  const d = useDatiTrader();
  const adesso = useAdesso(15_000);
  const st = d?.stato ?? null;
  const ultimaRiga = d?.diario.length ? secondi(d.diario[d.diario.length - 1].ora) : null;
  const avvisi: AvvisoStato[] = [];
  if (d?.errore) avvisi.push({ chiave: 'lettura', titolo: 'Dati non letti.', dettaglio: `Ultimo tentativo: ${d.errore}. Riprovo ogni minuto.` });
  if (st?.estraneo) avvisi.push({ chiave: 'estraneo', titolo: 'Trader fermo:', dettaglio: `il conto non è solo suo (${st.estraneo}).` });
  if (st?.esaurito) avvisi.push({ chiave: 'esaurito', titolo: 'Trader fermo:', dettaglio: 'il conto non basta più per l\'ordine minimo.' });
  const fermo = st?.fermo_fino && secondi(st.fermo_fino)! > adesso;
  return (
    <>
      <RigaStatoBase battito={ultimaRiga} arrivato={!!d && (!!st || !!d.errore)} adesso={adesso} sogliaS={80 * 60}
        nomeVivo="Trader vivo" nomeFermo="Trader fermo?" aggiornato={d?.letti ?? null} aggiornatoNome="dati letti" avvisi={avvisi}
        nessunAvviso={fermo ? 'Obiettivo del 3% raggiunto: fermo fino a mezzanotte UTC.'
          : st?.tetto_dalle ? `Tetto di spesa del giorno finito alle ${ora(st.tetto_dalle)}: niente chiamate fino a mezzanotte UTC.`
            : 'Conto simulato: niente soldi veri, nessun ordine a Binance.'} />
      <p className="cr-sotto ta-fonte">
        Stato e decisioni: li salva la macchina ogni 10 minuti; il prezzo e il risultato aperto sono di adesso, da Binance.
      </p>
    </>
  );
}

export function PaginaAdesso() {
  const d = useDatiTrader();
  if (!d?.stato) return <Attesa d={d} />;
  return <Adesso d={d} />;
}

const giornoUtcDi = (iso?: string) => (iso ?? '').slice(0, 10);

export function PaginaOperazioni() {
  const d = useDatiTrader();
  const giorni = useMemo(() => {
    const per: Record<string, Operazione[]> = {};
    for (const o of d?.stato?.operazioni ?? []) (per[giornoUtcDi(o.chiusa)] ??= []).push(o);
    return Object.entries(per).sort((a, b) => b[0].localeCompare(a[0]));
  }, [d]);
  if (!d?.stato) return <Attesa d={d} />;
  if (!giorni.length) return <section className="cr-pannello"><p className="cr-sotto" style={{ margin: 0 }}>Nessuna operazione chiusa.</p></section>;
  return (
    <>
      {giorni.map(([g, ops]) => {
        const totale = ops.reduce((t, o) => t + (o.risultato ?? 0), 0);
        const vinte = ops.filter((o) => (o.risultato ?? 0) > 0).length;
        return (
          <section className="cr-pannello" key={g}>
            <div className="cr-pannello-testa"><h2>{giornoBreve(g)}</h2></div>
            <p className="cr-sotto">
              {ops.length} operazioni, {vinte} in guadagno, netto <b style={{ color: coloreDi(totale) }}>{usd(totale, 2, true)} USDT</b>
              {' '}(spese e funding compresi)
            </p>
            <div className="cr-scorre">
              <table className="cr-tabella">
                <thead>
                  <tr><th>#</th><th style={{ textAlign: 'left' }}>Lato</th><th>Leva</th><th>Entrata</th><th>Uscita</th>
                    <th style={{ textAlign: 'left' }}>Come</th><th>Netto</th><th>R</th></tr>
                </thead>
                <tbody>
                  {[...ops].reverse().map((o) => (
                    <tr key={o.n}>
                      <td>{o.n}</td>
                      <td style={{ textAlign: 'left' }}>{LATO[o.lato] ?? o.lato}</td>
                      <td>{o.leva ?? '—'}</td>
                      <td>{prezzoBtc(o.entrata)}<span className="cr-fase">{ora(o.eseguita ?? o.aperta)}</span></td>
                      <td>{prezzoBtc(o.uscita)}<span className="cr-fase">{ora(o.chiusa)}</span></td>
                      <td style={{ textAlign: 'left' }}>{o.come ?? '—'}</td>
                      <td style={{ color: coloreDi(o.risultato) }}>{usd(o.risultato, 2, true)}</td>
                      <td>{o.r != null ? usd(o.r, 2, true) : '—'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <p className="cr-sotto" style={{ margin: '6px 0 0' }}>
              R: il risultato diviso per quanto si perdeva allo stop messo all&apos;apertura (−1 = perso tutto il rischio previsto).
            </p>
          </section>
        );
      })}
    </>
  );
}

export function PaginaDecisioni() {
  const d = useDatiTrader();
  const [tutto, setTutto] = useState(false);
  const righe = useMemo(() => {
    const r = [...(d?.diario ?? [])].reverse();
    return (tutto ? r : r.filter(eChiamata)).slice(0, 40);
  }, [d, tutto]);
  if (!d?.stato) return <Attesa d={d} />;
  return (
    <section className="cr-pannello">
      <div className="cr-pannello-testa">
        <h2>Le decisioni del modello</h2>
        <nav className="cr-scelta cr-pannello-destra" role="tablist" aria-label="che cosa mostrare">
          <button role="tab" aria-selected={!tutto} onClick={() => setTutto(false)}>solo le chiamate</button>
          <button role="tab" aria-selected={tutto} onClick={() => setTutto(true)}>anche il programma</button>
        </nav>
      </div>
      <p className="cr-sotto">Dalla più recente; ogni chiamata con il perché, la decisione e la sua nota (tocca la nota per leggerla tutta). Le ultime 40 righe.</p>
      <div className="ta-elenco">
        {righe.map((r, i) => eChiamata(r) ? (
          <div key={`${r.ora}-${i}`} className="ta-voce">
            <span className="ta-giorno">{giornoBreve(giornoUtcDi(r.ora))}</span>
            <UltimaDecisione r={r} breve />
          </div>
        ) : (
          <div key={`${r.ora}-${i}`} className="ta-voce ta-evento">
            <span className="ta-giorno">{giornoBreve(giornoUtcDi(r.ora))}</span>
            <p className="cr-riga"><b>{ora(r.ora)}</b> · {r.evento}
              {typeof r.risultato === 'number' ? <> · netto <b style={{ color: coloreDi(r.risultato) }}>{usd(r.risultato, 2, true)}</b></> : null}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}

/** Un resoconto in markdown, mostrato come testo: titoli, punti e tabelle; mai come HTML. */
function Testo({ md }: { md: string }) {
  const blocchi: JSX.Element[] = [];
  const righe = md.split('\n');
  for (let i = 0; i < righe.length; i++) {
    const r = righe[i];
    if (r.startsWith('|')) {
      const tab: string[][] = [];
      while (i < righe.length && righe[i].startsWith('|')) {
        const celle = righe[i].split('|').slice(1, -1).map((c) => c.trim());
        if (!celle.every((c) => /^-+$/.test(c))) tab.push(celle);
        i++;
      }
      i--;
      const [testa, ...corpo] = tab;
      blocchi.push(
        <div className="cr-scorre" key={`t${i}`}>
          <table className="cr-tabella">
            <thead><tr>{(testa ?? []).map((c, j) => <th key={j}>{c}</th>)}</tr></thead>
            <tbody>{corpo.map((riga, k) => <tr key={k}>{riga.map((c, j) => <td key={j}>{c}</td>)}</tr>)}</tbody>
          </table>
        </div>,
      );
    } else if (r.startsWith('# ')) {
      blocchi.push(<h3 key={i} className="ta-titolo">{r.slice(2)}</h3>);
    } else if (r.startsWith('* ')) {
      blocchi.push(<p key={i} className="cr-riga ta-punto">{r.slice(2)}</p>);
    } else if (r.trim()) {
      blocchi.push(<p key={i} className="cr-riga">{r}</p>);
    }
  }
  return <div className="ta-resoconto">{blocchi}</div>;
}

function Resoconto({ giorno, aperto }: { giorno: string; aperto: boolean }) {
  const [md, setMd] = useState<string | null | undefined>(undefined);
  const [apri, setApri] = useState(aperto);
  useEffect(() => {
    if (!apri || md !== undefined) return;
    let vivo = true;
    leggiResoconto(giorno).then((x) => { if (vivo) setMd(x); });
    return () => { vivo = false; };
  }, [apri, giorno, md]);
  return (
    <details className="cr-pannello cr-apri" open={aperto} onToggle={(e) => setApri((e.target as HTMLDetailsElement).open)}>
      <summary>{giornoBreve(giorno)}<span className="cr-apri-segno">›</span></summary>
      {md === undefined ? <p className="cr-sotto">Lettura…</p>
        : md === null ? <p className="cr-sotto">Il resoconto di questo giorno non c&apos;è ancora (si scrive a mezzanotte UTC).</p>
          : <Testo md={md} />}
    </details>
  );
}

export function PaginaResoconti() {
  const d = useDatiTrader();
  if (!d?.stato) return <Attesa d={d} />;
  const oggi = d.stato.giorno ?? '';
  const giorni = Object.keys(d.spesa).filter((g) => g < oggi).sort().reverse();
  if (!giorni.length) return <section className="cr-pannello"><p className="cr-sotto" style={{ margin: 0 }}>Nessun giorno finito ancora.</p></section>;
  return (
    <>
      <p className="cr-sotto">Il resoconto di ogni giorno finito, scritto dal trader a mezzanotte UTC.</p>
      {giorni.map((g, i) => <Resoconto key={g} giorno={g} aperto={i === 0} />)}
    </>
  );
}
