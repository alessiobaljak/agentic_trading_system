'use client';

/**
 * SCRIVERE A CLAUDE DA QUI.
 *
 * Nasce per un caso preciso: essere in viaggio, senza poter aprire Claude Code, e
 * avere comunque bisogno di chiedere qualcosa al sistema. La barra di testo manda il
 * messaggio a `/api/claude`, che lo pubblica come commento su una issue di GitHub; li'
 * un workflow fa partire una sessione di Claude con accesso al repo, che risponde nel
 * thread. Questo pannello rilegge il thread e lo mostra come una chat.
 *
 * DUE COSE DA SAPERE, ED E' ONESTO DIRLE INVECE DI NASCONDERLE DIETRO UNO SPINNER:
 *
 *  1. La risposta NON e' immediata. Deve partire una macchina su GitHub Actions,
 *     scaricare il repo e leggerlo: uno-tre minuti. Per questo si vede "sta
 *     leggendo il repo…" invece di un cursore che lampeggia.
 *  2. La sessione che risponde e' NUOVA ogni volta. Non ha la memoria delle
 *     conversazioni fatte dentro Claude Code — ha il repo, questo thread e
 *     `CLAUDE.md`. Conviene scrivere domande che stanno in piedi da sole.
 *
 * La conversazione vive su GitHub, non qui: se la dashboard e' giu' o Vercel cambia
 * deploy, il thread resta leggibile dal telefono aprendo la issue.
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { onAuthStateChanged, type User } from 'firebase/auth';
import { getAuthInstance } from '../lib/firebase';

type Msg = {
  id: number;
  from: 'io' | 'claude';
  author: string;
  text: string;
  at: string;
  url: string;
};

/** Ogni quanto rileggere il thread: piano di norma, in fretta mentre si aspetta. */
const IDLE_MS = 20_000;
const WAITING_MS = 6_000;

