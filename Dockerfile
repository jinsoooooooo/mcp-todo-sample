FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .

# 시스템 패키지 업데이트 및 필수 패키지 설치 
RUN apt-get update && apt-get install -y \
    --no-install-recomends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# requirements.txt 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY src/ ./src/
# EXPOSE 8080
# CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8080"]
# 파이썬(main.py) 안에서 settings.APP_HOST, APP_PORT를 실행 시킴으로써 Dockerfile을 유연하게 만듭니다.

# 비 root 사용자 생성 및 전환 (보안)
RUN adduser -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# 헬스 체크
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8082"] 
