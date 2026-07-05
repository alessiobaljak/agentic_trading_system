import { firebaseReady, missingFirebaseVars } from './lib/firebase';
import AuthGate from './components/AuthGate';
import DashboardShell from './components/DashboardShell';

function ConfigureNotice() {
  return (
    <div className="notice">
      <h2 style={{ marginTop: 0 }}>Configure Firebase to load the dashboard</h2>
      <p>
        The dashboard reads live state from Firebase. Set the following environment variables
        (copy <code>.env.local.example</code> to <code>.env.local</code> locally, or add them in
        your Vercel project settings):
      </p>
      <ul>
        {missingFirebaseVars.length > 0 ? (
          missingFirebaseVars.map((v) => (
            <li key={v}>
              <code>{v}</code> — missing
            </li>
          ))
        ) : (
          <li>
            <code>NEXT_PUBLIC_FIREBASE_*</code> values
          </li>
        )}
      </ul>
      <p className="muted" style={{ marginBottom: 0 }}>
        Required: API key, project id, app id and the Realtime Database URL. Also recommended: auth
        domain, storage bucket, messaging sender id.
      </p>
    </div>
  );
}

export default function Page() {
  return (
    <main className="container">
      {!firebaseReady ? (
        <ConfigureNotice />
      ) : (
        <AuthGate>
          <DashboardShell />
        </AuthGate>
      )}

      <footer className="muted" style={{ fontSize: 11, marginTop: 24, textAlign: 'center' }}>
        Hard caps enforced client-side (leverage ≤ 5x, risk ≤ 3%) and re-enforced by the bot.
      </footer>
    </main>
  );
}
