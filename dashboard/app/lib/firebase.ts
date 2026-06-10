/**
 * Firebase client initialization (modular Web SDK v9 / v10).
 *
 * All config comes from NEXT_PUBLIC_FIREBASE_* env vars so it can be embedded in
 * the client bundle. If the required vars are missing we DO NOT throw — instead
 * `firebaseReady` is false and the UI renders a "configure Firebase" notice.
 */

import { getApp, getApps, initializeApp, type FirebaseApp } from 'firebase/app';
import { getFirestore, type Firestore } from 'firebase/firestore';
import { getDatabase, type Database } from 'firebase/database';
import { getAuth, type Auth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  databaseURL: process.env.NEXT_PUBLIC_FIREBASE_DATABASE_URL,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

/**
 * Minimum config needed for Firestore + Realtime Database to work.
 * databaseURL is required for the Realtime Database (live positions / bot status).
 */
export const firebaseReady: boolean = Boolean(
  firebaseConfig.apiKey &&
    firebaseConfig.projectId &&
    firebaseConfig.appId &&
    firebaseConfig.databaseURL,
);

/** List of env vars that are missing, for a helpful notice in the UI. */
export const missingFirebaseVars: string[] = (
  [
    ['NEXT_PUBLIC_FIREBASE_API_KEY', firebaseConfig.apiKey],
    ['NEXT_PUBLIC_FIREBASE_PROJECT_ID', firebaseConfig.projectId],
    ['NEXT_PUBLIC_FIREBASE_APP_ID', firebaseConfig.appId],
    ['NEXT_PUBLIC_FIREBASE_DATABASE_URL', firebaseConfig.databaseURL],
  ] as const
)
  .filter(([, v]) => !v)
  .map(([k]) => k);

let app: FirebaseApp | null = null;
let firestoreInstance: Firestore | null = null;
let rtdbInstance: Database | null = null;
let authInstance: Auth | null = null;

if (firebaseReady) {
  app = getApps().length ? getApp() : initializeApp(firebaseConfig as Record<string, string>);
  firestoreInstance = getFirestore(app);
  rtdbInstance = getDatabase(app);
  authInstance = getAuth(app);
}

/**
 * Accessors. These return the live instances when Firebase is configured.
 * Components should gate on `firebaseReady` before calling these; if they are
 * called while unconfigured they throw a clear error (which won't happen in
 * normal flow because the page short-circuits to the config notice).
 */
export function getDb(): Firestore {
  if (!firestoreInstance) {
    throw new Error('Firestore not initialized: Firebase env vars are missing.');
  }
  return firestoreInstance;
}

export function getRtdb(): Database {
  if (!rtdbInstance) {
    throw new Error('Realtime Database not initialized: Firebase env vars are missing.');
  }
  return rtdbInstance;
}

export function getAuthInstance(): Auth {
  if (!authInstance) {
    throw new Error('Auth not initialized: Firebase env vars are missing.');
  }
  return authInstance;
}

export { app, firestoreInstance as firestore, rtdbInstance as rtdb, authInstance as auth };
