from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from ..models import Product, Review
from ..forms import ReviewForm


@login_required
def add_review(request, product_id):
    """
    View to add a review for a product.
    """
    product = get_object_or_404(Product, id=product_id)

    # Check if user has already reviewed this product
    existing_review = Review.objects.filter(
        user=request.user, product=product).first()
    if existing_review:
        messages.warning(request, _('You have already reviewed this product.'))
        return redirect('product_detail', id=product_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, _(
                'Your review has been added successfully.'))
            return redirect('product_detail', id=product_id)
    else:
        form = ReviewForm()

    return render(request, 'reviews/add_review.html', {
        'form': form,
        'product': product
    })


@login_required
def edit_review(request, review_id):
    """
    View to edit an existing review.
    """
    review = get_object_or_404(Review, id=review_id, user=request.user)

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, _(
                'Your review has been updated successfully.'))
            return redirect('product_detail', id=review.product.id)
    else:
        form = ReviewForm(instance=review)

    return render(request, 'reviews/edit_review.html', {
        'form': form,
        'review': review
    })


@login_required
def delete_review(request, review_id):
    """
    View to delete a review.
    """
    review = get_object_or_404(Review, id=review_id, user=request.user)
    product_id = review.product.id

    if request.method == 'POST':
        review.delete()
        messages.success(request, _(
            'Your review has been deleted successfully.'))
        return redirect('product_detail', id=product_id)

    return render(request, 'reviews/delete_review.html', {
        'review': review
    })
