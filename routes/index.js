import { Router } from 'express';
import authRoute from './authRoutes.js';
import uploadRoutes from './uploadRoutes.js';

const router = Router();

router.get('/health', (req, res) => res.json({ ok: true, ts: Date.now() }));
router.use('/user', authRoute);
router.use('/', uploadRoutes);

export default router;