# Node.js 20のベースイメージを使用
FROM node:20-alpine

# 作業ディレクトリを設定
WORKDIR /app

# package.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# 依存関係をインストール
RUN npm ci

# アプリケーションコードをコピー
COPY . .

# ポート5173を公開（Viteのデフォルトポート）
EXPOSE 5173

# 開発サーバーを起動（ポート5173、全てのホストからアクセス可能）
CMD ["npm", "run", "dev"]
