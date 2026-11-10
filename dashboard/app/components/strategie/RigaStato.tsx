'use client';

import { allarmiAccesi, nomeMoneta, oraItaliana, STRATEGIE, type DatiStrategie } from '../../lib/strategie';
import RigaStatoBase, { type AvvisoStato } from '../comuni/RigaStato';

/**
 * La riga in cima alla prima schermata: il bot è vivo? (l'ultimo battito del ciclo, /bot_status/heartbeat, scritto a ogni giro da
 * bot/main.py; la soglia di sempre, 900 s, era in TopVitals) e gli allarmi del demo, ben visibili: /demo_binance/allarme (conto non
 * vuoto da fermo), /demo_binance/allarmi/<tipo> (uno per tipo), il demo fermo (/demo_binance/fermo); con loro quelli del conto vero,
 * se un giorno ce ne saranno. Il disegno è quello comune (components/comuni/RigaStato.tsx).
 */
export default function RigaStato({ dati, adesso }: { dati: DatiStrategie; adesso: number }) {
  const { battito, battitoArrivato, demo, contoVero, rami } = dati;
  const aggiornamenti = STRATEGIE.map((s) => rami[s.ramo]?.stato?.aggiornato ?? 0).filter((x) => x > 0);
  const avvisi: AvvisoStato[] = [];
  if (demo.fermo) {
    avvisi.push({
      chiave: 'demo-fermo', titolo: 'Demo fermo',
      dettaglio: <>dal {oraItaliana(demo.fermo.ora)}: {demo.fermo.motivo}
        {demo.fermo.chiuse != null ? ` (${demo.fermo.chiuse} posizioni chiuse)` : ''}. Per farlo ripartire: «Riparti» nella scheda
        del demo, qui sotto.</>,
    });
  }
  allarmiAccesi(demo, contoVero).forEach((a, i) => avvisi.push({
    chiave: `${a.dove}-${a.tipo}-${i}`, titolo: `Allarme del ${a.dove}`,
    dettaglio: <>({a.tipo.replace(/_/g, ' ')}, {oraItaliana(a.ora)}): {a.testo}
      {a.monete.length ? ` (${a.monete.map(nomeMoneta).join(', ')})` : ''}</>,
  }));
  return (
    <RigaStatoBase battito={battito} arrivato={battitoArrivato} adesso={adesso}
      aggiornato={aggiornamenti.length ? Math.max(...aggiornamenti) : null} avvisi={avvisi} nessunAvviso="Nessun allarme sul demo." />
  );
}
