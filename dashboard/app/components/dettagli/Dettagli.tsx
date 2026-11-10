'use client';

import {
  discesaMassima, ordiniLimite, risultatiGiornalieri, speseEFunding, useDettaglio, type Operazione, type RibilancioDettaglio,
} from '../../lib/dettagli';
import {
  STRATEGIE, defDi, giornoBreve, metriche, nomeMoneta, oraItaliana, pct, soldi, useAdesso,
  type Confronto, type DatiRamo, type DefStrategia, type StatoRamo,
} from '../../lib/strategie';
import Paper6 from '../Paper6';
import { Info } from '../comuni/Info';
import Pesi from '../comuni/Pesi';
import ConfrontoGiorni from './ConfrontoGiorni';
import RisultatoGiorni from './RisultatoGiorni';

/**
 * La scheda «Dettagli», rifatta come la prima (seconda tornata, 10 nov 2026; il proprietario: «la sezione dettagli invece non mi
 * piace per niente troppo testo riesci a farla come la sezione strategia»): in cima si sceglie la strategia, sotto solo numeri,
 * riquadri e grafici di quella strategia (lib/dettagli.ts dice da dove arriva ogni numero). Le spiegazioni stanno nelle «i».
 */
export const SCELTE = STRATEGIE.filter((s) => s.tipo !== 'vero');

const ETICHETTA: Record<DefStrategia['tipo'], string> = { paper: 'ordini simulati', demo: 'ordini veri · soldi finti', vero: 'soldi veri' };

const classe = (x: number | null | undefined) =>
  x == null || Math.abs(x) < 0.00005 ? undefined : x > 0 ? 'cr-su' : 'cr-giu';

function soldiConSegno(x: number | null, unita: '$' | 'USDT'): string {
  if (x == null || !Number.isFinite(x)) return '—';
  const n = soldi(Math.abs(x), unita);
  return Math.abs(x) < 0.005 ? n : `${x > 0 ? '+' : '−'}${n}`;
}

function Riquadro({ nome, valore, cls, info }: { nome: string; valore: React.ReactNode; cls?: string; info?: React.ReactNode }) {
  return (
    <div className="cr-riquadro">
      <span>{nome}{info && <Info etichetta={`che cos'è: ${nome}`}>{info}</Info>}</span>
      <b className={cls}>{valore}</b>
    </div>
  );
}

function Pannello({ titolo, info, destra, children }: {
  titolo: string; info?: React.ReactNode; destra?: React.ReactNode; children: React.ReactNode;
}) {
  return (
    <section className="cr-pannello">
      <div className="cr-pannello-testa">
        <h2>{titolo}</h2>
        {info && <Info etichetta={`che cos'è: ${titolo}`}>{info}</Info>}
        {destra && <span className="cr-pannello-destra">{destra}</span>}
      </div>
      {children}
    </section>
  );
}

function Monete({ nomi }: { nomi: string[] }) {
  return (
    <div className="cr-gettoni">
      {nomi.map((n) => <span key={n} className="cr-gettone">{nomeMoneta(n)}</span>)}
    </div>
  );
}

function Ribilancio({ def, r }: { def: DefStrategia; r: RibilancioDettaglio }) {
  const ora = r.piazzati ?? r.eseguito;
  const rifiutati = (r.rifiutati ?? []).map((x) => (typeof x === 'string' ? x : x.simbolo ?? '?'));
  const mancanti = r.monete_mancanti_sul_demo ?? [];
  const limite = r.limite;
  return (
    <Pannello
      titolo={def.ramo === 'paper_f5' ? 'Ultimo cambio (il lunedì)' : 'Ultimo ribilancio'}
      destra={ora ? oraItaliana(ora) : giornoBreve(r.chiave.slice(0, 10))}
    >
      <div className="cr-riquadri">
        <Riquadro nome="Entrate" valore={r.entrate ?? '—'} />
        <Riquadro nome="Uscite" valore={r.uscite ?? '—'} />
        {def.tipo === 'demo' ? (
          <>
            <Riquadro nome="Ordini" valore={r.ordini ?? '—'} />
            {limite?.ordini ? <Riquadro nome="Eseguiti a limite" valore={`${limite.eseguiti_a_limite ?? 0} su ${limite.ordini}`} /> : null}
          </>
        ) : (
          <>
            {limite?.variazioni ? <Riquadro nome="Eseguiti a limite" valore={`${limite.eseguite ?? 0} su ${limite.variazioni}`} /> : null}
            {r.costo != null && <Riquadro nome="Spese del giro" valore={soldi(r.costo, def.unita)} />}
          </>
        )}
        {r.sotto_il_minimo?.variazioni != null && (
          <Riquadro nome="Sotto il minimo" valore={`${r.sotto_il_minimo.variazioni} (${pct(r.sotto_il_minimo.valore_in_frazione_del_conto, 1).replace('+', '')})`}
            info="Variazioni troppo piccole per i minimi di Binance: non si eseguono; fra parentesi il loro valore sul conto." />
        )}
      </div>
      {rifiutati.length > 0 && (<><div className="cr-etichetta-riga">Rifiutate da Binance</div><Monete nomi={rifiutati} /></>)}
      {mancanti.length > 0 && (<><div className="cr-etichetta-riga">Mancanti sul demo</div><Monete nomi={mancanti} /></>)}
    </Pannello>
  );
}

