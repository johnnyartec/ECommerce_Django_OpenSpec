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
    def add_mptt_fields_if_missing(apps, schema_editor):
        Category = apps.get_model('todolist_app', 'Category')
        table_name = Category._meta.db_table
        cursor = schema_editor.connection.cursor()
        try:
            existing = [c.name for c in schema_editor.connection.introspection.get_table_description(cursor, table_name)]
        except Exception:
            existing = []

        def add_field_if_missing(field_name):
            if field_name in existing:
                return
            field = models.PositiveIntegerField(default=0, db_index=True)
            field.set_attributes_from_name(field_name)
            schema_editor.add_field(Category, field)

        for name in ('lft', 'rght', 'tree_id', 'level'):
            add_field_if_missing(name)

        # attempt to populate/rebuild the MPTT tree
        try:
            from mptt.utils import rebuild_tree
            rebuild_tree(Category)
        except Exception:
            try:
                Category.objects.rebuild()
            except Exception:
                import sys
                sys.stdout.write('WARNING: mptt rebuild not available; manual rebuild may be required.\n')

    operations = [
        migrations.RunPython(add_mptt_fields_if_missing, reverse_code=migrations.RunPython.noop),
    ]
