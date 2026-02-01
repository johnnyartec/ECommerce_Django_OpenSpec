# Product Management

## Purpose

This specification defines the product management capabilities of the system, including CRUD operations, validation, security, and admin interface customization for managing product inventory.

## Requirements

### Requirement: 建立商品

The system SHALL allow authorized users to create new product records. 系統必須允許授權使用者建立新的商品記錄。

#### Scenario: 成功建立商品

- **WHEN** 授權使用者在 admin 介面輸入有效的商品資訊（名稱、描述、價格、庫存）並提交
- **THEN** 系統必須建立新的商品記錄並顯示成功訊息

```markdown
## MODIFIED Requirements

### Requirement: 檢視商品列表

The system SHALL provide a product list view displaying key information for all products. 系統必須提供商品列表檢視,顯示所有商品的關鍵資訊。

#### Scenario: 顯示商品列表

- **WHEN** 授權使用者存取商品管理頁面
- **THEN** 系統必須顯示商品列表，包含商品名稱、價格、庫存數量和啟用狀態

#### Scenario: 顯示商品主圖縮圖

- **WHEN** 授權使用者檢視商品列表頁
- **THEN** 系統必須在每個商品旁顯示主圖的 150x150 縮圖（如果商品有圖片）

#### Scenario: 無圖片商品顯示預設圖示

- **WHEN** 商品沒有上傳任何圖片
- **THEN** 系統必須在列表頁顯示預設的佔位圖示

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

#### Scenario: 檢視商品圖片庫

- **WHEN** 使用者檢視商品詳細資訊頁面
- **THEN** 系統必須顯示該商品的所有圖片，按照 displayOrder 排序，並標示主圖

### Requirement: Admin 介面自訂

The system SHALL provide a user-friendly admin management interface. 系統必須提供友善的 admin 管理介面。

#### Scenario: 列表頁顯示關鍵欄位

- **WHEN** 使用者檢視商品列表頁
- **THEN** 系統必須顯示商品名稱、價格、庫存數量和啟用狀態欄位

#### Scenario: 列表頁顯示圖片欄位

- **WHEN** 使用者檢視商品列表頁
- **THEN** 系統必須在列表中新增「圖片」欄位，顯示商品主圖的縮圖預覽

#### Scenario: 時間戳記為唯讀

- **WHEN** 使用者編輯商品
- **THEN** 系統必須將 createdAt 和 updatedAt 欄位設為唯讀，不允許手動修改

#### Scenario: 支援批次操作

- **WHEN** 使用者在列表頁選擇多個商品
- **THEN** 系統必須提供批次刪除或批次修改狀態的功能

#### Scenario: 商品編輯頁整合圖片管理

- **WHEN** 使用者編輯商品
- **THEN** 系統必須在編輯頁面內嵌顯示圖片管理區塊（使用 inline），允許直接上傳、刪除和排序圖片
```

### Requirement: 軟刪除功能
