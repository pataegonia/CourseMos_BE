import { auth, bucket, firestore } from '../config/firebase.js';
import { v4 as uuidv4 } from 'uuid';

export async function uploadProfilePhoto(req, res) {
  try {
    const uid = req.user.uid;
    if (!req.file) return res.status(400).json({ message: '파일이 없습니다.' });

    // 기존 파일 경로 조회(있으면 교체 시 삭제해주려고)
    const userRef = firestore.collection('users').doc(uid);
    const beforeSnap = await userRef.get();
    const before = beforeSnap.exists ? beforeSnap.data() : null;
    const beforePath = before?.photoStoragePath;

    // 저장 경로
    const original = req.file.originalname || 'upload.jpg';
    const storagePath = `profile/${uid}/${Date.now()}_${original}`;
    const file = bucket.file(storagePath);

    // 다운로드 토큰 달기
    const token = uuidv4();
    const metadata = {
      metadata: { firebaseStorageDownloadTokens: token },
      contentType: req.file.mimetype,
      cacheControl: 'public,max-age=31536000'
    };

    // 업로드
    await file.save(req.file.buffer, { metadata, resumable: false });

    // 공개 URL
    const photoURL =
      `https://firebasestorage.googleapis.com/v0/b/${bucket.name}/o/${encodeURIComponent(storagePath)}?alt=media&token=${token}`;

    // Auth/Firestore 업데이트
    await auth.updateUser(uid, { photoURL });
    await userRef.set(
      { photoURL, photoStoragePath: storagePath, updatedAt: new Date() },
      { merge: true }
    );

    // 이전 파일이 있으면 삭제(선택)
    if (beforePath && beforePath !== storagePath) {
      try { await bucket.file(beforePath).delete(); } catch (_) {}
    }

    return res.status(201).json({ photoURL });
  } catch (e) {
    console.error(e);
    return res.status(500).json({ message: '업로드 실패', detail: e.message });
  }
}
