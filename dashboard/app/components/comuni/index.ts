/**
 * I mattoni comuni della dashboard (10 nov 2026), da un punto solo: le schede crypto e quella delle azioni
 * (components/stock/) li importano da qui. Non sanno niente dei rami di Firebase: ricevono i dati come proprietà. Come usarli:
 * dashboard/GUIDA_SCHEDA_AZIONI.md.
 *
 *   SchedaBase      — la scheda di una strategia (valore, dall'inizio, oggi, 7 giorni, giorni in guadagno, posizioni, ultimo
 *                     ribilancio, etichetta «ordini simulati» / «conto demo»), con TestaScheda, RigaPosizioni, SchedaSenzaNumeri;
 *   CurveA100       — le curve di più strategie messe a 100 alla stessa data, con la scelta della partenza e la leggenda;
 *   RigaStatoBase   — vivo / ultimo segnale / ultimo aggiornamento e gli avvisi in rosso;
 *   Pesi            — comprate e vendute con i pesi, barre orizzontali;
 *   Info, Suggerimento, Colonna — la «i» che si apre al tocco, il riquadro dei grafici al tocco, la colonna arrotondata.
 *
 * E i conti (lib/conti.ts): metricheDaSerie, curveA100, pct, punti, soldi, giornoBreve, giornoNelFuso, oraItaliana, durataFa,
 * useAdesso.
 */
export { default as SchedaBase, ETICHETTE_TIPO, Delta, RigaPosizioni, SchedaSenzaNumeri, TestaScheda } from './SchedaBase';
export type { PropsSchedaBase, TipoScheda } from './SchedaBase';
export { default as CurveA100 } from './CurveA100';
export type { SerieCurva } from './CurveA100';
export { default as RigaStatoBase } from './RigaStato';
export type { AvvisoStato } from './RigaStato';
export { default as Pesi } from './Pesi';
export { Info } from './Info';
export { Suggerimento } from './Suggerimento';
export type { VoceSuggerimento } from './Suggerimento';
export { Colonna } from './Colonna';
export {
  curveA100, durataFa, giornoBreve, giornoNelFuso, giornoUtc, metricheDaSerie, oraItaliana, pct, punti, soldi, spostaGiorno, useAdesso,
} from '../../lib/conti';
export type { Giorni, IngressoMetriche, Metriche, RisultatoCurve } from '../../lib/conti';
