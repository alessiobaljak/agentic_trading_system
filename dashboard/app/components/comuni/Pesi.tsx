'use client';

import { useState } from 'react';

/** Il nome corto di un simbolo: 'BTCUSDT' → 'BTC'; gli altri restano come sono. */
const nomeCorto = (s: string) => s.replace(/USDT$/, '');

/**
 * (Mattone comune a crypto e azioni: `pesi` è `{simbolo: peso}`, peso > 0 comprata, < 0 venduta, in frazione del capitale.)
 * Le monete comprate e vendute con il loro peso (frazione del capitale), barre orizzontali, le più grandi in alto. Due colori fissi
 * per i due lati (blu comprate, rosso vendute: la coppia divergente della tavolozza, validata in chiaro e in scuro), più il titolo di
 * ogni colonna e il valore in cima alla barra: il lato non si legge solo dal colore. Le prime 10 per lato, le altre al tocco.
 */
const QUANTE = 10;

function Lato({ titolo, voci, colore, massimo, tutte, nomeDi }: {
  titolo: string; voci: [string, number][]; colore: string; massimo: number; tutte: boolean; nomeDi: (s: string) => string;
}) {
  const mostrate = tutte ? voci : voci.slice(0, QUANTE);
  return (
    <div className="cr-pesi-lato">
      <div className="cr-pesi-titolo">
        <span className="cr-quadro" style={{ background: colore }} aria-hidden="true" />
        {titolo} <b>{voci.length}</b>
      </div>
      {voci.length === 0 ? (
        <p className="cr-sotto" style={{ margin: 0 }}>nessuna</p>
      ) : (
        <ul className="cr-pesi-lista">
          {mostrate.map(([s, w]) => (
            <li key={s} title={`${nomeDi(s)}: ${(100 * Math.abs(w)).toLocaleString('it-IT', { maximumFractionDigits: 2 })}% del capitale`}>
              <span className="cr-pesi-nome">{nomeDi(s)}</span>
              <span className="cr-pesi-barra">
                <span style={{ width: `${Math.max(2, (100 * Math.abs(w)) / massimo)}%`, background: colore }} />
              </span>
              <span className="cr-pesi-num">{(100 * Math.abs(w)).toLocaleString('it-IT', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}%</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function Pesi({ pesi, nomeDi = nomeCorto, comprate: nomeComprate = 'Comprate', vendute: nomeVendute = 'Vendute' }: {
  pesi: Record<string, number>;
  /** come mostrare un simbolo (di serie toglie «USDT» in fondo) */
  nomeDi?: (s: string) => string;
  comprate?: string;
  vendute?: string;
}) {
  const [tutte, setTutte] = useState(false);
  const voci = Object.entries(pesi).map(([s, w]) => [s, Number(w)] as [string, number]).filter(([, w]) => Number.isFinite(w) && w !== 0);
  const comprate = voci.filter(([, w]) => w > 0).sort((a, b) => b[1] - a[1]);
  const vendute = voci.filter(([, w]) => w < 0).sort((a, b) => a[1] - b[1]);
  const massimo = Math.max(...voci.map(([, w]) => Math.abs(w)), 1e-9);
  const altre = Math.max(comprate.length, vendute.length) > QUANTE;
  return (
    <>
      <div className="cr-pesi">
        <Lato titolo={nomeComprate} voci={comprate} colore="var(--lato-comprate)" massimo={massimo} tutte={tutte} nomeDi={nomeDi} />
        <Lato titolo={nomeVendute} voci={vendute} colore="var(--lato-vendute)" massimo={massimo} tutte={tutte} nomeDi={nomeDi} />
      </div>
      {altre && (
        <button type="button" className="cr-link" onClick={() => setTutte((t) => !t)}>
          {tutte ? `Solo le prime ${QUANTE}` : `Tutte (${voci.length})`}
        </button>
      )}
    </>
  );
}
