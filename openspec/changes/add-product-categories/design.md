## Context

目前系統已有 Product 和 ProductImage 模型，並已配置 Pillow 和 MEDIA 設定用於圖片處理。現在需要新增階層式分類系統，讓商品可以被組織在多層分類中，同時支援：

- 分類的父子階層關係（樹狀結構）
- 產品與分類的多對多關聯
- 分類圖片上傳與顯示
- 分類顯示順序控制
- 特殊驗證規則：有產品的分類不能有子分類

**現有架構：**

- Django 6.x，使用 SQLite (開發) / PostgreSQL (生產)
- Product 模型位於 `todolist_app/models.py`，已有 ProductImage 一對多關係
- 已有完整的 Admin 介面和權限控制
- 已配置 MEDIA_ROOT 和圖片上傳處理（Pillow）
- 專案使用駝峰式命名慣例（camelCase）

**限制條件：**

- 需保持與現有 Product 和 ProductImage 模型的相容性
- 分類功能為選填，不強制商品必須有分類
- 需符合安全最佳實踐（圖片驗證、權限控制）
- 需有完整的測試覆蓋

## Goals / Non-Goals

**Goals:**

- 建立彈性的階層式分類系統，支援任意深度的父子關係
- 實作產品與分類的多對多關聯（一個商品可屬於多個分類）
- 為分類提供圖片上傳和顯示功能（複用 ProductImage 的圖片處理經驗）
- 實作分類顯示順序控制（同層級分類可排序）
- 實作業務規則：有產品的分類不能再有子分類（葉節點約束）
- 整合到 Django Admin 提供友善的管理介面
- 在商品管理介面整合分類選擇和顯示
- 確保分類功能有完整的測試覆蓋

**Non-Goals:**

- 不實作前端商品分類展示頁面（僅 Admin 管理功能）
- 不實作分類的複雜權限控制（使用 Django 預設權限即可）
- 不實作分類的軟刪除（硬刪除即可）
- 不實作分類的多語系支援
- 不實作分類的 SEO 優化（URL slug、meta 等）

## Decisions

### 決策 1: 階層式分類的實作方式

**選擇：使用 Django 原生 ForeignKey 自我參照（parent 欄位）**

**理由：**

- 簡單直接，無需額外套件依賴
- Django ORM 原生支援遞迴查詢（使用 `prefetch_related` 和遞迴邏輯）
- 適合中小規模分類數量（預期不超過 100 個分類）
- 維護成本低，團隊熟悉度高
- 可在未來需要時升級到 django-mptt 或 django-treebeard

**替代方案：**

- **django-mptt**：提供高效能的 Modified Preorder Tree Traversal 演算法，適合大量分類和頻繁查詢。缺點是增加複雜度和依賴。
- **django-treebeard**：提供多種樹演算法（Adjacency List, Nested Sets, Materialized Path）。功能強大但學習曲線較陡。
- **路徑儲存（Materialized Path）**：在資料庫儲存完整路徑字串（如 `/1/3/7/`）。查詢效率高但更新成本高。

**決定：先使用原生 ForeignKey，如果效能成為瓶頸再遷移到 MPTT**

### 決策 2: 產品與分類的關聯方式

**選擇：使用 Django ManyToManyField 建立多對多關聯**

**理由：**

- 符合業務需求：一個商品可屬於多個分類（例如「夏季新品」和「T恤」）
- Django ORM 原生支援，使用簡單
- 自動建立中間表管理關聯
- 支援雙向查詢（從商品找分類、從分類找商品）
- 可在未來擴充中間表（加入關聯屬性如排序、是否主要分類等）

**替代方案：**

- **單一分類（ForeignKey）**：簡單但限制太多，無法滿足商品屬於多分類的需求。
- **自訂中間模型（through）**：可加入額外欄位（如 isPrimary、displayOrder），但目前需求不明確，先保持簡單。

**決定：使用 ManyToManyField，未來如需要可加入 through 中間模型**

### 決策 3: 分類圖片的實作方式

**選擇：在 Category 模型直接加入 ImageField 欄位**

**理由：**

- 每個分類只需要一張代表圖片（不像商品需要多張圖片）
- 實作簡單，無需額外模型
- 複用現有的圖片處理邏輯（Pillow、驗證、縮圖產生）
- 符合大多數電商網站的分類圖片使用模式

**圖片處理策略：**

- 自動產生縮圖（150x150 列表用、800x800 詳細頁用）
- 檔案路徑：`media/categories/<category_id>/<uuid>_<filename>`
- 驗證：檔案類型（jpg/jpeg/png/webp）、大小限制（5MB）、尺寸限制（4000x4000）
- 刪除分類時自動清理圖片檔案

**替代方案：**

- **獨立 CategoryImage 模型**：過度設計，分類只需一張圖。
- **不支援圖片**：不符合現代電商需求，視覺化導覽很重要。

### 決策 4: 分類驗證規則 - 葉節點約束

