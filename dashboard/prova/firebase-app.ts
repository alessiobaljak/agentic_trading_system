/** SOLO PER LA PROVA IN LOCALE (`DASHBOARD_PROVA=1`, next.config.mjs): prende il posto di `firebase/app`, senza rete. */
export type FirebaseApp = { name: string };

const app: FirebaseApp = { name: 'prova' };

export function initializeApp(): FirebaseApp {
  return app;
}

export function getApps(): FirebaseApp[] {
  return [app];
}

export function getApp(): FirebaseApp {
  return app;
}
