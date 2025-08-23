import admin from 'firebase-admin';
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
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

const firebaseConfig = {
  apiKey: "AIzaSyAYSBOZRZOJIwGfodxIrXzfmky6quyNY-w",
  authDomain: "chungminjae-49bba.firebaseapp.com",
  projectId: "chungminjae-49bba",
  storageBucket: "chungminjae-49bba.firebasestorage.app",
  messagingSenderId: "201228656510",
  appId: "1:201228656510:web:83943526707bd6be5a5d2f",
  measurementId: "G-L7GWQGL0Y4"
};

const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);

export const firestore = admin.firestore();
export const auth = admin.auth();
export const bucket = admin.storage().bucket();
export default admin;
