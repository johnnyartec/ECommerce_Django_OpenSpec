from django.core.management.base import BaseCommand
from django.conf import settings
from todolist_app.models import Category
import os


class Command(BaseCommand):
    help = '掃描 MEDIA_ROOT/categories，刪除沒有在資料庫中被引用的圖檔與空目錄'

    def handle(self, *args, **options):
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if not media_root:
            self.stderr.write('MEDIA_ROOT 尚未設定')
            return

        base_dir = os.path.join(media_root, 'categories')
        if not os.path.isdir(base_dir):
            self.stdout.write('沒有 categories 目錄，無需清理')
            return

        # 收集 DB 中所有已知檔案路徑（相對於 MEDIA_ROOT）
        referenced = set()
        for c in Category.objects.all():
            for field in ('image', 'thumbnail150', 'thumbnail800'):
                f = getattr(c, field, None)
                try:
                    if f and f.name:
                        referenced.add(os.path.normpath(os.path.join(media_root, f.name)))
                except Exception:
                    pass

        removed_files = 0
        removed_dirs = 0

        for root, dirs, files in os.walk(base_dir, topdown=False):
            for name in files:
                path = os.path.join(root, name)
                norm = os.path.normpath(path)
                if norm not in referenced:
                    try:
                        os.remove(path)
                        removed_files += 1
                        self.stdout.write(f'Deleted orphan file: {path}')
                    except Exception as e:
                        self.stderr.write(f'Failed to delete {path}: {e}')

            # 嘗試刪除空目錄
            try:
                if not os.listdir(root):
                    os.rmdir(root)
                    removed_dirs += 1
                    self.stdout.write(f'Removed empty dir: {root}')
            except Exception:
                pass

        self.stdout.write(f'Done. Removed files: {removed_files}, removed dirs: {removed_dirs}')
