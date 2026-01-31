# 1. 選擇基礎鏡像
FROM python:3.12-slim

# 2. 設定工作目錄
WORKDIR /app

# Prevent Python from writing pyc files and enable unbuffered stdout/stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# 3. 安裝 uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 4. 複製專案設定檔 (先複製這些可以利用 Docker 快取)
COPY pyproject.toml uv.lock ./

# 5. 安裝依賴項目
RUN uv sync --frozen --no-install-project

# 6. 複製其餘程式碼
COPY . .

# 7. 再次同步 (確保專案本身也被安裝)
RUN uv sync --frozen

# 8. 設定生產環境指令
# 不加 --reload，並監聽 0.0.0.0
# 使用非 root 使用者執行以提高安全性
RUN adduser --disabled-password --gecos "" appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
# 預設命令：啟動 uvicorn。docker-compose 或 docker run 可以以 command/--entrypoint 覆蓋此命令。
CMD ["uv", "run", "uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000"]