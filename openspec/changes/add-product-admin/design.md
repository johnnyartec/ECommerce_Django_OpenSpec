## Context

目前的 Django 應用程式已經有 Todo 和 Blog 功能，使用 PostgreSQL 作為資料庫。專案遵循 camelCase 命名慣例來命名模型欄位，並使用 Django 內建的認證和授權系統。需要新增商品管理功能以支援電商或庫存管理需求。

**現有架構**：

- Django 6.x + Python 3.12+
- PostgreSQL 資料庫
- Django Templates 進行前端渲染
- 模型欄位使用 camelCase 命名（專案慣例）
- 使用 Django admin 作為管理介面
- 已有使用者認證和權限系統

## Goals / Non-Goals

**Goals:**

- 建立 Product 模型並整合到現有的 todolist_app
- 在 Django admin 提供完整的商品 CRUD 管理介面
- 實作適當的權限控制，確保只有授權使用者可以管理商品
- 為商品描述欄位提供 XSS 防護
- 提供完整的單元測試和整合測試

**Non-Goals:**

- 不建立前端使用者介面（僅限 admin 後台）
- 不實作商品圖片上傳功能（可在後續階段加入）
- 不實作複雜的庫存管理邏輯（如批次進出貨）
- 不實作購物車或訂單系統

## Decisions

### 1. 模型設計

**決定**：在 `todolist_app/models.py` 新增 Product 模型，包含以下欄位：

- `productName`：商品名稱（CharField，最大長度 200，必填）
- `description`：商品描述（TextField，選填）
- `price`：價格（DecimalField，最大 10 位數，小數 2 位）
- `stockQuantity`：庫存數量（PositiveIntegerField，預設 0）
- `isActive`：是否啟用（BooleanField，預設 True）
- `createdAt`：建立時間（DateTimeField，自動設定）
- `updatedAt`：更新時間（DateTimeField，自動更新）

**理由**：

- 遵循專案的 camelCase 命名慣例
- 使用 DecimalField 確保價格計算精確度
- `isActive` 欄位允許軟刪除，保留歷史資料
- 時間戳記欄位方便追蹤資料變更

**替代方案**：

- 考慮過將商品分類（Category）一起實作，但為了簡化初期開發，決定先實作基本功能，分類功能可後續擴充

### 2. Django Admin 整合

**決定**：在 `todolist_app/admin.py` 註冊 Product 模型，並自訂 ModelAdmin：

- 設定 list_display 顯示關鍵欄位（名稱、價格、庫存、狀態）
- 加入 search_fields 支援名稱和描述搜尋
- 使用 list_filter 提供狀態篩選
- 設定 readonly_fields 讓時間戳記欄位唯讀

**理由**：

- Django admin 已經提供完整的 CRUD 功能，不需要自行開發
- 自訂 ModelAdmin 可提升管理介面的使用者體驗
- 搜尋和篩選功能可協助快速定位商品

**替代方案**：

- 考慮過使用第三方套件如 django-grappelli，但為保持簡潔，使用原生 Django admin

### 3. 權限控制

**決定**：使用 Django 內建的權限系統：

- 依賴 Django 自動為 Product 模型建立的權限（add_product, change_product, delete_product, view_product）
- 透過 Django admin 的 `has_*_permission` 方法控制存取
- 只有 staff 使用者可以存取 admin

**理由**：

- 利用現有的認證授權系統，無需額外開發
- Django admin 已整合權限檢查機制
- 符合專案現有的安全架構

### 4. XSS 防護

**決定**：對商品描述欄位套用 XSS 防護：

- 在儲存前使用 bleach 清理 HTML（如同 Blog 功能）
- 只允許安全的 HTML 標籤（如 `<p>`, `<br>`, `<strong>`, `<em>`）

**理由**：

- 與現有的 Blog 功能保持一致的安全標準
- 防止惡意腳本注入

### 5. 測試策略

**決定**：建立 `todolist_app/tests/test_product.py`，包含：

- 模型測試：驗證欄位驗證、預設值、字串表示
- Admin 測試：驗證 CRUD 操作、權限控制
- 整合測試：驗證完整的管理流程

**理由**：

- 確保功能正確性和穩定性
- 符合專案要求所有功能都要有測試

## Risks / Trade-offs

### 風險 1：資料遷移

- **風險**：新增 Product 模型需要執行資料庫遷移
- **緩解措施**：使用 Django migrations 確保遷移可逆，遷移前備份資料庫

### 風險 2：價格精確度

- **風險**：浮點數運算可能導致精確度問題
- **緩解措施**：使用 DecimalField 而非 FloatField，確保金額計算精確

### 風險 3：庫存數量為負

- **風險**：使用者可能輸入負數庫存
- **緩解措施**：使用 PositiveIntegerField 限制為非負整數

### 風險 4：XSS 攻擊

- **風險**：商品描述可能包含惡意腳本
- **緩解措施**：使用 bleach 清理 HTML 內容

### 取捨：簡化的商品模型

- **取捨**：目前的模型不包含商品分類、規格、圖片等進階功能
- **考量**：這是有意的設計決定，優先實作核心功能，進階功能可後續擴充，避免初期過度設計
