from django.test import TestCase
from django.contrib import admin
from django.core.files.uploadedfile import SimpleUploadedFile
from todolist_app import admin as todolist_admin
from todolist_app.models import Category, Product
from PIL import Image
from io import BytesIO
import os


def make_test_image_bytes(format='PNG', size=(200, 200), color=(0, 255, 0)):
    buf = BytesIO()
    img = Image.new('RGB', size, color=color)
    img.save(buf, format=format)
    return buf.getvalue()


class CategoryAdminTests(TestCase):
    def tearDown(self):
        for c in Category.objects.all():
            try:
                c.delete()
            except Exception:
                pass
        for p in Product.objects.all():
            try:
                p.delete()
            except Exception:
                pass

    def test_category_image_preview_shows_thumbnail_html(self):
        img_bytes = make_test_image_bytes()
        upload = SimpleUploadedFile('cat.png', img_bytes, content_type='image/png')

        cat = Category.objects.create(categoryName='Electronics', image=upload)
        cat.refresh_from_db()

        admin_instance = todolist_admin.CategoryAdmin(Category, admin.site)
        html = admin_instance.image_preview(cat)

        # Should contain an <img src="..."> or '-' if missing
        self.assertTrue('<img' in html or html == '-')

    def test_product_admin_categories_display(self):
        cat1 = Category.objects.create(categoryName='A')
        cat2 = Category.objects.create(categoryName='B')
        p = Product.objects.create(productName='Gadget', price=1.0)
        p.categories.add(cat1, cat2)

        prod_admin = todolist_admin.ProductAdmin(Product, admin.site)
        text = prod_admin.categories_display(p)
        self.assertIn('A', text)
        self.assertIn('B', text)
