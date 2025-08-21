import express from 'express';
import morgan from 'morgan';
import cors from 'cors';
import './config/firebase.js';
import api from './routes/index.js';
import swaggerJsdoc from 'swagger-jsdoc';
import swaggerUi from 'swagger-ui-express';

const app = express();
app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

const swaggerOptions = {
	definition: {
		openapi: '3.0.0',
		info: {
			title: 'CourseMos_BE API',
			version: '1.0.0',
			description: 'AI 추천 및 인증 API 명세서',
		},
		servers: [
			{ url: 'http://localhost:4000' }
		],
	},
	apis: ['./routes/aiRoutes.js'], // AI 추천 API 명세 주석 위치
};

const swaggerSpec = swaggerJsdoc(swaggerOptions);
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

app.use('/api', api);

export default app;