'use client';

import { useControllo, type Controllo } from '../lib/controllo';
import { STATO, durata, formatta, numero, pct, quando, quota } from '../lib/viz';
import { Distribuzione, Fonte, useOrologio } from './GateCervello';
import { ColonnaMisurato, Voce } from './LearningMisurato';

/**
 * IL LEARNING, DIVISO IN DUE: cosa cambia le decisioni ADESSO e cosa e' solo
 * misurato (25 set 2026).
 *
 * La domanda del proprietario e' «cosa ha imparato il bot, e cosa e' cambiato
 * nelle ultime 24 ore?». Le risposte vecchie erano un elenco di pannelli, ognuno
 * con i suoi numeri, e nessuno diceva se quel numero TOCCAVA un trade oppure no.
 * Il contratto (docs/controllo_schema.md §1.4) li separa alla fonte:
 *
 *   * `attivo`  — freno globale, gate pronto, pesi in panchina, keep per coppia,
 *                 freno di serie, tetti, cooldown, fiducia della calibrazione:
 *                 ognuno cambia una decisione del bot in questo momento;
 *   * `misurato` — deriva, calibrazione, trailing, referti, selettore, AI:
 *                 osservati e scritti, ma nessun trade cambia per loro.
 *
 * In testa c'e' `cambiamenti_24h`: la differenza fra l'impronta di adesso e
 * quella del controllo precedente. Vuota vuol dire «nessun pezzo del learning ha
 * cambiato decisione», ed e' un'informazione, non un vuoto.
 */

type Attivo = NonNullable<NonNullable<Controllo['learning']>['attivo']>;

function Acceso({ on, si = 'ACCESO', no = 'spento' }: { on: boolean | null | undefined; si?: string; no?: string }) {
  if (on == null) return <span className="muted">non misurato</span>;
  return <b style={{ color: on ? STATO.critico : STATO.buono }}>{on ? si : no}</b>;
}

