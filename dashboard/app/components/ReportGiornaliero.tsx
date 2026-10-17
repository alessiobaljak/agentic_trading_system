'use client';

import { lista } from '../lib/controllo';
import { useReport, type DocReport, type SezioneReport } from '../lib/report';
import { durata } from '../lib/viz';

/**
 * La scheda REPORT GIORNALIERO (1 ott 2026): quello che il proprietario apre
 * al mattino. Nove sezioni fisse (in breve, paper, gate, cosa dicono i dati,
 * le funzioni servono?, cosa abbiamo capito, cosa e' cambiato, aspetta il tuo
 * si', salute e costi), scritte dalla macchina dopo ogni giro del gate. La
 * prima sezione e' aperta, le altre si aprono col tocco. Qui non si calcola
 * niente: si disegna il documento.
 */
/**
 * Una riga di tabella com'e' arrivata. Firestore non accetta liste dentro
 * liste: il bot le scrive come `{valori: [...]}` (`pulisci_per_firestore`), e
 * l'RTDB puo' restituire un array come oggetto con chiavi numeriche. Qui si
 * riportano tutte a un array semplice (1 ott 2026: senza, la scheda andava in
 * errore).
 */
type Cella = string | number | null;
function celle(r: unknown): Cella[] {
  if (Array.isArray(r)) return r as Cella[];
  if (r && typeof r === 'object') {
    const v = (r as { valori?: unknown }).valori;
    if (v !== undefined) return lista<Cella>(v);
    return Object.keys(r as object)
      .sort((a, b) => Number(a) - Number(b))
      .map((k) => (r as Record<string, Cella>)[k]);
  }
  return [];
}

function Tabella({ s }: { s: SezioneReport }) {
  const t = s.tabella;
  const righe = lista<unknown>(t?.righe).map(celle).filter((r) => r.length > 0);
  const colonne = lista<string>(t?.colonne);
  if (righe.length === 0) return null;
  return (
    <div style={{ overflowX: 'auto', marginTop: 8 }}>
      <table className="tabella-report">
        {colonne.length > 0 && (
          <thead>
            <tr>
              {colonne.map((c, i) => (
                <th key={i}>{c}</th>
              ))}
            </tr>
          </thead>
        )}
        <tbody>
          {righe.map((r, i) => {
            const intestazione = r.length > 1 && r.slice(1).every((x) => x === '' || x == null);
            return (
              <tr key={i} className={intestazione ? 'riga-gruppo' : undefined}>
                {intestazione ? (
                  <td colSpan={r.length}>{r[0]}</td>
                ) : (
                  r.map((x, j) => <td key={j}>{x == null ? '—' : String(x)}</td>)
                )}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}

function Sezione({ s, aperta }: { s: SezioneReport; aperta: boolean }) {
  const righe = lista<string>(s.righe);
  return (
    <details className="sezione panel" open={aperta || undefined}>
      <summary className="sezione-testa">
        <span className="sezione-titolo">{s.titolo}</span>
        {s.errore && <span className="sezione-eta" style={{ color: 'var(--red)' }}>non calcolata</span>}
      </summary>
      <div className="sezione-corpo">
        {righe.length > 0 && (
          <ul className="lista-grigia" style={{ marginTop: 0 }}>
            {righe.map((r, i) => (
              <li key={i}>{String(r)}</li>
            ))}
          </ul>
        )}
        <Tabella s={s} />
        {s.errore && (
          <p className="muted" style={{ margin: '8px 0 0', fontSize: 12 }}>
            errore: <code>{s.errore}</code>
          </p>
        )}
        {s.fonte && (
          <p className="muted" style={{ margin: '8px 0 0', fontSize: 11.5 }}>
            fonte: {s.fonte}
          </p>
        )}
      </div>
    </details>
  );
}

export default function ReportGiornaliero() {
  const { doc, caricamento, etaS } = useReport();
  return <VistaReport doc={doc} caricamento={caricamento} etaS={etaS} />;
}

/** Il disegno del report, senza letture: separato perche' si possa provare
 *  con un documento dato (quello vero, con le righe `{valori: [...]}`). */
export function VistaReport({
  doc,
  caricamento,
  etaS,
}: {
  doc: DocReport | null;
  caricamento: boolean;
  etaS: number | null;
}) {
  if (!doc) {
    return (
      <div className="panel" style={{ padding: 16 }}>
        <p className="muted" style={{ margin: 0 }}>
          {caricamento
            ? 'Carico il report…'
            : 'Il report giornaliero arriva qui dopo il prossimo giro del gate (ogni 3 ore).'}
        </p>
      </div>
    );
  }
  const vecchio = etaS != null && etaS > 6 * 3600;
  return (
    <>
      <p className="muted" style={{ margin: '0 0 10px', fontSize: 12.5 }}>
        Report del <b>{doc.meta?.giorno ?? '—'}</b> (giornata in ora italiana)
        {etaS != null && <> · aggiornato {durata(etaS)} fa</>}
        {doc.meta?.commit && <> · versione {doc.meta.commit}</>}
        {vecchio && (
          <span style={{ color: 'var(--red)' }}> · più vecchio di 6 ore: il gate o la macchina sono fermi?</span>
        )}
      </p>
      {lista<SezioneReport>(doc.sezioni).map((s, i) => (
        <Sezione key={s.id ?? i} s={s} aperta={i === 0} />
      ))}
    </>
  );
}
