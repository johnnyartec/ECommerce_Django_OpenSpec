## Why

為了支援電商或庫存管理需求，需要在 admin 後台新增完整的商品管理功能，讓管理員能夠有效管理商品資料。

## What Changes

- 新增 Product 模型，包含商品基本資訊（名稱、描述、價格、庫存等）
- 在 Django admin 註冊 Product 模型，提供完整的 CRUD 介面
- 新增商品列表檢視，支援搜尋和篩選功能
- 實作商品新增、編輯、刪除功能
- 加入適當的權限控制，確保只有授權使用者可以管理商品
- 新增商品管理相關的單元測試和整合測試

## Capabilities

### New Capabilities

- `product-management`: 商品管理功能，包含商品的建立、讀取、更新、刪除（CRUD）操作，以及在 Django admin 中的完整管理介面

### Modified Capabilities

無現有功能需要修改

## Impact

**新增檔案**：

- `todolist_app/models.py`：新增 Product 模型
- `todolist_app/admin.py`：註冊 Product 到 admin
- `todolist_app/tests/test_product.py`：商品功能測試

**資料庫變更**：

- 需要建立新的 migration 以新增 Product 資料表

**相依性**：

- 使用現有的 Django admin 框架
- 使用現有的認證和授權系統

**安全性**：

- 商品管理操作需要適當的權限控制
- 確保 XSS 防護適用於商品描述欄位
