// config/firebase.js (Server-side only: Admin SDK)
import admin from 'firebase-admin';
import fs from 'fs';

let credential;
if (process.env.GOOGLE_APPLICATION_CREDENTIALS) {
  const raw = fs.readFileSync(process.env.GOOGLE_APPLICATION_CREDENTIALS, 'utf-8');
  credential = admin.credential.cert(JSON.parse(raw));
} else {
  credential = admin.credential.applicationDefault();
}

if (!admin.apps.length) {
  admin.initializeApp({
    credential,
    // RTDB를 실제로 쓸 때만 유지
    databaseURL: process.env.FIREBASE_DB_URL || undefined,
    // ✅ 버킷 이름을 확실히 주입
    storageBucket: process.env.FIREBASE_STORAGE_BUCKET,
  });
}

export const auth = admin.auth();
export const firestore = admin.firestore();
// 기본 버킷 핸들 (위에서 storageBucket을 지정했으니 이름 생략 가능)
export const bucket = admin.storage().bucket();

export default admin;
