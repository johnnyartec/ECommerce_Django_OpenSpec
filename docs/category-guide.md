# 商品分類系統使用指南

## 概述

商品分類系統允許建立階層式的分類結構，每個商品可隸屬多個分類，適用於電商網站的商品組織與篩選。

## 核心特性

### 1. 階層式分類樹

- **無限層級**：支援任意深度的父子分類關係
- **父分類關聯**：透過 `parent` 欄位建立階層結構
- **子分類查詢**：API 支援遞迴查詢子分類商品

範例：

```
電子產品（根分類）
├── 手機
│   ├── iPhone
│   └── Android
└── 電腦
    ├── 筆電
    └── 桌機
```

### 2. 多分類標籤（ManyToMany）

每個商品可同時屬於多個分類，例如：

- 商品「iPhone 15」可同時屬於「手機」和「新品」分類
- 商品「電競筆電」可同時屬於「筆電」和「遊戲」分類

### 3. 葉節點約束（Leaf Node Constraint）

**重要業務規則**：含有商品的分類不可再新增子分類

原因：

- 避免商品歸屬混淆（父分類有商品，子分類也有商品）
- 簡化篩選邏輯（使用者只需選擇最末層分類）
- 確保分類樹清晰

系統會在以下時機自動驗證：

- Admin 儲存分類時（`Category.clean()`）
- API 指派商品時（`POST /app/api/products/<id>/categories/`）

違反約束時會回傳驗證錯誤。

### 4. 分類圖片與縮圖

每個分類可上傳圖片，系統自動產生兩種縮圖：

- **thumbnail150**：150x150 正方形縮圖（用於列表顯示）
- **thumbnail800**：800x800 保持比例縮圖（用於詳細頁）

圖片驗證規則：

- 格式：JPG、JPEG、PNG、WEBP
- 大小：最大 5MB
- 尺寸：最大 4000x4000 像素

## Admin 後台使用

### 管理分類

1. 登入 Django Admin：`http://localhost:8000/admin/`
2. 進入「Categories」管理頁面
3. 點選「Add Category」建立新分類

**欄位說明**：

- `Category Name`：分類名稱（必填）
- `Parent`：父分類（選填，留空為根分類）
- `Image`：分類圖片（選填）
- `Display Order`：排序順序（預設 0）
- `Description`：分類描述（選填）
- `Is Active`：啟用狀態（勾選後前台顯示）

**縮圖自動產生**：

- 上傳圖片後，儲存時會自動產生縮圖
- 列表頁會顯示 150x150 縮圖預覽

### 指派商品到分類

1. 進入「Products」管理頁面
2. 編輯任一商品
3. 在「Categories」欄位使用雙欄選擇器（filter_horizontal）選擇分類
4. 儲存商品

**注意**：

- 一個商品可選擇多個分類
- 無法選擇已有子分類的分類（系統會阻擋）

## API 使用

### 1. 取得所有分類列表

**請求**：

```bash
GET /app/api/categories/
```

**回應**：

```json
[
  {
    "id": 1,
    "categoryName": "電子產品",
    "parent": null,
    "thumbnail150": "/media/categories/thumbnails_150/electronics.jpg",
    "displayOrder": 0,
    "isActive": true
  },
  {
    "id": 2,
    "categoryName": "手機",
    "parent": 1,
    "thumbnail150": "/media/categories/thumbnails_150/phone.jpg",
    "displayOrder": 1,
    "isActive": true
  }
]
```

### 2. 取得分類商品（支援子分類）

**請求**：

```bash
# 僅該分類商品
GET /app/api/categories/2/products/

# 包含所有子分類商品
GET /app/api/categories/2/products/?include_children=1
```

**回應**：

```json
{
  "category": {
    "id": 2,
    "categoryName": "手機"
  },
  "products": [
    {
      "id": 10,
      "productName": "iPhone 15",
      "price": "29900.00",
      "stockQuantity": 50
    }
  ]
}
```

**參數說明**：

- `include_children=1`：包含該分類所有子分類的商品（遞迴查詢）
- 省略或 `include_children=0`：僅該分類直接關聯的商品

### 3. 指派商品到分類

**請求**：

```bash
POST /app/api/products/10/categories/
Content-Type: application/json

{
  "category_ids": [1, 2, 5]
}
```

**成功回應**：

```json
{
  "status": "ok",
  "product_id": 10,
  "categories": [
    { "id": 1, "categoryName": "電子產品" },
    { "id": 2, "categoryName": "手機" },
    { "id": 5, "categoryName": "新品" }
  ]
}
```

**錯誤回應**（違反葉節點約束）：

```json
{
  "error": "Category '電子產品' (ID=1) has child categories and cannot have products"
}
```

## 管理指令

### 清理孤立圖片檔案

當分類刪除或圖片更新後，舊檔案可能殘留在磁碟。使用此指令清理：

```powershell
python manage.py cleanup_category_images
```

**功能**：

