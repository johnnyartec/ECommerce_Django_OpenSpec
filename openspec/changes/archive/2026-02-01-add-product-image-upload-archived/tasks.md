```markdown
## 1. 安裝相依套件與環境設定

- [x] 1.1 安裝 Pillow 套件：執行 `uv add Pillow`
- [x] 1.2 在 `config/settings.py` 設定 MEDIA_ROOT（指向專案根目錄的 `media/` 資料夾）
- [x] 1.3 在 `config/settings.py` 設定 MEDIA_URL 為 `/media/`
- [x] 1.4 在 `config/settings.py` 設定 FILE_UPLOAD_MAX_MEMORY_SIZE（5MB 限制）
- [x] 1.5 在 `config/urls.py` 加入開發環境媒體檔案服務（僅在 DEBUG=True 時）
- [x] 1.6 建立 `media/products/` 目錄結構

## 2. 建立 ProductImage 模型

- [x] 2.1 在 `todolist_app/models.py` 建立 ProductImage 模型類別
- [x] 2.2 新增 product 欄位（ForeignKey 連結 Product，on_delete=CASCADE）
- [x] 2.3 新增 image 欄位（ImageField，upload_to 使用自訂函式）
- [x] 2.4 新增 thumbnail150 欄位（ImageField，儲存 150x150 縮圖）
- [x] 2.5 新增 thumbnail800 欄位（ImageField，儲存 800x800 縮圖）
- [x] 2.6 新增 isPrimary 欄位（BooleanField，預設 False，標記主圖）
- [x] 2.7 新增 displayOrder 欄位（PositiveIntegerField，預設 0，用於排序）
- [x] 2.8 新增 altText 欄位（CharField，選填，提供替代文字）
- [x] 2.9 新增 uploadedAt 欄位（DateTimeField，auto_now_add=True）
- [x] 2.10 實作 **str** 方法回傳商品名稱和圖片 ID
- [x] 2.11 加入 Meta 類別設定 ordering（按 displayOrder 和 uploadedAt 排序）

## 3. 實作檔案命名與路徑函式

- [x] 3.1 建立 upload_to 函式產生動態路徑（使用 UUID 和商品 ID）
- [x] 3.2 實作函式保留原始副檔名
- [x] 3.3 建立縮圖路徑函式（將縮圖存放在 `thumbs/` 子目錄）
- [x] 3.4 確保路徑格式為 `products/<product_id>/<uuid>_<filename>`

## 4. 實作圖片驗證

- [x] 4.1 建立自訂驗證器檢查檔案類型（僅允許 jpg, jpeg, png, webp）
- [x] 4.2 在 ProductImage 模型的 clean 方法中驗證檔案大小（最大 5MB）
- [x] 4.3 使用 Pillow 開啟圖片驗證真實格式（防止副檔名偽裝）
- [x] 4.4 驗證圖片尺寸不超過 4000x4000 像素
- [x] 4.5 在驗證失敗時拋出 ValidationError 並提供清楚的錯誤訊息

## 5. 實作縮圖產生功能

- [x] 5.1 在 ProductImage 模型建立 generate_thumbnails 方法
- [x] 5.2 使用 Pillow 產生 150x150 正方形縮圖（使用 LANCZOS 重採樣）
- [x] 5.3 使用 Pillow 產生 800x800 預覽圖（保持長寬比）
- [x] 5.4 設定 JPEG 品質為 85%
- [x] 5.5 將縮圖儲存到 thumbnail150 和 thumbnail800 欄位
- [x] 5.6 覆寫 save 方法在儲存時自動產生縮圖
- [x] 5.7 確保縮圖檔案儲存在 `thumbs/` 子目錄

## 6. 實作主圖邏輯

- [x] 6.1 建立 set_as_primary 方法設定圖片為主圖
- [x] 6.2 當設定主圖時，自動將同商品的其他圖片 isPrimary 設為 False
- [x] 6.3 在 save 方法中檢查 isPrimary 變更並執行主圖邏輯
- [x] 6.4 確保每個商品最多只有一張主圖

## 7. 實作檔案清理機制

- [x] 7.1 覆寫 ProductImage.delete 方法刪除實體圖片檔案
- [x] 7.2 刪除時同時移除原始圖片和所有縮圖檔案
- [x] 7.3 使用 Django signals (post_delete) 確保檔案清理
- [x] 7.4 處理檔案不存在的例外情況（避免刪除失敗）
- [x] 7.5 測試級聯刪除（刪除 Product 時清理所有圖片）

## 8. 建立資料庫遷移

- [x] 8.1 執行 `python manage.py makemigrations` 建立 ProductImage 模型的 migration
- [x] 8.2 檢查生成的 migration 檔案確保欄位設定正確
- [x] 8.3 執行 `python manage.py migrate` 套用資料庫變更
- [x] 8.4 驗證資料庫中 ProductImage 資料表已建立

## 9. 建立 Admin Inline

- [x] 9.1 在 `todolist_app/admin.py` 建立 ProductImageInline 類別（繼承 TabularInline）
- [x] 9.2 設定 model 為 ProductImage
- [x] 9.3 設定 extra = 1 允許新增一張圖片
- [x] 9.4 設定 fields 顯示 image, isPrimary, displayOrder, altText
- [x] 9.5 建立 image_preview 方法顯示縮圖預覽（使用 thumbnail150）
- [x] 9.6 設定 readonly_fields 包含 image_preview 和 uploadedAt
- [x] 9.7 使用 format_html 產生 HTML img 標籤顯示縮圖
- [x] 9.8 設定縮圖預覽大小為 100x100 像素

## 10. 更新 ProductAdmin

- [x] 10.1 在 ProductAdmin 類別加入 inlines = [ProductImageInline]
- [x] 10.2 建立 primary_image_preview 方法顯示主圖縮圖
- [x] 10.3 在 list_display 加入 primary_image_preview 欄位
- [x] 10.4 設定 primary_image_preview 在列表頁顯示 150x150 縮圖
- [x] 10.5 處理商品沒有圖片時顯示「-」文字
- [x] 10.6 設定 primary_image_preview 的 short_description 為「主要圖片」
- [x] 10.4 設定 primary_image_preview 在列表頁顯示 50x50 縮圖
- [x] 10.5 處理商品沒有圖片時顯示「無圖片」文字
- [x] 10.6 設定 primary_image_preview 的 short_description 為「圖片」

## 11. 建立單元測試

- [x] 11.1 在 `todolist_app/tests/test_product.py` 建立 ProductImageModelTest 測試類別
- [x] 11.2 測試成功建立 ProductImage（所有欄位有效）
- [x] 11.3 測試圖片檔案類型驗證（jpg, jpeg, png, webp 可通過）
- [x] 11.4 測試拒絕無效檔案類型（.txt, .pdf）
- [x] 11.5 測試圖片大小限制（拒絕超過 5MB 的檔案）
- [x] 11.6 測試圖片尺寸限制（拒絕超過 4000x4000 的圖片）
- [x] 11.7 測試縮圖產生（驗證 thumbnail150 和 thumbnail800 已建立）
- [x] 11.8 測試縮圖尺寸正確（150x150 和最大 800x800）
- [x] 11.9 測試主圖邏輯（設定主圖時其他圖片 isPrimary 變 False）
- [x] 11.10 測試檔案路徑包含商品 ID 和 UUID
- [x] 11.11 測試 displayOrder 排序功能
- [x] 11.12 測試 **str** 方法回傳正確字串

## 12. 建立檔案清理測試

- [x] 12.1 建立 ProductImageDeletionTest 測試類別
- [x] 12.2 測試刪除 ProductImage 時實體檔案被移除
- [x] 12.3 測試刪除 ProductImage 時縮圖檔案被移除
- [x] 12.4 測試級聯刪除（刪除 Product 時所有圖片檔案被清理）
- [x] 12.5 測試檔案不存在時刪除不會失敗
- [x] 12.6 使用 mock 或臨時檔案進行測試（避免污染實際 media 目錄)

## 13. 建立 Admin 整合測試

- [x] 13.1 建立 ProductImageAdminTest 測試類別
- [x] 13.2 測試 superuser 可以在商品編輯頁看到圖片 inline
- [x] 13.3 測試透過 admin 上傳圖片成功
- [x] 13.4 測試商品列表頁顯示主圖縮圖
- [x] 13.5 測試沒有圖片的商品顯示「無圖片」
- [x] 13.6 測試圖片預覽功能在 inline 中正常顯示
- [x] 13.7 測試透過 admin 刪除圖片成功

## 14. 建立整合測試

- [x] 14.1 建立 ProductImageIntegrationTest 測試類別
- [x] 14.2 測試完整流程：建立商品 → 上傳圖片 → 產生縮圖 → 設定主圖
- [x] 14.3 測試上傳多張圖片並調整排序
- [x] 14.4 測試變更主圖（從圖片 A 改為圖片 B）
- [x] 14.5 測試檔案驗證失敗的錯誤處理
- [x] 14.6 測試圖片與商品的關聯關係正確
- [x] 14.7 測試 altText 欄位儲存和顯示

## 15. 執行測試和驗證

- [x] 15.1 執行所有 ProductImage 相關測試
- [x] 15.2 確保所有測試通過
- [x] 15.3 執行完整測試套件：`python manage.py test`
- [x] 15.4 修正任何失敗的測試
- [x] 15.5 檢查測試覆蓋率

## 16. 手動驗證

- [x] 16.1 啟動開發伺服器：`python manage.py runserver`
- [x] 16.2 登入 admin 介面（/admin/）
- [x] 16.3 建立測試商品並上傳圖片
- [x] 16.4 驗證圖片在列表頁顯示縮圖
- [x] 16.5 驗證在商品編輯頁可以看到所有圖片
- [x] 16.6 測試上傳不同格式的圖片（jpg, png, webp）
- [x] 16.7 測試上傳大於 5MB 的圖片被拒絕
- [x] 16.8 測試設定主圖功能
- [x] 16.9 測試調整圖片排序（修改 displayOrder）
- [x] 16.10 測試刪除圖片並確認檔案被移除
- [x] 16.11 驗證縮圖檔案存在於 `media/products/<id>/thumbs/` 目錄
- [x] 16.12 測試刪除商品時所有圖片檔案被清理

## 17. 文件和清理

- [x] 17.1 在 ProductImage 模型新增詳細的 docstring
- [x] 17.2 在 ProductImageInline 新增 docstring 說明用途
- [x] 17.3 更新 README.md 說明圖片上傳功能
- [x] 17.4 建立圖片上傳功能的使用說明文件
- [x] 17.5 確保程式碼符合 PEP 8 風格
- [x] 17.6 檢查並移除任何 debug 程式碼或 print 語句
- [x] 17.7 確認所有檔案已儲存
- [x] 17.8 提交變更到版本控制

## 18. 效能和安全檢查

- [x] 18.1 測試上傳多張大圖片的回應時間
- [x] 18.2 驗證圖片檔案真實格式檢查正常運作
- [x] 18.3 確認副檔名偽裝攻擊被阻擋
- [x] 18.4 檢查媒體檔案目錄權限設定
- [x] 18.5 確認 .gitignore 包含 media/ 目錄（避免提交上傳檔案）
- [x] 18.6 文件化生產環境部署需求（Nginx 設定、媒體檔案服務）
```
