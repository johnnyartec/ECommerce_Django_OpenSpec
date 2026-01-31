from django import forms
from .models import Todo
from .models import BlogPost


# 文章表單：允許作者輸入標題、Markdown 內容、摘要與標籤
# 註解均以繁體中文撰寫，欄位名稱採駝峰式命名
class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'markdownContent', 'summary', 'tags', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'markdownContent': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 20}),
            'summary': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'tags': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'tag1,tag2'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['title'] # 我們只需要使用者輸入標題
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'flex-1 bg-transparent outline-none placeholder-gray-400 text-gray-700',
                'placeholder': '新增一個待辦事項...'
            })
        }