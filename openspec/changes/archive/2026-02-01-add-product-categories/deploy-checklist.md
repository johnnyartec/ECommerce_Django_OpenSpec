```markdown
# 部署與 PR 檢查表 — add-product-categories (MPTT)

此檢查表用於在發 PR 與部署前確認必要項目已完成，特別注意 `django-mptt` 的相依性與遷移步驟。

- **依賴安裝**: 確認 `django-mptt` 已加入專案相依（`pyproject.toml` / `requirements.txt`），並在 CI 與生產環境安裝。
- **測試**: 在 CI 上確認全部測試通過（含 `todolist_app` 的 65 個測試）。
- **Migration 檢查**: 確認新增的 migration 已包含 idempotent 的 RunPython（避免重複新增欄位），並在本地測試套件上成功執行 `migrate`。
- **備份**:
  - 資料庫備份（完整備份或匯出 categories/related 資料）。
  - 媒體檔案備份（`MEDIA_ROOT`）。
- **Maintenance window**: 排定維護時間，避免在高峰期執行轉換。
- **Migration Dry-run（建議）**:
  - 在 staging 環境執行：`python manage.py migrate`，並執行 `python manage.py convert_categories_mptt --backup <path>`（先做備份）。
  - 執行 `python manage.py check_category_integrity` 確認沒有不一致。
- **Post-migration 檢查**:
  - 執行 `python manage.py cleanup_category_images`（如需要）。
  - 在 Admin 與 API 上抽樣檢查分類與商品關聯是否正確。
  - 執行 `Category.objects.rebuild()` 或 `mptt.utils.rebuild_tree()`（如有必要）。
- **Rollback 計畫**:
  - 使用 `convert_categories_mptt` 所產生的備份 JSON 進行回復流程（已在 management command 中實作回滾選項）。
  - 若 migration 已修改 schema，依照事先準備的 DB 備份恢復資料庫。

**PR 說明建議（PR Body 範本）**

- 描述：採用 `django-mptt` 來支援 Category 樹狀結構；新增 migration、management command（convert/backup/check），並加入測試。
- 影響範圍：`todolist_app/models.py`, `openspec/changes/add-product-categories/*`, migrations 0006-0010。
- 部署步驟摘要：參考 `docs/migration-run-checklist.md`。
```
