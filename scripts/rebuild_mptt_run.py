import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from todolist_app.models import Category

try:
    from mptt.utils import rebuild_tree
    rebuild_tree(Category)
    print('rebuild_tree succeeded')
except Exception as e:
    try:
        Category.objects.rebuild()
        print('Category.objects.rebuild succeeded')
    except Exception as e2:
        print('rebuild failed:', e, e2)
        sys.exit(1)
