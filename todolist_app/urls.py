from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from . import views_api
from django.views.generic import TemplateView

urlpatterns = [
    # Todo 相關路由
    path('hello/', views.hello_world, name='hello'),
    path('complete/<int:todo_id>/', views.complete_todo, name='complete_todo'),
    path('delete/<int:todo_id>/', views.delete_todo, name='delete_todo'),
    
    # 認證相關路由
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup, name='signup'),
    
    # CSRF 測試（開發用）
    path('csrf-test/', TemplateView.as_view(template_name='csrf_test.html'), name='csrf_test'),
    
    # Blog 相關路由
    path('blog/', views.blog_list, name='blog_list'),
    path('blog/new/', views.blog_create, name='blog_create'),
    path('blog/drafts/', views.blog_drafts, name='blog_drafts'),
    path('blog/<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('blog/<slug:slug>/edit/', views.blog_edit, name='blog_edit'),
    # API: categories and product-category assignment
    path('api/categories/', views_api.api_categories_list, name='api_categories_list'),
    path('api/categories/<int:category_id>/products/', views_api.api_category_products, name='api_category_products'),
    path('api/products/<int:product_id>/categories/', views_api.api_assign_product_categories, name='api_assign_product_categories'),
]