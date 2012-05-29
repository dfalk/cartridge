
from django.template.defaultfilters import slugify

from mezzanine.conf import settings
from mezzanine.pages.page_processors import processor_for
from mezzanine.utils.views import paginate

from cartridge.shop.models import Category, Product, Vendor


@processor_for(Category)
def category_processor(request, page):
    """
    Add paging/sorting to the products for the category.
    """
    settings.use_editable()
    products = Product.objects.published(for_user=request.user
                                ).filter(page.category.filters()).distinct()
    vendors = Vendor.objects.published(for_user=request.user)
    vendor_filter = request.GET.get("vendor", "")
    if vendor_filter:
        products = products.filter(vendor__slug=vendor_filter)
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
    products.vendor_filter = vendor_filter
    return {"products": products, "vendors": vendors}
