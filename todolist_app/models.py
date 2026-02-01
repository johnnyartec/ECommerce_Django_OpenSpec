from django.db import models  # 👈 修正這裡，改為 import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils.text import slugify
from django.utils import timezone
from django.db.models.signals import post_delete, pre_delete
from django.dispatch import receiver
import bleach
import uuid
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from .image_utils import validate_image_file, make_square_thumbnail, make_preview_thumbnail
from .utils.markdown_renderer import render_markdown

class Todo(models.Model):
    # 👈 2. 建立關聯：一對多 (一個 User 有多個 Todo)
    # on_delete=models.CASCADE 表示如果 User 被刪除，他的 Todo 也一併刪除
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todos', null=True, blank=True)
    
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"    


class BlogPost(models.Model):
    # 作者（關聯到現有的 User 模型）
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blogPosts')  # 作者為必填

    # 文章欄位（命名遵循憲法要求使用駝峰式命名）
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=300, unique=True, blank=True)  # 可讀 slug，用於公開 URL
    markdownContent = models.TextField()  # 原始 Markdown 內容
    htmlContent = models.TextField(blank=True)  # 由 Markdown 轉出的安全 HTML
    summary = models.CharField(max_length=512, blank=True)  # 摘要
    tags = models.CharField(max_length=255, blank=True)  # 簡易標籤，以逗號分隔

    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    status = models.CharField(max_length=20, choices=[(STATUS_DRAFT, 'Draft'), (STATUS_PUBLISHED, 'Published')], default=STATUS_DRAFT)

    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    publishedAt = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-publishedAt', '-createdAt']

    def __str__(self):
        return f"{self.title} ({self.status})"

    def save(self, *args, **kwargs):
        # 如果沒有 slug，生成一個基於 title 的 slug（若衝突則附時間戳）
        if not self.slug:
            baseSlug = slugify(self.title)[:240]
            
            # 如果中文標題導致空 slug，使用 ID 或時間戳
            if not baseSlug:
                import uuid
                baseSlug = f"post-{uuid.uuid4().hex[:8]}"
            
            candidate = baseSlug
            suffix = 1
            while BlogPost.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
                candidate = f"{baseSlug}-{suffix}"
                suffix += 1
            self.slug = candidate

        # 處理發佈時間（由 draft -> published 時設定 publishedAt）
        if self.status == self.STATUS_PUBLISHED and not self.publishedAt:
            self.publishedAt = timezone.now()

        # 產生 htmlContent（先用 Markdown 轉 HTML，再做消毒）
        try:
            self.htmlContent = render_markdown(self.markdownContent)
        except Exception:
            # 若渲染失敗，保留原先的 htmlContent 並不阻斷保存
            pass

        super().save(*args, **kwargs)


class Product(models.Model):
    """
    商品模型，用於管理商品資訊。
    
    支援商品的基本資訊管理，包含名稱、描述、價格和庫存數量。
    提供軟刪除功能（透過 isActive 欄位）和 XSS 防護。
    """
    productName = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    stockQuantity = models.PositiveIntegerField(default=0)
    isActive = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField('Category', related_name='products', blank=True)

    class Meta:
        verbose_name = '商品'
        verbose_name_plural = '商品'
        ordering = ['-createdAt']

    def __str__(self):
        return self.productName

    def clean_description(self):
        """清理商品描述中的危險 HTML 內容"""
        if self.description:
            # 只允許安全的 HTML 標籤
            allowed_tags = ['p', 'br', 'strong', 'em', 'ul', 'ol', 'li']
            allowed_attrs = {}
            self.description = bleach.clean(
                self.description,
                tags=allowed_tags,
                attributes=allowed_attrs,
                strip=False  # 不保留被移除標籤的內容
            )

    def clean(self):
        """驗證模型資料"""
        if not self.productName or not self.productName.strip():
            raise ValidationError({'productName': '商品名稱為必填欄位'})
        
        if len(self.productName) > 200:
            raise ValidationError({'productName': '商品名稱長度不可超過 200 字元'})
        
        if self.price < 0:
            raise ValidationError({'price': '價格不可為負數'})

    def save(self, *args, **kwargs):
        """儲存前清理描述欄位"""
        self.clean_description()
        super().save(*args, **kwargs)


def product_image_upload_path(instance, filename):
    """
    產生商品圖片的上傳路徑。
    格式: products/<product_id>/<uuid>_<filename>
    """
    ext = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
    return f"products/{instance.product.id}/{unique_filename}"


