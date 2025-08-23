import { Router } from 'express';
import authRoute from './authRoutes.js';
import aiRoutes from './aiRoutes.js';
import uploadRoutes from './uploadRoutes.js';
import homeRoutes from './homeRoutes.js';
import profileRoutes from './profileRoutes.js';

const router = Router();

router.get('/health', (req, res) => res.json({ ok: true, ts: Date.now() }));
router.use('/user', authRoute);
router.use('/ai', aiRoutes);
router.use('/user/upload', uploadRoutes);
router.use('/home', homeRoutes);
router.use('/profile', profileRoutes);

export default router;