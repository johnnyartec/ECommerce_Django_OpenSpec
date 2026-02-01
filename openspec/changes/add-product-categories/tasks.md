# 實作任務清單：add-product-categories

## 1. 安裝相依與設定

- [x] 1.1 確認 Pillow 已安裝（用於分類圖片處理）
- [x] 1.2 決定是否加入 `django-mptt` 或 `django-treebeard`（已評估並決議：暫不加入，延後至需要時再引入）  
      (說明：目前使用自訂 `parent` FK 與遞迴查詢已足以應付小到中型分類樹。若未來需要優化大量讀取/階層查詢，可採用 `django-mptt` 或 `django-treebeard`，並執行遷移計畫。參考：docs/category-guide.md)
- [x] 1.3 檢查並確認 `config/settings.py` 的 `MEDIA_ROOT`/`MEDIA_URL` 設定

## 2. 建立資料模型

- [x] 2.1 在 `todolist_app/models.py` 新增 `Category` 模型（包含 `categoryName`, `parent`, `image`, `thumbnail150`, `thumbnail800`, `displayOrder`, `description`, `isActive`, `createdAt`, `updatedAt`）
- [x] 2.2 在 `Product` 模型新增 `categories = ManyToManyField(Category, related_name='products', blank=True)`
- [x] 2.3 實作 `category_image_upload_path`、縮圖路徑與縮圖產生方法（複用 ProductImage 邏輯）
- [x] 2.4 在 `Category.clean()` 實作葉節點約束與深度限制（如需）
- [x] 2.5 新增模型層級的驗證單元測試

## 3. 資料庫遷移

- [x] 3.1 執行 `python manage.py makemigrations todolist_app`，檢查 migration
- [x] 3.2 執行 `python manage.py migrate` 並驗證資料表結構

## 4. 圖片處理與儲存

- [x] 4.1 複用或抽取通用的縮圖產生與驗證工具（檔案類型、大小、尺寸）
- [x] 4.2 實作上傳時的縮圖產生（150x150、800x800）並儲存到對應欄位
- [x] 4.3 覆寫 `Category.delete()` 或使用 signal 清理圖片與縮圖檔案

## 5. Admin 整合

- [x] 5.1 建立 `CategoryAdmin`，在列表顯示名稱、父分類、商品數、displayOrder、圖片縮圖
- [x] 5.2 在 `ProductAdmin` 加入 `categories`（使用 `filter_horizontal` 或 `filter_vertical`）
- [x] 5.3 在 `ProductAdmin` 列表加入 `Categories` 欄位與分類篩選器
- [x] 5.4 在 Admin 詳細與列表頁顯示圖片預覽（使用 `format_html`）

## 6. 業務邏輯與 API

- [x] 6.1 實作在 model 層或儲存流程中確保葉節點約束（有商品的分類不可新增子分類）
- [x] 6.2 若有 API，更新相應的 serializer/視圖以支援分類關聯與驗證
- [x] 6.3 實作分類篩選器（支援包含子分類的選項）

## 7. 測試

- [x] 7.1 建立模型單元測試（Category 建立、parent/children 行為、clean 驗證）
- [x] 7.2 建立圖片驗證與縮圖產生測試
- [x] 7.3 建立 Admin 整合測試（在 Admin 上傳圖片、指派分類、刪除分類行為）
- [x] 7.4 建立整合測試（建立分類樹、將商品指派多個分類、分類篩選）

## 8. 文件與維運

- [x] 8.1 更新 `README.md` 與 `docs/` 中的相關說明（如何使用分類、管理圖片、清理指令）
- [x] 8.2 新增 management command：`cleanup_category_images`（清理孤立圖片）
- [x] 8.3 新增 management command：`check_category_integrity`（驗證資料一致性）

## 9. 部署注意事項

- [x] 9.1 在生產環境使用 Nginx/Cloud Storage 服務媒體檔案（不要用 Django 直接服務）  
      (參考：docs/spec/product-image-deployment.md、docs/category-guide.md)
- [x] 9.2 檢查磁碟配額與備份策略，避免大量圖片造成空間問題  
      (參考：docs/spec/product-image-deployment.md、docs/category-guide.md)
- [x] 9.3 如需效能優化，評估採用 `django-mptt` 並執行遷移計畫（已評估並決議：目前延後採用，文件包含遷移建議）  
      (說明：已在 `docs/category-guide.md` 中加入採納條件與遷移步驟與範例設定，若決定採用可依說明更新 `pyproject.toml` 並建立遷移腳本)

## 10. 最後驗收

- [x] 10.1 所有測試通過（unit + integration + admin tests）
- [x] 10.2 Documentation 已更新
- [x] 10.3 變更已提交至版本控制並建立 PR
