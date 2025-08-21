# FastAPI 서버 AWS EC2 배포 방법

## 1. EC2 인스턴스 준비
- Amazon Linux 2 또는 Ubuntu로 EC2 인스턴스 생성
- 보안 그룹에서 5000번 포트 인바운드 허용

## 2. 서버 환경 준비
- Python 3.8 이상 설치
- git, pip, virtualenv 설치

## 3. 코드 배포 및 환경설정
- EC2에 SSH로 접속 후, 프로젝트를 git clone 또는 파일 업로드
- 프로젝트 루트에 .env 파일 배치
- `python_ai_server` 폴더에 requirements.txt 존재

## 4. 실행 방법
```bash
bash run.sh
```
또는 직접 실행:
```bash
cd python_ai_server
uvicorn app:app --host 0.0.0.0 --port 5000
```

## 5. 백그라운드 실행 (선택)
```bash
nohup uvicorn app:app --host 0.0.0.0 --port 5000 &
```

## 6. 외부 접속 테스트
- EC2 퍼블릭 IP:5000 으로 접속

## 7. 기타
- 필요시 Nginx 등 Reverse Proxy 설정
