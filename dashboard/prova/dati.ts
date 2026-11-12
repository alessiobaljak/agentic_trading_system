/**
 * SOLO PER LA PROVA IN LOCALE (`DASHBOARD_PROVA=1`, vedi next.config.mjs): un albero finto con la stessa forma di quello che il bot
 * scrive su Firebase (bot/portafoglio/f5.py, eventi.py, demo_binance.py, conto_vero.py, bot/main.py). I numeri sono inventati e
 * generati a caso con un seme fisso: servono a guardare la pagina, non dicono niente delle strategie. In produzione questo file
 * non entra nel bundle: lo importano solo i moduli finti di firebase in questa cartella.
 *
 * Scenari dall'indirizzo: `?prova=calmo` (nessun allarme), `?prova=fermo` (demo fermo), `?prova=azioni_vuote` (niente in /azioni),
 * altrimenti un allarme acceso sul demo. Il ramo /azioni è l'esempio della forma proposta in dashboard/GUIDA_SCHEDA_AZIONI.md.
 * Il conto vero (12 nov 2026) è spento con la versione in esecuzione ancora da approvare; `?prova=vero_approvata` (spento, versione
 * approvata), `?prova=vero_acceso`, `?prova=vero_fermo` (per provare il «riparti» in due passi), `?prova=vero_diversa` (acceso, ma
 * la versione approvata non è quella in esecuzione: niente ordini nuovi).
 */

type Albero = Record<string, unknown>;

