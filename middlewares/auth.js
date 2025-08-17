import { auth } from '../config/firebase.js';

export async function verifyFirebaseIdToken(req, res, next) {
  const h = req.headers.authorization || '';
  const token = h.startsWith('Bearer ') ? h.slice(7) : null;
  if (!token) return res.status(401).json({ message: '토큰이 없습니다.' });

  try {
    req.user = await auth.verifyIdToken(token); // uid, email 등
    next();
  } catch (e) {
    return res.status(401).json({ message: '유효하지 않은 토큰입니다.', detail: e.message });
  }
}
