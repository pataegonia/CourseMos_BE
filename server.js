import 'dotenv/config.js';
import app from './app.js';

const PORT = process.env.PORT || 4000;
app.listen(PORT, () =>{
    console.log(`http://localhost:${PORT}`);
// 루트 경로 기본 응답
app.get('/', (req, res) => {
    res.send('Server is running!');
});
});
