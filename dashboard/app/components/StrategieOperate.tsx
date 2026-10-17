'use client';

import { Fragment, useEffect, useMemo, useState, type ReactNode } from 'react';
import { useGateDoc, type DocGate } from '../lib/gate';
import { STATO, formatta, numero, quando, segno } from '../lib/viz';
import { Fonte } from './GateCervello';

/**
 * LE STRATEGIE CHE IL BOT OPERA, coppia per coppia (25 set 2026).
 *
 * La domanda del proprietario e' sempre la stessa: «quello che il gate ha promesso
 * si sta vedendo nel paper?». Per rispondere servono, sulla stessa riga, la
 * promessa (PF del backtest, `pf_promesso`) e il vissuto (PF dei trade del paper
 * per QUELLA coppia, `paper.pf_vissuto`), piu' il verdetto della deriva se c'e'.
 * Prima i tre numeri stavano in tre documenti diversi e li si incrociava a mano.
 *
 * I dati sono la sezione `strategie` di `dashboard/gate` (docs/controllo_schema.md
 * §2.5), scritta dalla discovery a fine giro: la lista e' quella delle coppie
 * OPERATE (validate, fresche, non sostituite, robuste — la stessa regola di
 * `adaptation._robust_only`), non tutte le validate. Se e' troncata a 300 lo
 * dice `operate_troncate`.
 *
 * Il PF senza perdite e' `null` per contratto (non 99): qui si mostra «∞» col
 * numero di trade accanto, perche' 3 trade vinti su 3 non sono un edge.
 */

type Strategie = NonNullable<DocGate['strategie']>;
type Operata = NonNullable<Strategie['operate']>[number];

type Chiave = 'pf_vissuto' | 'trade' | 'coin' | 'pf_promesso' | 'pass';
type Ordine = { chiave: Chiave; disc: boolean } | null;

const VERDETTO: Record<string, { label: string; colore: string }> = {
  ok: { label: 'ok', colore: STATO.buono },
  watch: { label: 'sotto osservazione', colore: STATO.attenzione },
  drift: { label: 'deriva', colore: STATO.critico },
};

/** Sotto i 640 px la tabella mostra 5 colonne e il resto si apre nella riga. */
function useTelefono(): boolean {
  const [tel, setTel] = useState(false);
  useEffect(() => {
    const mq = window.matchMedia('(max-width: 640px)');
    const f = () => setTel(mq.matches);
    f();
    mq.addEventListener('change', f);
    return () => mq.removeEventListener('change', f);
  }, []);
  return tel;
}

/** PF con la regola del contratto: null + perdite 0 = «∞» (nessuna perdita). */
function Pf({ v, perdite, trade }: { v: number | null | undefined; perdite?: number | null; trade?: number | null }) {
  if (v == null) {
    if (perdite === 0 && (trade ?? 0) > 0) {
      return <span title="nessuna perdita finora: il PF non si calcola">∞</span>;
    }
    return <span className="muted">—</span>;
  }
  const colore = v >= 1.3 ? STATO.buono : v >= 1 ? 'var(--text)' : STATO.critico;
  return <span style={{ color: colore }}>{numero(v, 2)}</span>;
}

function Verdetto({ v, motivo }: { v: string | null | undefined; motivo?: string | null }) {
  if (!v) return <span className="muted">—</span>;
  const k = VERDETTO[v] ?? { label: v, colore: 'var(--text-dim)' };
  return (
    <span style={{ color: k.colore, fontWeight: 600, whiteSpace: 'nowrap' }} title={motivo ?? undefined}>
      {k.label}
    </span>
  );
}

function Riga({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div style={{ display: 'flex', gap: 8, fontSize: 12, padding: '2px 0' }}>
      <span className="muted" style={{ minWidth: 120 }}>{label}</span>
      <span style={{ minWidth: 0 }}>{children}</span>
    </div>
  );
}

/** Intestazione ordinabile. Sta fuori dal componente: definita dentro il render
 *  sarebbe un tipo nuovo a ogni giro e React smonterebbe le celle ogni volta. */
