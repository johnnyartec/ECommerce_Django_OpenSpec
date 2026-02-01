````markdown
# 遷移執行檢查表 — migration-run-checklist

此檢查表針對在 staging/production 執行 `django-mptt` 相關 migration 與資料轉換時的逐步操作。

1. **預備**
   - 確認已建立資料庫備份（點-in-time 或 SQL dump）。
   - 備份 `MEDIA_ROOT`（分類圖片、縮圖）。
   - 確認目標環境安裝 `django-mptt`（`pip install -r requirements.txt` 或相對應指令）。
   - 將服務切換到維護模式，避免使用者在轉換時寫入資料。

2. **執行 migration**
   - 拉取包含變更的 branch 並切換到部署分支。
   - 執行：

```bash
python -m pip install -r requirements.txt
python manage.py migrate --noinput
```

3. **執行轉換（備份 + 轉換）**
   - 執行 management command（會先建立 JSON 備份）：

```bash
python manage.py convert_categories_mptt --backup /path/to/backups/categories_backup_$(date +%Y%m%d%H%M%S).json
```

- 若 command 支援 `--dry-run`，先以 dry-run 檢查預期效果。

4. **資料檢查**
   - 執行 integrity 檢查：

```bash
python manage.py check_category_integrity
```

- 在 admin 或 API 上抽樣檢查樹狀關係與 `Product.categories` 關聯。
- 若需要，手動呼叫：

```bash
python manage.py shell -c "from todolist_app.models import Category; Category.objects.rebuild()"
```

5. **後處理**
   - 清理臨時或孤立的媒體檔案：

```bash
python manage.py cleanup_category_images
```

- 移除或記錄臨時欄位（如果 migration 有這類步驟）。

6. **回滾**
   - 若檢查失敗，先暫停對外服務，然後使用備份 JSON 或資料庫備份回復：

```bash
# 範例：使用 management command 提供的回復功能（如有）
python manage.py convert_categories_mptt --restore /path/to/backup.json

# 或：使用 DB 備份還原
# psql ... restore-db-dump
```

7. **驗收**
   - 解除維護模式並監控應用行為（API 錯誤率、DB latency、前端錯誤）。
   - 在 24 小時內密切觀察並保留回滾計畫。

**備註**

- 在 CI 中加入 `mptt` 的安裝步驟與一個小型遷移乾跑，能提早發現 migration idempotency 或 env 差異問題。
````
