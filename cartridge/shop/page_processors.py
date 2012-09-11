from django.db.models import Sum
from django.template.defaultfilters import slugify

from mezzanine.conf import settings
from mezzanine.pages.page_processors import processor_for
from mezzanine.utils.views import paginate

from cartridge.shop.models import Category, Product, ProductOption, ProductVariation


@processor_for(Category)
def category_processor(request, page):
    """
    Add paging/sorting to the products for the category.
    """
    settings.use_editable()
    products = Product.objects.published(for_user=request.user
                                ).filter(page.category.filters()).distinct()
    sort_options = [(slugify(option[0]), option[1])
                    for option in settings.SHOP_PRODUCT_SORT_OPTIONS]
    sort_by = request.GET.get("sort", sort_options[0][1])
    if sort_by == "position":
        products_list = products.order_by("-available_in_stock", sort_by, "-date_added")
    else:
        products_list = products.order_by("-available_in_stock", sort_by)
    products = paginate(products_list,
                        request.GET.get("page", 1),
                        settings.SHOP_PER_PAGE_CATEGORY,
                        settings.MAX_PAGING_LINKS)
    products.sort_by = sort_by
    # get stocked products
    product_stock = {}
    prod_ids = [x.id for x in products.object_list]
    _product_stock = ProductVariation.objects.filter(product__id__in=prod_ids).order_by('product__id').values('product').annotate(Sum('num_in_stock'))
    for row in _product_stock:
        product_stock[row['product']] = row['num_in_stock__sum']
    # inject product colors:
    product_options = ProductOption.objects.all()
    dict_options = {}
    for opt in product_options:
        dict_options[opt.name] = opt.image
    for product in products.object_list:
        product.stock = product_stock[product.id]
        if product.variations.all().count() > 1:
            product.colors = []
            for variation in product.variations.all():
                try:
                    if variation.option1:
                        product.colors.append(dict_options[variation.option1])
                except:
                    pass
    return {"products": products}
