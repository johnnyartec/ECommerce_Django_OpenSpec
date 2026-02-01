```markdown
## ADDED Requirements

### Requirement: 階層式產品分類管理

The system SHALL provide hierarchical product categories that support multiple levels of parent/child relationships. 系統必須提供階層式產品分類，支援多層父/子關係。

#### Scenario: 建立頂層分類

- **WHEN** Admin 在 Admin 介面建立一個新的分類且不選擇父分類
- **THEN** 系統必須建立該分類作為頂層節點並顯示成功訊息

#### Scenario: 建立子分類

- **WHEN** Admin 在建立分類時選擇另一分類為 parent
- **THEN** 系統必須建立該分類為 parent 的子分類，並在階層中正確鏈結

### Requirement: 商品與分類之多對多關聯

The system SHALL allow products to belong to multiple categories and categories to contain multiple products. 系統必須允許商品屬於多個分類，分類可包含多個商品（多對多關聯）。

#### Scenario: 將商品加到多個分類

- **WHEN** Admin 在商品編輯頁選擇多個分類並儲存
- **THEN** 系統必須將該商品與所選分類建立關聯，並在商品/分類查詢中可見

#### Scenario: 刪除分類解除關聯

- **WHEN** Admin 刪除一個分類
- **THEN** 系統必須解除該分類與商品之間的關聯（不刪除商品本身）並清理分類圖片檔案

### Requirement: 葉節點約束（有產品的分類不能有子分類）

The system SHALL enforce that a category containing products cannot have child categories, and conversely a category with children cannot directly contain products. 系統必須強制：若分類已有產品則不可新增子分類；若分類已有子分類則不得在該分類直接放置商品。

#### Scenario: 阻止在有產品的分類新增子分類

- **WHEN** Admin 嘗試為一個已有產品的分類新增子分類
- **THEN** 系統必須拒絕並回傳 ValidationError，提示「此分類已有商品，無法新增子分類」

#### Scenario: 阻止在有子分類的分類新增商品

- **WHEN** Admin 嘗試在有子分類的分類上直接加入商品（例如透過 API 或管理界面）
- **THEN** 系統必須拒絕並回傳 ValidationError，提示「此分類已有子分類，請選擇葉節點分類」

### Requirement: 分類顯示順序

The system SHALL provide a `displayOrder` integer for categories to control ordering among siblings. 系統必須提供 `displayOrder` 欄位以控制同層級分類之排序。

#### Scenario: 顯示順序在列表應用

- **WHEN** 前端或 Admin 列出同一 parent 的子分類
- **THEN** 系統必須依 `displayOrder` 升序（次條件為 `categoryName`）回傳結果

### Requirement: 分類圖片與縮圖

The system SHALL allow a single representative image per category and automatically generate thumbnails for display. 系統必須允許每個分類有一張代表圖，並自動產生縮圖。

#### Scenario: 上傳分類圖片並產生縮圖

- **WHEN** Admin 在分類表單上傳一張圖片並儲存
- **THEN** 系統必須儲存原始圖片、產生 150x150 與 800x800 縮圖，並在 Admin 列表/詳細頁顯示縮圖

#### Scenario: 圖片驗證

- **WHEN** Admin 上傳非圖片檔或超過 5MB 的檔案
- **THEN** 系統必須拒絕並回傳明確錯誤訊息（僅支援 JPG, JPEG, PNG, WEBP；大小上限 5MB；最大尺寸 4000x4000）

### Requirement: 管理介面

The system SHALL provide admin UI to manage categories (CRUD), show hierarchy, image preview, and bulk operations. 系統必須在 Django Admin 中提供分類管理功能（CRUD、階層檢視、圖片預覽、批次操作）。

#### Scenario: Admin 查看分類階層

- **WHEN** Admin 在 CategoryAdmin 列表或詳細頁檢視分類
- **THEN** 系統必須以清楚的階層方式（縮排或路徑）顯示分類結構並提供搜尋/篩選

### Requirement: 資料完整性與刪除策略

The system SHALL ensure category deletions clean up associated images and optionally remove associations to products. 系統必須在刪除分類時清理圖片並處理與商品的關聯。

#### Scenario: 刪除分類時清理圖片

- **WHEN** Admin 刪除分類
- **THEN** 系統必須刪除該分類的圖片與縮圖檔案

#### Scenario: 刪除分類時處理商品關聯

- **WHEN** Admin 刪除含有商品的分類
- **THEN** 系統必須解除該分類與商品的關聯（不刪除商品），並在 Admin 顯示警告訊息
```