- 掃描 `media/categories/` 目錄
- 比對資料庫中所有分類的圖片欄位（image、thumbnail150、thumbnail800）
- 刪除未被引用的檔案
- 移除空目錄

**輸出範例**：

```
Scanning media directory: c:\path\to\media\categories
Found 3 database-referenced files.
Checking 12 files on disk...
Removed 2 orphaned files.
Removed 1 empty directories.
```

**建議執行時機**：

- 每週定期執行（cron job）
- 大量刪除分類後
- 磁碟空間不足時

### 檢查分類資料完整性

驗證葉節點約束是否有違反情況：

```powershell
# 僅檢查，不修正
python manage.py check_category_integrity

# 自動修正（清除違反約束的商品關聯）
python manage.py check_category_integrity --fix
```

**檢查邏輯**：

- 找出同時有商品和子分類的分類
- 輸出違反約束的分類列表

**--fix 模式**：

- 自動清除違反約束分類的所有商品關聯
- 保留子分類結構
- 在交易中執行（失敗則回滾）

**輸出範例**：

```
Checking category integrity...
Found 1 categories with both products and children:
  - Category #5 "電子產品": 3 products, 2 children

--fix not specified. Run with --fix to clear product assignments.
```

**建議執行時機**：

- 資料遷移後
- 批次匯入分類資料後
- 懷疑資料不一致時

## 前台整合建議

### 分類篩選器

```python
# views.py
from django.shortcuts import render
from todolist_app.models import Category, Product

def product_list(request):
    category_id = request.GET.get('category')
    include_children = request.GET.get('include_children', '0') == '1'

    if category_id:
        category = Category.objects.get(id=category_id)
        if include_children:
            # 遞迴取得所有子分類 ID
            category_ids = [category.id]
            def gather_children(cat):
                for child in cat.children.all():
                    category_ids.append(child.id)
                    gather_children(child)
            gather_children(category)
            products = Product.objects.filter(categories__id__in=category_ids).distinct()
        else:
            products = category.products.all()
    else:
        products = Product.objects.all()

    return render(request, 'products/list.html', {
        'products': products,
        'categories': Category.objects.filter(parent=None, isActive=True)
    })
```

### 麵包屑導航

```python
def get_breadcrumbs(category):
    """遞迴建立分類麵包屑"""
    breadcrumbs = []
    while category:
        breadcrumbs.insert(0, category)
        category = category.parent
    return breadcrumbs

# 模板中使用
breadcrumbs = get_breadcrumbs(current_category)
```

## 資料庫架構

### Category 模型

```python
class Category(models.Model):
    categoryName = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True,
                               on_delete=models.CASCADE,
                               related_name='children')
    image = models.ImageField(upload_to=category_image_upload_path,
                              null=True, blank=True)
    thumbnail150 = models.ImageField(upload_to=category_thumbnail150_upload_path,
                                     null=True, blank=True, editable=False)
    thumbnail800 = models.ImageField(upload_to=category_thumbnail800_upload_path,
                                     null=True, blank=True, editable=False)
    displayOrder = models.IntegerField(default=0)
    description = models.TextField(blank=True)
    isActive = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
```

### Product-Category 關聯

```python
class Product(models.Model):
    # ... 其他欄位
    categories = models.ManyToManyField(Category, related_name='products', blank=True)
```

## 測試覆蓋

專案包含完整測試：

- **模型測試**（`test_category_model.py`）：縮圖產生、葉節點約束
- **Admin 測試**（`test_category_admin.py`）：圖片預覽、分類顯示
- **整合測試**（`test_category_integration.py`）：API 端點、遞迴查詢

執行測試：

```powershell
python manage.py test todolist_app.tests.test_category_model todolist_app.tests.test_category_admin todolist_app.tests.test_category_integration --keepdb
```

## 部署注意事項

### 1. 媒體檔案服務

生產環境**不要**使用 Django 直接服務媒體檔案（`MEDIA_URL`）：

**推薦方案**：

- **Nginx**：設定 `/media/` location 直接服務靜態檔案
- **AWS S3/Azure Blob**：使用 `django-storages` 將媒體檔存到雲端
- **CDN**：透過 CloudFront/Azure CDN 加速圖片載入

**Nginx 範例**：

