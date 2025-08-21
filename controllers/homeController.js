import { firestore } from '../config/firebase.js';

export async function getHome(req, res) {
  try {
    const uid = req.user.uid; // verifyFirebaseIdToken 미들웨어에서 세팅됨
    const userDoc = await firestore.collection('users').doc(uid).get();

    if (!userDoc.exists) {
      return res.status(404).json({ message: 'User not found' });
    }

    const { photoURL } = userDoc.data();

    return res.json({ photoURL });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ message: 'Internal server error' });
  }
}
