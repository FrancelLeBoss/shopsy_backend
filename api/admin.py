from django.contrib import admin
from django import forms
from .models import (
    Product,
    ProductVariant,
    ProductImage,
    Category,
    Rating,
    ProductVariantSize,
    SubCategory,
    Cart,
    Wishlist,
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  # Number of additional images by default


class ProductSizeInline(admin.TabularInline):
    model = ProductVariantSize  # Correctly reference the model
    extra = 1  # Number of additional sizes by default


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1  # Number of additional variants by default


class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "gender")
    search_fields = ("title", "category__title")
    list_filter = ("category", "gender")
    inlines = [ProductVariantInline]


class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ("product", "color", "price", "stock", "discount")
    list_filter = ("product", "color")
    search_fields = ("product__title", "color", "size")
    inlines = [ProductImageInline, ProductSizeInline]  # Add both inlines


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "short_desc")
    search_fields = ("title",)


class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "short_desc")
    search_fields = ("title", "short_desc")


class RatingAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "stars", "comment")
    search_fields = ("product__title", "user")


class CartForm(forms.ModelForm):
    class Meta:
        model = Cart
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.variant:
            # Filtrer les tailles en fonction de la variante sélectionnée
            self.fields["size"].queryset = ProductVariantSize.objects.filter(
                variant=self.instance.variant
            )
        else:
            # Si aucune variante n'est sélectionnée, ne pas afficher de tailles
            self.fields["size"].queryset = ProductVariantSize.objects.none()

    def clean_variant(self):
        variant = self.cleaned_data.get("variant")
        if not variant:
            raise forms.ValidationError("A variant must be selected.")
        return variant


class CartAdmin(admin.ModelAdmin):
    form = CartForm
    list_display = ("variant", "user", "quantity", "size")
    search_fields = ("variant__product__title", "user__username")
    list_filter = ("user",)
    raw_id_fields = (
        "variant",
        "user",
    )  # Utiliser raw_id_fields pour de meilleures performances
    autocomplete_fields = (
        "variant",
        "user",
    )  # Utiliser autocomplete_fields pour une meilleure UX


class WishlistAdmin(admin.ModelAdmin):
    list_display = ("product", "user")
    search_fields = ("product__title", "user__username")
    list_filter = ("user",)
    raw_id_fields = ("product", "user")  # Use raw_id_fields for better performance
    autocomplete_fields = ("product", "user")  # Use autocomplete_fields for better UX


# Register models in the Django admin
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductVariant, ProductVariantAdmin)
admin.site.register(ProductImage)
admin.site.register(ProductVariantSize)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Wishlist, WishlistAdmin)
