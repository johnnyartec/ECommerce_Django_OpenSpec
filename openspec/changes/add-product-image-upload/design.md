## Context

目前 Product 模型只支援文字資料（productName, description, price, stockQuantity），缺少圖片管理功能。此設計文件說明如何在現有架構中整合圖片上傳和管理功能。

**現有架構：**

- Django 6.x 專案，使用 SQLite (開發) / PostgreSQL (生產)
- Product 模型位於 `todolist_app/models.py`
- 已有 XSS 防護機制（使用 bleach 清理 description 欄位）
- 已有完整的 Admin 介面和權限控制
- 已有測試框架（單元測試和整合測試）

**限制條件：**

- 遵循專案駝峰式命名慣例（camelCase）
- 需保持與現有 Product 功能的相容性
- 需符合安全最佳實踐（檔案驗證、類型檢查）

## Goals / Non-Goals

**Goals:**

- 在 Product 模型新增圖片欄位，支援多張圖片上傳
- 實作完整的圖片驗證（檔案類型、大小、安全性）
- 自動產生縮圖以提升效能
- 整合 Admin 介面提供友善的圖片管理體驗
- 確保圖片上傳功能有完整的測試覆蓋
- 設定開發環境的媒體檔案服務

**Non-Goals:**

- 不實作前端商品展示頁面（僅 Admin 管理功能）
- 不實作雲端儲存整合（S3, Azure Blob）- 保留為未來擴充
- 不實作圖片編輯功能（裁切、旋轉、濾鏡）
- 不實作圖片 CDN 整合

## Decisions

### 決策 1: 使用獨立的 ProductImage 模型 vs. 單一 ImageField

**選擇：建立獨立的 ProductImage 模型（一對多關係）**

**理由：**

- 支援多張圖片上傳（商品可能需要多角度照片）
- 可為每張圖片增加額外屬性（排序、alt 文字、是否為主圖）
- 易於擴充（未來可加入圖片標籤、說明等）
- 刪除商品時可輕鬆級聯刪除所有圖片

**替代方案：**

- 單一 ImageField：僅支援一張圖片，無法滿足多圖需求
- JSONField 儲存圖片路徑陣列：難以管理檔案生命週期，缺少 Django ORM 優勢

### 決策 2: 縮圖產生策略

**選擇：在 save() 方法中同步產生縮圖**

**理由：**

- 簡單直接，無需額外的背景任務系統
- 適合開發階段和小規模應用
- 確保縮圖在儲存後立即可用
- 使用 Pillow 的高效能 API

**替代方案：**

- 非同步任務（Celery）：對目前專案規模過於複雜
- 即時產生（on-the-fly）：增加每次請求的延遲

**縮圖規格：**

- 列表頁縮圖：150x150px（正方形，裁切）
- 詳細頁預覽：800x800px（保持比例）

### 決策 3: 檔案命名和儲存路徑

**選擇：使用 upload_to 函式動態產生路徑**

**理由：**

- 避免檔名衝突（加入 UUID）
- 組織結構清晰（依商品 ID 分組）
- 保留原始副檔名以保持相容性

**路徑格式：**

```
media/
  products/
    <product_id>/
      <uuid>_<original_name>.jpg
      thumbs/
        <uuid>_<original_name>_150x150.jpg
        <uuid>_<original_name>_800x800.jpg
```

### 決策 4: 圖片驗證機制

**選擇：多層驗證策略**

1. **檔案類型驗證**：使用 `FileExtensionValidator` 限制為 jpg, jpeg, png, webp
2. **檔案大小限制**：最大 5MB（在模型和 Admin 設定中強制）
3. **真實格式檢查**：使用 Pillow 開啟圖片驗證真實格式（防止副檔名偽裝）
4. **圖片內容驗證**：檢查圖片尺寸限制（最大 4000x4000px）

**理由：**

- 多層防護確保安全性
- 防止上傳非圖片檔案或惡意檔案
- 限制儲存空間使用

### 決策 5: Admin 介面整合

**選擇：使用 TabularInline 顯示圖片列表**

**理由：**

- 在商品編輯頁面直接管理圖片，UX 流暢
- 支援拖曳排序（使用 ordering 欄位）
- 可預覽縮圖並提供刪除功能
- 符合 Django Admin 最佳實踐

**功能：**

- 圖片上傳表單（支援多檔案上傳）
- 縮圖預覽（使用自訂 admin 方法）
- 排序控制（displayOrder 欄位）
- 主圖標記（isPrimary 欄位）

## Risks / Trade-offs

### 風險 1: 同步縮圖產生可能影響回應時間

**風險描述：**
在 save() 中同步產生縮圖可能導致大圖片上傳時回應變慢（特別是上傳多張圖片時）。

**緩解措施：**

- 限制圖片檔案大小為 5MB
- 使用 Pillow 的高效壓縮演算法
- 未來如需優化，可改為非同步處理（Celery）

**監控指標：**

- 上傳回應時間 > 5 秒時需要評估優化

### 風險 2: 磁碟空間管理

**風險描述：**
隨著商品和圖片增加，媒體檔案會佔用大量磁碟空間。刪除商品時需確保清理圖片檔案。

**緩解措施：**

- 覆寫 ProductImage.delete() 方法確保刪除實體檔案
- 使用 Django signals (post_delete) 清理孤立檔案
- 定期備份媒體檔案目錄
- 文件化手動清理指令（`python manage.py clean_orphan_media`）

### 風險 3: 生產環境媒體檔案服務

**風險描述：**
Django 不應在生產環境直接服務媒體檔案，需要 Nginx 或 CDN。

**緩解措施：**

- 在文件中明確說明生產部署需求
- 提供 Nginx 設定範例
- 為未來 S3 整合預留擴充點（使用 django-storages）

### Trade-off: 儲存空間 vs. 效能

選擇預先產生多種尺寸的縮圖會增加儲存空間使用（每張原圖產生 2 張縮圖），但換取更快的頁面載入速度。這個 trade-off 對電商應用是值得的，因為圖片載入速度直接影響使用者體驗。

## Migration Plan

### 第一階段：模型和儲存設定

1. 安裝 Pillow：`uv add Pillow`
2. 設定 `settings.py` 的 MEDIA_ROOT 和 MEDIA_URL
3. 建立 ProductImage 模型
4. 執行 makemigrations 和 migrate
5. 設定開發環境 URL 以服務媒體檔案

### 第二階段：Admin 整合

1. 建立 ProductImageInline
2. 更新 ProductAdmin 整合 inline
3. 新增縮圖預覽方法
4. 測試圖片上傳和預覽功能

### 第三階段：測試

1. 建立單元測試（檔案驗證、縮圖產生）
2. 建立整合測試（Admin 介面上傳流程）
3. 手動測試各種圖片格式和大小

### Rollback 策略

如果需要回滾：

1. 移除 ProductImage 模型的 migration
2. 恢復 Admin 設定
3. 清理測試上傳的媒體檔案
4. 解除安裝 Pillow（如不再需要）

## Open Questions

1. **是否需要浮水印功能？** - 目前未規劃，如需要可在縮圖產生時加入
2. **圖片壓縮品質設定？** - 建議 JPEG 品質 85，需要實測找出最佳平衡點
3. **是否限制每個商品的圖片數量？** - 建議限制為 10 張，可在 Admin 表單驗證
4. **刪除商品時的圖片清理策略？** - 建議使用 CASCADE 級聯刪除 + signal 清理實體檔案
