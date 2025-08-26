from rest_framework import serializers
import uuid
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
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail

# from django.contrib.auth.models import User

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, style={"input_type": "password"}
    )
    newsletter_subscription = serializers.BooleanField(default=False)

    class Meta:
        model = User
        fields = ("username", "email", "password", "newsletter_subscription")
        extra_kwargs = {"email": {"required": True}}

    def validate(self, attrs):
        # Validate unique username/email (though ModelSerializer often handles this with unique=True)
        if User.objects.filter(username=attrs["username"]).exists():
            raise ValidationError({"username": "Ce nom d'utilisateur est déjà pris."})
        if User.objects.filter(email=attrs["email"]).exists():
            raise ValidationError({"email": "Cet email est déjà enregistré."})
        if len(attrs["username"]) < 3:
            raise ValidationError(
                {
                    "username": "Le nom d'utilisateur doit comporter au moins 3 caractères."
                }
            )
        if len(attrs["password"]) < 6:
            raise ValidationError(
                {"password": "Le mot de passe doit comporter au moins 6 caractères."}
            )

        return attrs

    def create(self, validated_data):
        # 1. Create user with is_active=False
        # IMPORTANT: Do NOT use validated_data.pop('is_active', False)
        # The backend dictates this, not the frontend.
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
            is_active=False,  # Always set to False for email verification flow
            newsletter_subscription=validated_data.get(
                "newsletter_subscription", False
            ),
        )

        # 2. Generate and store email verification token
        user.email_verification_token = uuid.uuid4()
        user.email_verification_sent_at = timezone.now()
        user.save()

        # 3. Send activation email
        # Configure your email settings in settings.py (EMAIL_BACKEND, EMAIL_HOST, etc.)
        # Make sure your frontend's activation page URL is correct
        # Example: http://localhost:3000/activate?token=... or http://yourdomain.com/activate?token=...
        # If your backend directly handles the activation link, it would be http://localhost:8000/api/activate/<token>/

        # This is an example of the backend generating a link that points to the FRONTEND
        # The frontend will then call the backend's /api/activate/<token>/ endpoint.
        # ADJUST THIS URL TO MATCH YOUR FRONTEND'S ACTIVATION ROUTE!
        frontend_activation_url = f"{settings.FRONTEND_BASE_URL}activate?token={user.email_verification_token}"

        try:
            send_mail(
                "Activez votre compte sur Shopsy!",
                f"Cher(e) {user.username},\n\n"
                f"Bienvenue sur Shopsy! Pour activer votre compte, veuillez cliquer sur le lien ci-dessous :\n\n"
                f"{frontend_activation_url}\n\n"  # Link to frontend activation page
                f"Ce lien expirera dans 24 heures.\n\n"
                f"Si vous n'avez pas créé de compte sur Shopsy, veuillez ignorer cet email.\n\n"
                f"Merci,\nL'équipe Shopsy",
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
        except Exception as e:
            user.delete()  # Clean up the user if email couldn't be sent
            raise ValidationError(
                {
                    "email": "Impossible d'envoyer l'email d'activation pour le moment. Veuillez réessayer plus tard."
                }
            )

        # Do NOT return a token here. The user is not yet active.
        return user


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
        fields = ["id", "title", "slug", "short_desc", "long_desc"]


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
        fields = ["id", "variant", "user", "size"]
