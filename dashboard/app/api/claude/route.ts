/**
 * LA CASSETTA POSTALE — da questa dashboard a una sessione di Claude Code.
 *
 * Il problema da risolvere: Claude non e' un servizio sempre acceso a cui mandare
 * una richiesta. Esiste quando una sessione parte. Quindi "scrivergli" vuol dire
 * far partire una sessione, e l'unico innesco che questo progetto ha gia' e'
 * GitHub Actions.
 *
 * Il giro, quindi:
 *
 *   dashboard  ->  questa rotta  ->  commento su una issue  ->  .github/workflows/claude.yml
 *                                                                        |
 *   dashboard  <-  questa rotta  <-  commenti della issue  <-  risposta di Claude
 *
 * La issue e' il thread: nessun database da tenere allineato, la conversazione
 * sopravvive ai deploy, ed e' leggibile anche da GitHub se la dashboard e' giu'.
 *
 * PERCHE' SERVE UN PEZZO DI SERVER. Il token GitHub puo' scrivere sul repo: se
 * stesse nel bundle del browser lo avrebbe chiunque apra la pagina. Qui vive solo
 * come variabile d'ambiente di Vercel (`GH_TOKEN`, senza `NEXT_PUBLIC_`), e il
 * browser non lo vede mai.
 *
 * CHI PUO' SCRIVERE. Il repo e' PUBBLICO e questo token ha permessi di scrittura:
 * la rotta non puo' essere aperta. Si riusa l'accesso che la dashboard ha gia'
 * (login Google/Firebase): il client manda il suo ID token, qui lo si fa validare a
 * Google e si controlla che l'UID sia nella lista `CLAUDE_CHAT_UIDS`. Senza quella
 * variabile la rotta NON funziona: preferisco che nasca muta piuttosto che aperta.
 *
 * Variabili d'ambiente (Vercel, tutte SENZA `NEXT_PUBLIC_`):
 *   GH_TOKEN           token GitHub fine-grained, solo questo repo, Issues read+write
 *   GH_REPO            owner/repo (default: alessiobaljak/agentic_trading_system)
 *   CLAUDE_CHAT_ISSUE  numero della issue usata come thread
 *   CLAUDE_CHAT_UIDS   UID Firebase autorizzati, separati da virgola
 */

import { NextResponse } from 'next/server';

export const runtime = 'nodejs';
export const dynamic = 'force-dynamic';

const GH_API = 'https://api.github.com';
const REPO = process.env.GH_REPO || 'alessiobaljak/agentic_trading_system';
const ISSUE = process.env.CLAUDE_CHAT_ISSUE || '';
const TOKEN = process.env.GH_TOKEN || '';
const UIDS = (process.env.CLAUDE_CHAT_UIDS || '')
  .split(',')
  .map((s) => s.trim())
  .filter(Boolean);

/** Lunghezza massima di un messaggio. Un commento GitHub arriva a 65536 caratteri;
 *  molto prima di quella soglia un messaggio non e' piu' una domanda. */
const MAX_LEN = 8000;

type Verified = { uid: string; email: string | null };

/**
 * Valida l'ID token Firebase facendolo verificare a Google.
 *
 * Si potrebbe verificare la firma in locale, ma servirebbe firebase-admin e una
 * service-account key da custodire: una chiave in piu' da proteggere per fare una
 * cosa che Google fa gratis e meglio. Questo endpoint controlla firma, scadenza e
 * progetto, e restituisce l'utente vero.
 */
async function verify(idToken: string): Promise<Verified | null> {
  const key = process.env.NEXT_PUBLIC_FIREBASE_API_KEY;
  if (!key || !idToken) return null;
  try {
    const r = await fetch(
      `https://identitytoolkit.googleapis.com/v1/accounts:lookup?key=${key}`,
      {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({ idToken }),
        cache: 'no-store',
      },
    );
    if (!r.ok) return null;
    const data = (await r.json()) as { users?: Array<{ localId?: string; email?: string }> };
    const u = data.users?.[0];
    if (!u?.localId) return null;
    return { uid: u.localId, email: u.email ?? null };
  } catch {
    return null;
  }
}