function ora(iso: string): string {
  const d = new Date(iso);
  return Number.isNaN(d.getTime())
    ? ''
    : d.toLocaleString('it-IT', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
}

export default function ClaudeChat() {
  const [user, setUser] = useState<User | null>(null);
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [text, setText] = useState('');
  const [err, setErr] = useState<string | null>(null);
  const [loaded, setLoaded] = useState(false);
  const [sending, setSending] = useState(false);
  const [issue, setIssue] = useState<{ n: number; repo: string } | null>(null);
  const fondo = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    try {
      return onAuthStateChanged(getAuthInstance(), setUser);
    } catch {
      return;
    }
  }, []);

  /** In attesa = l'ultimo messaggio e' mio. Finche' e' cosi' si sollecita spesso. */
  const attesa = msgs.length > 0 && msgs[msgs.length - 1].from === 'io';

  const carica = useCallback(async () => {
    if (!user) return;
    try {
      const token = await user.getIdToken();
      const r = await fetch('/api/claude', { headers: { authorization: `Bearer ${token}` } });
      const data = (await r.json()) as { messages?: Msg[]; issue?: number; repo?: string; error?: string };
      if (!r.ok) {
        setErr(data.error || `errore ${r.status}`);
      } else {
        setErr(null);
        setMsgs(data.messages ?? []);
        if (data.issue) setIssue({ n: data.issue, repo: data.repo ?? '' });
      }
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setLoaded(true);
    }
  }, [user]);

  useEffect(() => {
    void carica();
    const id = setInterval(() => void carica(), attesa ? WAITING_MS : IDLE_MS);
    return () => clearInterval(id);
  }, [carica, attesa]);

  useEffect(() => {
    fondo.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }, [msgs.length]);

  async function manda() {
    const t = text.trim();
    if (!t || !user || sending) return;
    setSending(true);
    setErr(null);
    try {
      const token = await user.getIdToken();
      const r = await fetch('/api/claude', {
        method: 'POST',
        headers: { authorization: `Bearer ${token}`, 'content-type': 'application/json' },
        body: JSON.stringify({ text: t }),
      });
      const data = (await r.json()) as { message?: Msg; error?: string };
      if (!r.ok) {
        setErr(data.error || `errore ${r.status}`);
      } else {
        setText('');
        if (data.message) setMsgs((m) => [...m, data.message as Msg]);
      }
    } catch (e) {
      setErr(e instanceof Error ? e.message : String(e));
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="panel">
      <h2>Claude</h2>
      <p className="subtitle">
        Scrivi qui e la domanda arriva a una sessione di Claude con accesso a questo repo.
        La risposta compare nel thread fra <b>uno e tre minuti</b>: deve partire una
        macchina su GitHub, scaricare il codice e leggerlo.
      </p>

      {err && (
        <div
          style={{
            background: 'rgba(248,81,73,.12)',
            border: '1px solid var(--red)',
            borderRadius: 8,
            padding: '10px 12px',
            marginBottom: 12,
            fontSize: 13,
          }}
        >
          {err}
        </div>
      )}

      <div
        style={{
          display: 'flex',
          flexDirection: 'column',
          gap: 10,
          maxHeight: 460,
          overflowY: 'auto',
          padding: '4px 2px',
          marginBottom: 12,
        }}
      >
        {!loaded && <p className="muted">Caricamento…</p>}
        {loaded && !err && msgs.length === 0 && (
          <p className="muted">
            Nessun messaggio. Una domanda che sta in piedi da sola funziona meglio: la
            sessione che risponde e&apos; nuova ogni volta e non ricorda le chat fatte
            altrove.
          </p>
        )}
        {msgs.map((m) => (
          <div
            key={m.id}
            style={{
              alignSelf: m.from === 'io' ? 'flex-end' : 'flex-start',
              maxWidth: '86%',
              background: m.from === 'io' ? 'rgba(88,166,255,.12)' : 'var(--panel-2, rgba(255,255,255,.04))',
              border: '1px solid var(--border, rgba(255,255,255,.08))',
              borderRadius: 10,
              padding: '8px 11px',
            }}
          >
            <div
              className="muted"
              style={{ fontSize: 11, marginBottom: 4, display: 'flex', gap: 8 }}
            >
              <span>{m.from === 'io' ? 'io' : m.author}</span>
              <span>{ora(m.at)}</span>
              <a href={m.url} target="_blank" rel="noreferrer" className="muted">
                ↗
              </a>
            </div>
            <div style={{ fontSize: 13, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
              {m.text}
            </div>
          </div>
        ))}
        {attesa && (
          <div className="muted" style={{ fontSize: 12, alignSelf: 'flex-start' }}>
            sta leggendo il repo… (uno-tre minuti)
          </div>
        )}
        <div ref={fondo} />
      </div>

      <div style={{ display: 'flex', gap: 8 }}>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={(e) => {
            // Invio manda, Maiusc+Invio va a capo: e' la convenzione che tutti
            // conoscono, e su un telefono evita di cercare il bottone.
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              void manda();
            }
          }}
          placeholder="Scrivi a Claude…"
          rows={2}
          disabled={!user || sending}
          style={{
            flex: 1,
            resize: 'vertical',
            background: 'var(--panel-2, rgba(255,255,255,.04))',
            border: '1px solid var(--border, rgba(255,255,255,.12))',
            borderRadius: 8,
            color: 'inherit',
            padding: '8px 10px',
            font: 'inherit',
            fontSize: 13,
          }}
        />
        <button
          className="btn btn-primary"
          onClick={() => void manda()}
          disabled={!user || sending || !text.trim()}
          style={{ alignSelf: 'stretch' }}
        >
          {sending ? 'Invio…' : 'Invia'}
        </button>
      </div>

      {issue && (
        <p className="muted" style={{ fontSize: 11, marginTop: 8 }}>
          La conversazione vive su GitHub —{' '}
          <a
            href={`https://github.com/${issue.repo}/issues/${issue.n}`}
            target="_blank"
            rel="noreferrer"
          >
            issue #{issue.n}
          </a>
          . Se questa pagina non fosse raggiungibile, il thread si legge da li&apos;.
        </p>
      )}
    </div>
  );
}
