'use client';

import { useState } from 'react';
import { ref, serverTimestamp, set } from 'firebase/database';
import { getRtdb } from '../../lib/firebase';
import { nomeMoneta, oraItaliana, pct, soldi, type Confronto, type Fermo, type StatoRamo } from '../../lib/strategie';

/**
 * Le protezioni del conto demo (il proprietario, 1° novembre 2026), spostate il 10 novembre 2026 dalla scheda del paper alla scheda
 * del demo nella prima schermata, con la stessa logica: il pulsante che chiude tutte le posizioni (con la conferma: un click per
 * sbaglio non deve chiudere tutto) e quello che fa ripartire il demo dopo uno stop. Scrivono `true` in
 * /commands/demo_binance_chiudi_tutto e /commands/demo_binance_riparti (più `_meta` con chi e quando); il bot li legge a ogni giro e li
 * rimette a false (bot/portafoglio/demo_binance.py, COMANDO_CHIUDI e COMANDO_RIPARTI). Gli allarmi del demo stanno nella riga di
 * stato in cima alla pagina.
 */
export default function ComandiDemo({ stato, fermo, confronto }: {
  stato: StatoRamo | null;
  fermo: Fermo | null;
  confronto: Confronto | null;
}) {
  const [conferma, setConferma] = useState(false);
  const [invio, setInvio] = useState<string | null>(null);
  const [errore, setErrore] = useState<string | null>(null);

  const manda = async (percorso: string, nomeComando: string) => {
    setErrore(null);
    try {
      await set(ref(getRtdb(), percorso), true);
      await set(ref(getRtdb(), `${percorso}_meta`), { da: 'dashboard', ora: serverTimestamp() }).catch(() => undefined);
      setInvio(`${nomeComando}: inviato, il bot lo esegue entro un minuto`);
      setConferma(false);
    } catch (e) {
      setErrore(e instanceof Error ? e.message : 'Invio non riuscito.');
    }
  };
  const dif = confronto?.differenze ?? [];

  return (
    <div className="cr-comandi">
      {stato?.stop_a != null && (
        <p className="cr-riga">
          <b>Stop sul conto:</b> si chiude tutto sotto <b>{soldi(stato.stop_a, 'USDT')}</b> (il più alto fra −35% dal massimo e il 65%
          del capitale di partenza; ora {pct(stato.dal_massimo)} dal massimo).
        </p>
      )}
      {confronto && (
        <p className="cr-riga">
          <b>Posizioni vere contro volute</b> ({oraItaliana(confronto.ora)}):{' '}
          {dif.length === 0 ? 'nessuna moneta con uno scarto oltre il 2% del conto'
            : <b>{dif.map((x) => `${nomeMoneta(x.simbolo)} ${pct(x.scarto, 1)}`).join(', ')}</b>}.
        </p>
      )}
      {fermo ? (
        <div className="cr-fermo">
          <p className="cr-riga" style={{ margin: 0 }}>
            <b>Demo fermo</b> dal {oraItaliana(fermo.ora)}: {fermo.motivo} ({fermo.chiuse ?? 0} posizioni chiuse).
          </p>
          <button className="btn" onClick={() => manda('commands/demo_binance_riparti', 'Riparti')}>Riparti</button>
        </div>
      ) : !conferma ? (
        <button className="btn btn-danger" onClick={() => setConferma(true)}>Chiudi tutto sul demo</button>
      ) : (
        <div className="cr-conferma" role="alertdialog" aria-label="conferma chiudi tutto">
          <p className="cr-riga" style={{ margin: 0 }}>
            Confermi? Chiude <b>tutte le posizioni</b> del conto demo a mercato e lo ferma finché non premi «Riparti».
          </p>
          <div className="cr-pulsanti">
            <button className="btn" onClick={() => setConferma(false)}>Annulla</button>
            <button className="btn btn-danger" onClick={() => manda('commands/demo_binance_chiudi_tutto', 'Chiudi tutto')}>
              Sì, chiudi tutto
            </button>
          </div>
        </div>
      )}
      {invio && <p className="cr-riga muted">{invio}</p>}
      {errore && <div className="warn">{errore}</div>}
    </div>
  );
}
