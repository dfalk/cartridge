
from django.template.defaultfilters import slugify

from mezzanine.conf import settings
from mezzanine.pages.page_processors import processor_for
from mezzanine.utils.views import paginate

from cartridge.shop.models import Category, Product, ProductOption


@processor_for(Category)
def category_processor(request, page):
    """
    Add paging/sorting to the products for the category.
    """
    settings.use_editable()

    product_options = ProductOption.objects.all()
    dict_options = {}
    for opt in product_options:
        dict_options[opt.name] = opt.image

    products = Product.objects.published(for_user=request.user
                                ).filter(page.category.filters()).distinct()


    sort_options = [(slugify(option[0]), option[1])
                    for option in settings.SHOP_PRODUCT_SORT_OPTIONS]
    sort_by = request.GET.get("sort", sort_options[0][1])
    if sort_by == "position":
        products_list = products.order_by(sort_by, "-date_added")
    else:
        products_list = products.order_by(sort_by)
    products = paginate(products_list,
                        request.GET.get("page", 1),
                        settings.SHOP_PER_PAGE_CATEGORY,
                        settings.MAX_PAGING_LINKS)
    products.sort_by = sort_by
    for product in products.object_list:
        product.colors = []
        for variation in product.variations.all():
            try:
                if variation.option1:
                    product.colors.append(dict_options[variation.option1])
            except:
                pass
        product.save()
    return {"products": products}
