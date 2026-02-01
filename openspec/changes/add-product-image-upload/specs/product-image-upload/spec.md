## ADDED Requirements

### Requirement: 上傳商品圖片

The system SHALL allow authorized users to upload product images. 系統必須允許授權使用者上傳商品圖片。

#### Scenario: 成功上傳單張圖片

- **WHEN** 授權使用者在 admin 介面選擇一張有效的圖片檔案並提交
- **THEN** 系統必須儲存圖片檔案、產生縮圖，並顯示成功訊息

#### Scenario: 成功上傳多張圖片

- **WHEN** 授權使用者一次選擇多張有效的圖片檔案並提交
- **THEN** 系統必須儲存所有圖片檔案、為每張圖片產生縮圖，並顯示成功訊息

#### Scenario: 圖片檔案類型驗證

- **WHEN** 使用者嘗試上傳非圖片檔案（如 .txt、.pdf）
- **THEN** 系統必須拒絕上傳並顯示錯誤訊息「僅支援圖片格式：JPG, JPEG, PNG, WEBP」

#### Scenario: 圖片副檔名偽裝檢查

- **WHEN** 使用者上傳副檔名為 .jpg 但實際內容為非圖片檔案
- **THEN** 系統必須檢測真實檔案格式並拒絕上傳，顯示錯誤訊息

#### Scenario: 圖片檔案大小限制

- **WHEN** 使用者嘗試上傳超過 5MB 的圖片檔案
- **THEN** 系統必須拒絕上傳並顯示錯誤訊息「圖片檔案大小不可超過 5MB」

#### Scenario: 圖片尺寸限制

- **WHEN** 使用者上傳尺寸超過 4000x4000 像素的圖片
- **THEN** 系統必須拒絕上傳並顯示錯誤訊息「圖片尺寸不可超過 4000x4000 像素」

### Requirement: 產生圖片縮圖

The system SHALL automatically generate thumbnails when images are uploaded. 系統必須在圖片上傳時自動產生縮圖。

#### Scenario: 產生列表頁縮圖

- **WHEN** 商品圖片上傳成功後
- **THEN** 系統必須自動產生 150x150 像素的正方形縮圖，用於列表頁顯示

#### Scenario: 產生詳細頁預覽圖

- **WHEN** 商品圖片上傳成功後
- **THEN** 系統必須自動產生最大 800x800 像素的預覽圖（保持原始長寬比），用於詳細頁顯示

#### Scenario: 縮圖儲存路徑

- **WHEN** 系統產生縮圖
- **THEN** 縮圖必須儲存在 `media/products/<product_id>/thumbs/` 目錄下

#### Scenario: 縮圖格式與品質

- **WHEN** 系統產生 JPEG 格式的縮圖
- **THEN** 系統必須使用 85% 的品質設定以平衡檔案大小與視覺品質

### Requirement: 管理商品圖片

The system SHALL provide functionality to manage product images including ordering and deletion. 系統必須提供管理商品圖片的功能，包含排序和刪除。

#### Scenario: 設定主要商品圖片

- **WHEN** 使用者標記某張圖片為主圖（isPrimary = True）
- **THEN** 系統必須將該圖片設為主圖，並自動取消其他圖片的主圖狀態

#### Scenario: 調整圖片顯示順序

- **WHEN** 使用者修改圖片的 displayOrder 欄位
- **THEN** 系統必須按照 displayOrder 數值由小到大排序圖片

#### Scenario: 刪除商品圖片

- **WHEN** 使用者刪除商品圖片記錄
- **THEN** 系統必須同時刪除原始圖片檔案和所有縮圖檔案

#### Scenario: 刪除商品時清理圖片

- **WHEN** 商品被刪除
- **THEN** 系統必須級聯刪除該商品的所有圖片記錄及實體檔案

### Requirement: Admin 介面圖片管理

The system SHALL provide an admin interface for managing product images. 系統必須提供 admin 介面以管理商品圖片。

#### Scenario: 在商品編輯頁顯示圖片管理區塊

- **WHEN** 使用者在 admin 介面編輯商品
- **THEN** 系統必須在同一頁面顯示該商品的所有圖片，並提供上傳、刪除和排序功能

#### Scenario: 顯示圖片縮圖預覽

- **WHEN** 使用者檢視商品圖片列表
- **THEN** 系統必須顯示每張圖片的 150x150 縮圖預覽

#### Scenario: 顯示圖片詳細資訊

- **WHEN** 使用者檢視商品圖片列表
- **THEN** 系統必須顯示每張圖片的檔案名稱、檔案大小、上傳時間和主圖標記

#### Scenario: 拖曳排序圖片

- **WHEN** 使用者在 admin 介面拖曳圖片以調整順序
- **THEN** 系統必須更新圖片的 displayOrder 欄位以反映新順序

### Requirement: 圖片檔案命名與儲存

The system SHALL use a structured file naming and storage strategy. 系統必須使用結構化的檔案命名與儲存策略。

#### Scenario: 產生唯一檔案名稱

- **WHEN** 系統儲存上傳的圖片
- **THEN** 系統必須使用 UUID 前綴與原始檔名組合，避免檔名衝突

#### Scenario: 按商品 ID 組織檔案

- **WHEN** 系統儲存商品圖片
- **THEN** 圖片必須儲存在 `media/products/<product_id>/` 目錄下

#### Scenario: 保留原始副檔名

- **WHEN** 系統儲存圖片檔案
- **THEN** 系統必須保留原始副檔名（.jpg, .jpeg, .png, .webp）以維持相容性

### Requirement: 圖片安全性檢查

The system SHALL perform security checks on uploaded images. 系統必須對上傳的圖片執行安全性檢查。

#### Scenario: 驗證圖片真實格式

- **WHEN** 圖片上傳時
- **THEN** 系統必須使用 Pillow 開啟圖片以驗證其為有效的圖片格式

#### Scenario: 防止上傳可執行檔案

- **WHEN** 使用者嘗試上傳副檔名為圖片但內容為可執行檔案
- **THEN** 系統必須檢測並拒絕上傳，顯示安全錯誤訊息

#### Scenario: 清理圖片 EXIF 資料（可選）

- **WHEN** 圖片包含敏感的 EXIF 資料（GPS 位置、相機資訊）
- **THEN** 系統可選擇性地移除 EXIF 資料以保護使用者隱私

### Requirement: 開發環境媒體檔案服務

The system SHALL serve media files in development environment. 系統必須在開發環境中提供媒體檔案服務。

#### Scenario: 設定 MEDIA_ROOT 和 MEDIA_URL

- **WHEN** 專案啟動
- **THEN** 系統必須在 settings.py 設定 MEDIA_ROOT 指向 `media/` 目錄，MEDIA_URL 設定為 `/media/`

#### Scenario: 開發環境提供媒體檔案

- **WHEN** 在開發模式（DEBUG=True）下執行
- **THEN** Django 必須透過 URL 路由提供 `/media/` 路徑下的檔案存取

#### Scenario: 生產環境不提供媒體檔案

- **WHEN** 在生產模式（DEBUG=False）下執行
- **THEN** Django 不應提供媒體檔案服務，需由 Nginx 或 CDN 處理
