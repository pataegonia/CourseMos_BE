import { Router } from 'express';
import authRoute from './authRoutes.js';

const router = Router();

router.get('/health', (req, res) => res.json({ ok: true, ts: Date.now() }));
router.use('/user', authRoute);

export default router;