/** L'utente autorizzato, oppure una risposta di errore gia' pronta. */
async function gate(req: Request): Promise<{ user: Verified } | { error: NextResponse }> {
  if (!TOKEN || !ISSUE) {
    return {
      error: NextResponse.json(
        { error: 'non configurato: mancano GH_TOKEN e/o CLAUDE_CHAT_ISSUE su Vercel' },
        { status: 503 },
      ),
    };
  }
  const auth = req.headers.get('authorization') || '';
  const user = await verify(auth.replace(/^Bearer\s+/i, ''));
  if (!user) {
    return { error: NextResponse.json({ error: 'accesso non valido' }, { status: 401 }) };
  }
  if (UIDS.length === 0) {
    // Fail-closed, ma con l'informazione che serve per aprire: chi e' loggato vede
    // il PROPRIO uid e puo' incollarlo su Vercel. Nessun altro puo' arrivare qui.
    return {
      error: NextResponse.json(
        {
          error:
            'CLAUDE_CHAT_UIDS non e\' impostata su Vercel, quindi nessuno e\' ' +
            `autorizzato. Il tuo UID e\': ${user.uid}`,
        },
        { status: 403 },
      ),
    };
  }
  if (!UIDS.includes(user.uid)) {
    return { error: NextResponse.json({ error: 'utente non autorizzato' }, { status: 403 }) };
  }
  return { user };
}

function gh(path: string, init: RequestInit = {}) {
  return fetch(`${GH_API}${path}`, {
    ...init,
    headers: {
      accept: 'application/vnd.github+json',
      authorization: `Bearer ${TOKEN}`,
      'x-github-api-version': '2022-11-28',
      ...(init.headers || {}),
    },
    cache: 'no-store',
  });
}

type GhComment = {
  id: number;
  body: string;
  created_at: string;
  html_url: string;
  user: { login: string; type: string };
};

export type ChatMessage = {
  id: number;
  from: 'io' | 'claude';
  author: string;
  text: string;
  at: string;
  url: string;
};

/** `@claude` e' l'innesco del workflow, non parte del messaggio: fuori dalla vista. */
function strip(body: string): string {
  return body.replace(/^\s*@claude\s*/i, '').trim();
}

/**
 * GET — la conversazione.
 *
 * Si prende l'ULTIMA pagina, non la prima: in un thread lungo le risposte recenti
 * sono in fondo, e mostrare la prima pagina significherebbe mostrare l'anno scorso.
 */
export async function GET(req: Request) {
  const g = await gate(req);
  if ('error' in g) return g.error;

  const first = await gh(`/repos/${REPO}/issues/${ISSUE}/comments?per_page=100`);
  if (!first.ok) {
    return NextResponse.json(
      { error: `GitHub ha risposto ${first.status}` },
      { status: 502 },
    );
  }
  let rows = (await first.json()) as GhComment[];
  const last = /<([^>]+)>;\s*rel="last"/.exec(first.headers.get('link') || '')?.[1];
  if (last) {
    const r = await gh(last.replace(GH_API, ''));
    if (r.ok) rows = (await r.json()) as GhComment[];
  }

  const messages: ChatMessage[] = rows.map((c) => ({
    id: c.id,
    // Chi ha scritto: se e' un bot, e' la risposta; se e' una persona, sono io.
    // (Il gate del workflow garantisce che l'unica persona qui sia il proprietario.)
    from: c.user?.type === 'Bot' ? 'claude' : 'io',
    author: c.user?.login ?? '?',
    text: strip(c.body || ''),
    at: c.created_at,
    url: c.html_url,
  }));
  return NextResponse.json({ messages, issue: Number(ISSUE), repo: REPO });
}

/** POST — manda un messaggio. Il prefisso `@claude` fa partire il workflow. */
export async function POST(req: Request) {
  const g = await gate(req);
  if ('error' in g) return g.error;

  let text = '';
  try {
    text = String(((await req.json()) as { text?: string })?.text ?? '').trim();
  } catch {
    return NextResponse.json({ error: 'richiesta illeggibile' }, { status: 400 });
  }
  if (!text) return NextResponse.json({ error: 'messaggio vuoto' }, { status: 400 });
  if (text.length > MAX_LEN) {
    return NextResponse.json(
      { error: `messaggio troppo lungo (${text.length} caratteri, massimo ${MAX_LEN})` },
      { status: 400 },
    );
  }

  const r = await gh(`/repos/${REPO}/issues/${ISSUE}/comments`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({ body: `@claude ${text}` }),
  });
  if (!r.ok) {
    return NextResponse.json(
      { error: `GitHub ha risposto ${r.status}` },
      { status: 502 },
    );
  }
  const c = (await r.json()) as GhComment;
  return NextResponse.json({
    ok: true,
    message: {
      id: c.id,
      from: 'io',
      author: c.user?.login ?? 'io',
      text,
      at: c.created_at,
      url: c.html_url,
    } satisfies ChatMessage,
  });
}
