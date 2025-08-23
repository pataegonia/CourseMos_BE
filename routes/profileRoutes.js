import { Router } from 'express';
import { verifyFirebaseIdToken } from '../middlewares/auth.js';
import { getMyPage } from '../controllers/profileController.js';

const router = Router();

// GET /api/mypage
router.get('/', verifyFirebaseIdToken, getMyPage);

export default router;
