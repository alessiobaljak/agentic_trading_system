import { firebaseReady, missingFirebaseVars } from './lib/firebase';
import AuthGate from './components/AuthGate';
import DashboardShell from './components/DashboardShell';

function ConfigureNotice() {
  return (
    <div className="notice">
      <h2 style={{ marginTop: 0 }}>Configura Firebase per vedere la dashboard</h2>
      <p>
        La dashboard legge lo stato vivo da Firebase. Imposta queste variabili d&apos;ambiente
        (copia <code>.env.local.example</code> in <code>.env.local</code> in locale, o aggiungile
        nelle impostazioni del progetto Vercel):
      </p>
      <ul>
        {missingFirebaseVars.length > 0 ? (
          missingFirebaseVars.map((v) => (
            <li key={v}>
              <code>{v}</code> — manca
            </li>
          ))
        ) : (
          <li>
            <code>NEXT_PUBLIC_FIREBASE_*</code>
          </li>
        )}
      </ul>
      <p className="muted" style={{ marginBottom: 0 }}>
        Obbligatorie: API key, project id, app id e l&apos;URL del Realtime Database. Consigliate:
        auth domain, storage bucket, messaging sender id.
      </p>
    </div>
  );
}

export default function Page() {
  if (!firebaseReady) {
    return (
      <main className="container">
        <ConfigureNotice />
      </main>
    );
  }

  return (
    <>
      <AuthGate>
        <DashboardShell />
      </AuthGate>

      <footer
        className="muted"
        style={{ fontSize: 11, margin: '4px auto 24px', textAlign: 'center', maxWidth: 1280, padding: '0 16px' }}
      >
        Nessun soldo vero: il bot lavora con DRY_RUN acceso, il paper con dollari virtuali e il demo di Binance con soldi finti.
        Il conto vero è spento e parte solo su tua richiesta esplicita.
      </footer>
    </>
  );
}
