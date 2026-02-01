"""Add explicit MPTT fields and populate them from existing parent FK.

This migration adds integer fields used by django-mptt (lft, rght, tree_id, level)
and then runs a Python step to rebuild the MPTT tree using django-mptt utilities.

Notes:
- Ensure `django-mptt` is installed before applying this migration.
- This migration is intended to be applied only once; test in staging first.
"""

from django.db import migrations, models


def populate_mptt(apps, schema_editor):
    Category = apps.get_model('todolist_app', 'Category')
    try:
        from mptt.utils import rebuild_tree
        rebuild_tree(Category)
    except Exception:
        try:
            Category.objects.rebuild()
        except Exception as e:
            import sys
            sys.stdout.write(f'WARNING: failed to rebuild mptt tree: {e}\n')


class Migration(migrations.Migration):

    dependencies = [
        ('todolist_app', '0007_convert_categories_to_mptt'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='lft',
            field=models.PositiveIntegerField(default=0, db_index=True),
        ),
        migrations.AddField(
            model_name='category',
            name='rght',
            field=models.PositiveIntegerField(default=0, db_index=True),
        ),
        migrations.AddField(
            model_name='category',
            name='tree_id',
            field=models.PositiveIntegerField(default=0, db_index=True),
        ),
        migrations.AddField(
            model_name='category',
            name='level',
            field=models.PositiveIntegerField(default=0, db_index=True),
        ),
        migrations.RunPython(populate_mptt, reverse_code=migrations.RunPython.noop),
    ]
