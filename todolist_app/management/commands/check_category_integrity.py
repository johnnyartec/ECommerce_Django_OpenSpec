from django.core.management.base import BaseCommand
from todolist_app.models import Category
from django.db import transaction


class Command(BaseCommand):
    help = '檢查 Category 的葉節點完整性，並可選擇性修復 (--fix)'

    def add_arguments(self, parser):
        parser.add_argument('--fix', action='store_true', help='嘗試自動修復可自動處理的問題')

    def handle(self, *args, **options):
        fix = options.get('fix', False)
        problems = []

        for c in Category.objects.all():
            has_products = c.products.exists()
            has_children = c.children.exists()
            if has_products and has_children:
                problems.append((c, has_products, has_children))

        if not problems:
            self.stdout.write('No integrity issues found.')
            return

        self.stdout.write(f'Found {len(problems)} category integrity issues:')
        for c, has_products, has_children in problems:
            self.stdout.write(f'- Category {c.pk} "{c.categoryName}": products={has_products} children={has_children}')

        if fix:
            self.stdout.write('Attempting automatic fixes: clearing product assignments from parent categories')
            fixed = 0
            with transaction.atomic():
                for c, _, _ in problems:
                    try:
                        c.products.clear()
                        fixed += 1
                    except Exception as e:
                        self.stderr.write(f'Failed to fix category {c.pk}: {e}')

            self.stdout.write(f'Auto-fixed {fixed} categories (cleared product assignments).')
        else:
            self.stdout.write('Run with --fix to attempt automatic fixes (this will clear product assignments on offending categories).')
