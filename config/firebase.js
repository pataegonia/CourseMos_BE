import admin from 'firebase-admin';
import fs from 'fs';

let credential;
if (process.env.GOOGLE_APPLICATION_CREDENTIALS) {
  const raw = fs.readFileSync(process.env.GOOGLE_APPLICATION_CREDENTIALS, 'utf-8');
  credential = admin.credential.cert(JSON.parse(raw));
} else {
  credential = admin.credential.applicationDefault();
}

admin.initializeApp({
  credential,
  databaseURL: process.env.FIREBASE_DB_URL || undefined,
});

export const firestore = admin.firestore();
export const auth = admin.auth();
export const bucket = admin.storage().bucket();
export default admin;
