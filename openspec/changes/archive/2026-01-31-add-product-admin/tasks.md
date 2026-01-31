## 1. 建立 Product 模型

- [x] 1.1 在 `todolist_app/models.py` 新增 Product 模型類別
- [x] 1.2 新增 productName 欄位（CharField，max_length=200，必填）
- [x] 1.3 新增 description 欄位（TextField，選填，blank=True）
- [x] 1.4 新增 price 欄位（DecimalField，max_digits=10，decimal_places=2，預設 0）
- [x] 1.5 新增 stockQuantity 欄位（PositiveIntegerField，預設 0）
- [x] 1.6 新增 isActive 欄位（BooleanField，預設 True）
- [x] 1.7 新增 createdAt 欄位（DateTimeField，auto_now_add=True）
- [x] 1.8 新增 updatedAt 欄位（DateTimeField，auto_now=True）
- [x] 1.9 實作 **str** 方法回傳 productName
- [x] 1.10 加入 Meta 類別設定 verbose_name 和 ordering

## 2. 實作 XSS 防護

- [x] 2.1 建立 clean_description 方法處理商品描述清理
- [x] 2.2 使用 bleach 套件清理 HTML，只允許安全標籤（p, br, strong, em, ul, ol, li）
- [x] 2.3 覆寫 save 方法，在儲存前自動清理 description 欄位
- [x] 2.4 確保清理邏輯與現有 BlogPost 的清理邏輯一致

## 3. 建立資料庫遷移

- [x] 3.1 執行 `python manage.py makemigrations` 建立 Product 模型的 migration
- [x] 3.2 檢查生成的 migration 檔案確保欄位設定正確
- [x] 3.3 執行 `python manage.py migrate` 套用資料庫變更

## 4. 註冊 Django Admin

- [x] 4.1 在 `todolist_app/admin.py` 建立 ProductAdmin 類別
- [x] 4.2 設定 list_display 顯示 productName, price, stockQuantity, isActive
- [x] 4.3 設定 list_filter 提供 isActive 和 createdAt 篩選
- [x] 4.4 設定 search_fields 搜尋 productName 和 description
- [x] 4.5 設定 readonly_fields 讓 createdAt 和 updatedAt 為唯讀
- [x] 4.6 設定 fieldsets 組織表單欄位（基本資訊、庫存、狀態、時間戳記）
- [x] 4.7 註冊 Product 模型到 admin.site

## 5. 實作模型驗證

- [x] 5.1 在 Product 模型新增 clean 方法
- [x] 5.2 驗證 productName 不可為空且長度不超過 200 字元
- [x] 5.3 驗證 price 必須為非負數
- [x] 5.4 驗證 stockQuantity 必須為非負整數（已由 PositiveIntegerField 處理）
- [x] 5.5 在需要時拋出 ValidationError 並提供清楚的錯誤訊息

## 6. 建立模型單元測試

- [x] 6.1 建立 `todolist_app/tests/test_product.py` 檔案
- [x] 6.2 建立 ProductModelTest 測試類別
- [x] 6.3 測試成功建立商品（所有欄位有效）
- [x] 6.4 測試 productName 必填驗證
- [x] 6.5 測試 productName 長度限制
- [x] 6.6 測試 price 非負數驗證
- [x] 6.7 測試 stockQuantity 預設值為 0
- [x] 6.8 測試 isActive 預設值為 True
- [x] 6.9 測試 createdAt 自動設定
- [x] 6.10 測試 updatedAt 自動更新
- [x] 6.11 測試 **str** 方法回傳 productName
- [x] 6.12 測試 description 的 XSS 清理（script 標籤被移除）
- [x] 6.13 測試 description 的安全 HTML 保留（p, strong 等標籤）

## 7. 建立 Admin 整合測試

- [x] 7.1 在 test_product.py 建立 ProductAdminTest 測試類別
- [x] 7.2 設定測試用的 staff 使用者和 superuser
- [x] 7.3 測試未登入使用者無法存取商品管理頁面
- [x] 7.4 測試非 staff 使用者無法存取商品管理頁面
- [x] 7.5 測試 staff 使用者可以檢視商品列表
- [x] 7.6 測試具備 add_product 權限的使用者可以建立商品
- [x] 7.7 測試沒有 add_product 權限的使用者無法建立商品
- [x] 7.8 測試具備 change_product 權限的使用者可以修改商品
- [x] 7.9 測試沒有 change_product 權限的使用者無法修改商品
- [x] 7.10 測試具備 delete_product 權限的使用者可以刪除商品
- [x] 7.11 測試沒有 delete_product 權限的使用者無法刪除商品

## 8. 建立功能整合測試

- [x] 8.1 在 test_product.py 建立 ProductIntegrationTest 測試類別
- [x] 8.2 測試完整的商品建立流程（透過 admin 介面）
- [x] 8.3 測試商品列表頁面的搜尋功能
- [x] 8.4 測試商品列表頁面的篩選功能（isActive）
- [x] 8.5 測試商品詳細頁面顯示所有欄位
- [x] 8.6 測試商品更新流程（包含驗證錯誤處理）
- [x] 8.7 測試商品刪除流程（包含確認對話框）
- [x] 8.8 測試軟刪除功能（修改 isActive 為 False）
- [x] 8.9 測試重新啟用商品（修改 isActive 為 True）

## 9. 執行測試和驗證

- [x] 9.1 執行所有 Product 相關測試：`python manage.py test todolist_app.tests.test_product`
- [x] 9.2 確保所有測試通過
- [x] 9.3 執行完整測試套件：`python manage.py test`
- [x] 9.4 修正任何失敗的測試

## 10. 手動驗證

- [x] 10.1 啟動開發伺服器：`python manage.py runserver`
- [x] 10.2 登入 admin 介面（/admin/）
- [x] 10.3 驗證商品列表頁面顯示正確
- [x] 10.4 建立測試商品並驗證所有欄位儲存正確
- [x] 10.5 測試搜尋功能（輸入商品名稱或描述關鍵字）
- [x] 10.6 測試篩選功能（選擇 isActive 篩選器）
- [x] 10.7 測試編輯商品並驗證 updatedAt 自動更新
- [x] 10.8 測試刪除商品並確認刪除對話框出現
- [x] 10.9 測試 XSS 防護（在描述輸入 `<script>alert('test')</script>` 並驗證被清理）
- [x] 10.10 測試權限控制（使用不同權限的使用者帳號測試）

## 11. 文件和清理

- [x] 11.1 在 Product 模型新增 docstring 說明用途
- [x] 11.2 在 ProductAdmin 新增 docstring 說明自訂設定
- [x] 11.3 確保程式碼符合專案的程式碼風格（PEP 8）
- [x] 11.4 檢查並移除任何 debug 程式碼或 print 語句
- [ ] 11.5 確認所有檔案已儲存並提交到版本控制
