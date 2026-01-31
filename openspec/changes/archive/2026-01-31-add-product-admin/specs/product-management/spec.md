## ADDED Requirements

### Requirement: 建立商品

The system SHALL allow authorized users to create new product records. 系統必須允許授權使用者建立新的商品記錄。

#### Scenario: 成功建立商品

- **WHEN** 授權使用者在 admin 介面輸入有效的商品資訊（名稱、描述、價格、庫存）並提交
- **THEN** 系統必須建立新的商品記錄並顯示成功訊息

#### Scenario: 商品名稱為必填

- **WHEN** 使用者嘗試建立商品但未填寫商品名稱
- **THEN** 系統必須拒絕建立並顯示錯誤訊息

#### Scenario: 價格必須為非負數

- **WHEN** 使用者輸入負數價格
- **THEN** 系統必須拒絕建立並顯示錯誤訊息

#### Scenario: 庫存數量必須為非負整數

- **WHEN** 使用者輸入負數或小數的庫存數量
- **THEN** 系統必須拒絕建立並顯示錯誤訊息

### Requirement: 檢視商品列表

The system SHALL provide a product list view displaying key information for all products. 系統必須提供商品列表檢視,顯示所有商品的關鍵資訊。

#### Scenario: 顯示商品列表

- **WHEN** 授權使用者存取商品管理頁面
- **THEN** 系統必須顯示商品列表，包含商品名稱、價格、庫存數量和啟用狀態

#### Scenario: 搜尋商品

- **WHEN** 使用者在搜尋欄輸入關鍵字
- **THEN** 系統必須顯示名稱或描述包含該關鍵字的商品

#### Scenario: 篩選商品狀態

- **WHEN** 使用者選擇篩選條件（例如：僅顯示啟用的商品）
- **THEN** 系統必須僅顯示符合篩選條件的商品

### Requirement: 檢視商品詳細資訊

The system SHALL allow users to view complete detailed information for a single product. 系統必須允許使用者檢視單一商品的完整詳細資訊。

#### Scenario: 檢視商品詳細資訊

- **WHEN** 使用者點擊商品列表中的商品
- **THEN** 系統必須顯示該商品的所有欄位資訊，包含名稱、描述、價格、庫存、啟用狀態、建立時間和更新時間

### Requirement: 更新商品資訊

The system SHALL allow authorized users to update existing product information. 系統必須允許授權使用者更新現有商品的資訊。

#### Scenario: 成功更新商品

- **WHEN** 授權使用者修改商品資訊並提交
- **THEN** 系統必須更新商品記錄、更新 updatedAt 時間戳記，並顯示成功訊息

#### Scenario: 更新時驗證必填欄位

- **WHEN** 使用者嘗試清空商品名稱後提交
- **THEN** 系統必須拒絕更新並顯示錯誤訊息

#### Scenario: 更新時驗證價格

- **WHEN** 使用者輸入無效的價格（負數或非數字）
- **THEN** 系統必須拒絕更新並顯示錯誤訊息

### Requirement: 刪除商品

The system SHALL allow authorized users to delete product records. 系統必須允許授權使用者刪除商品記錄。

#### Scenario: 成功刪除商品

- **WHEN** 授權使用者選擇刪除商品並確認
- **THEN** 系統必須刪除該商品記錄並顯示成功訊息

#### Scenario: 刪除前需確認

- **WHEN** 使用者選擇刪除商品
- **THEN** 系統必須顯示確認對話框，要求使用者確認刪除操作

### Requirement: 軟刪除功能

The system SHALL provide soft delete functionality by marking products as inactive through the isActive field. 系統必須提供軟刪除功能,透過 isActive 欄位標記商品為停用狀態。

#### Scenario: 停用商品

- **WHEN** 使用者將商品的 isActive 設定為 False
- **THEN** 系統必須保留商品記錄但標記為停用

#### Scenario: 重新啟用商品

- **WHEN** 使用者將已停用商品的 isActive 設定為 True
- **THEN** 系統必須將商品標記為啟用

### Requirement: XSS 防護

The system SHALL provide XSS protection for the product description field. 系統必須對商品描述欄位提供 XSS 防護。

#### Scenario: 清理危險 HTML

- **WHEN** 使用者在商品描述中輸入包含 script 標籤或其他危險 HTML 的內容
- **THEN** 系統必須清理危險內容，僅保留安全的 HTML 標籤（如 p、br、strong、em）

#### Scenario: 允許安全的 HTML

- **WHEN** 使用者在商品描述中輸入安全的 HTML 標籤（如 p、br、strong）
- **THEN** 系統必須保留這些安全標籤

### Requirement: 權限控制

The system SHALL ensure that only authorized users can manage products. 系統必須確保只有授權使用者可以管理商品。

#### Scenario: 未登入使用者無法存取

- **WHEN** 未登入使用者嘗試存取商品管理頁面
- **THEN** 系統必須重新導向至登入頁面

#### Scenario: 非 staff 使用者無法存取

- **WHEN** 已登入但非 staff 的使用者嘗試存取商品管理頁面
- **THEN** 系統必須拒絕存取並顯示權限錯誤訊息

#### Scenario: Staff 使用者可以檢視商品

- **WHEN** Staff 使用者存取商品管理頁面
- **THEN** 系統必須允許存取並顯示商品列表

#### Scenario: 具備特定權限才能新增商品

- **WHEN** 使用者沒有 add_product 權限時嘗試建立商品
- **THEN** 系統必須拒絕操作並顯示權限錯誤訊息

#### Scenario: 具備特定權限才能修改商品

- **WHEN** 使用者沒有 change_product 權限時嘗試修改商品
- **THEN** 系統必須拒絕操作並顯示權限錯誤訊息

#### Scenario: 具備特定權限才能刪除商品

- **WHEN** 使用者沒有 delete_product 權限時嘗試刪除商品
- **THEN** 系統必須拒絕操作並顯示權限錯誤訊息

### Requirement: 資料驗證

The system SHALL validate the integrity and correctness of product data. 系統必須驗證商品資料的完整性和正確性。

#### Scenario: 商品名稱長度限制

- **WHEN** 使用者輸入超過 200 字元的商品名稱
- **THEN** 系統必須拒絕並顯示錯誤訊息

#### Scenario: 價格精確度

- **WHEN** 使用者輸入價格
- **THEN** 系統必須確保價格最多 10 位數、小數點後最多 2 位

#### Scenario: 自動設定時間戳記

- **WHEN** 建立新商品
- **THEN** 系統必須自動設定 createdAt 和 updatedAt 為當前時間

#### Scenario: 自動更新時間戳記

- **WHEN** 更新商品資訊
- **THEN** 系統必須自動更新 updatedAt 為當前時間

### Requirement: Admin 介面自訂

The system SHALL provide a user-friendly admin management interface. 系統必須提供友善的 admin 管理介面。

#### Scenario: 列表頁顯示關鍵欄位

- **WHEN** 使用者檢視商品列表頁
- **THEN** 系統必須顯示商品名稱、價格、庫存數量和啟用狀態欄位

#### Scenario: 時間戳記為唯讀

- **WHEN** 使用者編輯商品
- **THEN** 系統必須將 createdAt 和 updatedAt 欄位設為唯讀，不允許手動修改

#### Scenario: 支援批次操作

- **WHEN** 使用者在列表頁選擇多個商品
- **THEN** 系統必須提供批次刪除或批次修改狀態的功能
