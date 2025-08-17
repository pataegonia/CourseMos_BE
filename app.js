import express from 'express';
import morgan from 'morgan';
import cors from 'cors';
import './config/firebase.js';
import api from './routes/index.js'

const app =  express();
app.use(cors());
app.use(express.json());
app.use(morgan('dev'));

app.use('/api', api);

export default app;