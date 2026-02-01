"""
商品功能測試
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.files.uploadedfile import SimpleUploadedFile
from todolist_app.models import Product, ProductImage
from PIL import Image
import io
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
            'isActive': True,
            # inline management form (no images)
            'images-TOTAL_FORMS': '0',
            'images-INITIAL_FORMS': '0',
            'images-MIN_NUM_FORMS': '0',
            'images-MAX_NUM_FORMS': '1000',
            '_save': 'Save',
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
            'isActive': True,
            # inline management form (no images)
            'images-TOTAL_FORMS': '0',
            'images-INITIAL_FORMS': '0',
            'images-MIN_NUM_FORMS': '0',
            'images-MAX_NUM_FORMS': '1000',
            '_save': 'Save',
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

class ProductImageModelTest(TestCase):
    """ProductImage 模型單元測試"""
    
    def setUp(self):
        """建立測試用商品"""
        self.product = Product.objects.create(
            productName='測試商品',
            description='測試商品描述',
            price=Decimal('99.99'),
            stockQuantity=100
        )
    
    def create_test_image(self, width=500, height=500, format='JPEG'):
        """建立測試用圖片"""
        image = Image.new('RGB', (width, height), color='red')
        image_io = io.BytesIO()
        image.save(image_io, format=format)
        image_io.seek(0)
        
        extension = format.lower()
        if extension == 'jpeg':
            extension = 'jpg'
        
        return SimpleUploadedFile(
            f'test_image.{extension}',
            image_io.read(),
            content_type=f'image/{extension}'
        )
    
    def test_create_product_image_successfully(self):
        """測試成功建立 ProductImage（所有欄位有效）"""
        test_image = self.create_test_image()
        product_image = ProductImage.objects.create(
            product=self.product,
            image=test_image,
            isPrimary=True,
            displayOrder=1,
            altText='測試圖片'
        )
        
        self.assertEqual(product_image.product, self.product)
        self.assertTrue(product_image.image)
        self.assertTrue(product_image.isPrimary)
        self.assertEqual(product_image.displayOrder, 1)
        self.assertEqual(product_image.altText, '測試圖片')
        
        # 清理檔案
        product_image.delete()
    
    def test_image_file_type_validation_success(self):
        """測試圖片檔案類型驗證（jpg, jpeg, png, webp 可通過）"""
        for format_type in ['JPEG', 'PNG', 'WEBP']:
            test_image = self.create_test_image(format=format_type)
            product_image = ProductImage(
                product=self.product,
                image=test_image
            )
            try:
                product_image.full_clean()
                product_image.save()
                # 驗證成功
                self.assertTrue(True)
                # 清理檔案
                product_image.delete()
            except ValidationError:
                self.fail(f'{format_type} 格式應該被接受')
    
    def test_reject_invalid_file_type(self):
        """測試拒絕無效檔案類型（.txt, .pdf）"""
        # 建立假的文字檔
        txt_file = SimpleUploadedFile(
            'test.txt',
            b'This is not an image',
            content_type='text/plain'
        )
        
        product_image = ProductImage(
            product=self.product,
            image=txt_file
        )
        
        with self.assertRaises(ValidationError):
            product_image.full_clean()
    
    def test_image_size_limit(self):
        """測試圖片大小限制（拒絕超過 5MB 的檔案）"""
        # 建立一個明確超過 5MB 的檔案
        # 創建 6MB 的二進位數據
        large_content = b'x' * (6 * 1024 * 1024)  # 6MB
        
        large_file = SimpleUploadedFile(
            'large_image.jpg',
            large_content,
            content_type='image/jpeg'
        )
        
        product_image = ProductImage(
            product=self.product,
            image=large_file
        )
        
        with self.assertRaises(ValidationError) as context:
            product_image.clean()
        
        # 驗證錯誤訊息包含大小限制
        error_messages = str(context.exception)
        self.assertTrue('5MB' in error_messages or '5242880' in error_messages or '大小' in error_messages)
    
    def test_image_dimension_limit(self):
        """測試圖片尺寸限制（拒絕超過 4000x4000 的圖片）"""
        # 建立超大尺寸圖片
        large_image = self.create_test_image(width=4500, height=4500)
        
        product_image = ProductImage(
            product=self.product,
            image=large_image
        )
        
        with self.assertRaises(ValidationError) as context:
            product_image.full_clean()
        
        # 驗證錯誤訊息包含尺寸限制
        self.assertTrue(any('4000' in str(e) for e in context.exception.messages))
    
    def test_thumbnail_generation(self):
        """測試縮圖產生（驗證 thumbnail150 和 thumbnail800 已建立）"""
        test_image = self.create_test_image(width=1200, height=1200)
        product_image = ProductImage.objects.create(
            product=self.product,
            image=test_image
        )
        
        # 驗證縮圖已建立
        self.assertTrue(product_image.thumbnail150)
        self.assertTrue(product_image.thumbnail800)
        
        # 清理檔案
        product_image.delete()
    
    def test_thumbnail_dimensions(self):
        """測試縮圖尺寸正確（150x150 和最大 800x800）"""
        test_image = self.create_test_image(width=1200, height=1200)
        product_image = ProductImage.objects.create(
            product=self.product,
            image=test_image
        )
        
        # 開啟縮圖並檢查尺寸
        with Image.open(product_image.thumbnail150.path) as thumb150:
            self.assertEqual(thumb150.width, 150)
            self.assertEqual(thumb150.height, 150)
        
        with Image.open(product_image.thumbnail800.path) as thumb800:
            # 800x800 是最大尺寸，實際可能更小（保持比例）
            self.assertLessEqual(thumb800.width, 800)
            self.assertLessEqual(thumb800.height, 800)
        
        # 清理檔案
        product_image.delete()
    
    def test_primary_image_logic(self):
        """測試主圖邏輯（設定主圖時其他圖片 isPrimary 變 False）"""
        # 建立第一張圖片作為主圖
        image1 = self.create_test_image()
        product_image1 = ProductImage.objects.create(
            product=self.product,
            image=image1,
            isPrimary=True
        )
        
        # 建立第二張圖片也設為主圖
        image2 = self.create_test_image()
        product_image2 = ProductImage.objects.create(
            product=self.product,
            image=image2,
            isPrimary=True
        )
        
        # 重新載入第一張圖片
        product_image1.refresh_from_db()
        
        # 驗證第一張圖片的 isPrimary 已變為 False
        self.assertFalse(product_image1.isPrimary)
        self.assertTrue(product_image2.isPrimary)
        
        # 清理檔案
        product_image1.delete()
        product_image2.delete()
    
    def test_file_path_contains_product_id_and_uuid(self):
        """測試檔案路徑包含商品 ID 和 UUID"""
        test_image = self.create_test_image()
        product_image = ProductImage.objects.create(
            product=self.product,
            image=test_image
        )
        
        # 驗證檔案路徑包含商品 ID
        self.assertIn(f'products/{self.product.id}/', product_image.image.name)
        
        # 驗證檔案名稱包含 UUID（8 字元十六進位）
        import re
        uuid_pattern = r'[0-9a-f]{8}_'
        self.assertTrue(re.search(uuid_pattern, product_image.image.name))
        
        # 清理檔案
        product_image.delete()
    
    def test_display_order_sorting(self):
        """測試 displayOrder 排序功能"""
        image1 = self.create_test_image()
        product_image1 = ProductImage.objects.create(
            product=self.product,
            image=image1,
            displayOrder=2
        )
        
        image2 = self.create_test_image()
        product_image2 = ProductImage.objects.create(
            product=self.product,
            image=image2,
            displayOrder=1
        )
        
        # 取得排序後的圖片列表
        images = ProductImage.objects.filter(product=self.product).order_by('displayOrder')
        
        # 驗證排序正確
        self.assertEqual(images[0].displayOrder, 1)
        self.assertEqual(images[1].displayOrder, 2)
        
        # 清理檔案
        product_image1.delete()
        product_image2.delete()
    
    def test_str_method(self):
        """測試 __str__ 方法回傳正確字串"""
        test_image = self.create_test_image()
        product_image = ProductImage.objects.create(
            product=self.product,
            image=test_image
        )
        
        # 驗證 __str__ 包含商品名稱
        str_repr = str(product_image)
        self.assertIn(self.product.productName, str_repr)
        
        # 清理檔案
        product_image.delete()


class ProductImageAdminTest(TestCase):
    """ProductImage Admin 整合測試"""
    
    def setUp(self):
        """設定測試環境"""
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        self.client.login(username='admin', password='admin123')
        
        self.product = Product.objects.create(
            productName='測試商品',
            description='測試描述',
            price=Decimal('99.99'),
            stockQuantity=50
        )
    
    def create_test_image(self, width=500, height=500):
        """建立測試用圖片"""
        image = Image.new('RGB', (width, height), color='blue')
        image_io = io.BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        
        return SimpleUploadedFile(
            'admin_test_image.jpg',
            image_io.read(),
            content_type='image/jpeg'
        )
    
    def test_superuser_can_see_product_image_inline(self):
        """測試 superuser 可以在商品編輯頁看到圖片 inline"""
        response = self.client.get(f'/admin/todolist_app/product/{self.product.id}/change/')
        self.assertEqual(response.status_code, 200)
        # 確認有 ProductImage inline 表單（使用 images 前綴）
        self.assertContains(response, 'images-TOTAL_FORMS')
    
    def test_product_list_shows_no_image_text(self):
        """測試沒有圖片的商品顯示「無圖片」"""
        response = self.client.get('/admin/todolist_app/product/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '無圖片')
    
    def test_product_list_shows_thumbnail(self):
        """測試商品列表頁顯示主圖縮圖"""
        # 建立帶圖片的商品
        test_image = self.create_test_image()
        product_image = ProductImage.objects.create(
            product=self.product,
            image=test_image,
            isPrimary=True
        )
        
        response = self.client.get('/admin/todolist_app/product/')
        self.assertEqual(response.status_code, 200)
        # 確認有 img 標籤（縮圖）
        self.assertContains(response, '<img')
        
        # 清理
        product_image.delete()
    
    def test_inline_image_preview(self):
        """測試圖片預覽功能在 inline 中正常顯示"""
        test_image = self.create_test_image()
        product_image = ProductImage.objects.create(
            product=self.product,
            image=test_image
        )
        
        response = self.client.get(f'/admin/todolist_app/product/{self.product.id}/change/')
        self.assertEqual(response.status_code, 200)
        # 確認有縮圖預覽
        self.assertContains(response, 'img')
        
        # 清理
        product_image.delete()


class ProductImageIntegrationTest(TestCase):
    """ProductImage 功能整合測試"""
    
    def setUp(self):
        """設定測試環境"""
        self.superuser = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123'
        )
        self.client.login(username='admin', password='admin123')
        
        self.product = Product.objects.create(
            productName='整合測試商品',
            description='測試描述',
            price=Decimal('199.99'),
            stockQuantity=100
        )
    
    def create_test_image(self, width=500, height=500, color='red'):
        """建立測試用圖片"""
        image = Image.new('RGB', (width, height), color=color)
        image_io = io.BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        
        return SimpleUploadedFile(
            f'integration_test_{color}.jpg',
            image_io.read(),
            content_type='image/jpeg'
        )
    
    def test_upload_multiple_images_and_adjust_order(self):
        """測試上傳多張圖片並調整排序"""
        # 建立多張圖片
        image1 = self.create_test_image(color='red')
        product_image1 = ProductImage.objects.create(
            product=self.product,
            image=image1,
            displayOrder=2
        )
        
        image2 = self.create_test_image(color='green')
        product_image2 = ProductImage.objects.create(
            product=self.product,
            image=image2,
            displayOrder=1
        )
        
        image3 = self.create_test_image(color='blue')
        product_image3 = ProductImage.objects.create(
            product=self.product,
            image=image3,
            displayOrder=3
        )
        
        # 驗證排序
        images = self.product.images.order_by('displayOrder')
        self.assertEqual(images[0].id, product_image2.id)
        self.assertEqual(images[1].id, product_image1.id)
        self.assertEqual(images[2].id, product_image3.id)
        
        # 調整排序
        product_image3.displayOrder = 0
        product_image3.save()
        
        images = self.product.images.order_by('displayOrder')
        self.assertEqual(images[0].id, product_image3.id)
        
        # 清理
        product_image1.delete()
        product_image2.delete()
        product_image3.delete()
    
    def test_change_primary_image(self):
        """測試變更主圖（從圖片 A 改為圖片 B）"""
        image1 = self.create_test_image(color='red')
        product_image1 = ProductImage.objects.create(
            product=self.product,
            image=image1,
            isPrimary=True
        )
        
        image2 = self.create_test_image(color='green')
        product_image2 = ProductImage.objects.create(
            product=self.product,
            image=image2,
            isPrimary=False
        )
        
        # 驗證初始狀態
        self.assertTrue(product_image1.isPrimary)
        self.assertFalse(product_image2.isPrimary)
        
        # 變更主圖
        product_image2.set_as_primary()
        
        product_image1.refresh_from_db()
        product_image2.refresh_from_db()
        
        # 驗證變更後狀態
        self.assertFalse(product_image1.isPrimary)
        self.assertTrue(product_image2.isPrimary)
        
        # 清理
        product_image1.delete()
        product_image2.delete()
    
    def test_validation_error_handling(self):
        """測試檔案驗證失敗的錯誤處理"""
        # 建立無效檔案
        invalid_file = SimpleUploadedFile(
            'test.txt',
            b'This is not an image',
            content_type='text/plain'
        )
        
        product_image = ProductImage(
            product=self.product,
            image=invalid_file
        )
        
        with self.assertRaises(ValidationError) as context:
            product_image.full_clean()
        
        # 驗證錯誤訊息
        self.assertTrue(len(context.exception.messages) > 0)
    
    def test_product_image_relationship(self):
        """測試圖片與商品的關聯關係正確"""
        test_image = self.create_test_image()
        product_image = ProductImage.objects.create(
            product=self.product,
            image=test_image
        )
        
        # 驗證正向關聯
        self.assertEqual(product_image.product.id, self.product.id)
        
        # 驗證反向關聯
        self.assertIn(product_image, self.product.images.all())
        
        # 驗證商品圖片數量
        self.assertEqual(self.product.images.count(), 1)
        
        # 清理
        product_image.delete()
    
    def test_alt_text_storage_and_display(self):
        """測試 altText 欄位儲存和顯示"""
        test_image = self.create_test_image()
        alt_text = '這是一張測試圖片的替代文字'
        
        product_image = ProductImage.objects.create(
            product=self.product,
            image=test_image,
            altText=alt_text
        )
        
        # 驗證儲存
        self.assertEqual(product_image.altText, alt_text)
        
        # 從資料庫重新載入並驗證
        product_image.refresh_from_db()
        self.assertEqual(product_image.altText, alt_text)
        
        # 清理
        product_image.delete()