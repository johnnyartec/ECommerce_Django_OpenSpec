from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
import os


ALLOWED_EXTENSIONS = ('jpg', 'jpeg', 'png', 'webp')
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_DIMENSIONS = (4000, 4000)


def _get_extension(name):
    return os.path.splitext(name)[1].lstrip('.').lower() if name else ''


def validate_image_file(file_obj, *, allowed_exts=ALLOWED_EXTENSIONS, max_bytes=MAX_FILE_SIZE, max_dims=MAX_DIMENSIONS):
    """Validate uploaded image file: extension, size, and dimensions.

    Raises `ValidationError` on failure.
    """
    # file_obj may be a Django FieldFile or UploadedFile
    name = getattr(file_obj, 'name', None)
    ext = _get_extension(name)
    if ext not in allowed_exts:
        raise ValidationError({'image': f'不支援的檔案類型: .{ext}'})

    size = getattr(file_obj, 'size', None)
    if size is not None and size > max_bytes:
        raise ValidationError({'image': f'圖片檔案大小不可超過 {max_bytes} bytes'})

    try:
        # PIL can accept file-like objects
        file_obj.seek(0)
    except Exception:
        pass

    try:
        with Image.open(file_obj) as img:
            img.verify()
        try:
            file_obj.seek(0)
        except Exception:
            pass
        with Image.open(file_obj) as img:
            width, height = img.size
            if width > max_dims[0] or height > max_dims[1]:
                raise ValidationError({'image': f'圖片尺寸不可超過 {max_dims[0]}x{max_dims[1]} 像素'})
    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError({'image': f'無效的圖片檔案: {str(e)}'})


def make_square_thumbnail(file_obj, size=150, quality=85):
    """Return (filename, ContentFile) for a square thumbnail of given size."""
    try:
        file_obj.seek(0)
    except Exception:
        pass

    with Image.open(file_obj) as img:
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        thumb = img.copy()
        thumb.thumbnail((size, size), Image.Resampling.LANCZOS)
        thumb_square = Image.new('RGB', (size, size), (255, 255, 255))
        offset = ((size - thumb.width) // 2, (size - thumb.height) // 2)
        thumb_square.paste(thumb, offset)

        bio = BytesIO()
        thumb_square.save(bio, format='JPEG', quality=quality)
        bio.seek(0)
        filename = f"thumb_{size}x{size}.jpg"
        return filename, ContentFile(bio.read())


def make_preview_thumbnail(file_obj, max_size=800, quality=85):
    """Return (filename, ContentFile) for a preview thumbnail keeping aspect ratio."""
    try:
        file_obj.seek(0)
    except Exception:
        pass

    with Image.open(file_obj) as img:
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background

        thumb = img.copy()
        thumb.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)

        bio = BytesIO()
        thumb.save(bio, format='JPEG', quality=quality)
        bio.seek(0)
        filename = f"preview_{max_size}x{max_size}.jpg"
        return filename, ContentFile(bio.read())
