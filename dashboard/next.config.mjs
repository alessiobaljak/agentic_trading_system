import path from 'node:path';
import { fileURLToPath } from 'node:url';

const qui = path.dirname(fileURLToPath(import.meta.url));

/**
 * La prova in locale (10 nov 2026): con `DASHBOARD_PROVA=1` i moduli di firebase sono sostituiti da quelli finti in `prova/` (dati
 * inventati, nessuna rete, utente finto), per guardare la pagina senza Firebase. Su Vercel la variabile non c'è: la configurazione
 * resta quella di sempre e `prova/` non entra nel bundle.
 */
const prova = process.env.DASHBOARD_PROVA === '1';

/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  ...(prova
    ? {
        webpack: (config) => {
          config.resolve.alias = {
            ...config.resolve.alias,
            'firebase/app$': path.join(qui, 'prova/firebase-app.ts'),
            'firebase/auth$': path.join(qui, 'prova/firebase-auth.ts'),
            'firebase/database$': path.join(qui, 'prova/firebase-database.ts'),
            'firebase/firestore$': path.join(qui, 'prova/firebase-firestore.ts'),
          };
          return config;
        },
      }
    : {}),
};

export default nextConfig;