def product_thumbnail_upload_path(instance, filename, size):
    """
    產生縮圖的上傳路徑。
    格式: products/<product_id>/thumbs/<uuid>_<filename>_<size>.ext
    """
    ext = os.path.splitext(filename)[1]
    base_name = os.path.splitext(filename)[0]
    unique_filename = f"{uuid.uuid4().hex[:8]}_{base_name}_{size}{ext}"
    return f"products/{instance.product.id}/thumbs/{unique_filename}"


def product_thumbnail150_upload_path(instance, filename):
    """產生 150x150 縮圖的上傳路徑"""
    return product_thumbnail_upload_path(instance, filename, '150x150')


def product_thumbnail800_upload_path(instance, filename):
    """產生 800x800 縮圖的上傳路徑"""
    return product_thumbnail_upload_path(instance, filename, '800x800')


def category_image_upload_path(instance, filename):
    """產生分類圖片的上傳路徑。
    格式: categories/<category_id>/<uuid>_<filename>
    """
    ext = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
    # If instance has no id yet, store under temporary folder 'categories/tmp'
    cat_id = getattr(instance, 'id', None) or 'tmp'
    return f"categories/{cat_id}/{unique_filename}"


def category_thumbnail_upload_path(instance, filename, size):
    base_name = os.path.splitext(filename)[0]
    ext = os.path.splitext(filename)[1]
    unique_filename = f"{uuid.uuid4().hex[:8]}_{base_name}_{size}{ext}"
    cat_id = getattr(instance, 'id', None) or 'tmp'
    return f"categories/{cat_id}/thumbs/{unique_filename}"


def category_thumbnail150_upload_path(instance, filename):
    return category_thumbnail_upload_path(instance, filename, '150x150')


def category_thumbnail800_upload_path(instance, filename):
    return category_thumbnail_upload_path(instance, filename, '800x800')


