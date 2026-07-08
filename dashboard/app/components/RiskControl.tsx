'use client';

import { useEffect, useState } from 'react';
import { doc, onSnapshot, serverTimestamp, setDoc } from 'firebase/firestore';
import { getDb } from '../lib/firebase';
import {
  MAX_LEVERAGE,
  MIN_LEVERAGE,
  MAX_RISK_PER_TRADE,
  MIN_RISK_PER_TRADE,
  clampLeverage,
  clampRiskPerTrade,
} from '../lib/hardLimits';
import type { RiskSettings } from '../lib/types';

/**
 * Risk control panel. Reads + writes user_risk_settings/current.
 *
 * The UI NEVER lets the user send values above the hard caps mirrored from the
 * bot (MAX_LEVERAGE=5, MAX_RISK_PER_TRADE=0.03). Values are clamped on the client
 * before writing; the bot re-enforces the same caps as the final authority.
 *
 * risk_per_trade is stored as a fraction (0.01 = 1%); the UI works in percent.
 */
// Default USATI DAL BOT quando user_risk_settings/current non esiste
// (bot/config.py: DEFAULT_LEVERAGE=2.0, DEFAULT_RISK_PER_TRADE=0.01). Devono
// combaciare con quei valori: altrimenti il pannello mostra numeri diversi da
// quelli realmente applicati dal bot finche' non premi "Save".
const BOT_DEFAULT_LEVERAGE = 2;
const BOT_DEFAULT_RISK_PCT = 1.0;

export default function RiskControl() {
  const [leverage, setLeverage] = useState<number>(BOT_DEFAULT_LEVERAGE);
  // percent units in the UI; converted to fraction on save
  const [riskPct, setRiskPct] = useState<number>(BOT_DEFAULT_RISK_PCT);
  const [loaded, setLoaded] = useState(false);
  const [hasStored, setHasStored] = useState(false);
  const [saving, setSaving] = useState(false);
  const [warning, setWarning] = useState<string | null>(null);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const db = getDb();
    const unsub = onSnapshot(
      doc(db, 'user_risk_settings', 'current'),
      (snap) => {
        setHasStored(snap.exists());
        if (snap.exists()) {
          const d = snap.data() as RiskSettings;
          if (typeof d.leverage === 'number') setLeverage(clampLeverage(d.leverage));
          if (typeof d.risk_per_trade === 'number') {
            setRiskPct(clampRiskPerTrade(d.risk_per_trade) * 100);
          }
        }
        setLoaded(true);
      },
      () => setLoaded(true),
    );
    return () => unsub();
  }, []);

  const onLeverage = (raw: number) => {
    setSaved(false);
    const clamped = clampLeverage(raw);
    if (raw > MAX_LEVERAGE) {
      setWarning(`Leverage capped at the hard limit of ${MAX_LEVERAGE}x.`);
    } else if (raw < MIN_LEVERAGE) {
      setWarning(`Leverage cannot go below ${MIN_LEVERAGE}x.`);
    } else {
      setWarning(null);
    }
    setLeverage(clamped);
  };

  const onRiskPct = (rawPct: number) => {
    setSaved(false);
    const fraction = rawPct / 100;
    const clamped = clampRiskPerTrade(fraction);
    if (fraction > MAX_RISK_PER_TRADE) {
      setWarning(`Risk per trade capped at the hard limit of ${(MAX_RISK_PER_TRADE * 100).toFixed(1)}%.`);
    } else if (fraction < MIN_RISK_PER_TRADE) {
      setWarning(`Risk per trade cannot go below ${(MIN_RISK_PER_TRADE * 100).toFixed(1)}%.`);
    } else {
      setWarning(null);
    }
    setRiskPct(Number((clamped * 100).toFixed(2)));
  };

  const handleSave = async () => {
    setError(null);
    setSaving(true);
    try {
      const db = getDb();
      // Final clamp guarantees we never write above the caps, regardless of UI state.
      const safeLeverage = clampLeverage(leverage);
      const safeRisk = clampRiskPerTrade(riskPct / 100);
      await setDoc(
        doc(db, 'user_risk_settings', 'current'),
        {
          leverage: safeLeverage,
          risk_per_trade: safeRisk,
          updated_by: 'dashboard',
          updated_at: serverTimestamp(),
        },
        { merge: true },
      );
      setSaved(true);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to save settings.');
    } finally {
      setSaving(false);
    }
  };

  const riskFraction = riskPct / 100;

  return (
    <div className="panel">
      <h2>Risk Control</h2>
      <p className="subtitle">
        Adjustable within hard safety caps. The bot may reduce these further under high volatility.
      </p>

      {!loaded && <p className="muted">Loading current settings…</p>}

      {loaded && !hasStored && (
        <div className="warn">
          Nessuna impostazione salvata su Firebase: il bot sta usando i suoi default
          (<strong>{BOT_DEFAULT_LEVERAGE}x</strong> · <strong>{BOT_DEFAULT_RISK_PCT.toFixed(1)}%</strong>).
          I valori qui sotto NON sono ancora attivi finché non premi «Save settings».
        </div>
      )}

      <div className="field">
        <div className="field-row">
          <label htmlFor="lev">Leverage</label>
          <span className="mono">{leverage}x</span>
        </div>
        <input
          id="lev"
          type="range"
          min={MIN_LEVERAGE}
          max={MAX_LEVERAGE}
          step={1}
          value={leverage}
          onChange={(e) => onLeverage(Number(e.target.value))}
        />
        <div className="field-row" style={{ marginTop: 6 }}>
          <span className="cap-note">
            Range {MIN_LEVERAGE}x – {MAX_LEVERAGE}x · hard cap {MAX_LEVERAGE}x
          </span>
          <input
            type="number"
            min={MIN_LEVERAGE}
            max={MAX_LEVERAGE}
            step={1}
            value={leverage}
            onChange={(e) => onLeverage(Number(e.target.value))}
          />
        </div>
      </div>

      <div className="field">
        <div className="field-row">
          <label htmlFor="risk">Risk per trade</label>
          <span className="mono">{riskPct.toFixed(2)}%</span>
        </div>
        <input
          id="risk"
          type="range"
          min={MIN_RISK_PER_TRADE * 100}
          max={MAX_RISK_PER_TRADE * 100}
          step={0.1}
          value={riskPct}
          onChange={(e) => onRiskPct(Number(e.target.value))}
        />
        <div className="field-row" style={{ marginTop: 6 }}>
          <span className="cap-note">
            Range {(MIN_RISK_PER_TRADE * 100).toFixed(1)}% – {(MAX_RISK_PER_TRADE * 100).toFixed(1)}% ·
            hard cap {(MAX_RISK_PER_TRADE * 100).toFixed(1)}%
          </span>
          <input
            type="number"
            min={MIN_RISK_PER_TRADE * 100}
            max={MAX_RISK_PER_TRADE * 100}
            step={0.1}
            value={riskPct}
            onChange={(e) => onRiskPct(Number(e.target.value))}
          />
        </div>
        <div className="muted" style={{ fontSize: 11, marginTop: 4 }}>
          Stored as fraction: {riskFraction.toFixed(4)}
        </div>
      </div>

      {warning && <div className="warn">{warning}</div>}
      {error && <div className="warn">{error}</div>}

      <div style={{ marginTop: 16, display: 'flex', alignItems: 'center', gap: 12 }}>
        <button className="btn btn-primary" onClick={handleSave} disabled={saving || !loaded}>
          {saving ? 'Saving…' : 'Save settings'}
        </button>
        {saved && <span className="ok-msg">Saved to Firebase.</span>}
      </div>
    </div>
  );
}
