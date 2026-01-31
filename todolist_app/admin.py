from django.contrib import admin
from .models import Todo, BlogPost, Product


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


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	"""
	商品管理介面設定。
	
	提供完整的商品 CRUD 功能，包含搜尋、篩選和欄位組織。
	"""
	list_display = ('productName', 'price', 'stockQuantity', 'isActive', 'createdAt')
	list_filter = ('isActive', 'createdAt')
	search_fields = ('productName', 'description')
	readonly_fields = ('createdAt', 'updatedAt')
	
	fieldsets = (
		('基本資訊', {
			'fields': ('productName', 'description')
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

