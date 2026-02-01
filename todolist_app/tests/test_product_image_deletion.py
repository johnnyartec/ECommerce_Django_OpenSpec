"""
商品圖片檔案刪除測試
"""
from decimal import Decimal
from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from todolist_app.models import Product, ProductImage
from PIL import Image
import io
import os


class ProductImageDeletionTest(TestCase):
    """ProductImage 檔案刪除測試"""
    
    def setUp(self):
        """建立測試用商品"""
        self.product = Product.objects.create(
            productName='測試商品',
            description='測試商品描述',
            price=Decimal('99.99'),
            stockQuantity=100
        )
    
    def create_test_image(self, width=500, height=500):
        """建立測試用圖片"""
        image = Image.new('RGB', (width, height), color='green')
        image_io = io.BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        
        return SimpleUploadedFile(
            'test_deletion.jpg',
            image_io.read(),
            content_type='image/jpeg'
        )
    
    def test_delete_product_image_removes_files(self):
        """測試刪除 ProductImage 時實體檔案被移除"""
        test_image = self.create_test_image()
        product_image = ProductImage.objects.create(
            product=self.product,
            image=test_image
        )
        
        # 記錄檔案路徑
        image_path = product_image.image.path
        
        # 驗證檔案存在
        self.assertTrue(os.path.exists(image_path))
        
        # 刪除物件
        product_image.delete()
        
        # 驗證檔案已被刪除
        self.assertFalse(os.path.exists(image_path))
    
    def test_delete_product_image_removes_thumbnails(self):
        """測試刪除 ProductImage 時縮圖檔案被移除"""
        test_image = self.create_test_image()
        product_image = ProductImage.objects.create(
            product=self.product,
            image=test_image
        )
        
        # 記錄縮圖路徑
        thumb150_path = product_image.thumbnail150.path
        thumb800_path = product_image.thumbnail800.path
        
        # 驗證縮圖存在
        self.assertTrue(os.path.exists(thumb150_path))
        self.assertTrue(os.path.exists(thumb800_path))
        
        # 刪除物件
        product_image.delete()
        
        # 驗證縮圖已被刪除
        self.assertFalse(os.path.exists(thumb150_path))
        self.assertFalse(os.path.exists(thumb800_path))
    
    def test_cascade_delete_removes_all_files(self):
        """測試級聯刪除（刪除 Product 時所有圖片檔案被清理）"""
        # 建立多張圖片
        image1 = self.create_test_image()
        product_image1 = ProductImage.objects.create(
            product=self.product,
            image=image1
        )
        
        image2 = self.create_test_image()
        product_image2 = ProductImage.objects.create(
            product=self.product,
            image=image2
        )
        
        # 記錄所有檔案路徑
        paths = [
            product_image1.image.path,
            product_image1.thumbnail150.path,
            product_image1.thumbnail800.path,
            product_image2.image.path,
            product_image2.thumbnail150.path,
            product_image2.thumbnail800.path,
        ]
        
        # 驗證所有檔案存在
        for path in paths:
            self.assertTrue(os.path.exists(path), f'檔案應存在: {path}')
        
        # 關閉所有檔案
        product_image1.image.close()
        product_image1.thumbnail150.close()
        product_image1.thumbnail800.close()
        product_image2.image.close()
        product_image2.thumbnail150.close()
        product_image2.thumbnail800.close()
        
        # 刪除商品（級聯刪除所有圖片）
        self.product.delete()
        
        # 驗證所有檔案已被刪除（給點時間讓 Windows 釋放檔案）
        import time
        time.sleep(0.5)
        
        for path in paths:
            self.assertFalse(os.path.exists(path), f'檔案應已刪除: {path}')
    
    def test_delete_nonexistent_file_does_not_fail(self):
        """測試檔案不存在時刪除不會失敗"""
        test_image = self.create_test_image()
        product_image = ProductImage.objects.create(
            product=self.product,
            image=test_image
        )
        
        # 記錄檔案路徑
        image_path = product_image.image.path
        thumb150_path = product_image.thumbnail150.path
        thumb800_path = product_image.thumbnail800.path
        
        # 關閉檔案
        product_image.image.close()
        product_image.thumbnail150.close()
        product_image.thumbnail800.close()
        
        # 手動刪除實體檔案
        if os.path.exists(image_path):
            os.remove(image_path)
        if os.path.exists(thumb150_path):
            os.remove(thumb150_path)
        if os.path.exists(thumb800_path):
            os.remove(thumb800_path)
        
        # 嘗試刪除物件（不應該拋出異常）
        try:
            product_image.delete()
            # 驗證成功刪除
            self.assertFalse(ProductImage.objects.filter(id=product_image.id).exists())
        except Exception as e:
            self.fail(f'刪除不存在的檔案時不應拋出異常: {e}')
    
    def test_file_cleanup_with_temporary_test_files(self):
        """使用臨時檔案進行測試（避免污染實際 media 目錄）"""
        from django.conf import settings
        
        test_image = self.create_test_image()
        product_image = ProductImage.objects.create(
            product=self.product,
            image=test_image
        )
        
        # 驗證檔案在 media 目錄內
        media_root = str(settings.MEDIA_ROOT)
        self.assertTrue(product_image.image.path.startswith(media_root))
        
        # 清理測試檔案
        product_image.delete()
        
        # 驗證清理成功
        self.assertFalse(os.path.exists(product_image.image.path))