function ContoDemo({ s, confronto }: { s: StatoRamo; confronto: Confronto | null }) {
  const dif = (confronto?.differenze ?? []) as { simbolo: string; scarto: number; voluto?: number; vero?: number }[];
  return (
    <Pannello titolo="Il conto demo" info="Lo stop chiude tutto sotto il più alto fra −35% dal massimo e il 65% del capitale di partenza.">
      <div className="cr-riquadri">
        <Riquadro nome="Stop sotto" valore={soldi(s.stop_a, 'USDT')} />
        <Riquadro nome="Dal massimo" valore={pct(s.dal_massimo)} cls={classe(s.dal_massimo)} />
        <Riquadro nome="Massimo" valore={soldi(s.massimo, 'USDT')} />
        {s.saldo != null && <Riquadro nome="Saldo" valore={soldi(s.saldo, 'USDT')} />}
      </div>
      <div className="cr-etichetta-riga">
        Vere contro volute{confronto?.ora ? ` · ${oraItaliana(confronto.ora)}` : ''}
        <Info>Le monete con una posizione vera lontana da quella voluta oltre il 2% del conto.</Info>
      </div>
      {!confronto ? <p className="cr-sotto" style={{ margin: 0 }}>—</p> : dif.length === 0 ? (
        <p className="cr-sotto" style={{ margin: 0 }}>Nessuna moneta oltre il 2%</p>
      ) : (
        <table className="cr-tabella">
          <thead><tr><th>Moneta</th><th>Voluta</th><th>Vera</th><th>Scarto</th></tr></thead>
          <tbody>
            {dif.map((x) => (
              <tr key={x.simbolo}>
                <td>{nomeMoneta(x.simbolo)}</td>
                <td>{pct(x.voluto, 1)}</td>
                <td>{pct(x.vero, 1)}</td>
                <td>{pct(x.scarto, 1)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Pannello>
  );
}

const TIPO_EVENTO: Record<string, string> = { N3: 'moneta nuova', E4: 'funding al tetto' };

function Eventi({ aperte, chiuse }: { aperte: Operazione[]; chiuse: Operazione[] }) {
  const ordinate = [...chiuse].sort((a, b) => (b.uscita ?? 0) - (a.uscita ?? 0)).slice(0, 10);
  return (
    <Pannello titolo="Le operazioni" info="Ogni operazione vende la moneta e compra Bitcoin per lo stesso valore (il 5% del capitale).">
      <div className="cr-etichetta-riga">Aperte <b>{aperte.length}</b></div>
      {aperte.length === 0 ? <p className="cr-sotto" style={{ margin: 0 }}>nessuna</p> : (
        <table className="cr-tabella">
          <thead><tr><th>Moneta</th><th>Ora</th><th>Esce il</th></tr></thead>
          <tbody>
            {aperte.map((x) => (
              <tr key={x.id}>
                <td>{nomeMoneta(x.simbolo)}<span className="cr-fase">{TIPO_EVENTO[x.tipo ?? ''] ?? x.tipo}</span></td>
                <td className={classe(x.rendimento_ora)}>{pct(x.rendimento_ora)}</td>
                <td>{giornoBreve(x.uscita_giorno)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <div className="cr-etichetta-riga">Chiuse, le ultime <b>{ordinate.length}</b></div>
      {ordinate.length === 0 ? <p className="cr-sotto" style={{ margin: 0 }}>nessuna</p> : (
        <table className="cr-tabella">
          <thead><tr><th>Moneta</th><th>Risultato</th><th>Chiusa il</th></tr></thead>
          <tbody>
            {ordinate.map((x) => (
              <tr key={x.id}>
                <td>{nomeMoneta(x.simbolo)}<span className="cr-fase">{x.motivo ?? TIPO_EVENTO[x.tipo ?? '']}</span></td>
                <td className={classe(x.rendimento)}>{pct(x.rendimento)}</td>
                <td>{x.uscita ? giornoBreve(new Date(x.uscita).toISOString().slice(0, 10)) : '—'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </Pannello>
  );
}

export default function Dettagli({ ramo, onRamo }: { ramo: string; onRamo: (r: string) => void }) {
  const def = SCELTE.find((s) => s.ramo === ramo) ?? defDi('demo_binance');
  const d = useDettaglio(def);
  const adesso = useAdesso();
  const dr: DatiRamo = { stato: d.stato, giorni: d.giorni, ultimoRibilancio: null, arrivato: d.arrivato };
  const s = d.stato;
  const m = metriche(def, dr, adesso);
  const dd = discesaMassima(def, dr);
  const { spese, funding } = speseEFunding(def, d);
  const ol = ordiniLimite(def, s);
  const giorni = risultatiGiornalieri(def, dr, m.giornoDiOggi);
  const su = giorni.filter((g) => !g.inCorso && g.r > 0).length;
  const chiusi = giorni.filter((g) => !g.inCorso).length;
  const eventi = def.ramo === 'paper_eventi';

  return (
    <>
      <nav className="cr-scelta" role="tablist" aria-label="strategia">
        {SCELTE.map((x) => (
          <button key={x.ramo} role="tab" aria-selected={x.ramo === def.ramo} onClick={() => onRamo(x.ramo)}>
            <span className="cr-chiave" style={{ background: x.colore }} aria-hidden="true" />
            {x.breve}
          </button>
        ))}
      </nav>

      <section className="cr-pannello">
        <div className="cr-pannello-testa">
          <span className="cr-chiave" style={{ background: def.colore }} aria-hidden="true" />
          <h2>{def.nome}</h2>
          <Info etichetta={`che cos'è ${def.nome}`}>{def.descrizione}</Info>
          <span className={`cr-etichetta ${def.tipo}`}>{ETICHETTA[def.tipo]}</span>
        </div>
        {!d.arrivato ? <p className="cr-sotto">Lettura…</p> : !s || s.equity == null ? (
          <p className="cr-sotto">{s?.stato ?? 'Spento o non ancora partito'}</p>
        ) : (
          <div className="cr-riquadri">
            <Riquadro nome="Valore" valore={soldi(m.valore, def.unita)} />
            <Riquadro nome="Oggi" valore={pct(m.oggi)} cls={classe(m.oggi)} />
            <Riquadro nome={m.setteEtichetta === '7 giorni' ? '7 giorni' : m.setteEtichetta} valore={pct(m.sette)} cls={classe(m.sette)} />
            <Riquadro nome="Dall'inizio" valore={pct(m.dallInizio)} cls={classe(m.dallInizio)}
              info={def.unita === 'USDT' ? `Dal capitale di partenza della fase in corso (${soldi(m.base, 'USDT', 0)}).`
                : `Da ${soldi(m.base, '$', 0)} virtuali.`} />
            <Riquadro nome="Discesa massima" valore={pct(dd)} cls={classe(dd)}
              info="La caduta più grande da un massimo, sui valori di fine giorno." />
            {spese != null && <Riquadro nome="Spese pagate" valore={soldi(spese, def.unita)}
              info={def.tipo === 'demo' ? 'Commissioni vere del conto demo, dalla partenza della fase.' : 'Commissioni simulate, dall\'inizio.'} />}
            {funding != null && <Riquadro nome="Funding incassato" valore={soldiConSegno(funding, def.unita)} cls={classe(funding)}
              info="Positivo: incassato; negativo: pagato." />}
            {ol && <Riquadro nome="Ordini limite eseguiti" valore={`${ol.eseguiti} su ${ol.totali}`}
              info="Gli ordini al prezzo fissato eseguiti entro un'ora; gli altri vanno a mercato." />}
            {eventi ? (
              <>
                <Riquadro nome="Aperte" valore={(s.aperte_n3 ?? 0) + (s.aperte_e4 ?? 0)} />
                <Riquadro nome="Chiuse" valore={s.chiuse ?? 0} />
                {s.rendimento_medio != null && <Riquadro nome="Media chiuse" valore={pct(s.rendimento_medio)} cls={classe(s.rendimento_medio)} />}
              </>
            ) : (
              <Riquadro nome="Comprate · vendute" valore={`${s.long ?? 0} · ${s.short ?? 0}`} />
            )}
          </div>
        )}
      </section>

      {giorni.length > 0 && (
        <Pannello titolo="Giorno per giorno" destra={chiusi ? <>in guadagno <b>{su} su {chiusi}</b></> : null}
          info="Il risultato di ogni giorno UTC sul giorno prima; il giorno in corso è più chiaro.">
          <RisultatoGiorni def={def} giorni={giorni} />
        </Pannello>
      )}

      {d.pesi && Object.keys(d.pesi).length > 0 && (
        <Pannello titolo={def.tipo === 'demo' ? 'Le monete volute' : 'Le monete'}
          info={def.tipo === 'demo' ? 'Il demo segue la decisione di G1: questi sono i pesi di G1, in percentuale del capitale.'
            : 'Il peso di ogni moneta, in percentuale del capitale.'}>
          <Pesi pesi={d.pesi} />
        </Pannello>
      )}

      {d.ribilancio && <Ribilancio def={def} r={d.ribilancio} />}

      {def.tipo === 'demo' && s && s.equity != null && <ContoDemo s={s} confronto={d.confronto} />}

      {eventi && <Eventi aperte={d.aperte} chiuse={d.chiuse} />}

      {(def.tipo === 'demo' || def.ramo === 'paper_g1') && <ConfrontoGiorni />}

      <Paper6 />
    </>
  );
}
