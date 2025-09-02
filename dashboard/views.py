from django.shortcuts import render
from products.models import Product, Category
from orders.models import Order

def custom_dashboard(request):
    context = {
        'total_products': Product.objects.count(),
        'total_orders': Order.objects.count(),
        'total_categories': Category.objects.count(),
        'new_orders_count': Order.objects.filter(status='pending').count(),
        'recent_products': Product.objects.order_by('-created_at')[:5],
        'recent_orders': Order.objects.order_by('-created_at')[:5],
    }
    return render(request, 'admin/custom_dashboard.html', context)
