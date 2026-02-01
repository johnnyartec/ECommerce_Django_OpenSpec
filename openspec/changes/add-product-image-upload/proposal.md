## Why

目前商品管理系統只能儲存文字資訊（名稱、描述、價格、庫存），缺少商品圖片功能。商品圖片對於電商應用至關重要，能讓使用者更直觀地了解商品，提升使用者體驗和轉換率。

## What Changes

- 在 Product 模型新增圖片欄位，支援單張或多張商品圖片上傳
- 實作圖片上傳驗證（檔案類型、大小限制）
- 整合 Django Admin 介面，提供商品圖片上傳和預覽功能
- 設定媒體檔案儲存（MEDIA_ROOT 和 MEDIA_URL）
- 新增圖片處理功能（自動產生縮圖、最佳化檔案大小）
- 實作圖片安全檢查（防止上傳惡意檔案）
- 更新測試覆蓋圖片上傳和處理功能

## Capabilities

### New Capabilities

- `product-image-upload`: 商品圖片上傳與管理功能，包含檔案驗證、儲存、縮圖產生和安全檢查

### Modified Capabilities

- `product-management`: 在商品管理功能中新增圖片欄位、Admin 介面顯示圖片預覽、列表頁顯示縮圖

## Impact

**受影響的程式碼：**

- `todolist_app/models.py` - Product 模型新增 ImageField 或相關欄位
- `todolist_app/admin.py` - ProductAdmin 新增圖片上傳和預覽功能
- `config/settings.py` - 設定 MEDIA_ROOT、MEDIA_URL、檔案上傳設定
- `config/urls.py` - 開發環境下提供媒體檔案服務
- `todolist_app/tests/test_product.py` - 新增圖片上傳測試

**新增相依套件：**

- Pillow - Python 圖片處理函式庫（用於圖片驗證、縮圖產生、格式轉換）

**資料庫變更：**

- 需要建立新的 migration 以新增圖片相關欄位

**檔案系統：**

- 需要設定媒體檔案儲存目錄（預設為專案根目錄下的 `media/` 資料夾）
- 生產環境需要規劃媒體檔案的儲存策略（本機儲存、雲端儲存如 S3）
