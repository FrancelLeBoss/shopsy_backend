from rest_framework import serializers
from .models import (
    Product,
    ProductVariant,
    ProductVariantSize,
    ProductImage,
    Category,
    SubCategory,
    Rating,
    Cart,
    Wishlist,
)
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    """Serializer pour les utilisateurs."""

    class Meta:
        model = User
        fields = ["id", "username", "email"]


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer pour les images de produit."""

    image = serializers.ImageField(use_url=True)

    class Meta:
        model = ProductImage
        fields = ["id", "image", "mainImage", "variant"]


class ProductVariantSizeSerializer(serializers.ModelSerializer):
    """Serializer pour les tailles de variantes de produit."""

    class Meta:
        model = ProductVariantSize
        fields = ["id", "variant", "size"]


class ProductVariantSerializer(serializers.ModelSerializer):
    sizes = ProductVariantSizeSerializer(many=True, read_only=True)
    images = ProductImageSerializer(
        many=True, read_only=True
    )  # Utiliser le sérialiseur des images

    class Meta:
        model = ProductVariant
        fields = ["id", "color", "price", "stock", "sizes", "images", "discount"]


class CategorySerializer(serializers.ModelSerializer):
    """Serializer pour les catégories."""

    class Meta:
        model = Category
        fields = ["id", "title", "short_desc", "long_desc"]


class SubCategorySerializer(serializers.ModelSerializer):
    """Serializer pour les sous-catégories."""

    category = CategorySerializer(read_only=True)  # Inclure la catégorie associée

    class Meta:
        model = SubCategory
        fields = ["id", "title", "short_desc", "long_desc", "category"]


class ProductSerializer(serializers.ModelSerializer):
    variants = ProductVariantSerializer(
        many=True, read_only=True
    )  # Inclure les variantes

    class Meta:
        model = Product
        fields = [
            "id",
            "title",
            "short_desc",
            "long_desc",
            "category",
            "subCategory",
            "gender",
            "variants",
        ]


class RatingSerializer(serializers.ModelSerializer):
    """Serializer pour les évaluations de produit."""

    class Meta:
        model = Rating
        fields = [
            "id",
            "product",
            "user",
            "stars",
            "comment",
            "created_at",
            "updated_at",
        ]


class CartSerializer(serializers.ModelSerializer):
    """Serializer pour le panier."""

    class Meta:
        model = Cart
        fields = ["id", "variant", "user", "quantity", "size"]


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer pour la liste de souhaits."""

    class Meta:
        model = Wishlist
        fields = ["id", "variant", "user"]
