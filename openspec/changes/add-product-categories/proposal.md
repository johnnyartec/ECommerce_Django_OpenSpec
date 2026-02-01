## Why

目前商品管理系統缺少分類功能，無法將商品按類別組織展示。電商應用需要階層式分類來幫助使用者瀏覽和篩選商品，提升商品的可發現性和購物體驗。分類的階層結構和視覺化呈現（包含分類圖片）對於建立清晰的商品導覽至關重要。

## What Changes

- 建立階層式產品分類系統，支援多層父子分類關係（樹狀結構）
- 實作產品與分類的多對多關聯（一個產品可屬於多個分類，一個分類可包含多個商品）
- 實作分類驗證規則：有產品的分類不能再建立子分類（確保分類結構清晰）
- 為分類新增圖片欄位，支援分類視覺化展示
- 為分類新增顯示順序欄位（displayOrder），控制同層級分類的前端排序
- 整合分類功能到 Django Admin 介面，提供分類管理和商品分類指派功能
- 更新商品管理介面，顯示商品所屬分類並支援分類篩選
- 新增分類驗證、圖片處理和安全檢查機制

## Capabilities

### New Capabilities

- `product-categories`: 階層式產品分類管理功能，包含分類 CRUD、階層關係管理、圖片上傳、顯示順序控制、分類與商品的多對多關聯、以及分類驗證規則（有產品的分類不能有子分類）

### Modified Capabilities

- `product-management`: 在商品管理功能中整合分類功能，包含商品編輯頁面的分類選擇、商品列表頁的分類欄位顯示、以及按分類篩選商品的功能

## Impact

**受影響的程式碼：**

- `todolist_app/models.py` - 新增 Category 模型，更新 Product 模型新增 categories 多對多關係
- `todolist_app/admin.py` - 新增 CategoryAdmin，更新 ProductAdmin 整合分類選擇和顯示
- `todolist_app/forms.py` - 可能需要新增自訂表單處理分類階層選擇
- `todolist_app/tests/test_product.py` - 新增分類相關測試
- `config/settings.py` - 已有 MEDIA 設定，分類圖片使用現有配置

**新增相依套件：**

- Pillow - 已安裝（用於分類圖片處理，與 ProductImage 共用）
- django-mptt 或 django-treebeard（可選）- 如果需要高效能階層查詢，可考慮使用專門的樹狀結構套件

**資料庫變更：**

- 新增 Category 資料表（包含父子關係、圖片、順序等欄位）
- 新增 Product-Category 多對多關聯表
- 需要建立新的 migration

**相容性考量：**

- 現有商品不受影響（分類為選填）
- 分類功能為新增功能，不影響現有商品管理流程