**選擇：在 Category 模型的 clean() 方法中驗證**

**驗證規則：**

1. 如果分類已有商品（`products.exists()`），則不允許新增子分類
2. 如果分類已有子分類（`children.exists()`），則不允許新增商品

**實作位置：**

- 模型層級：`Category.clean()` 驗證父分類是否為葉節點
- Admin 層級：儲存前呼叫 `full_clean()` 觸發驗證
- 使用 `ValidationError` 提供清楚的錯誤訊息

**理由：**

- 確保分類結構清晰：分類節點要麼是「容器」（有子分類）、要麼是「葉節點」（有商品）
- 避免混淆：防止同一分類同時有子分類和商品
- 提供明確的使用者體驗：商家知道如何組織分類結構

**替代方案：**

- **允許混合**：分類可同時有子分類和商品。靈活但容易混淆，不利於前端展示邏輯。
- **僅葉節點可有商品**：更嚴格的約束，但不強制。我們選擇雙向約束。

### 決策 5: 分類顯示順序

**選擇：使用 displayOrder 整數欄位（PositiveIntegerField）**

**理由：**

- 簡單直接，每個分類有自己的順序值
- 同層級分類按 displayOrder 升序排序
- Admin 介面可直接輸入數字調整順序
- 預設值為 0，新分類自動排在前面

**排序邏輯：**

- 同層級分類（相同 parent）按 displayOrder 排序
- 次要排序條件：categoryName（字母順序）
- 在查詢時使用：`.order_by('displayOrder', 'categoryName')`

**替代方案：**

- **拖曳排序（Drag & Drop）**：需要 JavaScript 和額外的 Admin 自訂，增加複雜度。可作為未來改進。
- **自動排序**：按建立時間或名稱排序。不夠彈性，商家無法控制展示順序。

### 決策 6: Admin 介面設計

**選擇：使用 Django Admin 原生功能 + 適度自訂**

**CategoryAdmin 功能：**

- 列表頁顯示：分類名稱、父分類、商品數量、順序、圖片縮圖
- 分類篩選：按父分類、是否有子分類、是否有商品
- 搜尋：按分類名稱
- 圖片預覽：在詳細頁和列表頁顯示縮圖
- 階層展示：使用縮排或麵包屑顯示分類路徑

**ProductAdmin 整合：**

- 在商品編輯頁加入分類選擇（使用 `filter_horizontal` 提供友善的多選介面）
- 商品列表頁加入「分類」欄位，顯示所屬分類（逗號分隔）
- 商品列表頁加入分類篩選器（`list_filter`）

**理由：**

- 充分利用 Django Admin 的內建功能
- 減少自訂程式碼，降低維護成本
- 提供足夠的管理功能滿足需求

### 決策 7: 資料模型設計

**Category 模型欄位：**

```python
class Category(models.Model):
    categoryName = CharField(max_length=200, unique=True)  # 分類名稱（唯一）
    parent = ForeignKey('self', null=True, blank=True, on_delete=CASCADE, related_name='children')  # 父分類
    image = ImageField(upload_to=category_image_upload_path, blank=True)  # 分類圖片
    thumbnail150 = ImageField(upload_to=category_thumbnail150_upload_path, blank=True)  # 150x150 縮圖
    thumbnail800 = ImageField(upload_to=category_thumbnail800_upload_path, blank=True)  # 800x800 縮圖
    displayOrder = PositiveIntegerField(default=0)  # 顯示順序
    description = TextField(blank=True)  # 分類說明（選填）
    isActive = BooleanField(default=True)  # 是否啟用（軟停用）
    createdAt = DateTimeField(auto_now_add=True)  # 建立時間
    updatedAt = DateTimeField(auto_now=True)  # 更新時間

    class Meta:
        ordering = ['displayOrder', 'categoryName']
        verbose_name = '商品分類'
        verbose_name_plural = '商品分類'
```

**Product 模型更新：**

```python
class Product(models.Model):
    # ... 現有欄位 ...
    categories = ManyToManyField(Category, related_name='products', blank=True)  # 商品分類（多對多）
```

**理由：**

- 遵循專案的駝峰命名慣例
- 包含所有必要欄位
- 使用適當的欄位類型和約束
- related_name 方便雙向查詢

## Risks / Trade-offs

### 風險 1: 原生 ForeignKey 的階層查詢效能

**風險描述：**
當分類數量增加且階層深度很深時（例如 5-6 層），遞迴查詢效能可能成為瓶頸。每次獲取完整路徑或子樹需要多次資料庫查詢。

**緩解措施：**

- 使用 `select_related('parent')` 和 `prefetch_related('children')` 優化查詢
- 限制分類階層深度（建議最多 4 層）
- 在 Admin 介面使用快取避免重複查詢
- 監控查詢效能，如成為瓶頸再遷移到 django-mppt

**監控指標：**