function Th({
  chiave, children, sinistra, ordine, clicca,
}: {
  chiave?: Chiave; children: ReactNode; sinistra?: boolean; ordine: Ordine; clicca: (k: Chiave) => void;
}) {
  const stile = { padding: '6px 8px', whiteSpace: 'nowrap', textAlign: sinistra ? 'left' : undefined } as const;
  return (
    <th
      style={{ ...stile, cursor: chiave ? 'pointer' : 'default', userSelect: 'none' }}
      onClick={chiave ? () => clicca(chiave) : undefined}
      title={chiave ? 'clicca per ordinare' : undefined}
      aria-sort={chiave && ordine?.chiave === chiave ? (ordine.disc ? 'descending' : 'ascending') : undefined}
    >
      {children}
      {chiave && ordine?.chiave === chiave ? <span aria-hidden="true"> {ordine.disc ? '▾' : '▴'}</span> : null}
    </th>
  );
}

function valore(o: Operata, k: Chiave): number | string {
  switch (k) {
    case 'pf_vissuto': return o.paper?.pf_vissuto ?? (o.paper?.perdite === 0 && (o.paper?.trades ?? 0) > 0 ? 999 : -1);
    case 'trade': return o.paper?.trades ?? -1;
    case 'coin': return o.coin ?? '';
    case 'pf_promesso': return o.pf_promesso ?? -1;
    case 'pass': return o.pass ?? -1;
  }
}

