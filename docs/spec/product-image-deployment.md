# 商品圖片功能 - 生產環境部署指南

## 概述

本文件說明如何在生產環境中正確部署商品圖片上傳功能。

## 前置需求

- Python 3.12+
- Django 6.x
- Pillow 12.x（圖片處理）
- Nginx 或其他 Web 伺服器（媒體檔案服務）
- 充足的磁碟空間

## 設定步驟

### 1. 環境變數設定

在 `.env.production` 中設定：

```bash
# 媒體檔案設定
MEDIA_ROOT=/var/www/yoursite/media
MEDIA_URL=https://cdn.yoursite.com/media/

# 上傳限制
FILE_UPLOAD_MAX_MEMORY_SIZE=5242880  # 5MB

# 安全設定
DEBUG=False
```

### 2. Django 設定

確保 `config/settings.py` 中的設定正確：

```python
from env_utility import env_get

# 媒體檔案設定
MEDIA_ROOT = env_get('MEDIA_ROOT', BASE_DIR / 'media')
MEDIA_URL = env_get('MEDIA_URL', '/media/')

# 上傳限制
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
```

### 3. Nginx 設定

#### 基本媒體檔案服務

```nginx
server {
    listen 80;
    server_name yoursite.com;

    # 媒體檔案（用戶上傳）
    location /media/ {
        alias /var/www/yoursite/media/;

        # 安全性設定
        location ~* \.(py|php|pl|sh|bash)$ {
            deny all;
        }

        # 快取設定
        expires 30d;
        add_header Cache-Control "public, no-transform";

        # 防止直接執行
        add_header X-Content-Type-Options nosniff;
    }

    # Django 應用
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 上傳大小限制
        client_max_body_size 10M;
    }
}
```

#### 使用 HTTPS

```nginx
server {
    listen 443 ssl http2;
    server_name yoursite.com;

    ssl_certificate /etc/letsencrypt/live/yoursite.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yoursite.com/privkey.pem;

    # 媒體檔案
    location /media/ {
        alias /var/www/yoursite/media/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
        add_header X-Content-Type-Options nosniff;
    }

    # 靜態檔案
    location /static/ {
        alias /var/www/yoursite/static/;
        expires 365d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        client_max_body_size 10M;
    }
}
```

### 4. 目錄權限設定

```bash
# 建立媒體目錄
sudo mkdir -p /var/www/yoursite/media/products

# 設定擁有者（假設使用 www-data 用戶）
sudo chown -R www-data:www-data /var/www/yoursite/media

# 設定權限
sudo chmod -R 755 /var/www/yoursite/media
```

### 5. 使用雲端儲存（選用）

對於大型應用，建議使用雲端儲存如 AWS S3：

#### 安裝套件

```bash
pip install django-storages boto3
```

#### 設定 Django

```python
# settings.py

# 安裝 storages
INSTALLED_APPS = [
    ...
    'storages',
]

# AWS S3 設定
AWS_ACCESS_KEY_ID = env_get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env_get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env_get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = env_get('AWS_S3_REGION_NAME', 'ap-northeast-1')
AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'

# 使用 S3 作為媒體檔案儲存
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'
```

## 效能最佳化

### 1. 縮圖快取

Nginx 已設定 30 天快取，但可以進一步優化：

```nginx
# 針對縮圖的快取設定
location ~* /media/products/.*/thumbs/.*\.(jpg|jpeg|png|webp)$ {
    expires 365d;
    add_header Cache-Control "public, immutable";
}
```

### 2. 圖片壓縮

考慮使用 CDN 的圖片最佳化功能，或安裝圖片壓縮套件：

```bash
pip install pillow-heif  # 支援 HEIF/HEIC 格式
```

### 3. 非同步縮圖產生

對於高流量網站，考慮使用 Celery 非同步產生縮圖：

```python
# tasks.py
from celery import shared_task

@shared_task
def generate_thumbnails_async(product_image_id):
    from todolist_app.models import ProductImage
    product_image = ProductImage.objects.get(id=product_image_id)
    product_image.generate_thumbnails()
    product_image.save()
```

## 安全性檢查清單

- [ ] Nginx 已設定 `client_max_body_size` 限制
- [ ] 媒體目錄已設定正確權限（755）
- [ ] `.gitignore` 已包含 `media/` 目錄
- [ ] 生產環境 `DEBUG=False`
- [ ] HTTPS 已啟用
- [ ] 已設定 `X-Content-Type-Options: nosniff`
- [ ] 已封鎖媒體目錄中的可執行檔案

## 監控與維護

### 磁碟空間監控

```bash
# 檢查媒體目錄大小
du -sh /var/www/yoursite/media/

# 設定磁碟空間告警
# 可使用 Prometheus + Alertmanager 或 CloudWatch
```

### 定期清理孤立檔案

```python
# management/commands/cleanup_orphan_images.py
from django.core.management.base import BaseCommand
from django.conf import settings
import os

class Command(BaseCommand):
    help = '清理孤立的圖片檔案'

    def handle(self, *args, **options):
        from todolist_app.models import ProductImage

        media_root = settings.MEDIA_ROOT
        products_dir = os.path.join(media_root, 'products')

        # 取得資料庫中的所有圖片路徑
        db_paths = set()
        for img in ProductImage.objects.all():
            if img.image:
                db_paths.add(img.image.path)
            if img.thumbnail150:
                db_paths.add(img.thumbnail150.path)
            if img.thumbnail800:
                db_paths.add(img.thumbnail800.path)

        # 掃描檔案系統
        orphan_count = 0
        for root, dirs, files in os.walk(products_dir):
            for filename in files:
                filepath = os.path.join(root, filename)
                if filepath not in db_paths:
                    os.remove(filepath)
                    orphan_count += 1
                    self.stdout.write(f'已刪除: {filepath}')

        self.stdout.write(self.style.SUCCESS(f'共清理 {orphan_count} 個孤立檔案'))
```

執行清理：

```bash
python manage.py cleanup_orphan_images
```

## 故障排除

### 上傳失敗

1. 檢查 Nginx `client_max_body_size` 設定
2. 檢查目錄權限
3. 檢查磁碟空間
4. 查看 Django 錯誤日誌

### 縮圖不顯示

1. 確認媒體目錄路徑正確
2. 檢查 Nginx 媒體檔案設定
3. 確認檔案存在且可讀取

### 檔案刪除失敗

1. 檢查目錄權限
2. 確認沒有其他程序鎖定檔案
3. 查看 Django 日誌中的錯誤訊息

## 備份策略

建議定期備份媒體檔案：

```bash
# 每日增量備份到 S3
aws s3 sync /var/www/yoursite/media/ s3://backup-bucket/media/ --delete

# 或使用 rsync 到備份伺服器
rsync -avz /var/www/yoursite/media/ backup-server:/backups/media/
```