function generatore(seme: number) {
  let a = seme >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const giorno = (ms: number) => new Date(ms).toISOString().slice(0, 10);

/** L'esempio di /azioni (la forma della guida): due strategie, giorni di borsa (niente sabato e domenica), pesi con «_» al posto
 *  del punto nei simboli. */
function creaAzioni(adesso: number, oggi0: number, normale: () => number): Albero {
  const borsa: string[] = [];
  for (let n = 20; n >= 0; n--) {
    const ms = oggi0 - n * 86400_000;
    const gs = new Date(ms).getUTCDay();
    if (gs !== 0 && gs !== 6) borsa.push(giorno(ms));
  }
  const serie = (capitale: number, media: number, vol: number) => {
    const out: Record<string, number> = {};
    let v = capitale;
    for (const g of borsa) {
      v *= 1 + media + vol * normale();
      out[g] = Math.round(v * 100) / 100;
    }
    return out;
  };
  const a = serie(10_000, 0.0012, 0.008);
  const b = serie(10_000, 0.0006, 0.005);
  const ultimo = (x: Record<string, number>) => x[borsa[borsa.length - 1]];
  return {
    battito: adesso - 300,
    soglia_battito_s: 6 * 3600,
    strategie: {
      momentum_ch: {
        nome: 'Momentum svizzero', descrizione: 'Compra le azioni dello SMI salite di più negli ultimi 6 mesi; cambia ogni mese.',
        tipo: 'demo', ordine: 1, valuta: 'CHF', capitale: 10_000, valore: ultimo(a), rendimento: ultimo(a) / 10_000 - 1,
        comprate: 5, vendute: 0, aggiornato: adesso - 600, giorni: a,
        pesi: { NESN_SW: 0.21, NOVN_SW: 0.2, ROG_SW: 0.2, UBSG_SW: 0.19, ABBN_SW: 0.18 },
        ultimo_ribilancio: { ora: adesso - 6 * 86400, entrate: 2, uscite: 2 },
        // le operazioni giorno per giorno (pagina «Operazioni», components/stock/Operazioni.tsx)
        operazioni: {
          [borsa[borsa.length - 1]]: [
            { simbolo: 'NESN_SW', lato: 'buy', quantita: 20, ingresso: 81.2, uscita_prezzo: 82.05, uscita: 'chiusura', guadagno: 17, proporzione: 0.0105, ora_ingresso: new Date((adesso - 3 * 3600) * 1000).toISOString() },
            { simbolo: 'UBSG_SW', lato: 'sell', quantita: 60, ingresso: 27.4, uscita_prezzo: 27.75, uscita: 'stop', guadagno: -21, proporzione: -0.0128, ora_ingresso: new Date((adesso - 3 * 3600) * 1000).toISOString() },
            { simbolo: 'ROG_SW', nota: 'saltato: candela piatta' },
          ],
        },
      },
      qualita_ch: {
        nome: 'Qualità svizzera', descrizione: 'Le 8 azioni dello SMI con i conti più solidi, pesi uguali.',
        tipo: 'paper', ordine: 2, valuta: 'CHF', capitale: 10_000, valore: ultimo(b), rendimento: ultimo(b) / 10_000 - 1,
        comprate: 8, vendute: 0, aggiornato: adesso - 600, giorni: b, pesi: null,
        ultimo_ribilancio: { ora: adesso - 9 * 86400, entrate: 1, uscite: 1 },
      },
    },
    allarmi: null,
  };
}

/** Il ramo /conto_vero e i suoi comandi, con la forma di bot/portafoglio/conto_vero.py (hash e titoli inventati). */
function creaContoVero(scenario: string | null, adesso: number): { ramo: Albero; comandi: Albero } {
  const COMMIT = '3f9c2a7e1b4d5c6f8a0b1c2d3e4f5a6b7c8d9e0f';
  const COMMIT_PRIMA = '9a1b2c3d4e5f60718293a4b5c6d7e8f901234567';
  const acceso = scenario === 'vero_acceso' || scenario === 'vero_fermo' || scenario === 'vero_diversa';
  const approvata = scenario === 'vero_diversa' ? COMMIT_PRIMA : scenario?.startsWith('vero_') ? COMMIT : null;
  const blocco = approvata === COMMIT ? null : approvata
    ? `il processo esegue il commit ${COMMIT.slice(0, 8)}, diverso dalla versione approvata (${COMMIT_PRIMA.slice(0, 8)}) in: `
      + 'bot/portafoglio/conto_vero.py: serve un riavvio su quella versione, o l\'approvazione di quella in esecuzione'
    : 'nessuna versione approvata dal proprietario (dashboard, scheda del conto vero, «Approva questa versione»)';
  const versione = {
    commit: COMMIT, data: new Date((adesso - 5 * 3600) * 1000).toISOString(),
    titolo: 'Conto vero: la versione si approva dalla dashboard, riparti in due passi', pulito: true,
    ...(approvata ? { approvata } : {}), coincidono: blocco === null, ...(blocco ? { blocco } : {}), aggiornato: adesso - 40,
  };
  const fermo = scenario === 'vero_fermo'
    ? { motivo: 'stop sul conto: 181,40 USDT, sotto il 65% del capitale di partenza (182,00)', ora: adesso - 55 * 60, chiuse: 38,
      vuoto: adesso - 54 * 60 }
    : null;
  const equity = fermo ? 181.4 : 287.35;
  const stato = !acceso
    ? { stato: "spento: manca l'interruttore ops/conto_vero_acceso", acceso: false, aggiornato: adesso - 30 }
    : fermo
      ? { stato: `fermo: ${fermo.motivo}`, equity, capitale_iniziale: 280, aggiornato: adesso - 54 * 60 }
      : {
        stato: blocco ? `solo protezioni, niente ordini nuovi: ${blocco}` : 'acceso', equity, saldo: equity - 1.2,
        capitale_iniziale: 280, rendimento: equity / 280 - 1, long: 20, short: 19, limite_eseguiti: 27, limite_totali: 39,
        ordini_in_attesa: 0, aggiornato: adesso - 12 * 60, massimo: 289.1, dal_massimo: equity / 289.1 - 1, stop_a: 187.92,
        conto_ridotto: 280,
      };
  return {
    ramo: {
      stato, versione, fermo,
      allarmi: acceso && blocco && !fermo
        ? { ordini_vietati: { ora: adesso - 9 * 60, testo: `niente ordini nuovi: ${blocco}; stop sul conto, pulsante e chiusure restano attivi` } }
        : null,
    },
    comandi: approvata ? { conto_vero_versione_approvata: { commit: approvata, ora: (adesso - 3 * 3600) * 1000 } } : {},
  };
}

export function creaDati(scenario: string | null): Albero {
  const rnd = generatore(20261110);
  const normale = () => {
    const u = Math.max(rnd(), 1e-9);
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * rnd());
  };
  const adessoMs = Date.now();
  const adesso = adessoMs / 1000;
  const oggi0 = Date.parse(`${giorno(adessoMs)}T00:00:00Z`);
  const g = (n: number) => giorno(oggi0 - n * 86400_000);

  // i rendimenti di ogni giorno di G1 (paper), dal giorno -18 a oggi
  const N = 18;
  const rG1: number[] = [];
  for (let i = 0; i <= N; i++) rG1.push(0.003 + 0.011 * normale());

  const serie = (inizio: number, capitale: number, r: (i: number) => number): Record<string, number> => {
    const out: Record<string, number> = {};
    let v = capitale;
    for (let i = inizio; i >= 0; i--) {
      v *= 1 + r(N - i);
      out[g(i)] = Math.round(v * 100) / 100;
    }
    return out;
  };

  const g1 = serie(18, 10_000, (i) => rG1[i]);
  const g11 = serie(18, 10_000, (i) => rG1[i] + 0.002 + 0.004 * normale());
  const g1n = serie(16, 10_000, (i) => 0.6 * rG1[i] + 0.0025 + 0.004 * normale());
  const f5 = serie(15, 10_000, (i) => 0.8 * rG1[i] + 0.003 * normale());
  const eventi = serie(7, 10_480, () => 0.001 + 0.006 * normale());
  // il demo: tre fasi (circa 5.000, poi 280, poi 1.000 da due giorni fa), ognuna vicina a G1 con un piccolo scarto
  const demoR = (i: number) => rG1[i] - 0.0006 + 0.0025 * normale();
  const fase5000 = serie(17, 5_000, demoR);
  for (const k of Object.keys(fase5000)) if (k > g(4)) delete fase5000[k];
  const fase280: Record<string, number> = {};
  let v280 = 280;
  for (let i = 4; i >= 2; i--) {
    v280 *= 1 + demoR(N - i);
    fase280[g(i)] = Math.round(v280 * 100) / 100;
  }
  const demo = serie(2, 1_000, demoR);
  const ultimo = (s: Record<string, number>) => s[Object.keys(s).sort().pop()!];

  const statoPaper = (s: Record<string, number>, long: number, short: number, ultimoCambio: string, aggiornatoFa: number) => {
    const e = ultimo(s);
    return {
      stato: 'acceso', equity: e, capitale: 10_000, rendimento: e / 10_000 - 1, long, short, ultimo_lunedi: ultimoCambio,
      costi_totali: 41.2, costi_a_mercato_totali: 88.5, limite_variazioni: 412, limite_eseguite: 301, ordini_in_attesa: 0,
      funding_totale: -12.4, aggiornato: adesso - aggiornatoFa,
    };
  };
  const ribGiornalieri = (giorni: number[], ora = 305) =>
    Object.fromEntries(giorni.map((n) => [g(n), {
      lunedi: g(n), universo: 100, long: 24, short: 24, entrate: Math.floor(rnd() * 6), uscite: Math.floor(rnd() * 6),
      eseguito: (oggi0 - n * 86400_000) / 1000 + ora, costo: 2.1, ordini_limite: 31,
      limite: { variazioni: 31, eseguite: 22, costo: 2.6, costo_a_mercato: 4.9, controllato: (oggi0 - n * 86400_000) / 1000 + 3905 },
    }]));
  const MONETE = ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'ADA', 'LINK', 'AVAX', 'DOT', 'LTC', 'BCH', 'TRX', 'NEAR', 'APT', 'ARB', 'OP',
    'SUI', 'SEI', 'TIA', 'INJ', 'FIL', 'ATOM', 'ETC', 'UNI', 'AAVE', 'MKR', 'LDO', 'RUNE', 'WLD', 'PEPE', 'WIF', 'BONK', 'JUP', 'PYTH',
    'ENA', 'ONDO', 'TAO', 'FET', 'RNDR', 'GALA', 'SAND', 'MANA', 'AXS', 'IMX', 'STX', 'ORDI', 'KAS', 'HBAR'];
  const pesi = (long: number, short: number) => {
    const out: Record<string, number> = {};
    const scelte = [...MONETE].sort(() => rnd() - 0.5);
    scelte.slice(0, long).forEach((m, i) => { out[`${m}USDT`] = Math.round((0.075 - i * 0.0022 + 0.004 * rnd()) * 1e6) / 1e6; });
    scelte.slice(long, long + short).forEach((m, i) => { out[`${m}USDT`] = -Math.round((0.07 - i * 0.002 + 0.004 * rnd()) * 1e6) / 1e6; });
    return out;
  };
  const diarioPaper = (s: Record<string, number>) =>
    Object.fromEntries(Object.entries(s).map(([k, v], i) => [k, { equity: v, long: 24, short: 24, costi_totali: 2.2 * (i + 1),
      funding_totale: -0.7 * (i + 1) }]));

  const eDemo = ultimo(demo);
  const allarmi = scenario === 'calmo' || scenario === 'fermo' ? null : {
    limiti_binance: {
      ora: adesso - 25 * 60, codice: 429,
      testo: 'Binance ha chiesto di rallentare (429): nessuna richiesta per 2 minuti, poi si riprende da solo',
    },
  };
  const fermo = scenario === 'fermo' ? { motivo: 'chiudi tutto dalla dashboard', ora: adesso - 40 * 60, chiuse: 47 } : null;
  const contoVero = creaContoVero(scenario, adesso);

  return {
    bot_status: { heartbeat: adesso - 35, state: 'running', updated_at: adesso - 35 },
    paper_g1: {
      stato: statoPaper(g1, 24, 24, g(0), 22 * 60),
      giorni: g1,
      diario: diarioPaper(g1),
      posizioni: pesi(24, 24),
      ribilanciamenti: ribGiornalieri([3, 2, 1, 0]),
    },
    paper_g11: {
      stato: statoPaper(g11, 25, 24, g(0), 22 * 60),
      giorni: g11,
      diario: diarioPaper(g11),
      posizioni: pesi(25, 24),
      ribilanciamenti: ribGiornalieri([2, 1, 0]),
    },
    paper_g1n: {
      stato: statoPaper(g1n, 23, 26, g(0), 22 * 60),
      giorni: g1n,
      diario: diarioPaper(g1n),
      posizioni: pesi(23, 26),
      ribilanciamenti: ribGiornalieri([2, 1, 0]),
    },
    paper_f5: {
      stato: statoPaper(f5, 22, 21, g(1), 23 * 60),
      giorni: f5,
      diario: diarioPaper(f5),
      posizioni: pesi(22, 21),
      ribilanciamenti: ribGiornalieri([8, 1]),
    },
    paper_eventi: {
      stato: {
        stato: 'acceso', equity: ultimo(eventi), capitale: 10_000, rendimento: ultimo(eventi) / 10_000 - 1, aperte_n3: 3,
        aperte_e4: 1, chiuse: 6, rendimento_medio: 0.021, e4_in_attesa: 0, aggiornato: adesso - 21 * 60,
      },
      giorni: eventi,
      ribilanciamenti: null,
      aperte: {
        a1: { tipo: 'N3', simbolo: 'NUOVAUSDT', entrata: oggi0 - 5 * 86400_000, rendimento_ora: 0.034, uscita_giorno: g(-25) },
        a2: { tipo: 'N3', simbolo: 'ALTRAUSDT', entrata: oggi0 - 3 * 86400_000, rendimento_ora: -0.052, uscita_giorno: g(-27) },
        a3: { tipo: 'N3', simbolo: 'TERZAUSDT', entrata: oggi0 - 86400_000, rendimento_ora: 0.008, uscita_giorno: g(-29) },
        a4: { tipo: 'E4', simbolo: 'QUARTAUSDT', entrata: oggi0 - 2 * 86400_000, rendimento_ora: 0.011, uscita_giorno: g(-5) },
      },
      chiuse: Object.fromEntries([0.12, -0.3, 0.05, 0.021, -0.04, 0.09].map((r, i) => [`c${i}`, {
        tipo: i % 2 ? 'E4' : 'N3', simbolo: `MONETA${i}USDT`, uscita: oggi0 - (i + 1) * 86400_000, rendimento: r, dollari: 500 * r,
        motivo: r < -0.25 ? 'uscita a +30%' : i % 2 ? '7 giorni' : '30 giorni',
      }])),
    },
    demo_binance: {
      stato: fermo
        ? { stato: `fermo: ${fermo.motivo}`, equity: eDemo, aggiornato: adesso - 40 * 60, capitale_iniziale: 1_000 }
        : {
          stato: 'acceso', equity: eDemo, saldo: eDemo - 3.1, capitale_iniziale: 1_000, rendimento: eDemo / 1_000 - 1, long: 24, short: 23,
          limite_eseguiti: 61, limite_totali: 96, ordini_in_attesa: 0, aggiornato: adesso - 18 * 60, massimo: Math.max(1_000, eDemo),
          dal_massimo: eDemo / Math.max(1_000, eDemo) - 1, stop_a: Math.round(Math.max(650, 0.65 * Math.max(1_000, eDemo)) * 100) / 100,
          conto_ridotto: 1_000, capitale_in_attesa: null,
        },
      giorni: demo,
      diario: Object.fromEntries(Object.entries(demo).map(([k, v]) => [k, { equity: v, long: 24, short: 23,
        entrate: { funding_incassato: 0.42, commissioni_pagate: 0.61, righe: 80, altre_valute: 0 } }])),
      fasi: {
        'conto_intero_fino_al_x': { giorni: fase5000 },
        [`capitale_280_fino_al_${g(2)}`]: { giorni: fase280 },
      },
      ribilanciamenti: {
        [g(1)]: { ordini: 46, equity: 1_004, entrate: 4, uscite: 3, rifiutati: [], piazzati: (oggi0 - 86400_000) / 1000 + 312,
          limite: { ordini: 46, eseguiti_a_limite: 30, a_mercato: 16 } },
        [g(0)]: { ordini: 44, equity: eDemo, entrate: 3, uscite: 2, piazzati: oggi0 / 1000 + 309,
          rifiutati: [{ simbolo: '龙虾USDT', errore: 'simbolo non trovato' }], monete_mancanti_sul_demo: ['龙虾USDT'],
          sotto_il_minimo: { variazioni: 2, valore_in_frazione_del_conto: 0.008 }, solo_eventi: false,
          limite: { ordini: 44, eseguiti_a_limite: 31, a_mercato: 13 } },
      },
      allarme: null,
      allarmi,
      fermo,
      confronto: { ora: adesso - 18 * 60, differenze: [{ simbolo: 'BTCUSDT', voluto: 0.071, vero: 0.102, scarto: 0.031 }],
        scarto_totale: 0.04, monete: 47 },
      errore: null,
    },
    conto_vero: contoVero.ramo,
    azioni: scenario === 'azioni_vuote' ? null : creaAzioni(adesso, oggi0, normale),
    commands: contoVero.comandi,
  };
}
