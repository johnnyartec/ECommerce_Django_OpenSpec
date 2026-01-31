# ECOMMERCE — 使用 Django + OpenSpec 的範例專案

## 簡介

這是一個使用 Django 建立的範例專案，包含：

- **待辦清單（Todo）**：使用者可管理個人待辦事項
- **部落格（Blog）**：支援 Markdown 撰寫、草稿管理與發佈功能
- **商品管理（Product）**：後台商品 CRUD 管理系統
- **使用者認證**：註冊、登入與權限控制

此專案適合作為學習 Django 專案結構、表單、使用者認證、內容管理與後台管理的起點。

## 功能特色

### 🎯 待辦清單 (Todo)

- 建立、完成、刪除待辦事項
- 使用者隔離（每個使用者只能看到自己的待辦）

### 📝 部落格系統 (Blog)

- **Markdown 編輯**：使用 CommonMark 規範撰寫文章
- **草稿與發佈**：支援草稿儲存，發佈後公開存取
- **安全防護**：自動清理 HTML 防止 XSS 攻擊
- **權限控制**：僅作者可編輯自己的文章
- **SEO 友善**：永久 slug URL、metadata 支援
- **測試覆蓋**：14 個單元與整合測試（100% 通過）

### 🛍️ 商品管理系統 (Product)

- **完整 CRUD 功能**：建立、檢視、更新、刪除商品
- **資料驗證**：商品名稱、價格、庫存的完整驗證
- **軟刪除**：透過 isActive 欄位標記商品狀態
- **XSS 防護**：商品描述欄位自動清理危險 HTML
- **Admin 整合**：完整的 Django Admin 後台管理介面
- **權限控制**：僅授權使用者可管理商品
- **時間戳記**：自動記錄建立與更新時間

## 需求

- Python 3.12+
- Django 6.x
- markdown, bleach（Blog 功能）

## 快速開始（本機開發）

1. **安裝相依套件**（使用 `uv` 工具）：

   ```powershell
   uv sync
   ```

   如果需要手動安裝 Blog 相關套件：

   ```powershell
   uv add markdown bleach
   ```

2. **啟用虛擬環境**：
   - Windows (PowerShell)：

     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```

   - macOS/Linux (bash/zsh):

     ```bash
     source .venv/bin/activate
     ```

3. **建立資料庫遷移並套用**：

   ```powershell
   python manage.py migrate
   ```

4. **建立管理者帳號**：

   ```powershell
   python manage.py createsuperuser
   ```

5. **啟動開發伺服器**：

   ```powershell
   python manage.py runserver
   ```

   或使用 ASGI 伺服器 `uvicorn`：

   ```powershell
   python -m uvicorn config.asgi:application --reload
   ```

6. **訪問應用**：
   - 待辦清單：http://localhost:8000/app/hello/
   - 部落格列表：http://localhost:8000/app/blog/
   - 管理後台：http://localhost:8000/admin/
     - 可在後台管理商品、文章、使用者等資料

## 部落格功能快速指南

詳細說明請參考：[docs/spec/quickstart-blog.md](docs/spec/quickstart-blog.md)

### 主要 URL

| 功能     | URL                      | 說明           |
| -------- | ------------------------ | -------------- |
| 文章列表 | `/app/blog/`             | 公開已發佈文章 |
| 新增文章 | `/app/blog/new/`         | 需登入         |
| 我的草稿 | `/app/blog/drafts/`      | 需登入         |
| 文章細節 | `/app/blog/<slug>/`      | 公開閱讀       |
| 編輯文章 | `/app/blog/<slug>/edit/` | 需作者權限     |

### 測試 Markdown

文章支援完整的 Markdown 語法：

```markdown
# 標題

**粗體** _斜體_

- 清單項目

1. 編號清單

