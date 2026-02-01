## MODIFIED Requirements

### Requirement: 商品編輯頁整合分類選擇

The system SHALL allow Admin to assign categories to a product from the product edit page. 系統必須在商品編輯頁允許管理者為商品指派分類。

#### Scenario: 在商品編輯頁選擇多個分類

- **WHEN** Admin 在商品編輯頁選擇多個分類並儲存
- **THEN** 系統必須儲存這些關聯，並在商品詳細資訊中顯示所屬分類

### Requirement: 商品列表頁顯示分類欄位

The system SHALL display a `Categories` column in the product list view showing assigned categories. 系統必須在商品列表頁顯示 `Categories` 欄位，列出該商品所屬分類（逗號分隔）。

#### Scenario: 列表頁顯示多分類

- **WHEN** Admin 在商品列表頁查看商品
- **THEN** 系統必須在 `Categories` 欄位顯示該商品的分類名稱（多個分類以逗號分隔）

### Requirement: 按分類篩選商品

The system SHALL provide a filter to limit product list to a selected category (including optionally its descendant leaf categories). 系統必須提供依分類篩選商品的功能，支援選擇該分類及其子分類篩選選項。

#### Scenario: 選擇分類篩選

- **WHEN** Admin 在商品列表頁使用分類篩選器選擇一個分類
- **THEN** 系統必須顯示所有屬於該分類或其可選子分類的商品

### Requirement: 列表頁主要圖片與分類顯示

The system SHALL continue to show primary product image in list view and additionally show assigned categories. 系統必須在列表頁保持主要圖片顯示，並在同一列顯示分類欄位。

#### Scenario: 列表綜合顯示

- **WHEN** 商品有主圖與多個分類
- **THEN** 系統必須顯示主圖縮圖與 `Categories` 欄位，且版面保持可讀性
