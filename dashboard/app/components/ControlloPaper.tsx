'use client';

import { lista, useControllo, type Giornata, type Uscita } from '../lib/controllo';
import { numero, pct, quota, segno } from '../lib/viz';
import ControlloLettura from './ControlloLettura';
import ControlloSezione from './ControlloSezione';
import EquityCurve from './EquityCurve';

/**
 * La sezione «Paper» del controllo orario (25 set 2026): come sta andando il
 * paper trading, coi numeri calcolati dal bot (§1.3 del contratto).
 *
 * L'ordine e' quello delle domande che il proprietario fa la mattina:
 *   quanti trade e quanti vinti · quanto ha reso · com'e' andata oggi;
 *   PERCHE' usciamo (stop, trailing, take profit: la diagnosi piu' diretta);
 *   le ultime sette giornate; long contro short; costi; gli stop «sbagliati»
 *   (prezzo tornato oltre il primo gradino dopo lo stop) e i verdetti del
 *   trailing; in fondo la curva di equity, bassa, dagli ultimi 1000 trade.
 *
 * Tutti i numeri vengono dal documento: qui non si ricalcola niente, cosi'
 * la dashboard e il comando ops `controllo` dicono la stessa cosa. `null` si
 * mostra come «—», mai come zero: un dato che manca non e' un dato a zero.
 */
function Riga({ children }: { children: React.ReactNode }) {
  return <p className="riga-paper">{children}</p>;
}

function classePnl(v: number | null | undefined): string {
  if (v == null) return '';
  return v > 0 ? 'pos' : v < 0 ? 'neg' : '';
}

