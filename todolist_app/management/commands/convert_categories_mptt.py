from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.db import transaction
from django.conf import settings
import json
import os
from pathlib import Path


class Command(BaseCommand):
    help = 'Backup Category data, rebuild MPTT tree, verify and optionally rollback from backup.'

    def add_arguments(self, parser):
        parser.add_argument('--backup', nargs='?', const=True, default=None,
                            help='Create a JSON backup before conversion. Optionally provide a file path.')
        parser.add_argument('--convert', action='store_true', help='Run MPTT tree rebuild (requires django-mptt and MPTT fields present).')
        parser.add_argument('--verify', action='store_true', help='Verify counts before/after conversion.')
        parser.add_argument('--rollback', nargs=1, help='Rollback categories from provided backup JSON file.')
        parser.add_argument('--no-input', action='store_true', help='Do not ask for confirmation.')

    def _default_backup_path(self):
        ts = timezone.now().strftime('%Y%m%d%H%M%S')
        return os.path.join(getattr(settings, 'BASE_DIR', '.'), 'backups', f'categories_backup_{ts}.json')

    def handle(self, *args, **options):
        from todolist_app.models import Category

        backup_opt = options.get('backup')
        do_convert = options.get('convert')
        do_verify = options.get('verify')
        rollback_args = options.get('rollback')
        no_input = options.get('no_input')

        if not (backup_opt or do_convert or do_verify or rollback_args):
            raise CommandError('請至少指定一個操作：--backup | --convert | --verify | --rollback <file>')

        if rollback_args:
            backup_file = rollback_args[0]
            return self._rollback_from_backup(backup_file, no_input)

        # Backup step
        backup_path = None
        if backup_opt:
            if backup_opt is True:
                backup_path = self._default_backup_path()
            else:
                backup_path = backup_opt

            backup_dir = os.path.dirname(backup_path)
            Path(backup_dir).mkdir(parents=True, exist_ok=True)

            self.stdout.write(f'Backing up Category data to {backup_path}...')
            data = list(Category.objects.all().values('id', 'categoryName', 'parent_id', 'displayOrder', 'description', 'isActive'))
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump({'metadata': {'created': timezone.now().isoformat(), 'count': len(data)}, 'items': data}, f, ensure_ascii=False, indent=2)
            self.stdout.write(self.style.SUCCESS(f'Backup written: {backup_path} ({len(data)} items)'))

        # Verify before conversion
        before_count = Category.objects.count()
        if do_verify:
            self.stdout.write(f'Category count: {before_count}')

        if do_convert:
            # Safety prompt
            if not no_input:
                confirm = input('Proceed to rebuild MPTT tree? This requires mptt fields present in schema. (y/N): ')
                if confirm.lower() != 'y':
                    self.stdout.write('Aborted by user.')
                    return

            # Attempt rebuild
            self.stdout.write('Rebuilding MPTT tree...')
            try:
                with transaction.atomic():
                    # preferred API
                    from mptt.utils import rebuild_tree
                    rebuild_tree(Category)
                self.stdout.write(self.style.SUCCESS('MPTT tree rebuilt using mptt.utils.rebuild_tree'))
            except Exception:
                try:
                    # fallback: manager method
                    Category.objects.rebuild()
                    self.stdout.write(self.style.SUCCESS('MPTT tree rebuilt using Category.objects.rebuild()'))
                except Exception as e:
                    raise CommandError(f'Failed to rebuild MPTT tree: {e}')

            after_count = Category.objects.count()
            self.stdout.write(f'Before: {before_count} categories; After: {after_count} categories')

            if do_verify:
                if before_count != after_count:
                    raise CommandError('Count mismatch after rebuild; aborting (counts differ)')
                else:
                    self.stdout.write(self.style.SUCCESS('Verification passed: counts match'))

        self.stdout.write(self.style.SUCCESS('Operation completed.'))

    def _rollback_from_backup(self, backup_file, no_input=False):
        from todolist_app.models import Category

        if not os.path.exists(backup_file):
            raise CommandError(f'Backup file not found: {backup_file}')

        if not no_input:
            confirm = input(f'Rollback will DELETE all current Category rows and restore from {backup_file}. Continue? (y/N): ')
            if confirm.lower() != 'y':
                self.stdout.write('Rollback aborted by user.')
                return

        with open(backup_file, 'r', encoding='utf-8') as f:
            payload = json.load(f)
        items = payload.get('items', [])
        id_map = {it['id']: it for it in items}

        self.stdout.write(f'Restoring {len(items)} Category records from backup...')

        # Delete existing categories
        with transaction.atomic():
            Category.objects.all().delete()

            # First pass: create categories without parent
            created = {}
            for it in items:
                obj = Category(id=it['id'], categoryName=it['categoryName'], displayOrder=it.get('displayOrder', 0), description=it.get('description', ''), isActive=it.get('isActive', True))
                obj.save()
                created[it['id']] = obj

            # Second pass: set parent relationships
            for it in items:
                pid = it.get('parent_id')
                if pid:
                    child = created.get(it['id'])
                    parent = created.get(pid)
                    if parent:
                        child.parent = parent
                        child.save()

        self.stdout.write(self.style.SUCCESS('Rollback complete.'))