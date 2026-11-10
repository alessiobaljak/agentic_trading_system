/**
 * SOLO PER LA PROVA IN LOCALE (`DASHBOARD_PROVA=1`, vedi next.config.mjs): un albero finto con la stessa forma di quello che il bot
 * scrive su Firebase (bot/portafoglio/f5.py, eventi.py, demo_binance.py, conto_vero.py, bot/main.py). I numeri sono inventati e
 * generati a caso con un seme fisso: servono a guardare la pagina, non dicono niente delle strategie. In produzione questo file
 * non entra nel bundle: lo importano solo i moduli finti di firebase in questa cartella.
 *
 * Scenari dall'indirizzo: `?prova=calmo` (nessun allarme), `?prova=fermo` (demo fermo), altrimenti un allarme acceso sul demo.
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
      eseguito: (oggi0 - n * 86400_000) / 1000 + ora, costo: 2.1,
    }]));

  const eDemo = ultimo(demo);
  const allarmi = scenario === 'calmo' || scenario === 'fermo' ? null : {
    limiti_binance: {
      ora: adesso - 25 * 60, codice: 429,
      testo: 'Binance ha chiesto di rallentare (429): nessuna richiesta per 2 minuti, poi si riprende da solo',
    },
  };
  const fermo = scenario === 'fermo' ? { motivo: 'chiudi tutto dalla dashboard', ora: adesso - 40 * 60, chiuse: 47 } : null;

  return {
    bot_status: { heartbeat: adesso - 35, state: 'running', updated_at: adesso - 35 },
    paper_g1: {
      stato: statoPaper(g1, 24, 24, g(0), 22 * 60),
      giorni: g1,
      ribilanciamenti: ribGiornalieri([3, 2, 1, 0]),
    },
    paper_g11: {
      stato: statoPaper(g11, 25, 24, g(0), 22 * 60),
      giorni: g11,
      ribilanciamenti: ribGiornalieri([2, 1, 0]),
    },
    paper_g1n: {
      stato: statoPaper(g1n, 23, 26, g(0), 22 * 60),
      giorni: g1n,
      ribilanciamenti: ribGiornalieri([2, 1, 0]),
    },
    paper_f5: {
      stato: statoPaper(f5, 22, 21, g(1), 23 * 60),
      giorni: f5,
      ribilanciamenti: ribGiornalieri([8, 1]),
    },
    paper_eventi: {
      stato: {
        stato: 'acceso', equity: ultimo(eventi), capitale: 10_000, rendimento: ultimo(eventi) / 10_000 - 1, aperte_n3: 3,
        aperte_e4: 1, chiuse: 6, rendimento_medio: 0.021, e4_in_attesa: 0, aggiornato: adesso - 21 * 60,
      },
      giorni: eventi,
      ribilanciamenti: null,
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
      fasi: {
        'conto_intero_fino_al_x': { giorni: fase5000 },
        [`capitale_280_fino_al_${g(2)}`]: { giorni: fase280 },
      },
      ribilanciamenti: {
        [g(1)]: { ordini: 46, equity: 1_004, entrate: 4, uscite: 3, rifiutati: [], piazzati: (oggi0 - 86400_000) / 1000 + 312 },
        [g(0)]: { ordini: 44, equity: eDemo, entrate: 3, uscite: 2, rifiutati: ['龙虾USDT'], piazzati: oggi0 / 1000 + 309 },
      },
      allarme: null,
      allarmi,
      fermo,
      confronto: { ora: adesso - 18 * 60, differenze: [{ simbolo: 'BTCUSDT', scarto: 0.031 }], scarto_totale: 0.04, monete: 47 },
      errore: null,
    },
    conto_vero: {
      stato: { stato: "spento: manca l'interruttore ops/conto_vero_acceso", acceso: false, aggiornato: adesso - 30 },
    },
    commands: {},
  };
}
