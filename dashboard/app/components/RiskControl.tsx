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
import { lista, useControllo, type PosizioneBreve } from '../lib/controllo';
import { pct } from '../lib/viz';

/**
 * Pannello del rischio. Legge e scrive user_risk_settings/current.
 *
 * L'interfaccia NON manda mai valori sopra i tetti duri copiati dal bot
 * (MAX_LEVERAGE=5, MAX_RISK_PER_TRADE=0.03): si taglia lato client prima di
 * scrivere, e il bot riapplica gli stessi tetti come ultima autorita'.
 *
 * risk_per_trade e' salvato come frazione (0.01 = 1%); qui si lavora in percento.
 *
 * Dal 25 set 2026 il pannello dice anche il rischio EFFETTIVO per posizione
 * di oggi (dal controllo orario, `salute.posizioni[].rischio_pct`): il numero
 * impostato qui e' un massimo, quello vero per ogni posizione e' piu' basso
 * (stop, leva, freno, tetti per coin e direzione), e vederli vicini spiega
 * perche' «1%» non vuol dire «1% per trade».
 */
// Default USATI DAL BOT quando user_risk_settings/current non esiste
// (bot/config.py: DEFAULT_LEVERAGE=2.0, DEFAULT_RISK_PER_TRADE=0.01). Devono
// combaciare con quei valori: altrimenti il pannello mostra numeri diversi da
// quelli realmente applicati dal bot finche' non premi "Save".
const BOT_DEFAULT_LEVERAGE = 2;
const BOT_DEFAULT_RISK_PCT = 1.0;

export default function RiskControl() {
  const { doc: controllo, etaS } = useControllo();
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
      setWarning(`Leva tagliata al tetto duro di ${MAX_LEVERAGE}x.`);
    } else if (raw < MIN_LEVERAGE) {
      setWarning(`La leva non puo' scendere sotto ${MIN_LEVERAGE}x.`);
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
      setWarning(`Rischio per trade tagliato al tetto duro del ${(MAX_RISK_PER_TRADE * 100).toFixed(1)}%.`);
    } else if (fraction < MIN_RISK_PER_TRADE) {
      setWarning(`Il rischio per trade non puo' scendere sotto ${(MIN_RISK_PER_TRADE * 100).toFixed(1)}%.`);
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
      // Ultimo taglio: mai scrivere sopra i tetti, qualunque sia lo stato dell'interfaccia.
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
      setError(e instanceof Error ? e.message : 'Salvataggio fallito.');
    } finally {
      setSaving(false);
    }
  };

  const riskFraction = riskPct / 100;

  // rischio effettivo per posizione, oggi: min-max fra le posizioni aperte
  const posizioni = lista<PosizioneBreve>(controllo?.salute?.posizioni);
  const rischi = posizioni.map((p) => p.rischio_pct).filter((v): v is number => v != null && Number.isFinite(v));
  const rischioEffettivo =
    !controllo ? 'controllo non disponibile'
    : rischi.length === 0 ? 'nessuna posizione aperta'
    : rischi.length === 1 ? `${pct(rischi[0], 2)} (1 posizione)`
    : `${pct(Math.min(...rischi), 2)} – ${pct(Math.max(...rischi), 2)} (${rischi.length} posizioni)`;

  return (
    <div className="panel">
      <h2>Rischio</h2>
      <p className="subtitle">
        Regolabile entro i tetti di sicurezza. Il bot puo&apos; abbassare ancora questi valori
        con volatilita&apos; alta.
      </p>

      {!loaded && <p className="muted">Caricamento delle impostazioni…</p>}

      {loaded && !hasStored && (
        <div className="warn">
          Nessuna impostazione salvata su Firebase: il bot sta usando i suoi default
          (<strong>{BOT_DEFAULT_LEVERAGE}x</strong> · <strong>{BOT_DEFAULT_RISK_PCT.toFixed(1)}%</strong>).
          I valori qui sotto NON sono ancora attivi finché non premi «Salva».
        </div>
      )}

      <p
        className="riga-paper"
        style={{ marginBottom: 14 }}
        title={
          controllo
            ? `dal controllo orario (${etaS != null ? Math.round(etaS / 60) : '?'} min fa): rischio_pct di ogni posizione aperta`
            : 'il controllo orario non e\' ancora arrivato'
        }
      >
        <b>rischio effettivo per posizione oggi</b>: {rischioEffettivo}
        {controllo?.salute?.rischio_aperto_pct != null && (
          <span className="muted"> · totale aperto {pct(controllo.salute.rischio_aperto_pct, 2)}</span>
        )}
      </p>

      <div className="field">
        <div className="field-row">
          <label htmlFor="lev">Leva</label>
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
            Da {MIN_LEVERAGE}x a {MAX_LEVERAGE}x · tetto duro {MAX_LEVERAGE}x
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
          <label htmlFor="risk">Rischio per trade</label>
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
            Da {(MIN_RISK_PER_TRADE * 100).toFixed(1)}% a {(MAX_RISK_PER_TRADE * 100).toFixed(1)}% ·
            tetto duro {(MAX_RISK_PER_TRADE * 100).toFixed(1)}%
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
          Salvato come frazione: {riskFraction.toFixed(4)}
        </div>
      </div>

      {warning && <div className="warn">{warning}</div>}
      {error && <div className="warn">{error}</div>}

      <div style={{ marginTop: 16, display: 'flex', alignItems: 'center', gap: 12 }}>
        <button className="btn btn-primary" onClick={handleSave} disabled={saving || !loaded}>
          {saving ? 'Salvataggio…' : 'Salva'}
        </button>
        {saved && <span className="ok-msg">Salvato su Firebase.</span>}
      </div>
    </div>
  );
}
