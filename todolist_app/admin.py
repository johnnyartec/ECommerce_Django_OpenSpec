from django.contrib import admin
from django.utils.html import format_html
from .models import Todo, BlogPost, Product, ProductImage, Category
try:
	from mptt.admin import MPTTModelAdmin
except Exception:
	MPTTModelAdmin = admin.ModelAdmin


# 註冊 Todo
admin.site.register(Todo)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
	# 顯示在 admin 列表的欄位
	list_display = ('title', 'author', 'status', 'publishedAt', 'createdAt')
	list_filter = ('status', 'author')
	search_fields = ('title', 'markdownContent', 'summary')
	prepopulated_fields = {'slug': ('title',)}
	readonly_fields = ('htmlContent', 'publishedAt', 'createdAt', 'updatedAt')


class ProductImageInline(admin.TabularInline):
	"""
	商品圖片內嵌管理介面。
	
	允許在商品編輯頁面直接管理商品圖片。
	"""
	model = ProductImage
	extra = 1
	fields = ('image_preview', 'image', 'isPrimary', 'displayOrder', 'altText')
	readonly_fields = ('image_preview', 'uploadedAt')
	ordering = ('-isPrimary', 'displayOrder')
	
	def image_preview(self, obj):
		"""
		顯示圖片縮圖預覽。
		
		如果圖片已上傳且縮圖存在，顯示 150x150 縮圖。
		"""
		if obj.thumbnail150:
			return format_html(
				'<img src="{}" width="150" height="150" style="object-fit: cover;" />',
				obj.thumbnail150.url
			)
		return '-'
	
	image_preview.short_description = '預覽'


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	"""
	商品管理介面設定。
	
	提供完整的商品 CRUD 功能，包含搜尋、篩選和欄位組織。
	"""
	list_display = ('productName', 'primary_image_preview', 'price', 'stockQuantity', 'isActive', 'createdAt', 'categories_display')
	list_filter = ('isActive', 'createdAt', 'categories')
	search_fields = ('productName', 'description')
	readonly_fields = ('primary_image_preview', 'createdAt', 'updatedAt')
	inlines = [ProductImageInline]
	filter_horizontal = ('categories',)
	
	fieldsets = (
		(None, {
			'fields': (),
			'description': '💡 提示：請先儲存商品後，即可在下方上傳圖片。'
		}),
		('基本資訊', {
			'fields': ('productName', 'description', 'primary_image_preview', 'categories')
		}),
		('價格與庫存', {
			'fields': ('price', 'stockQuantity')
		}),
		('狀態', {
			'fields': ('isActive',)
		}),
		('時間戳記', {
			'fields': ('createdAt', 'updatedAt'),
			'classes': ('collapse',)
		}),
	)
	
	def primary_image_preview(self, obj):
		"""
		顯示商品主要圖片的預覽。
		
		在列表頁面和詳情頁面顯示主要圖片的縮圖。
		"""
		primary_image = obj.images.filter(isPrimary=True).first()
		if primary_image and primary_image.thumbnail150:
			return format_html(
				'<img src="{}" width="150" height="150" style="object-fit: cover;" />',
				primary_image.thumbnail150.url
			)
		return '無圖片'
	
	primary_image_preview.short_description = '主要圖片'

	def categories_display(self, obj):
		cats = obj.categories.all()
		if not cats:
			return '-'
		return ', '.join([c.categoryName for c in cats])

	categories_display.short_description = 'Categories'


@admin.register(Category)
class CategoryAdmin(MPTTModelAdmin):
	list_display = ('categoryName', 'parent', 'product_count', 'displayOrder', 'image_preview')
	search_fields = ('categoryName',)
	list_filter = ('parent', 'isActive')
	readonly_fields = ('image_preview', 'createdAt', 'updatedAt')
	fields = ('categoryName', 'parent', 'description', 'displayOrder', 'image', 'image_preview', 'isActive')

	def product_count(self, obj):
		return obj.products.count()

	def image_preview(self, obj):
		if obj.thumbnail150:
			return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.thumbnail150.url)
		return '-'

	image_preview.short_description = '圖片預覽'
	product_count.short_description = '商品數'

