'use client';

import { allarmiAccesi, nomeMoneta, oraItaliana, useAdesso, useStatoCrypto } from '../../lib/strategie';
import RigaStatoBase, { type AvvisoStato } from '../comuni/RigaStato';

/**
 * La riga in cima a tutte le pagine dell'area Crypto: il bot è vivo? (l'ultimo battito del ciclo, /bot_status/heartbeat, scritto a
 * ogni giro da bot/main.py; la soglia di sempre, 900 s, era in TopVitals) e gli allarmi del demo, ben visibili: /demo_binance/allarme
 * (conto non vuoto da fermo), /demo_binance/allarmi/<tipo> (uno per tipo), il demo fermo (/demo_binance/fermo); con loro quelli del
 * conto vero e il conto vero fermo (/conto_vero/fermo, 12 nov 2026). Il disegno è quello comune (components/comuni/RigaStato.tsx).
 */
export default function RigaStato() {
  const { battito, battitoArrivato, aggiornato, demo, contoVero } = useStatoCrypto();
  const adesso = useAdesso();
  const avvisi: AvvisoStato[] = [];
  if (demo.fermo) {
    avvisi.push({
      chiave: 'demo-fermo', titolo: 'Demo fermo',
      dettaglio: <>dal {oraItaliana(demo.fermo.ora)}: {demo.fermo.motivo}
        {demo.fermo.chiuse != null ? ` (${demo.fermo.chiuse} posizioni chiuse)` : ''}. Per farlo ripartire: «Riparti» nella scheda
        del demo, nella pagina Strategie.</>,
    });
  }
  if (contoVero.fermo) {
    avvisi.push({
      chiave: 'conto-vero-fermo', titolo: 'Conto vero fermo',
      dettaglio: <>dal {oraItaliana(contoVero.fermo.ora)}: {contoVero.fermo.motivo}
        {contoVero.fermo.chiuse != null ? ` (${contoVero.fermo.chiuse} posizioni chiuse)` : ''}. Per farlo ripartire: «Riparti» in due
        passi nella scheda del conto vero, nella pagina Strategie.</>,
    });
  }
  allarmiAccesi(demo, contoVero).forEach((a, i) => avvisi.push({
    chiave: `${a.dove}-${a.tipo}-${i}`, titolo: `Allarme del ${a.dove}`,
    dettaglio: <>({a.tipo.replace(/_/g, ' ')}, {oraItaliana(a.ora)}): {a.testo}
      {a.monete.length ? ` (${a.monete.map(nomeMoneta).join(', ')})` : ''}</>,
  }));
  return (
    <RigaStatoBase battito={battito} arrivato={battitoArrivato} adesso={adesso} aggiornato={aggiornato} avvisi={avvisi}
      nessunAvviso="Nessun allarme sul demo." />
  );
}
