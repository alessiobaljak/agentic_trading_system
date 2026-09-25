'use client';

import { useEffect, useState, type ReactNode } from 'react';
import { useGateDoc, type DocGate } from '../lib/gate';
import { STATO, durata, formatta, numero, quando } from '../lib/viz';

/**
 * IL CERVELLO DEL GATE — cosa ha fatto l'ultimo giro e cosa ha scelto (25 set 2026).
 *
 * Prima queste righe vivevano solo nel log della VPS («[cervello] intorno …»,
 * «[cervello] keep del lock …») e per leggerle serviva un comando ops e qualche
 * minuto di attesa. Dal 25 set la discovery scrive il documento `dashboard/gate`
 * a fine giro (docs/controllo_schema.md §2) e questo pannello lo mostra: gli
 * STESSI numeri che il gate stampa, non una copia ricalcolata dal browser.
 *
 * Ogni blocco porta la data della sua sezione (`computed_at`) e le fonti, perche'
 * non hanno tutte la stessa eta': l'intorno gira solo nel giro completo delle
 * 03:30 UTC e negli altri giri viene ricopiato con la sua data
 * (`ultimo_completo_at`). Un numero senza data qui sarebbe una bugia comoda.
 */

/** Secondi «adesso», aggiornati ogni 30 s: le eta' («in corso da 12 min») devono
 *  muoversi anche quando il documento non cambia. */
export function useOrologio(passoMs = 30_000): number {
  const [now, setNow] = useState(() => Date.now() / 1000);
  useEffect(() => {
    const id = window.setInterval(() => setNow(Date.now() / 1000), passoMs);
    return () => window.clearInterval(id);
  }, [passoMs]);
  return now;
}

type Testata = {
  computed_at?: number | null;
  fonti?: string[] | null;
  errore?: string | null;
};

/** La riga «calcolato il … · fonti …» sotto ogni blocco. Un numero senza data e
 *  senza fonte e' una stima, e in questi pannelli non ce ne sono. */
export function Fonte({ sez, nota }: { sez: Testata | null | undefined; nota?: string }) {
  if (!sez) return null;
  return (
    <div className="muted" style={{ fontSize: 11, marginTop: 8, lineHeight: 1.5 }}>
      {sez.errore ? (
        <span style={{ color: STATO.critico }}>sezione non calcolata: {sez.errore} · </span>
      ) : null}
      calcolato {quando(sez.computed_at)}
      {sez.fonti && sez.fonti.length > 0 ? <> · fonti: {sez.fonti.join(', ')}</> : null}
      {nota ? <> · {nota}</> : null}
    </div>
  );
}

/**
 * Una distribuzione `[{valore, n}]` come barrette orizzontali. E' la forma con
 * cui il contratto scrive keep, scala e pass (niente liste di liste: Firestore
 * le rifiuta), quindi un solo componente le mostra tutte allo stesso modo.
 */
export function Distribuzione({
  voci,
  vuoto = 'nessuna',
  etichetta,
}: {
  voci: { valore: string | number; n: number }[] | null | undefined;
  vuoto?: string;
  etichetta?: (v: string | number) => string;
}) {
  const lista = (voci ?? []).filter((v) => v && Number.isFinite(Number(v.n)));
  if (lista.length === 0) {
    return <span className="muted" style={{ fontSize: 12 }}>{vuoto}</span>;
  }
  const max = Math.max(1, ...lista.map((v) => Number(v.n)));
  const tot = lista.reduce((s, v) => s + Number(v.n), 0);
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
      {lista.map((v) => {
        const n = Number(v.n);
        return (
          <div
            key={String(v.valore)}
            style={{
              display: 'grid',
              gridTemplateColumns: 'minmax(48px, auto) 1fr 72px',
              gap: 8,
              alignItems: 'center',
              fontSize: 12,
            }}
          >
            <span className="mono">{etichetta ? etichetta(v.valore) : String(v.valore)}</span>
            <span
              style={{
                height: 6,
                background: 'var(--border-soft)',
                borderRadius: 3,
                overflow: 'hidden',
                display: 'block',
              }}
            >
              <span
                style={{
                  display: 'block',
                  width: `${(n / max) * 100}%`,
                  height: '100%',
                  background: 'var(--accent)',
                  borderRadius: 3,
                }}
              />
            </span>
            <span className="muted mono" style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
              {formatta(n)} · {tot > 0 ? Math.round((n / tot) * 100) : 0}%
            </span>
          </div>
        );
      })}
    </div>
  );
}

