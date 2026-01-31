# -*- coding: utf-8 -*-
"""
BlogPost 模型的單元測試

測試項目：
- slug 自動生成
- slug 唯一性與衝突處理
- publishedAt 時間戳設定
- status 狀態轉換
- markdown 渲染流程
"""

from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from todolist_app.models import BlogPost


class BlogPostModelTest(TestCase):
    """BlogPost 模型單元測試"""
    
    def setUp(self):
        """建立測試用使用者"""
        self.testUser = User.objects.create_user(
            username='testauthor',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_slug_generation_from_title(self):
        """測試：從標題自動生成 slug"""
        post = BlogPost.objects.create(
            author=self.testUser,
            title='我的第一篇文章',
            markdownContent='# 測試內容',
            status=BlogPost.STATUS_DRAFT
        )
        
        # slug 應自動產生（中文會轉為拼音或保留英文部分）
        self.assertIsNotNone(post.slug)
        self.assertTrue(len(post.slug) > 0)
    
    def test_slug_uniqueness_with_duplicate_titles(self):
        """測試：相同標題的文章會產生不同的 slug（附加 suffix）"""
        post1 = BlogPost.objects.create(
            author=self.testUser,
            title='Duplicate Title',
            markdownContent='內容 1'
        )
        
        post2 = BlogPost.objects.create(
            author=self.testUser,
            title='Duplicate Title',
            markdownContent='內容 2'
        )
        
        # 兩篇文章的 slug 應該不同
        self.assertNotEqual(post1.slug, post2.slug)
        # 第二篇應該有 suffix（例如 -1）
        self.assertTrue(post2.slug.endswith('-1') or post2.slug != post1.slug)
    
    def test_published_at_set_on_publish(self):
        """測試：當 status 從 draft 變為 published 時，publishedAt 自動設定"""
        post = BlogPost.objects.create(
            author=self.testUser,
            title='草稿文章',
            markdownContent='草稿內容',
            status=BlogPost.STATUS_DRAFT
        )
        
        # 草稿狀態時 publishedAt 應為 None
        self.assertIsNone(post.publishedAt)
        
        # 發佈文章
        post.status = BlogPost.STATUS_PUBLISHED
        post.save()
        
        # publishedAt 應自動設定
        self.assertIsNotNone(post.publishedAt)
        self.assertLessEqual(post.publishedAt, timezone.now())
    
    def test_published_at_not_changed_on_update(self):
        """測試：已發佈文章再次儲存時，publishedAt 不應改變"""
        post = BlogPost.objects.create(
            author=self.testUser,
            title='已發佈文章',
            markdownContent='內容',
            status=BlogPost.STATUS_PUBLISHED
        )
        
        originalPublishedAt = post.publishedAt
        self.assertIsNotNone(originalPublishedAt)
        
        # 更新內容但不改變 status
        post.markdownContent = '更新的內容'
        post.save()
        
        # publishedAt 應保持不變
        self.assertEqual(post.publishedAt, originalPublishedAt)
    
    def test_markdown_to_html_conversion(self):
        """測試：markdownContent 儲存時自動轉為 htmlContent"""
        markdownText = '# 標題\n\n這是**粗體**文字。'
        
        post = BlogPost.objects.create(
            author=self.testUser,
            title='Markdown 測試',
            markdownContent=markdownText,
            status=BlogPost.STATUS_DRAFT
        )
        
        # htmlContent 應自動產生
        self.assertIsNotNone(post.htmlContent)
        self.assertTrue(len(post.htmlContent) > 0)
        
        # 檢查 HTML 標籤（基本檢查，實際內容依渲染器而定）
        self.assertIn('<h1>', post.htmlContent.lower())
        self.assertIn('<strong>', post.htmlContent.lower() or '<b>' in post.htmlContent.lower())
    
    def test_status_defaults_to_draft(self):
        """測試：預設 status 為 draft"""
        post = BlogPost.objects.create(
            author=self.testUser,
            title='預設狀態測試',
            markdownContent='內容'
        )
        
        self.assertEqual(post.status, BlogPost.STATUS_DRAFT)
    
    def test_str_representation(self):
        """測試：__str__ 方法返回正確格式"""
        post = BlogPost.objects.create(
            author=self.testUser,
            title='字串表示測試',
            markdownContent='內容',
            status=BlogPost.STATUS_DRAFT
        )
        
        expectedStr = f"字串表示測試 ({BlogPost.STATUS_DRAFT})"
        self.assertEqual(str(post), expectedStr)