[連結](https://example.com)

\`\`\`python
print("程式碼區塊")
\`\`\`
```

## 主要檔案與目錄

````
FirstTest/
├── config/              # Django 專案設定
│   ├── settings.py      # 主要設定檔
│   ├── urls.py          # 根 URL 配置
│   ├── wsgi.py / asgi.py
├── todolist_app/        # 主應用程式
│   ├── models.py        # 資料模型（Todo, BlogPost, Product）
│   ├── views.py         # 視圖邏輯
│   ├── forms.py         # 表單定義
│   ├── urls.py          # 應用 URL 配置
│   ├── admin.py         # Admin 設定（Blog & Product）
│   ├── utils/           # 工具函式
│   │   └── markdown_renderer.py  # Markdown 渲染器
│   └── templates/       # 模板
│       ├── base.html
│       ├── blog/        # 部落格相關模板
│       └── registration/  # 認證相關模板
├── openspec/            # OpenSpec 變更管理
│   ├── changes/         # 變更記錄與規格
│   └── specs/           # 功能規格文件
├── docs/                # 專案文件
│   └── spec/            # 技術規格與實作文件
├── static/              # 靜態檔案
├── db.sqlite3           # SQLite 資料庫
└── manage.py            # Django 管理指令
│ 所有測試：

```powershell
python manage.py test todolist_app.tests -v 2
````

測試統計：

- **總測試數**: 14
- **模型測試**: 7（slug 生成、狀態轉換、Markdown 渲染）
- **整合測試**: 7（完整流程、權限、XSS 防護）
- **成功率**: 100%

執行特定測試：

````powershell
# 僅模型測試
python manage.py test todolist_app.tests.test_models

# 僅整合測試
python manage.py test todolist_app.tests.test_integrationgration.py
│   └── templates/       # 模板
│       ├── base.html
│    文件

- [實作計畫](docs/spec/plan.md) - 技術架構與開發階段
- [任務清單](docs/spec/tasks.md) - 詳細任務拆解
- [快速啟動](docs/spec/quickstart-blog.md) - Blog 功能詳細指南
- [Phase 3 完成報告](docs/spec/phase3-completion-report.md) - 實作摘要
- [資料模型](specs/1-add-blog/data-model.md) - 資料庫設計
- [API 契約](specs/1-add-blog/contracts.md) - 路由與回應規範

## 部署準備

生產環境部署前請確保：

1. **安全設定**：
   - 設定 `DEBUG=False`
   - 更換 `SECRET_KEY`
   - 設定正確的 `ALLOWED_HOSTS`

2. **資料庫**：
   - 從 SQLite 遷移至 PostgreSQL
   - 執行所有遷移

3. **靜態檔案**：
   ```powershell
   python manage.py collectstatic
````

4. **環境變數**：
   - 使用 `.env.production` 管理敏感設定
   - 參考 `env_utility.py` 載入環境變數

詳細部署指南請參考 [docs/spec/plan.md](docs/spec/plan.md) Phase 6。

## 開發與貢獻

- 使用專案憲法規範（`.specify/memory/constitution.md`）
- 駝峰式命名、繁體中文註解
- 所有新功能需附測試
- 建議在功能開發前建立新的分支

## 測試

執行 Django 測試：

```powershell
python manage.py test
```

## 開發與貢獻

- 建議在功能開發前建立新的分支。
- 寫入簡短明確的 commit 訊息。

## 其他說明

如果需要將專案部署到生產環境，請調整 `settings.py` 中的 `DEBUG`、`ALLOWED_HOSTS`、資料庫設定與靜態檔（static）/媒體檔（media）設定。務必更換 `SECRET_KEY`、設定 `DEBUG=False`，並設定靜態檔收集 (`collectstatic`) 與適當的靜態/媒體伺服器或 CDN。

## 使用 .env 管理不同環境

專案支援以 .env 檔管理設定值，並可依 ENVIRONMENT 變數載入對應的 .env.{ENVIRONMENT}，後者會覆蓋 base .env 的值。專案提供 env_utility.py 來自動載入與轉換型別（env_get, env_bool, env_int, env_list）。範例：

1. 在專案根目錄建立 .env（通用設定）與 .env.production（生產覆蓋設定），例如：

   .env

   ```
   ENVIRONMENT=development
   DJANGO_DEBUG=True
   DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost
   DB_PORT=5432
   ```

   .env.production

   ```
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=example.com
   DB_PORT=5432
   ```

2. settings.py 頂端使用：

   from env_utility import load_env, env_bool, env_get
   load_env(BASE_DIR)

3. settings.py 使用範例：

   SECRET_KEY = env_get('DJANGO_SECRET_KEY', 'django-insecure-default-key')
   DEBUG = env_bool('DJANGO_DEBUG', True)

## 聯絡

如需協助或有問題，請在專案中提出 Issue。
