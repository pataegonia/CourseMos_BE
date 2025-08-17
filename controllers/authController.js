import fetch from 'node-fetch';
import Joi from 'joi';
import { firestore } from '../config/firebase.js';

const API_KEY = process.env.FIREBASE_WEB_API_KEY;
const usersCol = firestore.collection('users');

const SignInSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().min(8).max(72).required(),
  // 가입 시 함께 저장할 프로필
  name: Joi.string().min(1).max(50).required(),
  birthday: Joi.string().isoDate().required(),
  partnerBirthday: Joi.string().isoDate().required(),
  startDate: Joi.string().isoDate().required()
});

const LoginSchema = Joi.object({
  email: Joi.string().email().required(),
  password: Joi.string().required()
});

/** 회원가입: Firebase Auth 계정 생성 + Firestore 프로필 저장 */
export async function signIn(req, res) {
  const { error, value } = SignInSchema.validate(req.body);
  if (error) return res.status(400).json({ message: error.message });

  const { email, password, name, birthday, partnerBirthday, startDate } = value;

  // 1) Firebase Auth 계정 생성
  const signUpUrl = `https://identitytoolkit.googleapis.com/v1/accounts:signUp?key=${API_KEY}`;
  const r = await fetch(signUpUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, returnSecureToken: true })
  });
  const data = await r.json();
  if (!r.ok) {
    return res.status(400).json({ message: '회원가입 실패', detail: data.error?.message || data });
  }

  const { localId: uid, idToken } = data;

  // 2) 프로필 저장
  await usersCol.doc(uid).set({
    uid, email, name, birthday, partnerBirthday, startDate,
    createdAt: new Date(), updatedAt: new Date()
  });

  // 3) 토큰 반환
  return res.status(201).json({
    token: idToken,
    user: { uid, email, name, birthday, partnerBirthday, startDate }
  });
}

/** 로그인: 이메일/비번으로 ID 토큰 발급 */
export async function login(req, res) {
  const { error, value } = LoginSchema.validate(req.body);
  if (error) return res.status(400).json({ message: error.message });

  const { email, password } = value;

  const signInUrl = `https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=${API_KEY}`;
  const r = await fetch(signInUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, password, returnSecureToken: true })
  });
  const data = await r.json();
  if (!r.ok) {
    return res.status(401).json({ message: '로그인 실패', detail: data.error?.message || data });
  }

  // 프로필 없으면 최소 생성
  const uid = data.localId;
  const ref = usersCol.doc(uid);
  const doc = await ref.get();
  if (!doc.exists) {
    await ref.set({ uid, email, createdAt: new Date(), updatedAt: new Date() });
  }

  return res.json({
    token: data.idToken,
    refreshToken: data.refreshToken,
    expiresIn: data.expiresIn
  });
}
