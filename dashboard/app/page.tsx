import { firebaseReady, missingFirebaseVars } from './lib/firebase';
import AuthGate from './components/AuthGate';
import BotStatus from './components/BotStatus';
import OptimizedStrategies from './components/OptimizedStrategies';
import Positions from './components/Positions';
import EquityCurve from './components/EquityCurve';
import Heatmap from './components/Heatmap';
import StrategyWeights from './components/StrategyWeights';
import Insights from './components/Insights';
import RiskControl from './components/RiskControl';
import KillSwitch from './components/KillSwitch';

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
      <div className="grid" style={{ marginBottom: 16 }}>
        <header className="header-bar" style={{ paddingBottom: 4 }}>
          <h1 style={{ margin: 0, fontSize: 20 }}>Agentic Trading — Dashboard</h1>
          <span className="muted" style={{ fontSize: 12 }}>
            Live Firebase view · risk control · kill switch
          </span>
        </header>
      </div>

      {!firebaseReady ? (
        <ConfigureNotice />
      ) : (
        <AuthGate>
          <div className="grid">
            <BotStatus />

            <div className="grid grid-2">
              <RiskControl />
              <KillSwitch />
            </div>

            <Positions />

            <div className="grid grid-2">
              <EquityCurve />
              <StrategyWeights />
            </div>

            <Heatmap />

            <OptimizedStrategies />

            <Insights />
          </div>
        </AuthGate>
      )}

      <footer className="muted" style={{ fontSize: 11, marginTop: 24, textAlign: 'center' }}>
        Hard caps enforced client-side (leverage ≤ 5x, risk ≤ 3%) and re-enforced by the bot.
      </footer>
    </main>
  );
}
