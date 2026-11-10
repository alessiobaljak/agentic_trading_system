'use client';

import { useEffect, useMemo, useState } from 'react';
import { onValue, ref } from 'firebase/database';
import { getRtdb } from '../../lib/firebase';
import {
  confrontoDemoPaper, giornoBreve, pct, punti, riassumi,
  type DatiDemo, type DatiRamo, type RigaConfronto,
} from '../../lib/strategie';
import { Info } from '../comuni/Info';

/**
 * G1 sul demo contro G1 nel paper giorno per giorno, con le fasi passate del demo (/demo_binance/fasi/{nome}/giorni): chiuso finché
 * non si apre, e solo allora legge i dati. Il giorno del cambio di capitale non si confronta, tranne il primo della fase in corso.
 */
const VUOTO: DatiRamo = { stato: null, giorni: null, ultimoRibilancio: null, arrivato: false };

function useDatiConfronto(acceso: boolean) {
  const [paper, setPaper] = useState<DatiRamo>(VUOTO);
  const [demo, setDemo] = useState<DatiRamo>(VUOTO);
  const [fasi, setFasi] = useState<DatiDemo['fasi']>(null);
  useEffect(() => {
    if (!acceso) return undefined;
    const db = getRtdb();
    const stop = [
      onValue(ref(db, 'paper_g1/stato'), (x) => setPaper((p) => ({ ...p, stato: x.val(), arrivato: true }))),
      onValue(ref(db, 'paper_g1/giorni'), (x) => setPaper((p) => ({ ...p, giorni: x.val() }))),
      onValue(ref(db, 'demo_binance/stato'), (x) => setDemo((p) => ({ ...p, stato: x.val(), arrivato: true }))),
      onValue(ref(db, 'demo_binance/giorni'), (x) => setDemo((p) => ({ ...p, giorni: x.val() }))),
      onValue(ref(db, 'demo_binance/fasi'), (x) => setFasi(x.val())),
    ];
    return () => stop.forEach((f) => f());
  }, [acceso]);
  return { paper, demo, fasi };
}

function Riga({ titolo, righe }: { titolo: string; righe: RigaConfronto[] }) {
  const r = riassumi(righe);
  if (!r.giorni) return null;
  return (
    <div className="cr-riquadri cr-riquadri-3">
      <div className="cr-riquadro"><span>{titolo} · demo</span><b>{pct(r.demoComposto)}</b></div>
      <div className="cr-riquadro"><span>paper</span><b>{pct(r.paperComposto)}</b></div>
      <div className="cr-riquadro"><span>media al giorno</span><b>{punti(r.media)} <small>punti</small></b></div>
    </div>
  );
}

export default function ConfrontoGiorni() {
  const [aperto, setAperto] = useState(false);
  const [tutti, setTutti] = useState(false);
  const { paper, demo, fasi } = useDatiConfronto(aperto);
  const righe = useMemo(() => (paper.arrivato && demo.arrivato ? confrontoDemoPaper(paper, demo, fasi) : []), [paper, demo, fasi]);
  const inCorso = righe.filter((r) => r.fase === null && r.demo != null);
  const visibili = tutti ? [...righe].reverse() : [...righe].reverse().slice(0, 10);

  return (
    <details className="cr-pannello cr-apri" onToggle={(e) => setAperto((e.target as HTMLDetailsElement).open)}>
      <summary>
        <span>G1 demo contro G1 paper, giorno per giorno</span>
        <span className="cr-apri-segno" aria-hidden="true">›</span>
      </summary>
      {!aperto ? null : righe.length === 0 ? (
        <p className="cr-sotto">{paper.arrivato && demo.arrivato ? 'Ancora nessun giorno con tutti e due.' : 'Lettura…'}</p>
      ) : (
        <>
          <div className="cr-riga-info">
            <span className="cr-sotto" style={{ margin: 0 }}>Differenza = demo − paper, in punti</span>
            <Info>
              Il rendimento di ogni giorno UTC, dalla chiusura del giorno prima. Il demo ha cambiato capitale (circa 5.000, poi 280,
              poi 1.000): ogni fase si conta per conto suo; il giorno del cambio non si confronta.
            </Info>
          </div>
          <Riga titolo="Fase in corso" righe={inCorso} />
          {righe.some((r) => r.fase !== null && r.demo != null) && <Riga titolo="Tutte le fasi" righe={righe} />}
          <div className="cr-scorre">
            <table className="cr-tabella">
              <thead>
                <tr><th>Giorno</th><th>Demo</th><th>Paper</th><th>Differenza</th></tr>
              </thead>
              <tbody>
                {visibili.map((r) => (
                  <tr key={r.giorno}>
                    <td>
                      {giornoBreve(r.giorno)}
                      {r.inCorso && <span className="cr-fase">in corso</span>}
                      {r.nota ? <span className="cr-fase">{r.nota}</span> : r.fase && <span className="cr-fase">{r.fase}</span>}
                    </td>
                    <td>{pct(r.demo)}</td>
                    <td>{pct(r.paper)}</td>
                    <td>{punti(r.differenza)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {righe.length > 10 && (
            <button type="button" className="cr-link" onClick={() => setTutti((t) => !t)}>
              {tutti ? 'Solo gli ultimi 10 giorni' : `Tutti i ${righe.length} giorni`}
            </button>
          )}
        </>
      )}
    </details>
  );
}
