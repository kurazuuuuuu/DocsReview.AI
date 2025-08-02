# Backend
## エンドポイントURL
- `https://docsreview-ai.krz-tech.net/api`

## API
- AI機能 `POST /api/ai`
    - AI機能呼び出し用エンドポイント
    - ai_modeの内容によって機能を切り替える
    - `ai_mode` : レビュー、ファクトチェック、要約、添削、追加の各要求
    - REQUEST `content` : 処理してほしい文章
    - RESPONSE `response_content` : 処理後の文章
```
    POST Requset
    {
        "ai": {
            "ai_mode": "review | factcheck | summary | collection | addiction",
            "content": "ここに文章を入力"
        }
    }

    POST Response
    {
        "ai": {
            "ai_mode": "review | factcheck | summary | collection | addiction",
            "response_content": "ここに文章を入力"
        }
    }
```
- バックエンド状態確認 `GET /api/stats`
    - AIサービス接続状況を確認できる
```
    GET Response
    {
        "status": {
            "google_gemini": True | False,
            "local_llm": True | False #Optional
        }
    }
```