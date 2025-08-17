import { Router } from 'express';
import { signIn, login } from '../controllers/authController.js';
const router = Router();

router.post('/signIn', signIn); // 회원가입
router.post('/login', login);   // 로그인(토큰 발급)

export default router;
