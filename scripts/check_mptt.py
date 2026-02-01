from todolist_app.models import Category
qs = Category.objects.all().values('id','categoryName','parent_id','lft','rght','tree_id','level')
for row in qs:
    print(row)
