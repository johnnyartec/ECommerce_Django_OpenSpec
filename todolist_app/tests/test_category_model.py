from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from todolist_app.models import Category, Product
from PIL import Image
from io import BytesIO
import os


def make_test_image(format='PNG', size=(200, 200), color=(255, 0, 0)):
    buf = BytesIO()
    img = Image.new('RGB', size, color=color)
    img.save(buf, format=format)
    return buf.getvalue()


class CategoryModelTests(TestCase):
    def tearDown(self):
        # Clean up created categories to remove files
        for c in Category.objects.all():
            try:
                c.delete()
            except Exception:
                pass

    def test_category_thumbnail_generation(self):
        img_bytes = make_test_image()
        upload = SimpleUploadedFile('cat.png', img_bytes, content_type='image/png')

        cat = Category.objects.create(categoryName='Toys', image=upload)
        # refresh from db to ensure fields populated
        cat.refresh_from_db()

        # Thumbnails should be created and have file paths
        self.assertTrue(bool(cat.thumbnail150.name))
        self.assertTrue(bool(cat.thumbnail800.name))

        # Files should exist on disk
        if hasattr(cat.thumbnail150, 'path'):
            self.assertTrue(os.path.isfile(cat.thumbnail150.path))
        if hasattr(cat.thumbnail800, 'path'):
            self.assertTrue(os.path.isfile(cat.thumbnail800.path))

    def test_leaf_node_constraint_detects_products_and_children(self):
        parent = Category.objects.create(categoryName='Parent')
        child = Category.objects.create(categoryName='Child', parent=parent)

        p = Product.objects.create(productName='Toy Car', price=9.99)
        p.categories.add(parent)

        # Now parent has both products and children; full_clean should raise
        with self.assertRaises(ValidationError):
            parent.full_clean()
