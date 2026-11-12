'use client';

import { useState } from 'react';
import { ref, serverTimestamp, set } from 'firebase/database';
import { getRtdb } from '../../lib/firebase';
import { oraItaliana, pct, soldi, type DatiContoVero, type StatoRamo } from '../../lib/strategie';
import { Info } from '../comuni/Info';

/**
 * La scheda «G1 sul conto vero», la parte del proprietario (12 novembre 2026, «ok pulsante in dashboard»): la versione del codice
 * in esecuzione, quella approvata, se coincidono, e tre comandi che scrive solo lui, con il suo accesso a Firebase (le regole:
 * firebase/database.rules.json; il bot li legge soltanto, bot/portafoglio/conto_vero.py):
 *
 *   - «Approva questa versione»: scrive `{commit, ora}` in /commands/conto_vero_versione_approvata; il commit è quello che il bot
 *     dice di eseguire in /conto_vero/versione. Senza questa approvazione il conto vero non manda ordini nuovi.
 *   - «Chiudi tutto sul conto vero»: scrive `true` in /commands/conto_vero_chiudi_tutto, dopo una conferma.
 *   - «Riparti», in due passi, quando il conto è fermo: prima `true` in /commands/conto_vero_riparti, poi in
 *     /commands/conto_vero_riparti_conferma il testo esatto di quel fermo (la sua ora in secondi interi). Il bot riparte solo con
 *     tutti e due, e Firebase accetta la conferma solo dopo la richiesta.
 *
 * Finché il conto vero è spento tutto resta visibile, ma i comandi sono segnati «spento» e non si possono premere (da spento il bot
 * non li legge); l'approvazione della versione invece si può dare prima dell'accensione: da sola non accende niente.
 */
const corto = (commit?: string | null) => (commit ?? '').slice(0, 8);

/** Il testo esatto che conferma il «riparti» di questo fermo: lo stesso di `codice_riparti` nel bot. */
export function codiceRiparti(oraDelFermo?: number | null): string | null {
  return oraDelFermo && Number.isFinite(oraDelFermo) && oraDelFermo > 0 ? String(Math.floor(oraDelFermo)) : null;
}

type Aperto = null | 'approva' | 'chiudi';

