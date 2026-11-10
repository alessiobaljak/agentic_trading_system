'use client';

import { useEffect, useMemo, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { getRtdb } from '../../lib/firebase';
import {
  CurveA100, Pesi, RigaPosizioni, RigaStatoBase, SchedaBase,
  giornoNelFuso, metricheDaSerie, oraItaliana, soldi, useAdesso,
  type AvvisoStato, type Giorni, type SerieCurva,
} from '../comuni';

/**
 * La scheda «Azioni» (10 nov 2026): SEGNAPOSTO. La cartella components/stock/ è della sessione «trading stock», che la riempie;
 * questo file fa solo da punto di partenza: legge /azioni con la forma proposta in dashboard/GUIDA_SCHEDA_AZIONI.md e la mostra con i
 * mattoni comuni (components/comuni). Senza dati su Firebase mostra una riga sola.
 */
export interface StrategiaAzioni {
  nome?: string;
  descrizione?: string;
  tipo?: 'paper' | 'demo';
  /** 1-7, fisso: decide il colore (slot della tavolozza validata) */
  ordine?: number;
  valuta?: string;
  capitale?: number;
  valore?: number;
  rendimento?: number;
  comprate?: number;
  vendute?: number;
  pesi?: Record<string, number> | null;
  ultimo_ribilancio?: { ora?: number; entrate?: number; uscite?: number } | null;
  aggiornato?: number;
  /** vero se il primo giorno di `giorni` parte dal capitale */
  primo_giorno_dal_capitale?: boolean;
  giorni?: Giorni | null;
}

export interface DatiAzioni {
  battito?: number;
  soglia_battito_s?: number;
  strategie?: Record<string, StrategiaAzioni | null> | null;
  allarmi?: Record<string, { ora?: number; testo?: string } | null> | null;
}

const FUSO = 'Europe/Zurich';
const VUOTO = 'La scheda delle azioni la riempie la sessione “trading stock”: nessun dato ancora su Firebase.';
const coloreDi = (ordine?: number) => `var(--serie-${Math.min(7, Math.max(1, Math.round(ordine ?? 1)))})`;
/** Firebase non accetta il punto nelle chiavi: i simboli arrivano con «_» al posto del «.» (NESN_SW → NESN.SW). */
const simbolo = (s: string) => s.replace(/_/g, '.');
const quante = (n: number, uno: string, tanti: string) => `${n} ${n === 1 ? uno : tanti}`;

export default function Azioni() {
  const [dati, setDati] = useState<DatiAzioni | null>(null);
  const [arrivato, setArrivato] = useState(false);
  const adesso = useAdesso();
  useEffect(() => onValue(ref(getRtdb(), 'azioni'), (x) => { setDati(x.val()); setArrivato(true); }), []);

  const strategie = useMemo(
    () => Object.entries(dati?.strategie ?? {})
      .filter((e): e is [string, StrategiaAzioni] => !!e[1])
      .sort((a, b) => (a[1].ordine ?? 99) - (b[1].ordine ?? 99)),
    [dati],
  );
  const serie = useMemo(() => Object.fromEntries(strategie.map(([id, s]) => {
    const g: Giorni = { ...(s.giorni ?? {}) };
    if (s.valore != null && s.aggiornato) g[giornoNelFuso(s.aggiornato, FUSO)] = Number(s.valore);
    return [id, g];
  })) as Record<string, Giorni>, [strategie]);
  const curve = useMemo<SerieCurva[]>(
    () => strategie.map(([id, s]) => ({ chiave: id, nome: s.nome ?? id, colore: coloreDi(s.ordine), giorni: serie[id] })),
    [strategie, serie],
  );

  if (!arrivato) return <p className="cr-sotto">Lettura…</p>;
  if (!strategie.length) {
    return <section className="cr-pannello cr-vuoto"><p className="cr-sotto" style={{ margin: 0 }}>{VUOTO}</p></section>;
  }

  const avvisi: AvvisoStato[] = Object.entries(dati?.allarmi ?? {})
    .filter(([, a]) => a?.testo)
    .map(([tipo, a]) => ({ chiave: tipo, titolo: 'Allarme delle azioni', dettaglio: <>({tipo.replace(/_/g, ' ')}, {oraItaliana(a!.ora)}): {a!.testo}</> }));
  const aggiornati = strategie.map(([, s]) => s.aggiornato ?? 0).filter((x) => x > 0);
  const conPesi = strategie.filter(([, s]) => s.pesi && Object.keys(s.pesi).length > 0);

  return (
    <>
      <RigaStatoBase battito={dati?.battito ?? null} arrivato adesso={adesso} sogliaS={dati?.soglia_battito_s ?? 6 * 3600}
        nomeVivo="Azioni: dati vivi" nomeFermo="Azioni: dati fermi?" aggiornato={aggiornati.length ? Math.max(...aggiornati) : null}
        avvisi={avvisi} nessunAvviso="Nessun allarme sulle azioni." />

      <div className="cr-griglia">
        {strategie.map(([id, s]) => {
          const valuta = s.valuta ?? 'CHF';
          const m = metricheDaSerie({
            serie: serie[id], valore: s.valore ?? null, base: s.capitale ?? null, aggiornato: s.aggiornato ?? null,
            giornoDiOggi: s.aggiornato ? giornoNelFuso(s.aggiornato, FUSO) : null,
            primoGiornoDallaBase: s.primo_giorno_dal_capitale === true, adesso,
          });
          const rib = s.ultimo_ribilancio;
          return (
            <SchedaBase key={id} nome={s.nome ?? id} descrizione={s.descrizione} colore={coloreDi(s.ordine)}
              tipo={s.tipo === 'demo' ? 'demo' : 'paper'} etichetta={s.tipo === 'demo' ? 'conto demo · soldi finti' : 'ordini simulati'}
              unita={valuta} metriche={m} adesso={adesso}
              posizioni={s.comprate != null || s.vendute != null
                ? <RigaPosizioni comprate={s.comprate ?? 0} vendute={s.vendute ?? 0} cosa="azioni" /> : null}
              ultimoRibilancio={rib?.ora ? {
                testo: `${oraItaliana(rib.ora)}${rib.entrate != null || rib.uscite != null
                  ? ` (${quante(rib.entrate ?? 0, 'entrata', 'entrate')}, ${quante(rib.uscite ?? 0, 'uscita', 'uscite')})` : ''}`,
              } : null}
              partenza={s.capitale != null ? <>Partito con <b>{soldi(s.capitale, valuta, 0)}</b></> : null} />
          );
        })}
      </div>

      <CurveA100 curve={curve} oggi={giornoNelFuso(adesso, FUSO)} />

      {conPesi.map(([id, s]) => (
        <section className="cr-pannello" key={id}>
          <div className="cr-pannello-testa">
            <span className="cr-chiave" style={{ background: coloreDi(s.ordine) }} aria-hidden="true" />
            <h2>{s.nome ?? id}: le posizioni</h2>
          </div>
          <Pesi pesi={s.pesi!} nomeDi={simbolo} />
        </section>
      ))}
    </>
  );
}
