"""Re-add MPTT integer fields and populate them.

This migration restores the MPTT integer fields removed by a prior migration,
then attempts to rebuild the tree using django-mptt utilities.
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
        except Exception:
            import sys
            sys.stdout.write('WARNING: mptt rebuild not available; manual rebuild may be required.\n')


class Migration(migrations.Migration):

    dependencies = [
        ('todolist_app', '0009_remove_category_level_remove_category_lft_and_more'),
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