function ColonnaAttivo({ a, salute, now }: { a: Attivo | null | undefined; salute: Controllo['salute'] | null | undefined; now: number }) {
  if (!a) return <p className="muted" style={{ fontSize: 12 }}>sezione «attivo» assente</p>;
  if (a.errore) return <p className="muted" style={{ fontSize: 12 }}>sezione non calcolata: {a.errore}</p>;
  const f = a.freno_globale;
  const p = a.pesi;
  const t = a.tilt;
  const fs = a.freno_serie;
  const tt = a.tetti;
  const cdCoin = salute?.cooldown_coin ?? [];
  const cdStrat = salute?.cooldown_strategie ?? [];
  return (
    <>
      {a.lettura ? <p style={{ fontSize: 13, margin: '0 0 6px' }}>{a.lettura}</p> : null}

      <Voce titolo="Freno globale" nota="dimezza la size di tutti i trade quando il PF vissuto crolla">
        {f ? (
          <>
            <Acceso on={f.attivo} />
            {f.attivo && f.dal != null ? <> dal {quando(f.dal)} ({durata(now - f.dal)})</> : null}
            {' '}· verdetto {f.verdetto ?? '—'} su {f.trades == null ? '—' : formatta(f.trades)} trade
            {' '}· PF vissuto {f.pf_vissuto == null ? '—' : numero(f.pf_vissuto, 2)} contro atteso{' '}
            {f.pf_atteso == null ? '—' : numero(f.pf_atteso, 2)}
            {f.soglia_uscita_pf != null ? <> (si spegne sopra {numero(f.soglia_uscita_pf, 2)})</> : null}
            {' '}· size ×{numero(f.size_x, 2)}
            {f.motivo ? <div className="muted" style={{ fontSize: 11 }}>{f.motivo}</div> : null}
            {f.pf_atteso_nota ? <div className="muted" style={{ fontSize: 11 }}>PF atteso = {f.pf_atteso_nota}</div> : null}
          </>
        ) : (
          <span className="muted">non misurato</span>
        )}
      </Voce>

      <Voce titolo="Gate pronto" nota="senza il si' del gate il bot resta flat">
        {a.gate_pronto == null ? (
          <span className="muted">non misurato</span>
        ) : a.gate_pronto ? (
          <b style={{ color: STATO.buono }}>si&apos;: il bot puo&apos; aprire</b>
        ) : (
          <b style={{ color: STATO.critico }}>NO: il bot resta flat</b>
        )}
      </Voce>

      <Voce titolo="Pesi strategia × regime" nota={p?.at ? quando(p.at) : undefined}>
        {p ? (
          <>
            <b style={{ color: (p.in_panchina_n ?? 0) > 0 ? STATO.attenzione : 'var(--text)' }}>
              {formatta(p.in_panchina_n ?? 0)} in panchina
            </b>
            {' '}· <b style={{ color: (p.spente_n ?? 0) > 0 ? STATO.critico : 'var(--text)' }}>{formatta(p.spente_n ?? 0)} spente</b>
            {' '}su {formatta(p.combinazioni ?? 0)} combinazioni
            <div className="muted" style={{ fontSize: 11 }}>
              panchina = peso sotto {numero(p.soglia_panchina, 2)} (a convinzione 60 non passa piu&apos; la soglia); spenta = peso 0
              {p.campioni_sommati != null ? <> · {formatta(p.campioni_sommati)} trade sommati</> : null}
              {p.versione != null ? <> · versione {p.versione}</> : null}
              {p.aggiornato_da_nota ? <> · aggiornati da: {p.aggiornato_da_nota}</> : null}
            </div>
            {p.in_panchina && p.in_panchina.length > 0 ? (
              <div style={{ overflowX: 'auto', marginTop: 4 }}>
                <table style={{ borderCollapse: 'collapse', fontSize: 12, width: '100%' }}>
                  <thead>
                    <tr className="muted">
                      <th style={{ padding: '2px 6px 2px 0', textAlign: 'left' }}>strategia · regime</th>
                      <th style={{ padding: '2px 6px' }}>peso</th>
                      <th style={{ padding: '2px 6px' }}>campione</th>
                      <th style={{ padding: '2px 6px' }}>win rate</th>
                    </tr>
                  </thead>
                  <tbody>
                    {p.in_panchina.map((w) => (
                      <tr key={`${w.strategia}|${w.regime}`} style={{ borderTop: '1px solid var(--border-soft)' }}>
                        <td className="mono" style={{ padding: '2px 6px 2px 0', textAlign: 'left', whiteSpace: 'nowrap' }}>
                          {w.strategia} <span className="muted">· {w.regime}</span>
                        </td>
                        <td style={{ padding: '2px 6px', color: (w.peso ?? 0) <= 0 ? STATO.critico : STATO.attenzione, fontWeight: 600 }}>
                          {numero(w.peso, 2)}
                        </td>
                        <td style={{ padding: '2px 6px' }}>{w.campione == null ? '—' : formatta(w.campione)}</td>
                        <td style={{ padding: '2px 6px' }}>{w.win_rate == null ? '—' : quota(w.win_rate)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {(p.in_panchina_n ?? 0) > p.in_panchina.length ? (
                  <div className="muted" style={{ fontSize: 11 }}>
                    mostrate le prime {p.in_panchina.length} di {formatta(p.in_panchina_n)}: il resto nella scheda Apprendimento
                  </div>
                ) : null}
              </div>
            ) : null}
          </>
        ) : (
          <span className="muted">non misurati</span>
        )}
      </Voce>

      <Voce titolo="Inclinazioni (tilt)" nota="alzano o abbassano la convinzione di un segnale">
        {t ? (
          <>
            trend: <Acceso on={t.trend_enabled} si="attivo" no="spento" />
            {t.trend_enabled ? <> (forza {numero(t.trend_strength, 2)}, pavimento {numero(t.trend_floor, 2)})</> : null}
            {' '}· sentiment: <Acceso on={t.sentiment_enabled} si="attivo" no="spento" />
            {t.sentiment_enabled ? <> (forza {numero(t.sentiment_strength, 2)})</> : null}
          </>
        ) : (
          <span className="muted">non misurate</span>
        )}
      </Voce>

      <Voce titolo="Keep del profit-lock per coppia" nota="quanto del massimo raggiunto si tiene">
        <Distribuzione
          voci={a.keep_per_coppia?.distribuzione}
          vuoto="nessuna validata col keep per coppia"
          etichetta={(v) => `keep ${numero(Number(v), 2)}`}
        />
        <div className="muted" style={{ fontSize: 11, marginTop: 4 }}>
          non rivalutate ×{formatta(a.keep_per_coppia?.non_rivalutate ?? 0)}: operano col keep imparato per strategia
        </div>
      </Voce>

      <Voce titolo="Freno di serie" nota="dopo N perdite di fila la strategia rischia meno">
        {fs ? (
          <>
            <Acceso on={fs.enabled} si="attivo" no="spento" />
            {' '}· scatta a {formatta(fs.perdite_soglia ?? 0)} perdite di fila, size ×{numero(fs.fattore, 2)}
            {fs.serie && fs.serie.length > 0 ? (
              <div className="chip-row" style={{ marginTop: 4 }}>
                {fs.serie.map((s) => (
                  <span
                    key={s.strategia}
                    className="mini-chip"
                    style={(s.perdite ?? 0) >= (fs.perdite_soglia ?? Infinity) ? { color: STATO.critico } : undefined}
                  >
                    <span className="mono">{s.strategia}</span> {formatta(s.perdite ?? 0)} di fila
                  </span>
                ))}
              </div>
            ) : (
              <div className="muted" style={{ fontSize: 11 }}>nessuna serie di perdite in corso</div>
            )}
          </>
        ) : (
          <span className="muted">non misurato</span>
        )}
      </Voce>

      <Voce titolo="Tetti di rischio">
        {tt ? (
          <>
            per coin al giorno {pct(tt.coin_giorno_pct, 2)} · per direzione {pct(tt.direzione_pct, 2)}
            {' '}· posizioni max {formatta(tt.max_posizioni ?? 0)}
            {tt.max_posizioni_attivo === false ? <span className="muted"> (tetto spento in parita&apos; col backtest)</span> : null}
            {' '}· correlate max {formatta(tt.correlate_max ?? 0)}
          </>
        ) : (
          <span className="muted">non misurati</span>
        )}
      </Voce>

      <Voce titolo="Cooldown attivi" nota="coin o strategie ferme dopo una perdita">
        {a.cooldown_attivi == null ? (
          <span className="muted">non misurati</span>
        ) : a.cooldown_attivi === 0 ? (
          <span>nessuno</span>
        ) : (
          <>
            <b>{formatta(a.cooldown_attivi)}</b>
            <div className="chip-row" style={{ marginTop: 4 }}>
              {cdCoin.map((c) => (
                <span key={`c|${c.nome}`} className="mini-chip">
                  {c.nome} <span className="muted">fino a {quando(c.fino_a)}</span>
                </span>
              ))}
              {cdStrat.map((c) => (
                <span key={`s|${c.nome}`} className="mini-chip mono" style={{ fontWeight: 500 }}>
                  {c.nome} <span className="muted">fino a {quando(c.fino_a)}</span>
                </span>
              ))}
            </div>
          </>
        )}
      </Voce>

      <Voce titolo="Fiducia nella convinzione" nota="quanto la size segue la convinzione del segnale">
        {a.calibrazione_trust == null ? <span className="muted">non misurata</span> : <b>{numero(a.calibrazione_trust, 2)}</b>}
      </Voce>

      <Fonte sez={a} />
    </>
  );
}

export default function LearningAttivoMisurato() {
  const { doc, caricamento, etaS, stato } = useControllo();
  const now = useOrologio();
  const l = doc?.learning;
  const cambi = l?.attivo?.cambiamenti_24h ?? [];

  return (
    <div className="panel">
      <h2>Cosa fa il learning</h2>
      <p className="subtitle">
        A sinistra cio&apos; che cambia le decisioni del bot adesso; a destra cio&apos; che
        e&apos; solo misurato. In testa, cosa e&apos; cambiato dall&apos;ultimo controllo.
      </p>

      {caricamento ? (
        <p className="muted">Caricamento…</p>
      ) : !doc ? (
        <p className="muted">
          Nessun controllo ancora: il bot lo scrive ogni ora (ripiego: GitHub ogni 2 ore, comando ops «controllo»).
        </p>
      ) : (
        <>
          {stato !== 'ok' ? (
            <div className="warn" style={{ marginBottom: 10 }}>
              controllo {stato === 'assente' ? 'assente' : stato === 'fermo' ? 'fermo' : 'in ritardo'}
              {etaS != null ? <>: l&apos;ultimo e&apos; di {durata(etaS)} fa</> : null}. I numeri sotto sono di allora.
            </div>
          ) : null}

          {l?.lettura ? <p style={{ fontSize: 14, margin: '0 0 10px' }}>{l.lettura}</p> : null}
          {l?.errore ? <p className="muted" style={{ fontSize: 12 }}>errore: {l.errore}</p> : null}

          <div
            style={{
              background: 'var(--bg-elev)',
              border: '1px solid var(--border)',
              borderRadius: 10,
              padding: '10px 12px',
              marginBottom: 14,
            }}
          >
            <div style={{ fontSize: 12, fontWeight: 650, marginBottom: 4 }}>
              Cosa e&apos; cambiato nelle ultime 24 h
              <span className="muted" style={{ fontWeight: 400 }}>
                {' '}· confronto fra l&apos;impronta di adesso e quella del controllo precedente
                {doc.meta?.precedente_at != null ? <> ({quando(doc.meta.precedente_at)})</> : null}
              </span>
            </div>
            {cambi.length === 0 ? (
              <span style={{ fontSize: 13 }}>
                Niente: nessun pezzo del learning ha cambiato una decisione.
                {!doc.meta?.precedente_at ? <span className="muted"> (primo controllo: non c&apos;e&apos; un precedente con cui confrontare)</span> : null}
              </span>
            ) : (
              <ul style={{ margin: 0, paddingLeft: 18, fontSize: 13 }}>
                {cambi.map((c, i) => <li key={i}>{c}</li>)}
              </ul>
            )}
          </div>

          <div className="grid grid-2">
            <div style={{ minWidth: 0 }}>
              <div style={{ fontSize: 11, letterSpacing: '.04em', color: STATO.attenzione, marginBottom: 4 }}>
                CAMBIA LE DECISIONI ORA
              </div>
              <ColonnaAttivo a={l?.attivo} salute={doc.salute} now={now} />
            </div>
            <div style={{ minWidth: 0 }}>
              <div className="muted" style={{ fontSize: 11, letterSpacing: '.04em', marginBottom: 4 }}>
                SOLO MISURATO
              </div>
              <ColonnaMisurato m={l?.misurato} now={now} />
            </div>
          </div>

          <Fonte sez={l} nota={`controllo scritto da ${doc.meta?.generato_da ?? '?'}`} />
        </>
      )}
    </div>
  );
}
