from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .models import BlogPost, Todo
from .forms import BlogPostForm, TodoForm


# ==================== Blog 相關視圖 ====================

# 列出公開文章
def blog_list(request):
    posts = BlogPost.objects.filter(status=BlogPost.STATUS_PUBLISHED)
    return render(request, 'blog/list.html', {'posts': posts})


# 顯示單篇文章（公開）
def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status=BlogPost.STATUS_PUBLISHED)
    return render(request, 'blog/detail.html', {'post': post})


# 新增或編輯文章（僅限登入使用者）
@login_required
def blog_create(request):
    # 使用者可以選擇儲存為草稿或發佈
    if request.method == 'POST':
        form = BlogPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, '文章已儲存')
            if post.status == BlogPost.STATUS_PUBLISHED:
                return redirect('blog_detail', slug=post.slug)
            return redirect('blog_drafts')
    else:
        form = BlogPostForm()
    return render(request, 'blog/form.html', {'form': form})


@login_required
def blog_edit(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    # 只有作者可編輯
    if post.author != request.user:
        messages.error(request, '沒有權限編輯該文章')
        return redirect('blog_list')

    if request.method == 'POST':
        form = BlogPostForm(request.POST, instance=post)
        if form.is_valid():
            post = form.save()
            messages.success(request, '文章已更新')
            if post.status == BlogPost.STATUS_PUBLISHED:
                return redirect('blog_detail', slug=post.slug)
            return redirect('blog_drafts')
    else:
        form = BlogPostForm(instance=post)

    return render(request, 'blog/form.html', {'form': form, 'post': post})


@login_required
def blog_drafts(request):
    drafts = BlogPost.objects.filter(author=request.user, status=BlogPost.STATUS_DRAFT)
    return render(request, 'blog/drafts.html', {'drafts': drafts})


# ==================== 認證與註冊視圖 ====================

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('hello')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})


# ==================== Todo 相關視圖 ====================

@login_required
def hello_world(request):
    if request.method == "POST":
        form = TodoForm(request.POST)
        if form.is_valid():
            todo = form.save(commit=False)
            todo.user = request.user
            todo.save()
            return redirect('hello')
    
    form = TodoForm()
    todos = Todo.objects.filter(user=request.user).order_by('-created_at')
    
    context = {'todos': todos, 'form': form, 'message': f'{request.user.username} 的待辦清單'}
    return render(request, 'hello.html', context)


@login_required
def complete_todo(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id, user=request.user)
    
    if todo.user != request.user:
        return HttpResponseForbidden("你沒有權限操作這項任務！")
    
    todo.completed = True
    todo.save()
    return redirect('hello')


@login_required
def delete_todo(request, todo_id):
    todo = get_object_or_404(Todo, id=todo_id, user=request.user)
    
    if todo.user != request.user:
        return HttpResponseForbidden("你沒有權限刪除這項任務！")
    
    todo.delete()
    return redirect('hello')