class ProductImage(models.Model):
    """
    商品圖片模型，用於管理商品的多張圖片。
    
    功能：
    - 支援多張圖片上傳（一對多關係）
    - 自動產生縮圖（150x150 和 800x800）
    - 主圖標記（isPrimary）
    - 圖片排序（displayOrder）
    - 檔案驗證（類型、大小、尺寸）
    - 自動清理檔案（刪除時移除實體檔案）
    """
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='商品'
    )
    image = models.ImageField(
        upload_to=product_image_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp'])],
        verbose_name='圖片'
    )
    thumbnail150 = models.ImageField(
        upload_to=product_thumbnail150_upload_path,
        blank=True,
        verbose_name='縮圖 150x150'
    )
    thumbnail800 = models.ImageField(
        upload_to=product_thumbnail800_upload_path,
        blank=True,
        verbose_name='縮圖 800x800'
    )
    isPrimary = models.BooleanField(default=False, verbose_name='主圖')
    displayOrder = models.PositiveIntegerField(default=0, verbose_name='顯示順序')
    altText = models.CharField(max_length=255, blank=True, verbose_name='替代文字')
    uploadedAt = models.DateTimeField(auto_now_add=True, verbose_name='上傳時間')

    class Meta:
        verbose_name = '商品圖片'
        verbose_name_plural = '商品圖片'
        ordering = ['displayOrder', 'uploadedAt']

    def __str__(self):
        return f"{self.product.productName} - 圖片 #{self.id}"

    def clean(self):
        """驗證圖片檔案"""
        if not self.image:
            return

        # 檢查檔案大小（最大 5MB）
        if self.image.size > 5242880:
            raise ValidationError({'image': '圖片檔案大小不可超過 5MB'})

        # 使用 Pillow 驗證真實格式並檢查尺寸
        try:
            with Image.open(self.image) as img:
                img.verify()
            
            # 重新開啟以取得尺寸（verify() 後需要重新開啟）
            self.image.seek(0)
            with Image.open(self.image) as img:
                # 檢查圖片尺寸
                width, height = img.size
                if width > 4000 or height > 4000:
                    raise ValidationError({'image': '圖片尺寸不可超過 4000x4000 像素'})
            
            # 重置檔案指針以便後續使用
            self.image.seek(0)
                
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError({'image': f'無效的圖片檔案: {str(e)}'})

    def generate_thumbnails(self):
        """產生 150x150 和 800x800 縮圖"""
        if not self.image:
            return

        try:
            # validate first (may raise ValidationError)
            validate_image_file(self.image)

            name = os.path.splitext(os.path.basename(self.image.name))[0]

            fname150, content150 = make_square_thumbnail(self.image, size=150)
            self.thumbnail150.save(f"{name}_150x150.jpg", content150, save=False)

            fname800, content800 = make_preview_thumbnail(self.image, max_size=800)
            self.thumbnail800.save(f"{name}_800x800.jpg", content800, save=False)
        except Exception:
            # Don't let thumbnail errors block the save flow
            pass

    def set_as_primary(self):
        """設定此圖片為主圖，並將同商品的其他圖片主圖狀態取消"""
        if not self.isPrimary:
            # 取消同商品其他圖片的主圖狀態
            ProductImage.objects.filter(product=self.product, isPrimary=True).update(isPrimary=False)
            self.isPrimary = True
            self.save()

    def save(self, *args, **kwargs):
        """儲存前執行驗證並產生縮圖"""
        # 如果是新圖片且沒有縮圖，產生縮圖
        is_new = self.pk is None
        
        # 檢查主圖邏輯
        if self.isPrimary:
            # 如果設定為主圖，取消同商品其他圖片的主圖狀態
            ProductImage.objects.filter(product=self.product, isPrimary=True).exclude(pk=self.pk).update(isPrimary=False)
        
        super().save(*args, **kwargs)
        
        # 在儲存後產生縮圖（需要 pk 存在才能產生路徑）
        if is_new and self.image and not self.thumbnail150:
            self.generate_thumbnails()
            # 再次儲存以更新縮圖欄位（使用 update_fields 避免遞迴）
            super().save(update_fields=['thumbnail150', 'thumbnail800'])

    def delete(self, *args, **kwargs):
        """刪除時移除實體檔案"""
        # 先關閉檔案
        if self.image:
            self.image.close()
        if self.thumbnail150:
            self.thumbnail150.close()
        if self.thumbnail800:
            self.thumbnail800.close()
        
        # 記錄檔案路徑
        image_path = self.image.path if self.image else None
        thumb150_path = self.thumbnail150.path if self.thumbnail150 else None
        thumb800_path = self.thumbnail800.path if self.thumbnail800 else None
        
        # 先執行資料庫刪除
        super().delete(*args, **kwargs)
        
        # 刪除實體檔案
        try:
            if image_path and os.path.isfile(image_path):
                os.remove(image_path)
        except Exception:
            pass
        
        try:
            if thumb150_path and os.path.isfile(thumb150_path):
                os.remove(thumb150_path)
        except Exception:
            pass
        
        try:
            if thumb800_path and os.path.isfile(thumb800_path):
                os.remove(thumb800_path)
        except Exception:
            pass


@receiver(pre_delete, sender=ProductImage)
def product_image_pre_delete(sender, instance, **kwargs):
    """
    Signal：在刪除 ProductImage 之前刪除實體檔案
    """
    # 收集所有需要刪除的檔案路徑
    files_to_delete = []
    
    try:
        if instance.image and instance.image.name:
            files_to_delete.append(instance.image.path)
    except Exception:
        pass
    
    try:
        if instance.thumbnail150 and instance.thumbnail150.name:
            files_to_delete.append(instance.thumbnail150.path)
    except Exception:
        pass
    
    try:
        if instance.thumbnail800 and instance.thumbnail800.name:
            files_to_delete.append(instance.thumbnail800.path)
    except Exception:
        pass
    
    # 強制關閉所有檔案（包括 Django 內部的 file descriptor）
    try:
        if instance.image:
            if hasattr(instance.image, 'file') and instance.image.file:
                instance.image.file.close()
            instance.image.close()
    except Exception:
        pass
    
    try:
        if instance.thumbnail150:
            if hasattr(instance.thumbnail150, 'file') and instance.thumbnail150.file:
                instance.thumbnail150.file.close()
            instance.thumbnail150.close()
    except Exception:
        pass
    
    try:
        if instance.thumbnail800:
            if hasattr(instance.thumbnail800, 'file') and instance.thumbnail800.file:
                instance.thumbnail800.file.close()
            instance.thumbnail800.close()
    except Exception:
        pass
    
    # 強制垃圾回收
    import gc
    gc.collect()
    
    # 記錄需要清理的目錄
    dirs_to_clean = set()
    
    # 刪除檔案
    for file_path in files_to_delete:
        try:
            if os.path.isfile(file_path):
                # 記錄檔案所在目錄
                dirs_to_clean.add(os.path.dirname(file_path))
                os.remove(file_path)
        except PermissionError:
            # Windows 上檔案被鎖定，嘗試延遲刪除
            import time
            time.sleep(0.1)
            try:
                if os.path.isfile(file_path):
                    dirs_to_clean.add(os.path.dirname(file_path))
                    os.remove(file_path)
            except Exception:
                pass
        except Exception:
            pass
    
    # 清理空目錄（從最深層開始）
    for dir_path in sorted(dirs_to_clean, key=lambda x: -len(x)):
        try:
            # 只刪除空目錄
            if os.path.isdir(dir_path) and not os.listdir(dir_path):
                os.rmdir(dir_path)
                # 嘗試刪除父目錄（商品目錄）
                parent_dir = os.path.dirname(dir_path)
                if os.path.isdir(parent_dir) and not os.listdir(parent_dir):
                    os.rmdir(parent_dir)
        except Exception:
            pass


