from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django import forms


def product_image_path(instance, filename):
    """Stocker l’image principale d'un produit dans un dossier basé sur son ID."""
    return f"products/{instance.id}/{filename}"


def variant_image_path(instance, filename):
    """Stocker les images des variantes dans un sous-dossier spécifique."""
    return f"products/{instance.product.id}/{instance.color}/{filename}"


class Category(models.Model):
    title = models.CharField(max_length=255)
    img = models.ImageField(upload_to="categories/")
    short_desc = models.TextField(blank=True, null=True)
    long_desc = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title


class SubCategory(models.Model):
    title = models.CharField(max_length=255)
    short_desc = models.TextField(blank=True, null=True)
    long_desc = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Product(models.Model):
    """Produit de base, qui regroupe les variantes."""

    title = models.CharField(max_length=255)
    short_desc = models.TextField(blank=True, null=True)
    long_desc = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subCategory = models.ForeignKey(
        SubCategory, on_delete=models.CASCADE, null=True, blank=True
    )  # Permettre des valeurs nulles
    gender = models.CharField(
        max_length=50, choices=[("m", "M"), ("f", "F"), ("b", "B")]
    )

    def __str__(self):
        return self.title


class ProductVariant(models.Model):
    """Variante d’un produit avec sa couleur, taille, stock et prix."""

    product = models.ForeignKey(
        Product, related_name="variants", on_delete=models.CASCADE
    )
    color = models.CharField(max_length=50)  # Example: Red, Blue, Green
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=0)
    discount = models.IntegerField(default=0)  # Discount percentage

    def __str__(self):
        return f"{self.product.title} - {self.color} - {self.price}"

    def get_images(self):
        """Retourne les images associées à la couleur de cette variante."""
        return self.product.images.filter(color=self.color)

    def get_sizes(self):
        """Retourne les tailles disponibles pour cette variante."""
        return self.product.variants.values_list("size", flat=True).distinct()


class ProductVariantSize(models.Model):
    """Model to manage available sizes for each variant."""

    variant = models.ForeignKey(
        ProductVariant,
        related_name="sizes",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    size = models.CharField(max_length=50)  # Example: S, M, L, XL

    def __str__(self):
        return f"{self.variant.product.title} - {self.size}"


class ProductImage(models.Model):
    """Stocke plusieurs images pour une couleur spécifique d’un produit."""

    product = models.ForeignKey(
        Product, related_name="images", on_delete=models.CASCADE
    )
    variant = models.ForeignKey(
        ProductVariant,
        related_name="images",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )  # Add this field to link images to a specific variant
    color = models.CharField(
        max_length=50, default=""
    )  # La couleur associée aux images
    mainImage = models.BooleanField(default=False)
    image = models.ImageField(upload_to=variant_image_path)

    def __str__(self):
        main_image_text = "principale " if self.mainImage else ""
        return f"Image {main_image_text}de {self.product.title} ({self.color})"


class Rating(models.Model):
    """Avis des utilisateurs avec une note et un commentaire."""

    product = models.ForeignKey(
        Product, related_name="ratings", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        "auth.User", related_name="ratings", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now=True)
    updated_at = models.DateTimeField(auto_now=True)
    stars = models.IntegerField(default=0)  # Note sur 5
    comment = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.product.title} - {self.stars}★ by {self.user}"


class Cart(models.Model):
    """Modèle de panier d'achat."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)  # Quantité du produit dans le panier
    size = models.ForeignKey(
        ProductVariantSize, on_delete=models.CASCADE, null=True, blank=True
    )  # Taille de la variante
    created_at = models.DateTimeField(auto_now_add=True)  # Date d'ajout au panier
    updated_at = models.DateTimeField(auto_now=True)  # Date de mise à jour

    class Meta:
        unique_together = (
            "user",
            "variant",
            "size",
        )  # Empêche les doublons pour le même utilisateur, variante et taille

    def __str__(self):
        return f"Panier de {self.user.username} - {self.variant.product} - ({self.quantity})"

    def clean(self):
        if not self.variant:
            raise forms.ValidationError("A variant must be selected for the cart item.")


class Wishlist(models.Model):
    """Modèle de liste de souhaits."""

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(
        auto_now_add=True
    )  # Date d'ajout à la liste de souhaits
    updated_at = models.DateTimeField(auto_now=True)  # Date de mise à jour

    def __str__(self):
        return f"Liste de souhaits de {self.user.username} - {self.product.title}"
