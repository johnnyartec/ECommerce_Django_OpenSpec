from django.test import TestCase, Client
from todolist_app.models import Category, Product


class CategoryIntegrationTests(TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        for p in Product.objects.all():
            try:
                p.delete()
            except Exception:
                pass
        for c in Category.objects.all():
            try:
                c.delete()
            except Exception:
                pass

    def test_category_products_include_children(self):
        # Build category tree: Root -> A -> A1
        root = Category.objects.create(categoryName='Root')
        a = Category.objects.create(categoryName='A', parent=root)
        a1 = Category.objects.create(categoryName='A1', parent=a)

        # Products assigned at different levels
        p_root = Product.objects.create(productName='RootProduct', price=1.0)
        p_a = Product.objects.create(productName='AProduct', price=2.0)
        p_a1 = Product.objects.create(productName='A1Product', price=3.0)

        p_root.categories.add(root)
        p_a.categories.add(a)
        p_a1.categories.add(a1)

        # Request products for 'A' including children
        resp = self.client.get(f'/app/api/categories/{a.pk}/products/?include_children=1')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        ids = {item['productName'] for item in data.get('results', [])}
        # Should include AProduct and A1Product (and not RootProduct)
        self.assertIn('AProduct', ids)
        self.assertIn('A1Product', ids)
        self.assertNotIn('RootProduct', ids)

    def test_assign_product_to_category_with_children_rejected(self):
        parent = Category.objects.create(categoryName='Parent')
        child = Category.objects.create(categoryName='Child', parent=parent)
        product = Product.objects.create(productName='Gizmo', price=5.0)

        resp = self.client.post(f'/app/api/products/{product.pk}/categories/', data='{"category_ids": [%d]}' % parent.pk, content_type='application/json')
        self.assertEqual(resp.status_code, 400)
        body = resp.json()
        self.assertIn('bad_category_ids', body)