```nginx
location /media/ {
    alias /path/to/project/media/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### 2. 磁碟配額與備份

- **定期清理**：排程執行 `cleanup_category_images`（建議每週）
- **監控空間**：使用 `du -sh media/categories/` 監控目錄大小
- **備份策略**：
  - 資料庫：每日備份（包含 category 和 product-category 關聯）
  - 媒體檔案：每週完整備份，每日增量備份
- **配額限制**：設定雲端儲存空間上限通知（如 AWS S3 Lifecycle）

### 3. 效能優化

## 效能考量與 Tree Library 決策

### 推薦策略（目前）

- 採用內建的自我關聯 `parent` 欄位與必要時的遞迴查詢，對於小型或中型分類樹（數百到數千個分類）通常足夠，且維護與遷移成本最低。
- 若預期分類數會非常龐大（數萬以上）或需要大量階層查詢、頻繁的祖先/後代查詢與樹結構操作，建議改用專門的 tree library（如 `django-mptt` 或 `django-treebeard`）。

### 何時採用 `django-mptt` / `django-treebeard`

- 查詢效能成為瓶頸（例如：頁面載入需遞迴查詢完整子孫集合且造成明顯延遲）。
- 需要經常進行祖先或子孫的快速聚合查詢（COUNT、聚合等）。
- 分類數量成長至數萬級別，並且頻繁變更樹結構。

### 簡要遷移計劃（若決定採用）

1. 在 `pyproject.toml` 或 requirements 中加入相依：例如 `django-mptt`：

```toml
[tool.poetry.dependencies]
django-mptt = "^1.1"
```

2. 新增 migration 腳本或 management command：

- 建立對應的 MPTT 欄位（如 `lft`, `rght`, `tree_id`, `level`），或利用 `django-mptt` 的 `register` 工具。
- 寫入一次性遷移腳本，將現有 `Category` 的 `parent` 關係轉換為 MPTT 結構。

3. 在 staging 環境大量測試：

- 對完整分類資料執行遷移並驗證結果一致性。
- 執行效能基準測試（遞迴查詢、聚合查詢）以確認改善效果。

4. 部署於生產環境並監控：

- 部署前備份資料庫與媒體檔案。
- 在部署後密切監控查詢延遲與錯誤率。

### 附註

- 本專案當前決策：暫不加入 `django-mptt` / `django-treebeard`；如需我可協助執行完整評估與遷移實作（含測試與 migration 腳本）。

#### 使用 django-mptt（選項）

若分類樹層級深（>4 層）且查詢頻繁，考慮使用 `django-mptt`：

**優點**：

- 一次查詢取得整棵樹（不需遞迴）
- 內建 `get_descendants()` 方法
- 減少 N+1 查詢問題

**缺點**：

- 額外資料表欄位（lft、rght、tree_id、level）
- 新增/刪除節點需重建樹結構
- 學習曲線較高

**安裝**：

```powershell
pip install django-mptt
```

**遷移步驟**：

1. 安裝 django-mptt
2. 更新 `Category` 模型繼承 `MPTTModel`
3. 執行 `rebuild_tree` management command
4. 更新查詢邏輯使用 `get_descendants()`

#### 資料庫索引

確保以下欄位有索引（Django 預設已建立）：

- `Category.parent_id`（外鍵自動建立）
- `Product-Category` 關聯表（ManyToMany 自動建立）
- `Category.isActive`（常用篩選條件，手動新增）

```python
# models.py
class Category(models.Model):
    # ...
    isActive = models.BooleanField(default=True, db_index=True)
```

#### 快取策略

```python
from django.core.cache import cache

def get_category_tree():
    tree = cache.get('category_tree')
    if tree is None:
        tree = Category.objects.filter(parent=None, isActive=True).prefetch_related('children')
        cache.set('category_tree', tree, timeout=3600)  # 快取 1 小時
    return tree
```

## 常見問題

### Q1：為何無法將商品指派到某個分類？

**A**：該分類可能已有子分類。系統強制執行葉節點約束（有商品的分類不可有子分類）。

**解決方法**：

- 刪除該分類的所有子分類
- 或將商品改指派到子分類

### Q2：刪除分類後圖片檔案還在嗎？

**A**：Django 的 `ImageField` 不會自動刪除實體檔案。需手動執行清理：

```powershell
python manage.py cleanup_category_images
```

### Q3：如何批次匯入分類資料？

**A**：使用 Django management command 或 Admin Actions。範例：

```python
# management/commands/import_categories.py
import csv
from django.core.management.base import BaseCommand
from todolist_app.models import Category

class Command(BaseCommand):
    def handle(self, *args, **options):
        with open('categories.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                Category.objects.create(
                    categoryName=row['name'],
                    displayOrder=int(row['order']),
                    isActive=row['active'] == 'true'
                )
```

執行後記得執行 `check_category_integrity` 驗證資料。

### Q4：分類圖片太大影響載入速度？

**A**：系統已自動產生縮圖（150x150、800x800），前台應使用縮圖而非原圖：

```html
<!-- 列表頁使用小縮圖 -->
<img src="{{ category.thumbnail150.url }}" alt="{{ category.categoryName }}" />

<!-- 詳細頁使用大縮圖 -->
<img src="{{ category.thumbnail800.url }}" alt="{{ category.categoryName }}" />
```

## 相關文件

- [OpenSpec 變更提案](../../openspec/changes/add-product-categories/proposal.md)
- [設計文件](../../openspec/changes/add-product-categories/design.md)
- [實作任務清單](../../openspec/changes/add-product-categories/tasks.md)
- [分類管理規範](../../openspec/changes/add-product-categories/specs/product-management/spec.md)
