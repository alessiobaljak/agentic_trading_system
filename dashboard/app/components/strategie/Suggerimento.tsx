'use client';

/**
 * Il riquadro che segue il dito o il mouse sui grafici (skill dataviz, interaction.md): prima il valore, poi il nome; ogni riga con
 * il suo segno di colore (una linea per le curve, un quadratino per le colonne); tutte le serie di quel giorno, non solo quella
 * toccata. I nomi entrano come testo (React li scrive come testo, mai come HTML).
 */
export interface VoceSuggerimento {
  chiave: string;
  nome: string;
  colore: string;
  valore: string;
  forma: 'linea' | 'quadro';
}

export function Suggerimento({ titolo, voci, nota }: { titolo: string; voci: VoceSuggerimento[]; nota?: string | null }) {
  return (
    <div className="cr-suggerimento">
      <div className="cr-suggerimento-titolo">{titolo}</div>
      {voci.map((v) => (
        <div className="cr-suggerimento-riga" key={v.chiave}>
          {v.forma === 'linea'
            ? <span className="cr-chiave" style={{ background: v.colore }} aria-hidden="true" />
            : <span className="cr-quadro" style={{ background: v.colore }} aria-hidden="true" />}
          <b>{v.valore}</b>
          <span>{v.nome}</span>
        </div>
      ))}
      {nota && <div className="cr-suggerimento-riga"><span>{nota}</span></div>}
    </div>
  );
}
