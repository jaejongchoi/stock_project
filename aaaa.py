# Git 초기화 (처음 한 번만 실행)
git init
git add .
git commit -m "FastAPI 클라우드 배포"

# GitHub에 업로드 (본인 GitHub 저장소 연결 필요)
git remote add origin https://github.com/사용자명/저장소명.git
git branch -M main
git push -u origin main
