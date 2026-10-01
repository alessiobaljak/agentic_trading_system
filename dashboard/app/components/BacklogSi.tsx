'use client';

import { lista } from '../lib/controllo';
import { useBacklog, type GruppoBacklog, type VoceBacklog } from '../lib/backlog';
import ControlloSezione from './ControlloSezione';

/**
 * «Cosa aspetta il tuo sì» e il resto del backlog (1 ott 2026, J2).
 *
 * Il documento lo pubblica la macchina dopo ogni giro del gate leggendo
 * `docs/backlog.md`: qui non c'e' niente da aggiornare a mano. In cima le voci
 * del gruppo 0 (le proposte che aspettano il si' del proprietario), sotto gli
 * altri gruppi chiusi, ognuno con «cosa lo sblocca».
 */
export default function BacklogSi({ aperta = false }: { aperta?: boolean }) {
  const { doc, caricamento, etaS } = useBacklog();
  const si = lista<VoceBacklog>(doc?.aspetta_si);
  const gruppi: GruppoBacklog[] = lista<GruppoBacklog>(doc?.gruppi).filter((g) => (g.numero ?? 0) !== 0);

  return (
    <ControlloSezione
      titolo="Aspettano il tuo sì"
      aggiornatoS={etaS}
      errore={doc?.meta?.errore ?? null}
      aperta={aperta || si.length > 0}
      riassunto={
        caricamento && !doc
          ? 'carico…'
          : !doc
            ? 'non ancora pubblicato'
            : si.length
              ? `${si.length} in attesa`
              : 'niente in attesa'
      }
    >
      {!doc ? (
        <p className="muted" style={{ margin: 0, fontSize: 12.5 }}>
          Il backlog arriva qui dopo il prossimo giro del gate (ogni 3 ore).
        </p>
      ) : (
        <>
          {si.length === 0 ? (
            <p className="muted" style={{ margin: 0, fontSize: 12.5 }}>
              Nessuna proposta aspetta il tuo sì.
            </p>
          ) : (
            <ul className="lista-grigia">
              {si.map((v, i) => (
                <li key={i}>
                  <b>
                    {v.sigla}. {v.titolo}
                  </b>
                  {v.testo && <> — {v.testo}</>}
                </li>
              ))}
            </ul>
          )}
          {gruppi.map((g, i) => (
            <details key={i} style={{ marginTop: 10 }}>
              <summary className="sotto-titolo" style={{ cursor: 'pointer' }}>
                {g.numero}. {g.nome} ({lista<VoceBacklog>(g.voci).length})
                {g.cosa_serve && <span className="muted"> · lo sblocca: {g.cosa_serve}</span>}
              </summary>
              <ul className="lista-grigia">
                {lista<VoceBacklog>(g.voci).map((v, j) => (
                  <li key={j}>
                    <b>
                      {v.sigla}. {v.titolo}
                    </b>
                    {v.testo && <> — {v.testo}</>}
                  </li>
                ))}
              </ul>
            </details>
          ))}
          <p className="muted" style={{ margin: '10px 0 0', fontSize: 12 }}>
            Fonte: docs/backlog.md{doc.aggiornato ? `, aggiornato il ${doc.aggiornato}` : ''}
            {doc.meta?.commit ? ` (versione ${doc.meta.commit})` : ''}. Pubblicato dalla macchina
            dopo ogni giro del gate.
          </p>
        </>
      )}
    </ControlloSezione>
  );
}
