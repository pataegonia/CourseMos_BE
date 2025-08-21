// AI 추천 관련 컨트롤러
import axios from 'axios';
import { getFirestore } from 'firebase-admin/firestore';
const db = getFirestore();

export async function getRecommendations(req, res) {
  try {
    // 위치, 날짜, 시간 3가지 정보 받기
    const { location, date, time } = req.body;
    const response = await axios.post('http://localhost:5000/recommend', { location, date, time });
    const result = response.data;

    // Firebase에 저장 (change me: 컬렉션/문서 구조는 실제에 맞게 수정)
    await db.collection('recommendations').add({
      location,
      date,
      time,
      places: result.places,
      createdAt: new Date()
    });

    res.json(result);
  } catch (error) {
    res.status(500).json({ error: 'AI 추천 서버 오류' });
  }
}