export default function ComandiContoVero({ stato, spento, dati }: {
  stato: StatoRamo | null;
  /** vero se il conto vero è spento (lib: `eSpento`): da spento il bot non legge «chiudi tutto» e «riparti» */
  spento: boolean;
  dati: DatiContoVero;
}) {
  const [aperto, setAperto] = useState<Aperto>(null);
  const [invio, setInvio] = useState<string | null>(null);
  const [errore, setErrore] = useState<string | null>(null);
  const { versione, approvata, fermo } = dati;

  const scrivi = async (scritture: [string, unknown][], fatto: string) => {
    setErrore(null);
    setInvio(null);
    try {
      for (const [percorso, valore] of scritture) await set(ref(getRtdb(), percorso), valore);
      setInvio(fatto);
      setAperto(null);
    } catch (e) {
      const testo = e instanceof Error ? e.message : 'Invio non riuscito.';
      setErrore(/permission/i.test(testo)
        ? 'Firebase ha rifiutato la scrittura: le regole pubblicate non hanno ancora questo comando (vanno aggiornate con quelle di firebase/database.rules.json).'
        : testo);
    }
  };

  // ---- la versione del codice ----
  const inEsecuzione = versione?.commit ?? null;
  const giaApprovata = !!inEsecuzione && approvata?.commit === inEsecuzione;
  // il giudizio è del bot (confronta i file, non solo i nomi dei commit); vale se ha già letto l'approvazione di adesso
  const lettaDalBot = (versione?.approvata ?? null) === (approvata?.commit ?? null);
  const coincidono = lettaDalBot ? versione?.coincidono === true : null;
  const dataCommit = versione?.data ? Date.parse(versione.data) / 1000 : null;
  const puoApprovare = !!inEsecuzione && versione?.pulito !== false && !giaApprovata;

  // ---- «riparti» in due passi ----
  const codice = codiceRiparti(fermo?.ora);
  const richiesto = dati.riparti === true;
  const confermato = richiesto && !!codice && dati.ripartiConferma === codice;

  return (
    <div className="cr-comandi" data-spento={spento ? 'si' : 'no'}>
      <div className="cr-versione">
        <p className="cr-versione-titolo">
          <b>Versione del codice</b>
          <Info etichetta="come funziona l'approvazione della versione">
            Il conto vero manda ordini solo con il codice che hai approvato tu da qui. Il bot confronta ogni minuto i suoi file con
            la versione approvata: se cambia anche un solo file del percorso degli ordini, niente ordini nuovi finché non approvi la
            versione nuova (dopo la revisione e il riavvio). L&apos;approvazione da sola non accende niente: servono anche
            l&apos;interruttore, DRY_RUN spento e il capitale.
          </Info>
        </p>
        <dl className="cr-versione-righe">
          <div>
            <dt>In esecuzione</dt>
            <dd>
              {!dati.versioneArrivata ? 'lettura in corso…' : !inEsecuzione ? (
                'il bot non l\'ha ancora scritta (serve il riavvio che carica questo codice)'
              ) : (
                <>
                  <code className="cr-hash" title={inEsecuzione}>{corto(inEsecuzione)}</code>
                  {dataCommit ? ` · ${oraItaliana(dataCommit)}` : ''}
                  {versione?.titolo ? <span className="cr-versione-nome">«{versione.titolo}»</span> : null}
                </>
              )}
            </dd>
          </div>
          <div>
            <dt>Approvata da te</dt>
            <dd>
              {approvata?.commit ? (
                <>
                  <code className="cr-hash" title={approvata.commit}>{corto(approvata.commit)}</code>
                  {typeof approvata.ora === 'number' && approvata.ora > 0 ? ` · ${oraItaliana(approvata.ora / 1000)}` : ''}
                </>
              ) : 'nessuna'}
            </dd>
          </div>
        </dl>
        {versione?.pulito === false && (
          <p className="cr-riga cr-esito no">
            <span aria-hidden="true">✗</span> I file caricati dal bot non sono quelli di questo commit: serve un riavvio prima di
            approvare{versione.motivo ? ` (${versione.motivo})` : ''}.
          </p>
        )}
        {inEsecuzione && (
          coincidono === true ? (
            <p className="cr-riga cr-esito si"><span aria-hidden="true">✓</span> Coincidono: il bot esegue la versione approvata.</p>
          ) : coincidono === false ? (
            <p className="cr-riga cr-esito no">
              <span aria-hidden="true">✗</span> Non coincidono{versione?.blocco ? `: ${versione.blocco}` : ''}.
            </p>
          ) : (
            <p className="cr-riga cr-esito attesa">
              <span aria-hidden="true">…</span> {giaApprovata ? 'Approvata: il bot la rilegge entro un minuto.'
                : 'Il bot rilegge l\'approvazione entro un minuto.'}
            </p>
          )
        )}
        {aperto !== 'approva' ? (
          <button className="btn" disabled={!puoApprovare} onClick={() => { setInvio(null); setAperto('approva'); }}>
            {giaApprovata ? 'Versione già approvata' : 'Approva questa versione'}
          </button>
        ) : (
          <div className="cr-conferma" role="alertdialog" aria-label="conferma approvazione della versione">
            <p className="cr-riga" style={{ margin: 0 }}>
              Confermi? Approvi per gli <b>ordini con soldi veri</b> il codice del commit{' '}
              <code className="cr-hash" title={inEsecuzione ?? ''}>{corto(inEsecuzione)}</code>
              {versione?.titolo ? <> «{versione.titolo}»</> : null}
              {dataCommit ? ` (${oraItaliana(dataCommit)})` : ''}.
            </p>
            <div className="cr-pulsanti">
              <button className="btn" onClick={() => setAperto(null)}>Annulla</button>
              <button className="btn btn-primary" onClick={() => scrivi(
                [['commands/conto_vero_versione_approvata', { commit: inEsecuzione, ora: serverTimestamp() }]],
                `Versione ${corto(inEsecuzione)} approvata: il bot la legge entro un minuto`,
              )}>
                Sì, approva {corto(inEsecuzione)}
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="cr-comandi-vero">
        {spento && (
          <p className="cr-riga cr-spento-nota">
            <span className="cr-etichetta vero">spento</span> Comandi non attivi: da spento il bot non li legge e non c&apos;è niente da
            chiudere.
          </p>
        )}
        {!spento && stato?.stop_a != null && (
          <p className="cr-riga">
            <b>Stop sul conto:</b> si chiude tutto sotto <b>{soldi(stato.stop_a, 'USDT')}</b> (ora {pct(stato.dal_massimo)} dal
            massimo).
          </p>
        )}
        {fermo ? (
          <div className="cr-fermo">
            <p className="cr-riga" style={{ margin: 0 }}>
              <b>Conto vero fermo</b> dal {oraItaliana(fermo.ora)}: {fermo.motivo} ({fermo.chiuse ?? 0} posizioni chiuse).
            </p>
            {confermato ? (
              <p className="cr-riga cr-esito attesa">
                <span aria-hidden="true">…</span> Riparti confermato: il bot lo esegue entro un minuto, se il conto è vuoto e sopra il
                65% del capitale; poi riapre alla prossima decisione di G1.
              </p>
            ) : !richiesto ? (
              <button className="btn" disabled={spento || !codice}
                onClick={() => scrivi([['commands/conto_vero_riparti', true]], 'Riparti: primo passo fatto, ora serve la conferma')}>
                Riparti (passo 1 di 2)
              </button>
            ) : (
              <div className="cr-conferma" role="alertdialog" aria-label="conferma riparti del conto vero">
                <p className="cr-riga" style={{ margin: 0 }}>
                  Passo 2 di 2. Confermi? Il conto vero fermo dal {oraItaliana(fermo.ora)} riparte e <b>riapre le posizioni con soldi
                  veri</b> alla prossima decisione di G1 (dopo la mezzanotte UTC).
                </p>
                <div className="cr-pulsanti">
                  <button className="btn" onClick={() => scrivi(
                    [['commands/conto_vero_riparti_conferma', null], ['commands/conto_vero_riparti', false]], 'Riparti annullato',
                  )}>
                    Annulla
                  </button>
                  <button className="btn btn-danger" disabled={spento || !codice}
                    onClick={() => scrivi([['commands/conto_vero_riparti_conferma', codice]], 'Riparti confermato')}>
                    Sì, riparti
                  </button>
                </div>
              </div>
            )}
          </div>
        ) : aperto !== 'chiudi' ? (
          <button className="btn btn-danger" disabled={spento} onClick={() => { setInvio(null); setAperto('chiudi'); }}>
            Chiudi tutto sul conto vero
          </button>
        ) : (
          <div className="cr-conferma" role="alertdialog" aria-label="conferma chiudi tutto sul conto vero">
            <p className="cr-riga" style={{ margin: 0 }}>
              Confermi? Chiude a mercato <b>tutte le posizioni del conto vero</b> (soldi veri) e lo ferma finché non lo fai ripartire
              in due passi.
            </p>
            <div className="cr-pulsanti">
              <button className="btn" onClick={() => setAperto(null)}>Annulla</button>
              <button className="btn btn-danger" disabled={spento}
                onClick={() => scrivi([['commands/conto_vero_chiudi_tutto', true]], 'Chiudi tutto: inviato, il bot lo esegue entro un minuto')}>
                Sì, chiudi tutto
              </button>
            </div>
          </div>
        )}
      </div>
      {invio && <p className="cr-riga muted">{invio}</p>}
      {errore && <div className="warn">{errore}</div>}
    </div>
  );
}
