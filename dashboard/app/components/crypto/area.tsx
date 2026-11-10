'use client';

import type { Area, PropsPagina } from '../aree';
import Archivio, { SEZIONI_ARCHIVIO, type SezioneArchivio } from '../Archivio';
import Dettagli, { SCELTE } from '../dettagli/Dettagli';
import RigaStato from '../strategie/RigaStato';
import Strategie from '../strategie/Strategie';

/**
 * L'area Crypto della plancia: la schermata principale Strategie, poi Dettagli (una strategia alla volta, #crypto/dettagli/<g1demo,
 * g1, g1neutra, g11, f5, eventi>) e l'Archivio del vecchio sistema (#crypto/archivio/<controllo, report, operativita, gate, learning,
 * impostazioni>). In cima a ogni pagina il bot vivo e gli allarmi del demo.
 */
function PaginaDettagli({ resto, vai }: PropsPagina) {
  const def = SCELTE.find((s) => s.pagina === resto[0]) ?? SCELTE[0];
  return <Dettagli ramo={def.ramo} onRamo={(r) => vai([SCELTE.find((s) => s.ramo === r)?.pagina ?? ''], { sostituisci: true })} />;
}

function PaginaArchivio({ resto, vai }: PropsPagina) {
  const sezione = (SEZIONI_ARCHIVIO.find((s) => s.id === resto[0])?.id ?? 'controllo') as SezioneArchivio;
  return <Archivio sezione={sezione} onSezione={(s) => vai([s], { sostituisci: true })} />;
}

const icona = (d: React.ReactNode) => (
  <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round"
    strokeLinejoin="round" aria-hidden="true">{d}</svg>
);

export const AREA_CRYPTO: Area = {
  id: 'crypto',
  nome: 'Crypto',
  Testata: RigaStato,
  pagine: [
    { id: 'strategie', nome: 'Strategie', icona: icona(<path d="M3 17l5-6 4 3 5-7 4 4" />), Contenuto: () => <Strategie /> },
    { id: 'dettagli', nome: 'Dettagli', icona: icona(<><path d="M4 20V10M10 20V4M16 20v-7M22 20H2" /></>), Contenuto: PaginaDettagli },
    { id: 'archivio', nome: 'Archivio', icona: icona(<><path d="M3 4h18v4H3zM5 8v12h14V8M10 12h4" /></>), Contenuto: PaginaArchivio },
  ],
};