export default function StrategieOperate() {
  const { doc, caricamento } = useGateDoc();
  const telefono = useTelefono();
  const [ordine, setOrdine] = useState<Ordine>(null);
  const [famiglia, setFamiglia] = useState<string | null>(null);
  const [soloPaper, setSoloPaper] = useState(false);
  const [aperte, setAperte] = useState<Set<string>>(new Set());
  const [quante, setQuante] = useState(60);

  const s = doc?.strategie;
  const operate = useMemo<Operata[]>(() => (s?.operate ?? []) as Operata[], [s]);

  const famiglie = useMemo(() => {
    const set = new Map<string, number>();
    for (const o of operate) {
      const f = o.famiglia ?? 'ignota';
      set.set(f, (set.get(f) ?? 0) + 1);
    }
    return [...set.entries()].sort((a, b) => b[1] - a[1]);
  }, [operate]);

  const righe = useMemo(() => {
    let out = operate.filter(
      (o) => (!famiglia || (o.famiglia ?? 'ignota') === famiglia) && (!soloPaper || (o.paper?.trades ?? 0) > 0),
    );
    if (ordine) {
      const { chiave, disc } = ordine;
      out = [...out].sort((a, b) => {
        const va = valore(a, chiave);
        const vb = valore(b, chiave);
        const cmp = typeof va === 'string' || typeof vb === 'string'
          ? String(va).localeCompare(String(vb))
          : va - vb;
        return disc ? -cmp : cmp;
      });
    }
    return out;
  }, [operate, famiglia, soloPaper, ordine]);

  useEffect(() => setQuante(60), [famiglia, soloPaper, ordine]);

  const clicca = (chiave: Chiave) =>
    setOrdine((o) => (o && o.chiave === chiave ? (o.disc ? { chiave, disc: false } : null) : { chiave, disc: chiave !== 'coin' }));

  const toggle = (k: string) =>
    setAperte((prev) => {
      const next = new Set(prev);
      if (next.has(k)) next.delete(k);
      else next.add(k);
      return next;
    });

  const cell = { padding: '6px 8px', whiteSpace: 'nowrap' } as const;
  const testo = { ...cell, textAlign: 'left' } as const;
  const chip = (attivo: boolean) =>
    ({
      padding: '4px 12px',
      fontSize: 12,
      borderRadius: 999,
      cursor: 'pointer',
      border: `1px solid ${attivo ? 'var(--accent)' : 'var(--border)'}`,
      background: attivo ? 'var(--accent-soft)' : 'var(--bg-elev)',
      color: attivo ? 'var(--text)' : 'var(--text-dim)',
      whiteSpace: 'nowrap',
    }) as const;

  return (
    <div className="panel">
      <h2>Strategie operate</h2>
      <p className="subtitle">
        Coppia per coppia: cosa ha promesso il gate (PF del backtest) e cosa si e&apos; visto nel
        paper. Clicca un&apos;intestazione per ordinare, una riga per il dettaglio.
      </p>

      {caricamento ? (
        <p className="muted">Caricamento…</p>
      ) : !s ? (
        <p className="muted">
          Nessun documento del gate ancora: la lista arriva con il primo giro finito col codice
          del 25 set.
        </p>
      ) : s.errore ? (
        <p className="muted">Sezione non calcolata: {s.errore}</p>
      ) : (
        <>
          {s.lettura ? <p style={{ fontSize: 13, margin: '0 0 10px' }}>{s.lettura}</p> : null}

          <div className="muted" style={{ fontSize: 12, marginBottom: 12, lineHeight: 1.6 }}>
            <b style={{ color: 'var(--text)' }}>{formatta(s.n_operate ?? 0)} operate</b>
            {' '}· {s.n_con_paper == null ? '?' : formatta(s.n_con_paper)} con trade nel paper
            {' '}· {formatta(s.n_senza_promessa ?? 0)} senza promessa
            {' '}· {formatta(s.n_sostituite ?? 0)} madri sostituite da una figlia
            {' '}· {formatta(s.n_nate_intorno ?? 0)} nate nell&apos;intorno
            {' '}· {formatta(s.n_da_referto ?? 0)} da referto
            {' '}· {formatta(s.n_scadute_dal_giro ?? 0)} validate ma non operate (scadute o non robuste)
            {s.vite ? (
              s.vite.parziale ? (
                <> · vite ultimi 7 g: non disponibili</>
              ) : (
                <> · ultimi 7 g: {formatta(s.vite.promosse_7g ?? 0)} promosse, {formatta(s.vite.rimosse_7g ?? 0)} rimosse</>
              )
            ) : null}
            {(s.operate_troncate ?? 0) > 0 ? (
              <span style={{ color: STATO.attenzione }}> · lista troncata: {formatta(s.operate_troncate)} coppie fuori</span>
            ) : null}
          </div>

          {s.promessa_vs_vissuto ? (
            <div
              style={{
                background: 'var(--bg-elev)',
                border: '1px solid var(--border)',
                borderRadius: 10,
                padding: '10px 12px',
                marginBottom: 12,
                fontSize: 13,
              }}
            >
              <b>Promessa contro vissuto:</b> PF promesso mediano delle operate{' '}
              <b><Pf v={s.promessa_vs_vissuto.pf_promesso_mediano_operate} /></b>
              {' '}· PF atteso medio del registro{' '}
              <b><Pf v={s.promessa_vs_vissuto.pf_atteso_media_registro} /></b>
              {' '}· PF vissuto negli ultimi 30 g{' '}
              <b><Pf v={s.promessa_vs_vissuto.pf_vissuto_30g} /></b>
              <span className="muted"> (dal documento di deriva; «—» = nessuna perdita o niente trade)</span>
            </div>
          ) : null}

          {s.per_famiglia && s.per_famiglia.length > 0 ? (
            <div className="stat-grid" style={{ marginBottom: 14 }}>
              {s.per_famiglia.map((f) => (
                <div
                  key={f.famiglia ?? 'ignota'}
                  className="stat-tile"
                  style={{ cursor: 'pointer' }}
                  onClick={() => setFamiglia((cur) => (cur === (f.famiglia ?? 'ignota') ? null : f.famiglia ?? 'ignota'))}
                  title="clicca per filtrare la tabella su questa famiglia"
                >
                  <div className="stat-label">{f.famiglia ?? 'ignota'}</div>
                  <div className="stat-value">{formatta(f.coppie ?? 0)}</div>
                  <div className="stat-sub">
                    coppie su {formatta(f.coin ?? 0)} coin · PF promesso mediano {numero(f.pf_promesso_mediano, 2)}
                  </div>
                  <div className="stat-sub">
                    paper: {f.paper_trades == null ? '—' : formatta(f.paper_trades)} trade ·{' '}
                    <span className={(f.paper_pnl ?? 0) >= 0 ? 'pos' : 'neg'}>{segno(f.paper_pnl, 2)}</span>
                    {' '}· PF <Pf v={f.paper_pf} />
                  </div>
                </div>
              ))}
            </div>
          ) : null}

          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center', marginBottom: 10 }}>
            <button onClick={() => setFamiglia(null)} style={chip(famiglia === null)}>tutte le famiglie</button>
            {famiglie.map(([f, n]) => (
              <button key={f} onClick={() => setFamiglia((cur) => (cur === f ? null : f))} style={chip(famiglia === f)}>
                {f} <span className="muted">{n}</span>
              </button>
            ))}
            <button onClick={() => setSoloPaper((v) => !v)} style={chip(soloPaper)} aria-pressed={soloPaper}>
              solo con trade in paper
            </button>
            <span className="muted" style={{ fontSize: 12, marginLeft: 'auto' }}>
              {formatta(righe.length)} coppie
            </span>
          </div>

          {righe.length === 0 ? (
            <p className="muted" style={{ fontSize: 13 }}>Nessuna coppia con questi filtri.</p>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
                <thead>
                  <tr style={{ color: 'var(--text-dim)' }}>
                    <Th ordine={ordine} clicca={clicca} chiave="coin" sinistra>Coin</Th>
                    <Th ordine={ordine} clicca={clicca} sinistra>Strategia</Th>
                    {!telefono ? <Th ordine={ordine} clicca={clicca} sinistra>Famiglia</Th> : null}
                    {!telefono ? <Th ordine={ordine} clicca={clicca} sinistra>Origine</Th> : null}
                    {!telefono ? <Th ordine={ordine} clicca={clicca} chiave="pass">Pass</Th> : null}
                    <Th ordine={ordine} clicca={clicca} chiave="pf_promesso">PF promesso</Th>
                    <Th ordine={ordine} clicca={clicca} chiave="pf_vissuto">PF vissuto</Th>
                    <Th ordine={ordine} clicca={clicca} chiave="trade">Trade paper</Th>
                    <Th ordine={ordine} clicca={clicca} sinistra>Verdetto</Th>
                    {!telefono ? <Th ordine={ordine} clicca={clicca}>Keep</Th> : null}
                    {!telefono ? <Th ordine={ordine} clicca={clicca}>Scala</Th> : null}
                    {!telefono ? <Th ordine={ordine} clicca={clicca}>BE</Th> : null}
                  </tr>
                </thead>
                <tbody>
                  {righe.slice(0, quante).map((o) => {
                    const k = o.chiave ?? `${o.coin}|${o.strategia}`;
                    const aperta = aperte.has(k);
                    const colonne = telefono ? 6 : 12;
                    return (
                      <Fragment key={k}>
                        <tr
                          onClick={() => toggle(k)}
                          style={{ borderTop: '1px solid var(--border-soft)', cursor: 'pointer', background: aperta ? 'var(--bg-elev)' : undefined }}
                          aria-expanded={aperta}
                        >
                          <td style={testo}><b>{o.coin}</b></td>
                          <td style={{ ...testo, fontFamily: 'ui-monospace, monospace', fontSize: 12 }}>{o.strategia}</td>
                          {!telefono ? <td style={testo}>{o.famiglia ?? <span className="muted">—</span>}</td> : null}
                          {!telefono ? (
                            <td
                              style={testo}
                              title={[o.genitore ? `genitore: ${o.genitore}` : null, o.ipotesi ? `ipotesi: ${o.ipotesi}` : null]
                                .filter(Boolean)
                                .join(' · ') || undefined}
                            >
                              {o.origine ?? <span className="muted">—</span>}
                              {o.genitore || o.ipotesi ? <span className="muted"> ⓘ</span> : null}
                            </td>
                          ) : null}
                          {!telefono ? <td style={cell}>{o.pass ?? '—'}</td> : null}
                          <td style={cell}><Pf v={o.pf_promesso} /></td>
                          <td style={cell}><Pf v={o.paper?.pf_vissuto} perdite={o.paper?.perdite} trade={o.paper?.trades} /></td>
                          <td style={cell}>
                            {o.paper ? (
                              <>
                                {formatta(o.paper.trades ?? 0)}
                                <span className="muted" style={{ fontSize: 11 }}> ({formatta(o.paper.vinti ?? 0)} vinti)</span>
                              </>
                            ) : (
                              <span className="muted">0</span>
                            )}
                          </td>
                          <td style={testo}><Verdetto v={o.paper?.verdetto} motivo={o.paper?.motivo} /></td>
                          {!telefono ? <td style={cell}>{o.keep == null ? <span className="muted">—</span> : numero(o.keep, 2)}</td> : null}
                          {!telefono ? <td style={{ ...cell, fontFamily: 'ui-monospace, monospace', fontSize: 12 }}>{o.scala ?? <span className="muted">—</span>}</td> : null}
                          {!telefono ? (
                            <td style={cell} title="stop a pareggio dopo il primo take-profit">
                              {o.breakeven == null ? <span className="muted">—</span> : o.breakeven ? 'si’' : 'no'}
                            </td>
                          ) : null}
                        </tr>
                        {aperta ? (
                          <tr style={{ background: 'var(--bg-elev)' }}>
                            <td colSpan={colonne} style={{ padding: '6px 12px 10px', textAlign: 'left' }}>
                              <div style={{ display: 'grid', gridTemplateColumns: telefono ? '1fr' : 'repeat(2, minmax(0, 1fr))', gap: '0 16px' }}>
                                <div>
                                  <Riga label="famiglia · origine">{o.famiglia ?? '—'} · {o.origine ?? '—'}</Riga>
                                  {o.genitore ? <Riga label="genitore">{o.genitore}</Riga> : null}
                                  {o.ipotesi ? <Riga label="ipotesi">{o.ipotesi}</Riga> : null}
                                  <Riga label="conferme">{o.pass ?? '—'} · validata {quando(o.validata_at)} · ultimo pass {quando(o.ultimo_pass_at)}</Riga>
                                  <Riga label="promessa">
                                    PF <Pf v={o.pf_promesso} /> · PnL {o.pnl_promesso_pct == null ? '—' : `${segno(o.pnl_promesso_pct, 1)}%`}
                                    {' '}· t {o.t == null ? '—' : numero(o.t, 2)}
                                    {' '}· holdout {o.holdout_ok == null ? '—' : o.holdout_ok ? 'ok' : 'NO'}
                                  </Riga>
                                  {o.direzione_pf ? (
                                    <Riga label="PF per direzione">
                                      long <Pf v={o.direzione_pf.long} /> · short <Pf v={o.direzione_pf.short} />
                                    </Riga>
                                  ) : null}
                                </div>
                                <div>
                                  <Riga label="piano">
                                    keep {o.keep == null ? '—' : numero(o.keep, 2)} · scala {o.scala ?? '—'} · pareggio dopo TP1{' '}
                                    {o.breakeven == null ? '—' : o.breakeven ? 'si’' : 'no'}
                                  </Riga>
                                  {o.paper ? (
                                    <>
                                      <Riga label="paper">
                                        {formatta(o.paper.trades ?? 0)} trade, {formatta(o.paper.vinti ?? 0)} vinti, {formatta(o.paper.perdite ?? 0)} persi ·{' '}
                                        <span className={(o.paper.pnl ?? 0) >= 0 ? 'pos' : 'neg'}>{segno(o.paper.pnl, 2)}</span>
                                        {' '}· PF <Pf v={o.paper.pf_vissuto} perdite={o.paper.perdite} trade={o.paper.trades} />
                                      </Riga>
                                      <Riga label="deriva">
                                        <Verdetto v={o.paper.verdetto} />{o.paper.motivo ? <> — {o.paper.motivo}</> : null}
                                      </Riga>
                                    </>
                                  ) : (
                                    <Riga label="paper">nessun trade ancora</Riga>
                                  )}
                                </div>
                              </div>
                            </td>
                          </tr>
                        ) : null}
                      </Fragment>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}

          {righe.length > quante ? (
            <button onClick={() => setQuante((q) => q + 60)} style={{ ...chip(false), marginTop: 10, padding: '5px 14px' }}>
              mostra altre ({formatta(righe.length - quante)})
            </button>
          ) : null}

          <Fonte sez={s} nota="operate = validate fresche, non sostituite e robuste; paper = trade per coppia senza esiti esterni" />
        </>
      )}
    </div>
  );
}
