import { Router } from 'express';
import { verifyFirebaseIdToken } from '../middlewares/auth.js';
import { getHome } from '../controllers/homeController.js';

const router = Router();

// GET /api/home
router.get('/', verifyFirebaseIdToken, getHome);

export default router;
