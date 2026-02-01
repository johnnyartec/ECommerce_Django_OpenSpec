from django.test import TestCase
from todolist_app.models import Category
from mptt.utils import rebuild_tree


class MPTTBehaviorTests(TestCase):
    def setUp(self):
        # Create a small category tree
        self.root = Category.objects.create(categoryName='Root')
        self.child_a = Category.objects.create(categoryName='Child A', parent=self.root)
        self.child_b = Category.objects.create(categoryName='Child B', parent=self.root)
        self.grandchild = Category.objects.create(categoryName='Grandchild', parent=self.child_a)

    def test_rebuild_populates_mptt_fields(self):
        # Ensure rebuild populates lft/rght/level/tree_id
        rebuild_tree(Category)
        a = Category.objects.get(pk=self.child_a.pk)
        g = Category.objects.get(pk=self.grandchild.pk)

        # MPTT provides level attribute and numeric tree fields
        self.assertIsNotNone(a.level)
        self.assertIsNotNone(g.level)
        self.assertTrue(hasattr(a, 'lft'))
        self.assertTrue(hasattr(a, 'rght'))
        self.assertTrue(hasattr(a, 'tree_id'))

        # level relation: grandchild level = child level + 1
        self.assertEqual(g.level, a.level + 1)

    def test_get_descendants_and_ancestors(self):
        rebuild_tree(Category)
        root = Category.objects.get(pk=self.root.pk)
        descendants = list(root.get_descendants())
        descendant_names = [c.categoryName for c in descendants]
        self.assertIn('Child A', descendant_names)
        self.assertIn('Child B', descendant_names)
        self.assertIn('Grandchild', descendant_names)

        # ancestors of grandchild
        gc = Category.objects.get(pk=self.grandchild.pk)
        ancestors = [a.categoryName for a in gc.get_ancestors()]
        self.assertIn('Root', ancestors)
        self.assertIn('Child A', ancestors)

    def test_query_ordering_and_count(self):
        rebuild_tree(Category)
        # ensure product counts unaffected and tree functions available
        roots = list(Category.objects.root_nodes())
        self.assertTrue(any(r.categoryName == 'Root' for r in roots))
        # total count
        self.assertEqual(Category.objects.count(), 4)
