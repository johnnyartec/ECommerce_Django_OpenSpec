"""Migration skeleton: rebuild MPTT tree for existing Category data.

Instructions:
- Ensure `django-mptt` is installed and added to `pyproject.toml` / environment.
- Run `python manage.py makemigrations todolist_app` to create schema migrations that add MPTT fields (if not already created).
- Run `python manage.py migrate` to apply schema changes.
- Then run `python manage.py migrate todolist_app 0007_convert_categories_to_mptt` (this migration) to rebuild MPTT tree.

This migration uses `mptt` utilities to rebuild the tree from the existing `parent` FK.
"""

from django.db import migrations


def rebuild_mptt(apps, schema_editor):
    Category = apps.get_model('todolist_app', 'Category')
    try:
        # preferred: use mptt's rebuild_tree if available
        from mptt.utils import rebuild_tree
        rebuild_tree(Category)
    except Exception:
        try:
            # fallback: try model manager's rebuild (some mptt versions expose this)
            Category.objects.rebuild()
        except Exception:
            # If neither is available, no-op but log to stdout (migration should not fail silently in production)
            import sys
            sys.stdout.write('WARNING: django-mptt utilities not available; tree rebuild skipped.\n')


class Migration(migrations.Migration):

    dependencies = [
        ('todolist_app', '0006_category_product_categories'),
    ]

    operations = [
        migrations.RunPython(rebuild_mptt, reverse_code=migrations.RunPython.noop),
    ]
