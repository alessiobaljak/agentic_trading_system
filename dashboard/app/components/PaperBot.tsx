'use client';

import { useEffect, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { getRtdb } from '../lib/firebase';

/**
 * Il paper delle strategie nuove eseguito dal bot (22 ott 2026, backlog P16): F5 e G1 (bot/portafoglio/f5.py) e le monete
 * appena quotate con il funding al tetto (bot/portafoglio/eventi.py). Ordini simulati con i prezzi del momento, capitale
 * virtuale, nessun ordine vero. Legge in diretta /paper_f5, /paper_g1 e /paper_eventi del database del bot.
 */

type StatoF5 = {
  stato?: string; equity?: number; capitale?: number; rendimento?: number; long?: number; short?: number;
  ultimo_lunedi?: string; costi_totali?: number; funding_totale?: number; aggiornato?: number;
  costi_a_mercato_totali?: number; limite_variazioni?: number; limite_eseguite?: number; ordini_in_attesa?: number;
};
type ProvaF5 = { lunedi?: string; universo?: number; long?: number; short?: number; pesi_maggiori?: Record<string, number>; eseguita?: number };
type StatoEventi = {
  stato?: string; equity?: number; capitale?: number; rendimento?: number; aperte_n3?: number; aperte_e4?: number;
  chiuse?: number; rendimento_medio?: number | null; e4_in_attesa?: number; aggiornato?: number;
};
type Aperta = { tipo?: string; simbolo?: string; entrata?: number; rendimento_ora?: number; uscita_giorno?: string };
type Chiusa = { tipo?: string; simbolo?: string; uscita?: number; rendimento?: number; motivo?: string };

function pct(x: number | null | undefined, cifre = 2): string {
  if (x == null || !Number.isFinite(x)) return '—';
  return `${x >= 0 ? '+' : ''}${(100 * x).toFixed(cifre)}%`;
}

function quando(s?: number): string {
  if (!s) return '—';
  return new Date(s * 1000).toISOString().slice(0, 16).replace('T', ' ') + ' UTC';
}

function giorno(ms?: number): string {
  return ms ? new Date(ms).toISOString().slice(0, 10) : '—';
}

function nome(s?: string): string {
  return (s ?? '').replace('USDT', '');
}

function Portafoglio({ ramo, titolo, inizio }: { ramo: string; titolo: string; inizio: string }) {
  const [f5, setF5] = useState<StatoF5 | null>(null);
  const [prova, setProva] = useState<ProvaF5 | null>(null);
  const [pos, setPos] = useState<Record<string, number> | null>(null);

  useEffect(() => {
    const db = getRtdb();
    const u = [
      onValue(ref(db, `${ramo}/stato`), (s) => setF5(s.val())),
      onValue(ref(db, `${ramo}/prova`), (s) => setProva(s.val())),
      onValue(ref(db, `${ramo}/posizioni`), (s) => setPos(s.val())),
    ];
    return () => u.forEach((x) => x());
  }, [ramo]);

  const pesi = Object.entries(pos ?? {}).sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]));

  return (
    <>
      <div className="sotto-titolo">{titolo}</div>
      {!f5 ? (
        <p className="muted" style={{ margin: '2px 0 8px', fontSize: 12.5 }}>Spento o non ancora partito.</p>
      ) : (
        <>
          <p style={{ margin: '2px 0', fontSize: 12.5 }}>
            <b>{f5.stato}</b> (aggiornato {quando(f5.aggiornato)})
            {f5.equity != null && (
              <> · valore <b>${f5.equity.toLocaleString('it-IT', { maximumFractionDigits: 2 })}</b> ({pct(f5.rendimento)}) ·{' '}
                {f5.long} long, {f5.short} short · ultimo cambio {f5.ultimo_lunedi} · costi ${f5.costi_totali?.toFixed(2)} ·
                funding pagato ${f5.funding_totale?.toFixed(2)}</>
            )}
          </p>
          {(f5.limite_variazioni ?? 0) > 0 && (
            <p className="muted" style={{ margin: '2px 0', fontSize: 12.5 }}>
              Ordini limite: {f5.limite_eseguite} eseguiti su {f5.limite_variazioni}; costi ${f5.costi_totali?.toFixed(2)} invece
              di ${f5.costi_a_mercato_totali?.toFixed(2)} tutto a mercato.
            </p>
          )}
          {(f5.ordini_in_attesa ?? 0) > 0 && (
            <p className="muted" style={{ margin: '2px 0', fontSize: 12.5 }}>
              {f5.ordini_in_attesa} ordini limite in attesa del controllo dopo un'ora (eseguiti se il prezzo ci passa sopra o
              sotto, altrimenti a mercato).
            </p>
          )}
          {f5.equity == null && prova && (
            <p className="muted" style={{ margin: '2px 0', fontSize: 12.5 }}>
              Prova a secco ({quando(prova.eseguita)}): {prova.universo} monete, {prova.long} long, {prova.short} short; {inizio}
            </p>
          )}
          {pesi.length > 0 && (
            <p style={{ margin: '2px 0 8px', fontSize: 12.5 }}>
              <b>Pesi maggiori:</b> {pesi.slice(0, 12).map(([s, w]) => `${nome(s)} ${pct(w, 1)}`).join(', ')}
            </p>
          )}
        </>
      )}
    </>
  );
}