- 分類列表頁載入時間 > 2 秒
- 資料庫查詢數量 > 50 次（N+1 問題）

**遷移路徑：**

如需要可無痛遷移到 django-mptt：

1. 安裝 django-mptt
2. 繼承 `MPTTModel` 並加入 `parent = TreeForeignKey(...)`
3. 執行 `rebuild()` 重建樹結構
4. 更新查詢方法使用 MPTT API

### 風險 2: 葉節點約束可能限制使用彈性

**風險描述：**
強制「有商品的分類不能有子分類」可能在某些情況下造成不便，例如商家想在父分類也放一些通用商品。

**緩解措施：**

- 在文件中清楚說明這個限制和原因
- 提供清楚的錯誤訊息指導使用者如何調整結構
- 如果未來需求改變，可以透過設定開關（`ALLOW_CATEGORY_HYBRID`）控制是否啟用此約束
- 建議使用方式：建立「其他」或「通用」子分類來放置跨類商品

### 風險 3: 分類圖片儲存空間

**風險描述：**
每個分類會產生原圖 + 2 個縮圖，如果有大量分類會佔用儲存空間。刪除分類時需確保清理圖片檔案。

**緩解措施：**

- 覆寫 `Category.delete()` 方法確保刪除實體檔案
- 使用 Django signals (pre_delete) 作為備援清理機制
- 限制分類圖片大小（5MB）和尺寸（4000x4000）
- 提供管理指令清理孤立圖片：`python manage.py cleanup_category_images`
- 定期備份媒體檔案目錄

### 風險 4: 多對多關聯的資料一致性

**風險描述：**
商品可屬於多個分類，如果分類階層調整（移動、刪除），可能導致商品的分類關聯不符合預期。

**緩解措施：**

- 刪除分類時提供選項：
  - 選項 1：同時解除該分類下所有商品的關聯（預設）
  - 選項 2：阻止刪除有商品的分類（CASCADE 保護）
- 移動分類時不影響商品關聯（商品仍屬於該分類，無論它在哪個父分類下）
- 在 Admin 介面提供「重新分類」批次操作
- 新增管理指令檢查資料一致性：`python manage.py check_category_integrity`

### Trade-off: 簡單性 vs. 功能性

選擇使用原生 Django 功能（ForeignKey 自我參照、ManyToManyField）而非專門的樹狀結構套件，犧牲了一些進階功能（如高效能祖先查詢、樹遍歷）換取更簡單的實作和維護成本。這個 trade-off 對目前專案規模是合理的，因為：

- 預期分類數量不會太大（< 100 個）
- 階層深度有限（建議 3-4 層）
- 團隊熟悉度高，無需學習新套件
- 可在未來需要時升級

## Migration Plan

### 第一階段：模型和資料庫

1. 建立 `Category` 模型（包含所有欄位）
2. 更新 `Product` 模型新增 `categories` ManyToManyField
3. 建立圖片上傳路徑函式（複用 ProductImage 經驗）
4. 建立縮圖產生方法（複用 ProductImage 邏輯）
5. 實作分類驗證規則（clean 方法）
6. 執行 `makemigrations` 和 `migrate`

### 第二階段：Admin 整合

1. 建立 `CategoryAdmin`（列表頁、篩選、搜尋、圖片預覽）
2. 更新 `ProductAdmin` 加入分類選擇（`filter_horizontal`）
3. 在 `ProductAdmin` 列表頁加入分類欄位和篩選
4. 實作自訂 admin 方法（商品計數、階層顯示）
5. 測試 Admin 介面功能

### 第三階段：測試

1. 建立單元測試（模型驗證、階層關係、圖片處理）
2. 建立整合測試（Admin 操作、多對多關聯）
3. 測試邊界情況（循環參照、深層階層、葉節點約束）
4. 效能測試（大量分類、深層查詢）

### 第四階段：文件和部署

1. 更新 README 說明分類功能
2. 建立使用說明文件
3. 建立管理指令（資料一致性檢查、孤立圖片清理）
4. 生產環境部署（檢查 MEDIA 設定、權限）

### Rollback 策略

如果需要回滾：

1. 移除 `Product.categories` 欄位的 migration
2. 移除 `Category` 模型的 migration
3. 恢復 Admin 設定
4. 清理測試上傳的分類圖片
5. 移除分類相關測試

## Open Questions

1. **是否需要限制分類階層深度？** - 建議最多 4 層，可在 `clean()` 中驗證
2. **是否需要分類的 URL slug？** - 目前不需要（只有 Admin），未來前端需要時可加入
3. **是否需要分類的排序批次操作？** - 可作為未來改進，初期手動輸入數字即可
4. **刪除有商品的分類應該如何處理？** - 建議使用 CASCADE 自動解除關聯，並提供警告訊息
5. **是否需要分類的複製功能？** - 目前不需要，可作為未來改進
6. **是否需要分類的匯入/匯出功能？** - 可考慮在初期建立大量分類時使用 management command