const FASE: Record<string, string> = {
  optimize: 'ottimizzatore, strategie base',
  discover: 'discovery',
  passata_1h: 'passata extra a 1 h',
};

/**
 * La riga «ultimo giro: …» da `meta` del documento del gate. Vive qui e la
 * importano anche l'imbuto e l'autopsia, cosi' tutti i pannelli della Ricerca
 * dicono la stessa cosa sullo stesso giro.
 */
export function RigaUltimoGiro() {
  const { doc, caricamento, etaS } = useGateDoc();
  const now = useOrologio();
  if (caricamento) {
    return <span className="muted" style={{ fontSize: 12 }}>ultimo giro: caricamento…</span>;
  }
  const meta = doc?.meta;
  if (!meta) {
    return (
      <span className="muted" style={{ fontSize: 12 }}>
        ultimo giro: nessun documento del gate ancora (lo scrive la discovery a fine giro).
      </span>
    );
  }
  const eta = etaS ?? (meta.generato_at != null ? now - meta.generato_at : null);
  const modalita = meta.modalita ?? 'modalita’ ignota';
  let testo: ReactNode;
  let colore = 'var(--text)';
  if (meta.stato === 'in_corso') {
    const da = meta.iniziato_at != null ? now - meta.iniziato_at : null;
    testo = (
      <>
        in corso da <b>{durata(da)}</b>
        {meta.fase ? <> ({FASE[meta.fase] ?? meta.fase})</> : null}
        {eta != null ? <> · le sezioni sotto sono del giro finito {durata(eta)} fa</> : null}
      </>
    );
  } else if (meta.stato === 'errore') {
    colore = STATO.critico;
    testo = (
      <>
        <b>ERRORE</b> {eta != null ? `${durata(eta)} fa` : ''}
        {meta.errore ? <> — {meta.errore}</> : null}
      </>
    );
  } else {
    testo = (
      <>
        finito <b>{eta != null ? `${durata(eta)} fa` : '—'}</b>, {modalita}
        {meta.durata_s != null ? <>, durata {durata(meta.durata_s)}</> : null}
      </>
    );
  }
  return (
    <span style={{ fontSize: 12, color: colore }}>
      <span className="muted">ultimo giro:</span> {testo}
    </span>
  );
}

/** Tre numeri con le frecce: madri → figlie passate → promosse. E' un imbuto
 *  piccolo, non un grafico: la domanda e' «quante sopravvivono», non «quante sono». */
function Imbutino({ tappe }: { tappe: { label: string; n: number | null | undefined }[] }) {
  return (
    <div style={{ display: 'flex', gap: 6, alignItems: 'baseline', flexWrap: 'wrap' }}>
      {tappe.map((t, i) => (
        <span key={t.label} style={{ display: 'inline-flex', gap: 6, alignItems: 'baseline' }}>
          {i > 0 ? <span className="muted" aria-hidden="true">→</span> : null}
          <b style={{ fontSize: 18, lineHeight: 1.1 }}>{t.n == null ? '—' : formatta(t.n)}</b>
          <span className="muted" style={{ fontSize: 11 }}>{t.label}</span>
        </span>
      ))}
    </div>
  );
}

function Chips({ voci, vuoto }: { voci: string[] | null | undefined; vuoto?: string }) {
  const lista = (voci ?? []).filter(Boolean);
  if (lista.length === 0) return vuoto ? <span className="muted" style={{ fontSize: 12 }}>{vuoto}</span> : null;
  return (
    <div className="chip-row" style={{ marginTop: 4 }}>
      {lista.map((v) => (
        <span key={v} className="mini-chip mono" style={{ fontWeight: 500 }}>{v}</span>
      ))}
    </div>
  );
}

