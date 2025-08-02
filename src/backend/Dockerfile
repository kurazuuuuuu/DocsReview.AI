# Python 3.12のベースイメージを使用
FROM python:3.12-slim

# 作業ディレクトリを設定
WORKDIR /app

# uvをインストール
RUN pip install uv

# プロジェクトファイルをコピー
COPY pyproject.toml uv.lock ./

# 依存関係をインストール
RUN uv sync --frozen

# アプリケーションコードをコピー
COPY . .

# ポート8000を公開
EXPOSE 8000

# FastAPIアプリケーションを起動
CMD ["uv", "run", "fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "8000"]
