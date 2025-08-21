import express from 'express';
import { getRecommendations } from '../controllers/aiController.js';

const router = express.Router();


/**
 * @swagger
 * /api/ai/recommend:
 *   post:
 *     summary: AI 추천 장소 리스트 반환
 *     description: 위치, 날짜, 시간 정보를 받아 AI가 추천 장소 리스트를 반환합니다.
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               location:
 *                 type: string
 *                 example: 서울 강남역
 *               date:
 *                 type: string
 *                 example: 2025-08-17
 *               time:
 *                 type: string
 *                 example: 15:00
 *     responses:
 *       200:
 *         description: 추천 장소 리스트
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 places:
 *                   type: array
 *                   items:
 *                     type: object
 *                     properties:
 *                       name:
 *                         type: string
 *                         example: 스타벅스 강남역점
 *                       desc:
 *                         type: string
 *                         example: 커피와 대화를 즐길 수 있는 분위기 좋은 카페
 *       500:
 *         description: AI 추천 서버 오류
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 error:
 *                   type: string
 *                   example: AI 추천 서버 오류
 */
router.post('/recommend', getRecommendations);

export default router;
