import { firestore } from '../config/firebase.js';

/** 날짜를 '날짜만' 비교하도록 UTC 기준 date-only 로 normalize */
function toUtcDateOnly(d) {
  const t = new Date(d);
  return new Date(Date.UTC(t.getUTCFullYear(), t.getUTCMonth(), t.getUTCDate()));
}

export async function getMyPage(req, res) {
  try {
    const uid = req.user.uid; // verifyFirebaseIdToken 에서 세팅됨
    const snap = await firestore.collection('users').doc(uid).get();
    if (!snap.exists) return res.status(404).json({ message: 'User not found' });

    const { name, birthday, partnerBirthday, startDate, photoURL = null } = snap.data() || {};

    // startDate가 없으면 0일 처리
    let daysTogether = 0;
    if (startDate) {
      const start = toUtcDateOnly(startDate);
      const today = toUtcDateOnly(new Date());
      // 포함일 계산(오늘 포함): +1
      daysTogether = Math.floor((today - start) / (1000 * 60 * 60 * 24)) + 1;
      if (daysTogether < 0) daysTogether = 0;
    }

    return res.json({
      name,
      birthday,
      partnerBirthday,
      startDate,
      daysTogether,
      photoURL,
    });
  } catch (e) {
    console.error(e);
    return res.status(500).json({ message: 'Internal server error' });
  }
}
