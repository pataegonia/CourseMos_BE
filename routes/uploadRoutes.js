import { Router } from 'express';
import multer from 'multer';
import { verifyFirebaseIdToken } from '../middlewares/auth.js';
import { uploadProfilePhoto } from '../controllers/uploadController.js';

const router = Router();
const upload = multer({ storage: multer.memoryStorage(), limits: { fileSize: 5 * 1024 * 1024 } }); // 5MB

// 인증 필요, multipart/form-data 로 파일 전송 (field name = "file")
router.post('/uploadPhoto', verifyFirebaseIdToken, upload.single('file'), uploadProfilePhoto);

export default router;