function Blocco({ titolo, children }: { titolo: string; children: ReactNode }) {
  return (
    <div
      style={{
        border: '1px solid var(--border-soft)',
        borderRadius: 10,
        padding: '12px 14px',
        marginBottom: 12,
        minWidth: 0,
      }}
    >
      <div className="muted" style={{ fontSize: 11, letterSpacing: '.04em', marginBottom: 8 }}>
        {titolo.toUpperCase()}
      </div>
      {children}
    </div>
  );
}

function Voce({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div style={{ marginTop: 10 }}>
      <div style={{ fontSize: 12, fontWeight: 600, marginBottom: 4 }}>{label}</div>
      {children}
    </div>
  );
}

const CANDIDATE: { chiave: string; label: string }[] = [
  { chiave: 'totale', label: 'valutate su ogni coin' },
  { chiave: 'ai', label: 'da AI' },
  { chiave: 'varianti_referti', label: 'varianti da referto' },
  { chiave: 'intorno', label: 'figlie dell’intorno' },
  { chiave: 'casuali', label: 'casuali' },
  { chiave: 'semi', label: 'semi' },
  { chiave: 'rivalutate', label: 'rivalutate' },
  { chiave: 'gemelle_scartate', label: 'gemelle scartate' },
];

export default function GateCervello() {
  const { doc, caricamento } = useGateDoc();
  const now = useOrologio();

  const g = doc?.giro;
  const c = doc?.cervello;
  const r = doc?.registro;

  return (
    <div className="panel">
      <h2>Il cervello del gate</h2>
      <p className="subtitle">
        Cosa ha fatto l&apos;ultimo giro e cosa ha scelto: gli stessi numeri che il gate
        scrive nel suo log, con la data di ogni blocco.
      </p>
      <div style={{ marginBottom: 12 }}>
        <RigaUltimoGiro />
      </div>

      {caricamento ? (
        <p className="muted">Caricamento…</p>
      ) : !doc ? (
        <p className="muted">
          Nessun documento del gate ancora: lo scrive la discovery alla fine del primo giro
          col codice del 25 set (ogni 3 ore).
        </p>
      ) : (
        <>
          <Blocco titolo="Il giro">
            {g ? (
              <>
                {g.lettura ? <p style={{ margin: '0 0 10px', fontSize: 13 }}>{g.lettura}</p> : null}
                <div className="stat-grid">
                  <div className="stat-tile">
                    <div className="stat-label">Coin valutate</div>
                    <div className="stat-value">{g.coin_valutate == null ? '—' : formatta(g.coin_valutate)}</div>
                  </div>
                  <div className="stat-tile">
                    <div className="stat-label">Valutazioni</div>
                    <div className="stat-value">{g.valutazioni == null ? '—' : formatta(g.valutazioni)}</div>
                    <div className="stat-sub">coppia × strategia provate</div>
                  </div>
                  <div className={`stat-tile${(g.passate ?? 0) > 0 ? ' good' : ''}`}>
                    <div className="stat-label">Passate</div>
                    <div className="stat-value">{g.passate == null ? '—' : formatta(g.passate)}</div>
                    <div className="stat-sub">hanno superato tutti i criteri</div>
                  </div>
                </div>

                <Voce label="Di cosa era fatta la lista delle candidate">
                  {g.candidate ? (
                    <div className="chip-row" style={{ marginTop: 0 }}>
                      {CANDIDATE.map(({ chiave, label }) => {
                        const v = (g.candidate as Record<string, number | null | undefined>)[chiave];
                        if (v == null) return null;
                        return (
                          <span key={chiave} className="mini-chip">
                            <span className="mono" style={{ color: 'var(--text)' }}>{formatta(v)}</span>
                            {label}
                          </span>
                        );
                      })}
                    </div>
                  ) : (
                    <span className="muted" style={{ fontSize: 12 }}>
                      non contabile in questo giro (documento fuso dagli shard di GitHub)
                    </span>
                  )}
                  {g.spec_rivalutate != null || g.spec_tagliate != null ? (
                    <div className="muted" style={{ fontSize: 12, marginTop: 4 }}>
                      spec note {g.spec_note == null ? '—' : formatta(g.spec_note)} · rivalutate{' '}
                      {g.spec_rivalutate == null ? '—' : formatta(g.spec_rivalutate)} (con conferme{' '}
                      {g.spec_con_conferme == null ? '—' : formatta(g.spec_con_conferme)}) · tagliate dal tetto{' '}
                      {g.spec_tagliate == null ? '—' : formatta(g.spec_tagliate)}
                      {g.tetto_rivalutazione != null ? <> (tetto {formatta(g.tetto_rivalutazione)})</> : null}
                    </div>
                  ) : null}
                </Voce>

                {g.passate_lista && g.passate_lista.length > 0 ? (
                  <Voce label="Le passate di questo giro">
                    <div className="chip-row" style={{ marginTop: 0 }}>
                      {g.passate_lista.map((p, i) => (
                        <span
                          key={`${p.coin}|${p.id}|${i}`}
                          className="mini-chip"
                          title={`PF ${numero(p.pf)} · PnL ${numero(p.pnl, 1)}%`}
                        >
                          {p.coin} <span className="mono">{p.id}</span>
                          <span className="muted" style={{ fontSize: 10 }}>PF {numero(p.pf)}</span>
                        </span>
                      ))}
                    </div>
                  </Voce>
                ) : null}

                {g.passata_1h ? (
                  <div className="muted" style={{ fontSize: 12, marginTop: 8 }}>
                    passata extra a 1 h: {quando(g.passata_1h.at)}, durata {durata(g.passata_1h.durata_s)},{' '}
                    {g.passata_1h.coin == null ? '—' : formatta(g.passata_1h.coin)} coin,{' '}
                    {g.passata_1h.valutazioni == null ? '—' : formatta(g.passata_1h.valutazioni)} valutazioni,{' '}
                    {g.passata_1h.passate == null ? '—' : formatta(g.passata_1h.passate)} passate
                  </div>
                ) : null}

                <div style={{ fontSize: 13, marginTop: 10 }}>
                  <b>Il paper propone:</b>{' '}
                  scala {g.paper_propone?.scala ?? <span className="muted">nessuna</span>} · keep{' '}
                  {g.paper_propone?.keep == null ? <span className="muted">nessuno</span> : numero(g.paper_propone.keep, 2)}{' '}
                  <span className="muted">
                    (su {formatta(g.paper_propone?.verdetti_trailing ?? 0)} verdetti trailing; e&apos; un
                    candidato in piu&apos; per il gate, non una decisione)
                  </span>
                </div>

                {g.worker != null || g.rss_max_mb != null ? (
                  <div className="muted" style={{ fontSize: 11, marginTop: 6 }}>
                    {g.worker != null ? <>{g.worker} worker</> : null}
                    {g.worker != null && g.rss_max_mb != null ? ' · ' : null}
                    {g.rss_max_mb != null ? <>RAM massima {numero(g.rss_max_mb, 0)} MB</> : null}
                  </div>
                ) : null}

                {r ? (
                  <div style={{ fontSize: 12, marginTop: 10 }}>
                    <b>Registro dopo il giro:</b> {formatta(r.validate ?? 0)} validate
                    {r.validate_delta_giro != null ? (
                      <span style={{ color: r.validate_delta_giro >= 0 ? STATO.buono : STATO.serio }}>
                        {' '}({r.validate_delta_giro >= 0 ? '+' : ''}{r.validate_delta_giro} dal giro prima)
                      </span>
                    ) : null}
                    {' '}· copertura {r.copertura == null ? '—' : `${Math.round(r.copertura * 100)}%`}
                    {r.obiettivo_copertura != null ? <> (obiettivo {Math.round(r.obiettivo_copertura * 100)}%)</> : null}
                    {' '}· pronto: {r.pronto == null ? '—' : r.pronto ? `si’ (per ${r.pronto_per ?? '?'})` : 'NO'}
                    {' '}· occupazione {formatta(r.occupazione ?? 0)}/{formatta(r.limite ?? 0)}
                    {r.senza_promessa ? <> · {formatta(r.senza_promessa)} validate senza promessa</> : null}
                  </div>
                ) : null}
                <Fonte sez={g} />
              </>
            ) : (
              <span className="muted">sezione assente</span>
            )}
          </Blocco>

          <Blocco titolo="Cosa ha scelto il cervello">
            {c ? (
              <>
                {c.riga ? (
                  <div className="mono" style={{ fontSize: 12, marginBottom: 8, whiteSpace: 'pre-wrap' }}>
                    {c.riga}
                  </div>
                ) : null}

                <Voce label="Intorno delle madri (gira solo nel giro completo delle 03:30 UTC)">
                  {c.intorno ? (
                    <>
                      <Imbutino
                        tappe={[
                          { label: 'madri', n: c.intorno.madri },
                          { label: 'figlie passate', n: c.intorno.figlie_passate },
                          { label: 'promosse', n: c.intorno.promosse?.length ?? 0 },
                        ]}
                      />
                      <Chips voci={c.intorno.promosse} />
                      <div className="muted" style={{ fontSize: 12, marginTop: 4 }}>
                        senza margine {formatta(c.intorno.senza_margine ?? 0)} · madre non valutata{' '}
                        {formatta(c.intorno.madre_non_valutata ?? 0)} · scartate {formatta(c.intorno.scartate ?? 0)}
                        {' '}· ultimo giro completo: {quando(c.intorno.ultimo_completo_at)}
                        {c.intorno.ultimo_completo_at != null && now - c.intorno.ultimo_completo_at > 30 * 3600 ? (
                          <span style={{ color: STATO.attenzione }}> (piu&apos; di un giorno fa)</span>
                        ) : null}
                      </div>
                    </>
                  ) : (
                    <span className="muted" style={{ fontSize: 12 }}>
                      nessun giro completo registrato ancora: l&apos;intorno arriva col giro delle 03:30 UTC
                    </span>
                  )}
                </Voce>

                <Voce label="Varianti dai referti del paper">
                  {c.varianti ? (
                    <>
                      <Imbutino
                        tappe={[
                          { label: 'create', n: c.varianti.create },
                          { label: 'passate', n: c.varianti.passate },
                          { label: 'retro ok', n: c.varianti.retro_ok },
                          { label: 'promosse', n: c.varianti.promosse?.length ?? 0 },
                        ]}
                      />
                      <Chips voci={c.varianti.promosse} />
                      {c.varianti.sostituzioni && c.varianti.sostituzioni.length > 0 ? (
                        <div style={{ marginTop: 6 }}>
                          <div className="muted" style={{ fontSize: 11 }}>sostituzioni (figlia al posto della madre)</div>
                          <div className="chip-row" style={{ marginTop: 4 }}>
                            {c.varianti.sostituzioni.map((s, i) => (
                              <span key={`${s.figlia}|${s.madre}|${i}`} className="mini-chip mono" style={{ fontWeight: 500 }}>
                                {s.figlia} <span className="muted">al posto di</span> {s.madre}
                              </span>
                            ))}
                          </div>
                        </div>
                      ) : null}
                      <div className="muted" style={{ fontSize: 12, marginTop: 4 }}>
                        scartate {formatta(c.varianti.scartate ?? 0)}
                      </div>
                    </>
                  ) : (
                    <span className="muted" style={{ fontSize: 12 }}>nessuna variante in questo giro</span>
                  )}
                </Voce>

                <div className="grid grid-2" style={{ marginTop: 10 }}>
                  <div>
                    <Voce label="Keep del profit-lock scelto in QUESTO giro">
                      <Distribuzione
                        voci={c.keep_giro?.scelti}
                        vuoto="nessuna coppia passata"
                        etichetta={(v) => `keep ${numero(Number(v), 2)}`}
                      />
                      <div className="muted" style={{ fontSize: 12, marginTop: 4 }}>
                        non scelto ×{formatta(c.keep_giro?.non_scelto ?? 0)}
                        {c.keep_giro?.dal_paper != null ? (
                          <>
                            {' '}· il candidato del paper ({numero(c.keep_giro.dal_paper, 2)}) ha vinto{' '}
                            {formatta(c.keep_giro.dal_paper_n ?? 0)} volte
                          </>
                        ) : (
                          <> · il paper non aveva un candidato</>
                        )}
                      </div>
                    </Voce>
                  </div>
                  <div>
                    <Voce label="Keep delle validate (tutto il registro)">
                      <Distribuzione
                        voci={c.keep_validate?.distribuzione}
                        vuoto="nessuna validata col keep per coppia"
                        etichetta={(v) => `keep ${numero(Number(v), 2)}`}
                      />
                      <div className="muted" style={{ fontSize: 12, marginTop: 4 }}>
                        non rivalutate ×{formatta(c.keep_validate?.non_rivalutate ?? 0)}: validate prima del
                        parametro, operano col keep di allora
                      </div>
                    </Voce>
                  </div>
                  <div>
                    <Voce label="Scala di take-profit delle validate">
                      <Distribuzione
                        voci={(c.scala_validate ?? []).map((s) => ({ valore: s.scala ?? 'senza scala', n: s.n }))}
                        vuoto="nessuna"
                        etichetta={(v) => `${v}R`}
                      />
                      <div className="muted" style={{ fontSize: 12, marginTop: 4 }}>
                        stop a pareggio dopo il primo gradino: {formatta(c.breakeven_validate ?? 0)} validate
                      </div>
                    </Voce>
                  </div>
                  <div>
                    <Voce label="Autopsia e supervisore">
                      {c.autopsia ? (
                        <div style={{ fontSize: 12 }}>
                          autopsia discovery ({quando(c.autopsia.at)}): {formatta(c.autopsia.valutazioni ?? 0)} valutazioni,{' '}
                          {formatta(c.autopsia.passate ?? 0)} passate
                          {c.autopsia.quota != null ? <> ({numero(c.autopsia.quota * 100, 2)}%)</> : null}
                          {c.autopsia.criterio_principale ? (
                            <>
                              {' '}· ferma di piu&apos;: <b>{c.autopsia.criterio_principale}</b>
                              {c.autopsia.quota_criterio != null ? <> ({Math.round(c.autopsia.quota_criterio * 100)}% delle bocciate)</> : null}
                            </>
                          ) : null}
                          {c.autopsia.quasi_passaggi != null ? <> · {formatta(c.autopsia.quasi_passaggi)} a un passo</> : null}
                        </div>
                      ) : (
                        <div className="muted" style={{ fontSize: 12 }}>autopsia della discovery assente</div>
                      )}
                      {c.autopsia_base_congelata_da_s != null ? (
                        <div className="muted" style={{ fontSize: 12, marginTop: 4 }}>
                          autopsia delle strategie base ferma da {durata(c.autopsia_base_congelata_da_s)}
                        </div>
                      ) : null}
                      <div style={{ fontSize: 12, marginTop: 6 }}>
                        {c.supervisore ? (
                          <>
                            supervisore ({quando(c.supervisore.at)}):{' '}
                            {c.supervisore.ultima_decisione ? (
                              <>
                                <b>{c.supervisore.ultima_decisione.kind ?? '—'}</b>
                                {c.supervisore.ultima_decisione.reason ? <> — {c.supervisore.ultima_decisione.reason}</> : null}
                              </>
                            ) : (
                              'nessuna decisione'
                            )}
                            {(c.supervisore.decisioni_none_di_fila ?? 0) > 0 ? (
                              <span className="muted"> · {formatta(c.supervisore.decisioni_none_di_fila)} «nessuna azione» di fila</span>
                            ) : null}
                          </>
                        ) : (
                          <span className="muted">supervisore: nessun documento</span>
                        )}
                      </div>
                    </Voce>
                  </div>
                </div>
                <Fonte sez={c} />
              </>
            ) : (
              <span className="muted">sezione assente</span>
            )}
          </Blocco>
        </>
      )}
    </div>
  );
}
