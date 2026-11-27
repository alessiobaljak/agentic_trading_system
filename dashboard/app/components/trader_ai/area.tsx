'use client';

import type { Area } from '../aree';
import { PaginaAdesso, PaginaDecisioni, PaginaOperazioni, PaginaResoconti, StatoTrader } from './Pagine';

/**
 * L'area «Trader AI» della plancia (27 novembre 2026, il proprietario: «crea un'altra sezione dove posso vedere come va questo agente
 * AI live»): l'intelligenza artificiale che decide gli ordini su BTC, sul conto simulato (area trader_ai, AREE.md). La scrive solo la
 * sessione «trading AI». Indirizzi: #traderai/adesso, #traderai/operazioni, #traderai/decisioni, #traderai/resoconti.
 */
const icona = (d: React.ReactNode) => (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round"
    strokeLinejoin="round" aria-hidden="true">{d}</svg>
);

export const AREA_TRADER_AI: Area = {
  id: 'traderai',
  nome: 'Trader AI',
  Testata: StatoTrader,
  pagine: [
    { id: 'adesso', nome: 'Adesso', icona: icona(<><circle cx="12" cy="12" r="8" /><path d="M12 8v4l3 2" /></>), Contenuto: PaginaAdesso },
    { id: 'operazioni', nome: 'Operazioni', icona: icona(<path d="M4 6h16M4 12h16M4 18h10" />), Contenuto: PaginaOperazioni },
    { id: 'decisioni', nome: 'Decisioni', icona: icona(<path d="M4 5h16v11H8l-4 4z" />), Contenuto: PaginaDecisioni },
    { id: 'resoconti', nome: 'Resoconti', icona: icona(<><path d="M6 3h9l3 3v15H6z" /><path d="M9 11h6M9 15h6" /></>), Contenuto: PaginaResoconti },
  ],
};
