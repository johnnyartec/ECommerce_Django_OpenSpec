"""
商品功能測試
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from todolist_app.models import Product
import time


class ProductModelTest(TestCase):
    """Product 模型單元測試"""

    def test_create_product_successfully(self):
        """測試成功建立商品（所有欄位有效）"""
        product = Product.objects.create(
            productName='測試商品',
            description='這是測試商品描述',
            price=Decimal('99.99'),
            stockQuantity=100,
            isActive=True
        )
        self.assertEqual(product.productName, '測試商品')
        self.assertEqual(product.description, '這是測試商品描述')
        self.assertEqual(product.price, Decimal('99.99'))
        self.assertEqual(product.stockQuantity, 100)
        self.assertTrue(product.isActive)

    def test_product_name_required(self):
        """測試 productName 必填驗證"""
        product = Product(
            productName='',
            price=Decimal('10.00')
        )
        with self.assertRaises(ValidationError) as context:
            product.clean()
        self.assertIn('productName', context.exception.message_dict)

    def test_product_name_max_length(self):
        """測試 productName 長度限制"""
        long_name = 'A' * 201
        product = Product(
            productName=long_name,
            price=Decimal('10.00')
        )
        with self.assertRaises(ValidationError) as context:
            product.clean()
        self.assertIn('productName', context.exception.message_dict)

    def test_price_non_negative(self):
        """測試 price 非負數驗證"""
        product = Product(
            productName='測試商品',
            price=Decimal('-10.00')
        )
        with self.assertRaises(ValidationError) as context:
            product.clean()
        self.assertIn('price', context.exception.message_dict)

    def test_stock_quantity_default_value(self):
        """測試 stockQuantity 預設值為 0"""
        product = Product.objects.create(
            productName='測試商品',
            price=Decimal('10.00')
        )
        self.assertEqual(product.stockQuantity, 0)

    def test_is_active_default_value(self):
        """測試 isActive 預設值為 True"""
        product = Product.objects.create(
            productName='測試商品',
            price=Decimal('10.00')
        )
        self.assertTrue(product.isActive)

    def test_created_at_auto_set(self):
        """測試 createdAt 自動設定"""
        before = timezone.now()
        product = Product.objects.create(
            productName='測試商品',
            price=Decimal('10.00')
        )
        after = timezone.now()
        self.assertIsNotNone(product.createdAt)
        self.assertGreaterEqual(product.createdAt, before)
        self.assertLessEqual(product.createdAt, after)

    def test_updated_at_auto_update(self):
        """測試 updatedAt 自動更新"""
        product = Product.objects.create(
            productName='測試商品',
            price=Decimal('10.00')
        )
        original_updated_at = product.updatedAt
        
        # 等待一小段時間確保時間戳記不同
        time.sleep(0.1)
        
        product.productName = '更新後的商品'
        product.save()
        product.refresh_from_db()
        
        self.assertGreater(product.updatedAt, original_updated_at)

    def test_str_method_returns_product_name(self):
        """測試 __str__ 方法回傳 productName"""
        product = Product.objects.create(
            productName='測試商品',
            price=Decimal('10.00')
        )
        self.assertEqual(str(product), '測試商品')

    def test_description_xss_cleaning_removes_script(self):
        """測試 description 的 XSS 清理（script 標籤被移除或轉義）"""
        product = Product.objects.create(
            productName='測試商品',
            description='<script>alert("XSS")</script><p>安全內容</p>',
            price=Decimal('10.00')
        )
        # script 標籤應該被轉義或移除，不會以原始形式存在
        self.assertNotIn('<script>', product.description)
        self.assertNotIn('</script>', product.description)
        # 安全內容應該保留
        self.assertIn('<p>安全內容</p>', product.description)

    def test_description_preserves_safe_html(self):
        """測試 description 的安全 HTML 保留（p, strong 等標籤）"""
        safe_html = '<p>段落</p><strong>粗體</strong><em>斜體</em><ul><li>項目</li></ul>'
        product = Product.objects.create(
            productName='測試商品',
            description=safe_html,
            price=Decimal('10.00')
        )
        self.assertIn('<p>', product.description)
        self.assertIn('<strong>', product.description)
        self.assertIn('<em>', product.description)
        self.assertIn('<ul>', product.description)
        self.assertIn('<li>', product.description)


class ProductAdminTest(TestCase):
    """Product Admin 整合測試"""

    def setUp(self):
        """設定測試用的使用者"""
        # 建立 superuser
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        
        # 建立 staff 使用者
        self.staff_user = User.objects.create_user(
            username='staff',
            email='staff@test.com',
            password='staff123'
        )
        self.staff_user.is_staff = True
        self.staff_user.save()
        
        # 建立普通使用者
        self.normal_user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='user123'
        )
        
        # 建立測試商品
        self.product = Product.objects.create(
            productName='測試商品',
            description='測試描述',
            price=Decimal('99.99'),
            stockQuantity=50
        )

    def test_unauthenticated_user_cannot_access_admin(self):
        """測試未登入使用者無法存取商品管理頁面"""
        response = self.client.get('/admin/todolist_app/product/')
        # 應該重新導向到登入頁面
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response.url)

    def test_non_staff_user_cannot_access_admin(self):
        """測試非 staff 使用者無法存取商品管理頁面"""
        self.client.login(username='user', password='user123')
        response = self.client.get('/admin/todolist_app/product/')
        # 應該重新導向到登入頁面
        self.assertEqual(response.status_code, 302)

    def test_staff_user_can_view_product_list(self):
        """測試 staff 使用者可以檢視商品列表"""
        self.client.login(username='admin', password='admin123')
        response = self.client.get('/admin/todolist_app/product/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '測試商品')

    def test_user_with_add_permission_can_create_product(self):
        """測試具備 add_product 權限的使用者可以建立商品"""
        from django.contrib.auth.models import Permission
        
        add_permission = Permission.objects.get(codename='add_product')
        self.staff_user.user_permissions.add(add_permission)
        
        self.client.login(username='staff', password='staff123')
        response = self.client.get('/admin/todolist_app/product/add/')
        self.assertEqual(response.status_code, 200)

    def test_user_without_add_permission_cannot_create_product(self):
        """測試沒有 add_product 權限的使用者無法建立商品"""
        # staff_user 沒有任何權限
        self.client.login(username='staff', password='staff123')
        response = self.client.get('/admin/todolist_app/product/add/')
        self.assertEqual(response.status_code, 403)

    def test_user_with_change_permission_can_edit_product(self):
        """測試具備 change_product 權限的使用者可以修改商品"""
        from django.contrib.auth.models import Permission
        
        change_permission = Permission.objects.get(codename='change_product')
        self.staff_user.user_permissions.add(change_permission)
        
        self.client.login(username='staff', password='staff123')
        response = self.client.get(f'/admin/todolist_app/product/{self.product.id}/change/')
        self.assertEqual(response.status_code, 200)

    def test_user_without_change_permission_cannot_edit_product(self):
        """測試沒有 change_product 權限的使用者無法修改商品"""
        self.client.login(username='staff', password='staff123')
        response = self.client.get(f'/admin/todolist_app/product/{self.product.id}/change/')
        self.assertEqual(response.status_code, 403)

    def test_user_with_delete_permission_can_delete_product(self):
        """測試具備 delete_product 權限的使用者可以刪除商品"""
        from django.contrib.auth.models import Permission
        
        delete_permission = Permission.objects.get(codename='delete_product')
        self.staff_user.user_permissions.add(delete_permission)
        
        self.client.login(username='staff', password='staff123')
        response = self.client.get(f'/admin/todolist_app/product/{self.product.id}/delete/')
        self.assertEqual(response.status_code, 200)

    def test_user_without_delete_permission_cannot_delete_product(self):
        """測試沒有 delete_product 權限的使用者無法刪除商品"""
        self.client.login(username='staff', password='staff123')
        response = self.client.get(f'/admin/todolist_app/product/{self.product.id}/delete/')
        self.assertEqual(response.status_code, 403)


class ProductIntegrationTest(TestCase):
    """Product 功能整合測試"""

    def setUp(self):
        """設定測試環境"""
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        self.client.login(username='admin', password='admin123')

    def test_complete_product_creation_flow(self):
        """測試完整的商品建立流程（透過 admin 介面）"""
        response = self.client.post('/admin/todolist_app/product/add/', {
            'productName': '新商品',
            'description': '新商品描述',
            'price': '49.99',
            'stockQuantity': '20',
            'isActive': True
        })
        
        # 應該重新導向到商品列表
        self.assertEqual(response.status_code, 302)
        
        # 驗證商品已建立
        product = Product.objects.get(productName='新商品')
        self.assertEqual(product.price, Decimal('49.99'))
        self.assertEqual(product.stockQuantity, 20)

    def test_product_list_search_functionality(self):
        """測試商品列表頁面的搜尋功能"""
        Product.objects.create(productName='蘋果手機', price=Decimal('999'))
        Product.objects.create(productName='香蕉', price=Decimal('5'))
        
        response = self.client.get('/admin/todolist_app/product/?q=蘋果')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '蘋果手機')
        self.assertNotContains(response, '香蕉')

    def test_product_list_filter_by_is_active(self):
        """測試商品列表頁面的篩選功能（isActive）"""
        Product.objects.create(productName='啟用商品', price=Decimal('10'), isActive=True)
        Product.objects.create(productName='停用商品', price=Decimal('10'), isActive=False)
        
        response = self.client.get('/admin/todolist_app/product/?isActive__exact=1')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '啟用商品')

    def test_product_detail_page_shows_all_fields(self):
        """測試商品詳細頁面顯示所有欄位"""
        product = Product.objects.create(
            productName='測試商品',
            description='測試描述',
            price=Decimal('99.99'),
            stockQuantity=50
        )
        
        response = self.client.get(f'/admin/todolist_app/product/{product.id}/change/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '測試商品')
        self.assertContains(response, '測試描述')
        self.assertContains(response, '99.99')
        self.assertContains(response, '50')

    def test_product_update_flow_with_validation(self):
        """測試商品更新流程（包含驗證錯誤處理）"""
        product = Product.objects.create(
            productName='原始商品',
            price=Decimal('50')
        )
        
        # 成功更新
        response = self.client.post(f'/admin/todolist_app/product/{product.id}/change/', {
            'productName': '更新後的商品',
            'description': '',
            'price': '75.00',
            'stockQuantity': '100',
            'isActive': True
        })
        
        product.refresh_from_db()
        self.assertEqual(product.productName, '更新後的商品')
        self.assertEqual(product.price, Decimal('75.00'))

    def test_product_delete_flow(self):
        """測試商品刪除流程（包含確認對話框）"""
        product = Product.objects.create(
            productName='待刪除商品',
            price=Decimal('10')
        )
        
        # 顯示刪除確認頁面
        response = self.client.get(f'/admin/todolist_app/product/{product.id}/delete/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '待刪除商品')
        
        # 確認刪除
        response = self.client.post(f'/admin/todolist_app/product/{product.id}/delete/', {
            'post': 'yes'
        })
        
        # 驗證商品已刪除
        self.assertFalse(Product.objects.filter(id=product.id).exists())

    def test_soft_delete_by_setting_is_active_false(self):
        """測試軟刪除功能（修改 isActive 為 False）"""
        product = Product.objects.create(
            productName='測試商品',
            price=Decimal('10'),
            isActive=True
        )
        
        # 停用商品
        product.isActive = False
        product.save()
        product.refresh_from_db()
        
        self.assertFalse(product.isActive)
        # 商品仍存在於資料庫
        self.assertTrue(Product.objects.filter(id=product.id).exists())

    def test_reactivate_product(self):
        """測試重新啟用商品（修改 isActive 為 True）"""
        product = Product.objects.create(
            productName='測試商品',
            price=Decimal('10'),
            isActive=False
        )
        
        # 重新啟用
        product.isActive = True
        product.save()
        product.refresh_from_db()
        
        self.assertTrue(product.isActive)