export default function ControlloPaper() {
  const { doc, stato } = useControllo();
  if (stato === 'assente' || !doc) return null;

  const p = doc.paper ?? {};
  const oggi = p.oggi ?? {};
  const uscite = lista<Uscita>(p.uscite);
  const ultime = lista<Giornata>(p.giornate?.ultime_7);
  const maxPnlGiorno = Math.max(1e-9, ...ultime.map((g) => Math.abs(g.pnl ?? 0)));
  const lungo = p.direzione?.long ?? null;
  const corto = p.direzione?.short ?? null;
  const costi = p.costi ?? null;
  const stop = p.stop ?? null;
  const tr = p.trailing ?? null;
  // il paper esplorativo (25 set 2026, F1bis): una riga sola, coi suoi numeri
  // tenuti a parte da quelli delle validate qui sopra
  const esp = p.esplorative ?? null;

  const riassunto = (
    <>
      <span className={classePnl(p.pnl_realizzato)}>{segno(p.pnl_realizzato, 2)}</span>
      {p.trades != null && <span className="muted"> · {p.trades} trade</span>}
    </>
  );

  return (
    <ControlloSezione
      titolo="Paper"
      computedAt={p.computed_at}
      errore={p.errore}
      aperta
      riassunto={riassunto}
    >
      <ControlloLettura sezione={p} style={{ marginTop: 0 }} />

      <div className="stat-grid" style={{ marginTop: 12 }}>
        <div className="stat-tile">
          <div className="stat-label">Trade</div>
          <div className="stat-value">{p.trades ?? '—'}</div>
          <div className="stat-sub">
            {p.vinti ?? '—'} vinti · {p.perdite ?? '—'} persi
            {p.giorni_paper != null && ` · ${p.giorni_paper} giorni`}
          </div>
        </div>
        <div className={`stat-tile ${p.win_rate != null ? (p.win_rate >= 0.5 ? 'good' : 'warnb') : ''}`}>
          <div className="stat-label">Win rate</div>
          <div className="stat-value">{quota(p.win_rate, 0)}</div>
          <div className="stat-sub">
            PF {p.pf_vissuto != null ? numero(p.pf_vissuto, 2) : p.perdite === 0 && p.trades ? 'senza perdite' : '—'}
            {p.expectancy != null && ` · attesa ${segno(p.expectancy, 2)}/trade`}
          </div>
        </div>
        <div className={`stat-tile ${p.pnl_realizzato != null ? (p.pnl_realizzato >= 0 ? 'good' : 'bad') : ''}`}>
          <div className="stat-label">PnL realizzato</div>
          <div className={`stat-value ${classePnl(p.pnl_realizzato)}`}>{segno(p.pnl_realizzato, 2)}</div>
          <div className="stat-sub">
            {p.rendimento_pct != null ? `${segno(p.rendimento_pct, 2)}%` : 'rendimento n/d'}
            {p.drawdown_portafoglio != null && ` · drawdown ${numero(p.drawdown_portafoglio, 2)}`}
            {p.max_posizioni_insieme != null && ` · max ${p.max_posizioni_insieme} insieme`}
          </div>
        </div>
        <div className={`stat-tile ${oggi.pnl != null && oggi.trades ? (oggi.pnl >= 0 ? 'good' : 'bad') : ''}`}>
          <div className="stat-label">Oggi (UTC)</div>
          <div className={`stat-value ${classePnl(oggi.pnl)}`}>
            {oggi.trades ? segno(oggi.pnl, 2) : 'nessun trade'}
          </div>
          <div className="stat-sub">
            {oggi.trades ? `${oggi.trades} trade · ${oggi.vinti ?? 0} vinti` : 'ancora niente chiuso oggi'}
            {oggi.migliore?.coin && ` · meglio ${oggi.migliore.coin} ${segno(oggi.migliore.pnl, 2)}`}
            {oggi.peggiore?.coin && ` · peggio ${oggi.peggiore.coin} ${segno(oggi.peggiore.pnl, 2)}`}
          </div>
        </div>
      </div>

      {/* --- perche' usciamo --- */}
      {uscite.length > 0 && (
        <div style={{ marginTop: 14 }}>
          <div className="sotto-titolo">Uscite per motivo</div>
          <ul className="lista-compatta">
            {uscite.map((u, i) => (
              <li key={`${u.motivo ?? i}`} title={u.motivo ?? undefined}>
                <span className="lc-nome">{u.etichetta || u.motivo || '—'}</span>
                <span className="lc-numeri">
                  {u.trades ?? '—'} <span className="muted">({quota(u.quota, 0)})</span>{' '}
                  <span className={classePnl(u.pnl)}>{segno(u.pnl, 2)}</span>
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* --- ultime 7 giornate: barre minuscole, proporzionali al giorno peggiore/migliore --- */}
      {ultime.length > 0 && (
        <div style={{ marginTop: 14 }}>
          <div className="sotto-titolo">
            Ultime 7 giornate
            {p.giornate && (
              <span className="muted" style={{ fontWeight: 500 }}>
                {' '}· {p.giornate.positive ?? 0} positive, {p.giornate.negative ?? 0} negative su{' '}
                {p.giornate.con_trade ?? 0} con trade
              </span>
            )}
          </div>
          <ul className="barre-mini">
            {ultime.map((g, i) => {
              const v = g.pnl ?? 0;
              const w = Math.round((Math.abs(v) / maxPnlGiorno) * 100);
              return (
                <li key={g.data ?? i} title={`${g.data}: ${g.trades ?? 0} trade, ${segno(v, 2)}`}>
                  <span className="bm-data mono">{(g.data ?? '').slice(5)}</span>
                  <span className="bm-track">
                    <span
                      className="bm-fill"
                      style={{ width: `${w}%`, background: v >= 0 ? 'var(--green)' : 'var(--red)' }}
                    />
                  </span>
                  <span className={`bm-val ${classePnl(v)}`}>
                    {g.trades ? segno(v, 2) : <span className="muted">—</span>}
                  </span>
                </li>
              );
            })}
          </ul>
        </div>
      )}

      {/* --- direzione --- */}
      {(lungo || corto) && (
        <div style={{ marginTop: 14 }}>
          <div className="sotto-titolo">Long e short</div>
          <Riga>
            <b>long</b>: {lungo?.trade ?? 0} trade, {lungo?.vinti ?? 0} vinti,{' '}
            <span className={classePnl(lungo?.pnl)}>{segno(lungo?.pnl, 2)}</span>
            {lungo?.mfe_mediana != null && ` · MFE mediana ${numero(lungo.mfe_mediana, 2)} R`}
          </Riga>
          <Riga>
            <b>short</b>: {corto?.trade ?? 0} trade, {corto?.vinti ?? 0} vinti,{' '}
            <span className={classePnl(corto?.pnl)}>{segno(corto?.pnl, 2)}</span>
            {corto?.mfe_mediana != null && ` · MFE mediana ${numero(corto.mfe_mediana, 2)} R`}
          </Riga>
        </div>
      )}

      {/* --- costi, stop, trailing: una riga ciascuno --- */}
      {costi && (
        <Riga>
          <b>costi{costi.stimati ? ' stimati' : ''}</b>: {numero(costi.totale, 2)} USDT
          {costi.per_trade != null && ` (${numero(costi.per_trade, 2)} a trade)`}
          {' '}· commissioni {numero(costi.commissioni, 2)} · spread {numero(costi.spread, 2)} · funding{' '}
          {numero(costi.funding, 2)}
          {costi.lordo != null && costi.netto != null && ` · lordo ${segno(costi.lordo, 2)} → netto ${segno(costi.netto, 2)}`}
          {costi.break_even_pct != null && ` · pareggio a ${pct(costi.break_even_pct, 2)}`}
          {(costi.avvisi ?? []).length > 0 && (
            <span style={{ color: 'var(--amber)' }} title={(costi.avvisi ?? []).join('\n')}>
              {' '}· {(costi.avvisi ?? []).length} avvisi
            </span>
          )}
        </Riga>
      )}
      {stop && (
        <Riga>
          <span title={stop.nota ?? undefined}>
            <b>stop</b>: {stop.totale ?? '—'} totali · {stop.sbagliati ?? '—'} sbagliati ·{' '}
            {stop.quasi ?? '—'} quasi
            {stop.quasi_durata_mediana_h != null && ` (mediana ${numero(stop.quasi_durata_mediana_h, 1)} h)`}
            {' '}· {stop.oltre_primo_tp ?? '—'} oltre il primo TP
            {stop.primo_gradino_r != null && ` · primo gradino ${numero(stop.primo_gradino_r, 2)} R`}
          </span>
        </Riga>
      )}
      {tr && (
        <Riga>
          <b>trailing</b>: {tr.verdetti_totali ?? '—'} verdetti · {tr.prematuri ?? '—'} prematuri ·{' '}
          {tr.protetti ?? '—'} protetti · {tr.neutri ?? '—'} neutri
          {tr.proposta_paper != null
            ? ` · il paper propone keep ${numero(tr.proposta_paper, 2)}`
            : ` · nessuna proposta di keep`}
          {tr.verdetti_per_proposta != null && tr.soglia != null && (
            <span className="muted"> ({tr.verdetti_per_proposta} verdetti utili su soglia {tr.soglia})</span>
          )}
        </Riga>
      )}

      {esp && (
        <Riga>
          <span title="quasi-passaggi del gate operati a un quarto della size, marcati «espl.» fra i trade chiusi; fuori dai numeri delle validate e dai pesi">
            <b>Paper esplorativo</b>: {esp.trades ?? '—'} trade
            {esp.vinti != null && ` (${esp.vinti} vinti)`}
            {', '}
            <span className={classePnl(esp.pnl)}>{segno(esp.pnl, 2)}</span>
            {' '}· {esp.aperte ?? '—'} aperte · {esp.coppie_attive ?? '—'} coppie
          </span>
        </Riga>
      )}

      {p.benchmark && (p.benchmark.btc_24h_pct != null || p.benchmark.btc_7g_pct != null) && (
        <Riga>
          <span title={p.benchmark.nota ?? undefined}>
            <b>BTC</b>: {segno(p.benchmark.btc_24h_pct, 2)}% in 24 h · {segno(p.benchmark.btc_7g_pct, 2)}% in 7 g
            {p.benchmark.portafoglio?.lettura && ` · portafoglio: ${p.benchmark.portafoglio.lettura}`}
          </span>
        </Riga>
      )}

      <div style={{ marginTop: 14 }}>
        <div className="sotto-titolo">Curva di equity (PnL cumulato, ultimi 1000 trade)</div>
        <EquityCurve altezza={200} limite={1000} compatta />
      </div>
    </ControlloSezione>
  );
}
