import express from 'express';
import { getRecommendations } from '../controllers/aiController.js';

const router = express.Router();

router.post('/recommend', getRecommendations);

export default router;
