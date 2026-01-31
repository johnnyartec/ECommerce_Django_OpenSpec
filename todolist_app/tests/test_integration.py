# -*- coding: utf-8 -*-
"""
Blog 功能的整合測試

測試完整流程：
- 建立草稿 → 編輯 → 發佈 → 公開讀取
- 權限控制（登入/未登入、作者/非作者）
- XSS 防護
"""

from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from todolist_app.models import BlogPost


class BlogIntegrationTest(TestCase):
    """Blog 功能整合測試"""
    
    def setUp(self):
        """建立測試環境：使用者、客戶端"""
        self.client = Client()
        
        # 建立作者
        self.author = User.objects.create_user(
            username='author',
            email='author@example.com',
            password='authorpass'
        )
        
        # 建立另一位使用者（非作者）
        self.otherUser = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass'
        )
    
    def test_create_draft_edit_publish_public_read_flow(self):
        """測試：完整流程 - 建立草稿 → 編輯 → 發佈 → 公開讀取"""
        
        # 1. 登入作者
        self.client.login(username='author', password='authorpass')
        
        # 2. 建立草稿
        createUrl = reverse('blog_create')
        createData = {
            'title': '測試文章標題',
            'markdownContent': '# 標題\n\n這是測試內容。',
            'summary': '這是摘要',
            'tags': 'test, integration',
            'status': BlogPost.STATUS_DRAFT
        }
        response = self.client.post(createUrl, createData)
        
        # 應重導向到草稿列表
        self.assertEqual(response.status_code, 302)
        
        # 檢查草稿是否建立
        post = BlogPost.objects.get(title='測試文章標題')
        self.assertEqual(post.status, BlogPost.STATUS_DRAFT)
        self.assertEqual(post.author, self.author)
        self.assertIsNone(post.publishedAt)
        
        # 3. 編輯草稿
        editUrl = reverse('blog_edit', kwargs={'slug': post.slug})
        editData = {
            'title': '測試文章標題（已編輯）',
            'markdownContent': '# 更新的標題\n\n更新的內容。',
            'summary': '更新的摘要',
            'tags': 'test, updated',
            'status': BlogPost.STATUS_DRAFT
        }
        response = self.client.post(editUrl, editData)
        self.assertEqual(response.status_code, 302)
        
        post.refresh_from_db()
        self.assertEqual(post.title, '測試文章標題（已編輯）')
        
        # 4. 發佈文章
        publishData = editData.copy()
        publishData['status'] = BlogPost.STATUS_PUBLISHED
        response = self.client.post(editUrl, publishData)
        self.assertEqual(response.status_code, 302)
        
        post.refresh_from_db()
        self.assertEqual(post.status, BlogPost.STATUS_PUBLISHED)
        self.assertIsNotNone(post.publishedAt)
        
        # 5. 登出，以匿名訪客身分讀取
        self.client.logout()
        
        detailUrl = reverse('blog_detail', kwargs={'slug': post.slug})
        response = self.client.get(detailUrl)
        
        # 匿名訪客應能讀取已發佈文章
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '測試文章標題（已編輯）')
    
    def test_anonymous_cannot_create_post(self):
        """測試：未登入使用者無法新增文章"""
        createUrl = reverse('blog_create')
        response = self.client.get(createUrl)
        
        # 應重導向到登入頁面
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login/', response.url)
    
    def test_non_author_cannot_edit_post(self):
        """測試：非作者無法編輯他人文章"""
        # 建立作者的文章
        post = BlogPost.objects.create(
            author=self.author,
            title='作者的文章',
            markdownContent='內容',
            status=BlogPost.STATUS_DRAFT
        )
        
        # 以另一位使用者登入
        self.client.login(username='otheruser', password='otherpass')
        
        editUrl = reverse('blog_edit', kwargs={'slug': post.slug})
        response = self.client.get(editUrl)
        
        # 應被拒絕或重導向
        self.assertIn(response.status_code, [302, 403])
    
    def test_anonymous_cannot_read_draft(self):
        """測試：匿名訪客無法讀取草稿"""
        post = BlogPost.objects.create(
            author=self.author,
            title='草稿文章',
            markdownContent='草稿內容',
            status=BlogPost.STATUS_DRAFT
        )
        
        detailUrl = reverse('blog_detail', kwargs={'slug': post.slug})
        response = self.client.get(detailUrl)
        
        # 應回傳 404（草稿不公開）
        self.assertEqual(response.status_code, 404)
    
    def test_xss_prevention_in_markdown(self):
        """測試：Markdown 中的惡意腳本應被清理"""
        self.client.login(username='author', password='authorpass')
        
        # 嘗試插入惡意腳本
        maliciousMarkdown = '<script>alert("XSS")</script>\n\n# 正常內容'
        
        createData = {
            'title': 'XSS 測試',
            'markdownContent': maliciousMarkdown,
            'summary': '測試 XSS',
            'tags': 'security',
            'status': BlogPost.STATUS_PUBLISHED
        }
        
        response = self.client.post(reverse('blog_create'), createData)
        post = BlogPost.objects.get(title='XSS 測試')
        
        # htmlContent 不應包含未清理的 <script> 標籤（應被轉義或移除）
        self.assertNotIn('<script>', post.htmlContent)
        # 檢查腳本內容被轉義（&lt;script&gt; 是可接受的，因為無法執行）
        # 或者完全被移除
    
    def test_drafts_list_shows_only_author_drafts(self):
        """測試：草稿列表僅顯示當前作者的草稿"""
        # 建立作者的草稿
        BlogPost.objects.create(
            author=self.author,
            title='作者的草稿',
            markdownContent='內容',
            status=BlogPost.STATUS_DRAFT
        )
        
        # 建立其他使用者的草稿
        BlogPost.objects.create(
            author=self.otherUser,
            title='他人的草稿',
            markdownContent='內容',
            status=BlogPost.STATUS_DRAFT
        )
        
        # 以作者登入
        self.client.login(username='author', password='authorpass')
        
        draftsUrl = reverse('blog_drafts')
        response = self.client.get(draftsUrl)
        
        # 應只看到自己的草稿
        self.assertContains(response, '作者的草稿')
        self.assertNotContains(response, '他人的草稿')
    
    def test_public_list_shows_only_published_posts(self):
        """測試：公開列表僅顯示已發佈文章"""
        # 建立已發佈文章
        BlogPost.objects.create(
            author=self.author,
            title='已發佈文章',
            markdownContent='內容',
            status=BlogPost.STATUS_PUBLISHED
        )
        
        # 建立草稿
        BlogPost.objects.create(
            author=self.author,
            title='草稿文章',
            markdownContent='內容',
            status=BlogPost.STATUS_DRAFT
        )
        
        listUrl = reverse('blog_list')
        response = self.client.get(listUrl)
        
        # 應只顯示已發佈文章
        self.assertContains(response, '已發佈文章')
        self.assertNotContains(response, '草稿文章')
