with open("c:/Django Task/Project/myenv/bkshop/customerapp/views.py", "a") as f:
    f.write("""
def product_details(request, pk):
    prod = get_object_or_404(product, id=pk)
    reviews = ProductReview.objects.filter(product=prod)
    related_products = product.objects.filter(product_category=prod.product_category).exclude(id=prod.id)[:4]
    
    if reviews.exists():
        total_rating = sum(r.rating for r in reviews)
        prod.rating = round(total_rating / reviews.count(), 1)
        prod.review_count = reviews.count()
    
    context = {
        "product": prod,
        "reviews": reviews,
        "related_products": related_products,
    }
    return render(request, "customerapp/product_details.html", context)
""")