export default function PaperBot() {
  const [ev, setEv] = useState<StatoEventi | null>(null);
  const [aperte, setAperte] = useState<Record<string, Aperta> | null>(null);
  const [chiuse, setChiuse] = useState<Record<string, Chiusa> | null>(null);

  useEffect(() => {
    const db = getRtdb();
    const u = [
      onValue(ref(db, 'paper_eventi/stato'), (s) => setEv(s.val())),
      onValue(ref(db, 'paper_eventi/aperte'), (s) => setAperte(s.val())),
      onValue(ref(db, 'paper_eventi/chiuse'), (s) => setChiuse(s.val())),
    ];
    return () => u.forEach((x) => x());
  }, []);

  const lista_aperte = Object.values(aperte ?? {});
  const lista_chiuse = Object.values(chiuse ?? {}).sort((a, b) => (b.uscita ?? 0) - (a.uscita ?? 0)).slice(0, 15);

  return (
    <div className="panel">
      <h2>Il paper nel bot (ordini simulati, senza soldi veri)</h2>
      <p className="muted" style={{ margin: '0 0 8px', fontSize: 12.5 }}>
        Le strategie nuove eseguite dal bot sulla macchina con i prezzi del momento, ognuna con 10.000 dollari virtuali.
      </p>

      <Portafoglio ramo="paper_f5" titolo="Funding con la banda, cambio ogni lunedì (F5)"
        inizio="il primo cambio vero è il lunedì alle 00:05 UTC." />
      <div style={{ marginTop: 10 }} />
      <Portafoglio ramo="paper_g1" titolo="Funding con la banda, decisione ogni giorno (G1)"
        inizio="la prima decisione vera è alle 00:05 UTC del giorno dopo." />

      <div className="sotto-titolo" style={{ marginTop: 10 }}>Monete appena quotate e funding al tetto</div>
      {!ev ? (
        <p className="muted" style={{ margin: '2px 0', fontSize: 12.5 }}>Spento o non ancora partito.</p>
      ) : (
        <>
          <p style={{ margin: '2px 0', fontSize: 12.5 }}>
            <b>{ev.stato}</b> (aggiornato {quando(ev.aggiornato)}) · valore{' '}
            <b>${(ev.equity ?? 0).toLocaleString('it-IT', { maximumFractionDigits: 2 })}</b> ({pct(ev.rendimento)}) · aperte{' '}
            {(ev.aperte_n3 ?? 0) + (ev.aperte_e4 ?? 0)} · chiuse {ev.chiuse ?? 0}
            {ev.rendimento_medio != null ? ` (media ${pct(ev.rendimento_medio)})` : ''}
          </p>
          {lista_aperte.length > 0 && (
            <ul className="lista-grigia">
              {lista_aperte.map((x, i) => (
                <li key={i}>
                  {x.tipo === 'N3' ? 'moneta nuova' : 'funding al tetto'} <b>{nome(x.simbolo)}</b> short dal {giorno(x.entrata)}:{' '}
                  {pct(x.rendimento_ora)} ora, esce il {x.uscita_giorno}
                </li>
              ))}
            </ul>
          )}
          {lista_chiuse.length > 0 && (
            <ul className="lista-grigia">
              {lista_chiuse.map((x, i) => (
                <li key={i}>
                  {x.tipo === 'N3' ? 'moneta nuova' : 'funding al tetto'} <b>{nome(x.simbolo)}</b> chiusa il {giorno(x.uscita)}:{' '}
                  {pct(x.rendimento)} ({x.motivo})
                </li>
              ))}
            </ul>
          )}
        </>
      )}
    </div>
  );
}
