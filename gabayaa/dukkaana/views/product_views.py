from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpRequest, Http404
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.contrib import messages

# from ..models import Cloth, Shoe, Electronic, ProductImage, Product
from ..models import ProductImage, Product, Review
from ..forms import ReviewForm

ITEMS_PER_PAGE = 12


# @cache_page(60 * 15)  # Cache for 15 minutes
def home(request):
    """
    View to display the homepage with featured products and categories.
    """
    try:
        featured_products = Product.objects.filter(
            is_active=True
        ).order_by('-rating', '-created_at')[:8]

        context = {
            'featured_products': featured_products,
        }

        return render(request, 'base.html', context)

    except Exception as e:
        return render(request, 'error.html', {
            'error_message': _('An error occurred while loading the homepage.')
        })


# @cache_page(60 * 15)  # Cache for 15 minutes
def product_list(request, category):
    """
    View to display a list of products in a specific category.
    """
    try:
        # Get all active products in the category
        products = Product.objects.filter(
            category=category,
            is_active=True
        ).select_related().prefetch_related('images')
        # Apply search filter if provided
        search_query = request.GET.get('search', '')
        if search_query:
            products = products.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Apply sorting
        sort_by = request.GET.get('sort', '-created_at')
        valid_sort_fields = ['name', '-name', 'price',
                             '-price', 'rating', '-rating', '-created_at']
        if sort_by in valid_sort_fields:
            products = products.order_by(sort_by)

        # Apply pagination
        paginator = Paginator(products, ITEMS_PER_PAGE)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context = {
            'products': page_obj,
            'category': category,
            'search_query': search_query,
            'sort_by': sort_by,
            'page_number': page_obj.number,
            # 'is_logged_in': request.user.is_authenticated
            # 'isAnon': request.user == "AnonymousUser"
        }

        return render(request, 'view/products.html', context)

    except Exception as e:
        messages.error(request, _('An error occurred while loading products.'))
        return redirect('home')
        # return render(request, 'view/products.html', context)


def cloths(request):
    """
    View to display all cloth products.
    """
    print("attempting to display cloths")
    return product_list(request, 'Huccuu')


def shoes(request):
    """
    View to display all shoe products.
    """
    return product_list(request, 'Kophee')


def electronics(request):
    """
    View to display all electronic products.
    """
    return product_list(request, 'Electrooniksii')


def renting(request):
    """
    View for the renting page.
    """
    try:
        # Add renting-specific logic here
        return render(request, 'renting.html', {})
    except Exception as e:
        # Log the error here
        return render(request, 'error.html', {
            'error_message': _('An error occurred while loading the renting page.')
        })


def buying(request):
    """
    View for the buying page.
    """
    try:
        # Add buying-specific logic here
        return render(request, 'buying.html', {})
    except Exception as e:
        # Log the error here
        return render(request, 'error.html', {
            'error_message': _('An error occurred while loading the buying page.')
        })


def product_info(request, category, id):
    """
    View to display detailed information about a specific product.
    """
    try:
        product = get_object_or_404(
            Product.objects.select_related().prefetch_related('images', 'reviews'),
            id=id,
            category=category,
            is_active=True
        )

        # Get related products from the same category
        related_products = Product.objects.filter(
            category=category,
            is_active=True
        ).exclude(id=id).select_related().prefetch_related('images')[:4]

        # Get reviews for the product
        reviews = product.reviews.all().select_related('user').order_by('-created_at')

        context = {
            'product': product,
            'related_products': related_products,
            'reviews': reviews,
        }
        print("context", context)

        return render(request, 'view/product_info.html', context)

    except Http404:
        print("Http404")
        messages.error(request, _('Product not found.'))
        return redirect('home')
    except Exception as e:
        print("Exception", e)
        messages.error(request, _(
            'An error occurred while loading the product details.'))
        return redirect('home')


# @login_required
def add_review(request, product_id):
    """
    View to add a review to a product.
    """

    product = get_object_or_404(Product, id=product_id)
    if not request.user.is_authenticated:
        messages.warning(
            request, 'Please Login to leave a review.')
        return redirect('product_info', category=product.category, id=product.id)

    existing_review = Review.objects.filter(
        product=product, user=request.user).first()
    if existing_review:
        messages.error(request, _('You have already reviewed this product.'))
        return redirect('product_info', category=product.category, id=product.id)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product_id = product_id
            review.user = request.user
            review.save()
            messages.success(request, _('Review added successfully.'))
            return redirect('product_info', category=product.category, id=product.id)
        else:
            messages.error(request, _('Please correct the errors below.'))
    else:
        form = ReviewForm()
    return render(request, 'view/add_review.html', {'product_id': product_id})


def search_results(request):
    """
    View to display search results across all products.
    """
    try:
        search_query = request.GET.get('q', '')
        if not search_query:
            return render(request, 'view/search_results.html', {
                'products': [],
                'search_query': '',
                'message': _('Please enter a search term.')
            })

        products = Product.objects.filter(
            is_active=True
        ).filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query)
        ).select_related().prefetch_related('images')

        sort_by = request.GET.get('sort', '-created_at')
        valid_sort_fields = ['name', '-name', 'price',
                             '-price', 'rating', '-rating', '-created_at']
        if sort_by in valid_sort_fields:
            products = products.order_by(sort_by)

        paginator = Paginator(products, ITEMS_PER_PAGE)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        context = {
            'products': page_obj,
            'search_query': search_query,
            'sort_by': sort_by,
        }

        return render(request, 'view/search_results.html', context)

    except Exception as e:
        return render(request, 'error.html', {
            'error_message': _('An error occurred while searching products.')
        })
