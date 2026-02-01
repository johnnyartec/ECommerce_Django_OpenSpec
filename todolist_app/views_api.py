import json
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_http_methods
from .models import Category, Product


def category_to_dict(cat):
    return {
        'id': cat.pk,
        'categoryName': cat.categoryName,
        'parent': cat.parent.pk if cat.parent else None,
        'thumbnail150': cat.thumbnail150.url if cat.thumbnail150 else None,
        'thumbnail800': cat.thumbnail800.url if cat.thumbnail800 else None,
        'displayOrder': cat.displayOrder,
    }


@require_http_methods(['GET'])
def api_categories_list(request):
    cats = Category.objects.filter(isActive=True).order_by('displayOrder', 'categoryName')
    data = [category_to_dict(c) for c in cats]
    return JsonResponse({'results': data})


def _gather_descendant_ids(cat):
    ids = [cat.pk]
    for child in cat.children.all():
        ids.extend(_gather_descendant_ids(child))
    return ids


@require_http_methods(['GET'])
def api_category_products(request, category_id):
    include_children = request.GET.get('include_children') in ('1', 'true', 'True')
    cat = get_object_or_404(Category, pk=category_id)
    if include_children:
        ids = _gather_descendant_ids(cat)
        products = Product.objects.filter(categories__in=ids).distinct()
    else:
        products = Product.objects.filter(categories=cat)

    out = []
    for p in products:
        out.append({
            'id': p.pk,
            'productName': p.productName,
            'price': str(p.price),
        })
    return JsonResponse({'results': out})


@require_http_methods(['POST'])
def api_assign_product_categories(request, product_id):
    try:
        payload = json.loads(request.body.decode('utf-8'))
    except Exception:
        return HttpResponseBadRequest('Invalid JSON')

    if not isinstance(payload, dict) or 'category_ids' not in payload:
        return HttpResponseBadRequest('Expecting {"category_ids": [1,2,...]}')

    ids = payload.get('category_ids')
    if not isinstance(ids, list):
        return HttpResponseBadRequest('category_ids must be a list')

    product = get_object_or_404(Product, pk=product_id)

    # Validate each category: cannot assign to a category that has children
    cats = Category.objects.filter(pk__in=ids)
    bad = [c.pk for c in cats if c.children.exists()]
    if bad:
        return JsonResponse({'error': 'Cannot assign product to categories that have children', 'bad_category_ids': bad}, status=400)

    product.categories.set(cats)
    return JsonResponse({'status': 'ok', 'assigned_ids': [c.pk for c in cats]})