class Category(models.Model):
    """商品分類模型（階層式）
    - categoryName: 分類名稱
    - parent: 自我參照父分類
    - image, thumbnail150, thumbnail800: 圖片與縮圖
    - displayOrder: 同層級排序
    - description, isActive, createdAt, updatedAt
    """
    categoryName = models.CharField(max_length=200, unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')
    image = models.ImageField(upload_to=category_image_upload_path, blank=True, validators=[FileExtensionValidator(allowed_extensions=['jpg','jpeg','png','webp'])])
    thumbnail150 = models.ImageField(upload_to=category_thumbnail150_upload_path, blank=True)
    thumbnail800 = models.ImageField(upload_to=category_thumbnail800_upload_path, blank=True)
    displayOrder = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True)
    isActive = models.BooleanField(default=True)
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '商品分類'
        verbose_name_plural = '商品分類'
        ordering = ['displayOrder', 'categoryName']

    def __str__(self):
        return self.categoryName

    def clean(self):
        # 葉節點約束：如果此分類已有子分類，則不能直接被指派商品；
        # 如果已有商品，則不可新增子分類。
        from django.core.exceptions import ValidationError

        # Prevent cycles: parent cannot be self or a descendant
        if self.parent:
            ancestor = self.parent
            while ancestor:
                if ancestor == self:
                    raise ValidationError({'parent': '循環的父分類參考不被允許'})
                ancestor = getattr(ancestor, 'parent', None)

        # If this category has products (existing in DB), it must not have children
        if self.pk:
            if self.products.exists() and self.children.exists():
                raise ValidationError('此分類已有商品，無法同時擁有子分類')

    def generate_thumbnails(self):
        if not self.image:
            return

        try:
            validate_image_file(self.image)
            name = os.path.splitext(os.path.basename(self.image.name))[0]
            fname150, content150 = make_square_thumbnail(self.image, size=150)
            self.thumbnail150.save(f"{name}_150x150.jpg", content150, save=False)
            fname800, content800 = make_preview_thumbnail(self.image, max_size=800)
            self.thumbnail800.save(f"{name}_800x800.jpg", content800, save=False)
        except Exception:
            # swallow errors to avoid save failures
            pass

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        # ensure thumbnails created after initial save (so path available)
        if is_new and self.image and (not self.thumbnail150):
            self.generate_thumbnails()
            super().save(update_fields=['thumbnail150', 'thumbnail800'])

    def delete(self, *args, **kwargs):
        # close files then delete
        try:
            if self.image:
                self.image.close()
        except Exception:
            pass
        try:
            if self.thumbnail150:
                self.thumbnail150.close()
        except Exception:
            pass
        try:
            if self.thumbnail800:
                self.thumbnail800.close()
        except Exception:
            pass

        # record paths
        image_path = self.image.path if self.image and hasattr(self.image, 'path') else None
        t150 = self.thumbnail150.path if self.thumbnail150 and hasattr(self.thumbnail150, 'path') else None
        t800 = self.thumbnail800.path if self.thumbnail800 and hasattr(self.thumbnail800, 'path') else None

        super().delete(*args, **kwargs)

        # remove files
        for p in (image_path, t150, t800):
            try:
                if p and os.path.isfile(p):
                    os.remove(p)
            except Exception:
                pass