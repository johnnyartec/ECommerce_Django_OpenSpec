from django.db import models  # 👈 修正這裡，改為 import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils import timezone
import bleach
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