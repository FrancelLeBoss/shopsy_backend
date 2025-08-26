from datetime import timezone
from django.utils import timezone
from django.shortcuts import render
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Cart, Product, ProductVariant, ProductVariantSize, Rating, Wishlist
from .models import SubCategory
from .models import Category
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_200_OK
from rest_framework import status
import random
from .serializers import RegisterSerializer
from django.core.mail import send_mail
from .serializers import (
    ProductSerializer,
    ProductVariantSerializer,
    ProductVariantSizeSerializer,
    RatingSerializer,
    SubCategorySerializer,
    CategorySerializer,
    CartSerializer,
    UserSerializer,
    WishlistSerializer,
)

from django.contrib.auth import get_user_model

User = get_user_model()
from rest_framework import generics, status
from django.http import HttpResponseRedirect
from django.utils import timezone
from datetime import timedelta
from django.conf import settings


def generate_verification_code():
    """Générer un code de vérification aléatoire à 6 chiffres."""
    return str(random.randint(100000, 999999))


# Create your views here.
@api_view(["GET"])
def hello_world(request):
    return Response({"message": "Hello from Django API!"})


@api_view(["GET"])
def get_products(request):
    """Retourne la liste des produits avec leurs variantes."""
    products = Product.objects.prefetch_related(
        "variants"
    ).all()  # Précharger les variantes
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_product(request, pk):
    """Retourne un produit spécifique."""
    try:
        product = Product.objects.prefetch_related(
            "variants__images", "variants__sizes"
        ).get(
            pk=pk
        )  # Précharger les images et tailles des variantes
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)


@api_view(["GET"])
def get_product_by_category(request, category_id):
    """Retourne les produits d’une catégorie spécifique."""
    products = Product.objects.filter(category_id=category_id).prefetch_related(
        "variants"
    )
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_product_by_subcategory(request, subcategory_id):
    """Retourne les produits d’une sous-catégorie spécifique."""
    products = Product.objects.filter(subCategory_id=subcategory_id).prefetch_related(
        "variants"
    )
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_size_details(request, size_id):
    """Retourne les détails d’une taille spécifique."""
    try:
        size = ProductVariantSize.objects.get(pk=size_id)
        serializer = ProductVariantSizeSerializer(size)
        return Response(serializer.data)
    except ProductVariantSize.DoesNotExist:
        return Response({"error": "Size not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
def get_variant_details(request, variant_id):
    """Retourne les détails d’une variante spécifique."""
    try:
        variant = ProductVariant.objects.prefetch_related("images", "sizes").get(
            pk=variant_id
        )  # Précharger les images et tailles de la variante
        product = variant.product  # Obtenir le produit associé à la variante
        product_serializer = ProductSerializer(product)
        variant_serializer = ProductVariantSerializer(variant)
        # Inclure les détails du produit dans la réponse de la variante
        response_data = variant_serializer.data
        response_data["product"] = product_serializer.data
        return Response(response_data)
    except ProductVariant.DoesNotExist:
        return Response({"error": "Variant not found"}, status=404)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)
    except Exception as e:
        return Response({"error": str(e)}, status=500)
    # Gérer les exceptions potentielles
    except ProductVariant.DoesNotExist:
        return Response({"error": "Variant not found"}, status=404)


@api_view(["GET"])
def get_subcateregory_by_category(request, category_id):
    """Retourne les sous-catégories d’une catégorie spécifique."""
    subcategories = SubCategory.objects.filter(category_id=category_id)
    serializer = SubCategorySerializer(subcategories, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_categories(request):
    """Retourne la liste des catégories."""
    categories = Category.objects.all()
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def get_category(request, pk):
    """Retourne une catégorie spécifique."""
    try:
        category = Category.objects.get(pk=pk)
        serializer = CategorySerializer(category)
        return Response(serializer.data)
    except Category.DoesNotExist:
        return Response({"error": "Category not found"}, status=404)


@api_view(["GET"])
def get_comments(request, product_id):
    """Retourne les évaluations d’un produit spécifique."""
    product = Product.objects.get(pk=product_id)
    ratings = Rating.objects.filter(product=product)
    serializer = RatingSerializer(ratings, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def send_verification_code(request):
    """Envoie un e-mail de vérification à l'utilisateur."""
    email = request.data.get("email")
    if not email:
        return Response({"error": "Email is required."}, status=HTTP_400_BAD_REQUEST)
    code = generate_verification_code()
    subject = "Your verification code"
    message = "Here is your verification code : " + code

    from_email = (
        "Shopsy Online Shop"  # Assurez-vous que cela correspond à EMAIL_HOST_USER
    )

    try:
        send_mail(subject, message, from_email, [email])
        return Response(
            {"message": "Verification email sent!", "code": code, "to": email},
            status=HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def reset_password(request):
    """Réinitialise le mot de passe de l'utilisateur."""
    email = request.data.get("email")
    new_password = request.data.get("newPassword")
    if not email or not new_password:
        return Response(
            {"error": "Email and new password are required."},
            status=HTTP_400_BAD_REQUEST,
        )
    try:
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        return Response({"message": "Password reset successfully!"}, status=HTTP_200_OK)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_user(request, user_id):
    """Retourne les informations d’un utilisateur spécifique."""
    try:
        user = User.objects.get(pk=user_id)
        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
            status=HTTP_200_OK,
        )
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def save_comment(request):
    """Gère l’ajout d’un commentaire."""
    # Implémentez la logique d’ajout de commentaire ici
    product_id = request.data.get("product")
    user_id = request.data.get("user")
    content = request.data.get("comment")
    stars = request.data.get("stars")
    # Vérifier que les champs sont remplis
    if not product_id or not user_id or not stars:
        return Response(
            {"error": "Product ID, user ID, and stars are required."},
            status=HTTP_400_BAD_REQUEST,
        )
    # Vérifier que le produit existe
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found."}, status=HTTP_400_BAD_REQUEST)
    # Vérifier que l’utilisateur existe
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=HTTP_400_BAD_REQUEST)
    # Créer le commentaire
    comment = Rating.objects.create(
        product=product,
        user=user,
        comment=content,
        stars=stars,
        created_at=timezone.now(),
        updated_at=timezone.now(),
    )
    # Enregistrer le commentaire
    comment.save()
    return Response(
        {
            "message": "Comment added successfully!",
            "comment": {
                "product_id": product_id,
                "product_title": product.title,
                "user_id": user_id,
                "content": content,
                "stars": stars,
                "created_at": comment.created_at,
                "updated_at": comment.updated_at,
            },
        },
        status=HTTP_200_OK,
    )


@csrf_exempt
@api_view(["POST"])
def login(request):
    """Gère la connexion de l’utilisateur."""
    # Implémentez la logique de connexion ici
    username = request.data.get("username")
    password = request.data.get("password")
    # Vérifier que les champs sont remplis
    if not username or not password:
        return Response(
            {"error": "Username and password are required."},
            status=HTTP_400_BAD_REQUEST,
        )

    user = authenticate(username=username, password=password)
    if user is None:
        return Response(
            {"error": "Invalid username or password."}, status=HTTP_400_BAD_REQUEST
        )
    else:
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "message": "Login successful!",
                "token": token.key,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=HTTP_200_OK,
        )


# This is for the /api/register/ endpoint
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)  # Calls the create method of the serializer

        # Return a success message, but NO TOKEN yet
        return Response(
            {
                "message": "Votre compte a été créé avec succès. Veuillez vérifier votre email pour l'activer."
            },
            status=status.HTTP_201_CREATED,
            headers=self.get_success_headers(serializer.data),
        )


class ActivateAccountView(generics.RetrieveAPIView):
    queryset = User.objects.all()
    lookup_field = "email_verification_token"

    def get(self, request, *args, **kwargs):
        try:
            user = self.get_object()  # Récupère l'utilisateur par le token

            # Vérifie si le token a expiré (ex: après 24 heures)
            if user.email_verification_sent_at and (
                timezone.now() - user.email_verification_sent_at
            ) > timedelta(hours=24):
                user.email_verification_token = None  # Invalide le token expiré
                user.save()
                return Response(
                    {
                        "detail": "Le lien d'activation a expiré. Veuillez vous réinscrire ou demander un nouveau lien."
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Vérifie si le compte est déjà actif
            if user.is_active:
                return Response(
                    {"detail": "Votre compte est déjà actif."},
                    status=status.HTTP_200_OK,  # Ou 409 Conflict si vous préférez être plus strict
                )

            # Active le compte
            user.is_active = True
            user.email_verification_token = None  # Invalide le token après utilisation
            user.email_verification_sent_at = None
            user.save()
            print(f"je test 1")
            return Response(
                {"message": "Votre compte a été activé avec succès !"},
                status=status.HTTP_200_OK,
            )

        except (
            User.DoesNotExist
        ):  # Gère le cas où le token ne correspond à aucun utilisateur
            return Response(
                {"detail": "Lien d'activation invalide."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:  # Pour toute autre erreur inattendue
            print(f"Erreur lors de l'activation du compte: {e}")
            return Response(
                {
                    "detail": "Une erreur est survenue lors de l'activation de votre compte."
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# @csrf_exempt
# @api_view(["POST"])
# def register(request):
#     """Gère l'enregistrement d'un nouvel utilisateur."""
#     username = request.data.get("username")
#     email = request.data.get("email")
#     password = request.data.get("password")
#     newsLetterSubscription = request.data.get("newsLetterSubscription")
#     is_active = request.data.get("is_active")

#     # Vérifier que tous les champs sont remplis
#     if not username or not email or not password:
#         return Response(
#             {"error": "Username, email, and password are required."},
#             status=HTTP_400_BAD_REQUEST,
#         )

#     # Vérifier si le nom d'utilisateur existe déjà
#     if User.objects.filter(username=username).exists():
#         return Response(
#             {"error": "Username already exists."},
#             status=HTTP_400_BAD_REQUEST,
#         )

#     # Vérifier si l'email existe déjà
#     if User.objects.filter(email=email).exists():
#         return Response(
#             {"error": "Email already exists."},
#             status=HTTP_400_BAD_REQUEST,
#         )

#     # Créer un nouvel utilisateur
#     try:
#         user = User.objects.create_user(
#             username=username, email=email, password=password, newsLetterSubscription = newsLetterSubscription,
#             is_active=is_active
#         )
#         user.save()

#         # Générer un token pour l'utilisateur
#         token, created = Token.objects.get_or_create(user=user)

#         return Response(
#             {
#                 "message": "User registered successfully!",
#                 "user": {
#                     "username": user.username,
#                     "email": user.email,
#                 },
#                 "token": token.key,
#             },
#             status=HTTP_200_OK,
#         )
#     except Exception as e:
#         return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(["POST"])
def logout(request):
    """Gère la déconnexion de l’utilisateur."""
    token = request.data.get("token")
    if not token:
        return Response({"error": "Token is required."}, status=HTTP_400_BAD_REQUEST)
    try:
        token_obj = Token.objects.get(key=token)
        token_obj.delete()
        return Response({"message": "Logout successful!"}, status=HTTP_200_OK)
    except Token.DoesNotExist:
        return Response({"error": "Invalid token."}, status=HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_me(request):
    user = request.user
    return Response(
        {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            # Ajoute d'autres champs si besoin
        },
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
def username_exists(request):
    """Vérifie si le nom d’utilisateur existe déjà."""
    if User.objects.filter(username=request.data.get("username")).exists():
        return Response({"exists": True}, status=HTTP_200_OK)
    else:
        return Response({"exists": False}, status=HTTP_200_OK)


@api_view(["POST"])
def email_exists(request):
    """Vérifie si l'email existe déjà."""
    if User.objects.filter(email=request.data.get("email")).exists():
        return Response({"exists": True}, status=HTTP_200_OK)
    else:
        return Response({"exists": False}, status=HTTP_200_OK)


@permission_classes([IsAuthenticated])
@api_view(["GET"])
def get_cart_user(request):
    """ "Retourne le panier d’un utilisateur spécifique."""
    user = request.user  # Utilisateur authentifié
    cart_items = (
        Cart.objects.filter(user=user)
        .prefetch_related("variant")
        .prefetch_related("size")
    )
    serializer = CartSerializer(cart_items, many=True)
    return Response(serializer.data, status=HTTP_200_OK)


@api_view(["POST"])
def already_in_wishlist(request):
    """Vérifie si un produit est déjà dans la liste de souhaits."""
    user_id = request.data.get("user_id")
    variant_id = request.data.get("variant_id")
    # Vérifier que les champs sont remplis
    if not user_id or not variant_id:
        return Response(
            {"error": "User ID and variant ID are required."},
            status=HTTP_400_BAD_REQUEST,
        )
    # Vérifier que l’utilisateur existe
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=HTTP_400_BAD_REQUEST)
    # Vérifier que la variante existe
    try:
        variant = ProductVariant.objects.get(pk=variant_id)
    except ProductVariant.DoesNotExist:
        return Response({"error": "Variant not found."}, status=HTTP_400_BAD_REQUEST)
    # Vérifier si l’élément est déjà dans la liste de souhaits
    wishlist_items = Wishlist.objects.filter(user=user, variant=variant)
    if wishlist_items.exists():
        return Response({"exists": True}, status=HTTP_200_OK)
    else:
        return Response({"exists": False}, status=HTTP_200_OK)


@api_view(["POST"])
def add_to_wishlist(request):
    """Ajoute un produit à la liste de souhaits."""
    user_id = request.data.get("user_id")
    variant_id = request.data.get("variant_id")
    created_at = timezone.now()
    updated_at = timezone.now()
    # Vérifier que les champs sont remplis
    if not user_id or not variant_id:
        return Response(
            {"error": "User ID and variant ID are required."},
            status=HTTP_400_BAD_REQUEST,
        )
    # Vérifier que l’utilisateur existe
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=HTTP_400_BAD_REQUEST)
    # Vérifier que la variante existe
    try:
        variant = ProductVariant.objects.get(pk=variant_id)
    except ProductVariant.DoesNotExist:
        return Response({"error": "Variant not found."}, status=HTTP_400_BAD_REQUEST)
    # Vérifier si l’élément est déjà dans la liste de souhaits
    try:
        wishlist_items = Wishlist.objects.filter(user=user, variant=variant)
        if wishlist_items.exists():
            # Si des éléments existent, mettez à jour le premier
            wishlist_item = wishlist_items.first()
            wishlist_item.updated_at = updated_at
            wishlist_item.save()
            id = wishlist_item.id
        else:
            # Sinon, créez un nouvel élément de liste de souhaits
            wishlist_item = Wishlist.objects.create(
                user=user,
                variant=variant,
                created_at=created_at,
                updated_at=updated_at,
            )
            id = wishlist_item.id
    except Exception as e:
        return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)
    return Response(
        {
            "message": "Product added to wishlist successfully!",
            "wishlist_item": {
                "user_id": user_id,
                "id": id,
                "user": UserSerializer(user).data,
                "variant_id": variant_id,
                "variant": ProductVariantSerializer(
                    variant
                ).data,  # Sérialiser l'objet variant
                "created_at": created_at,
                "updated_at": updated_at,
            },
        }
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_wishlist(request):
    """Retourne la liste de souhaits d’un utilisateur spécifique."""
    user = request.user  # <-- L'utilisateur est déjà défini par le token JWT
    # La gestion d'erreur User.DoesNotExist n'est plus nécessaire ici
    # car si l'utilisateur n'existait pas, IsAuthenticated aurait déjà rejeté la requête.

    wishlist_items = Wishlist.objects.filter(user=user).prefetch_related("variant")
    serializer = WishlistSerializer(wishlist_items, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def remove_from_wishlist(request):
    """Supprime un produit de la liste de souhaits."""
    user_id = request.data.get("user_id")
    variant_id = request.data.get("variant_id")
    # Vérifier que les champs sont remplis
    if not user_id or not variant_id:
        return Response(
            {"error": "User ID and variant ID are required."},
            status=HTTP_400_BAD_REQUEST,
        )
    # Vérifier que l’utilisateur existe
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=HTTP_400_BAD_REQUEST)
    # Vérifier que la variante existe
    try:
        variant = ProductVariant.objects.get(pk=variant_id)
    except ProductVariant.DoesNotExist:
        return Response({"error": "Variant not found."}, status=HTTP_400_BAD_REQUEST)
    # Vérifier si l’élément est déjà dans la liste de souhaits
    try:
        wishlist_item = Wishlist.objects.get(user=user, variant=variant)
        # Si l’élément est trouvé, supprimez-le de la liste de souhaits
        deletedID = wishlist_item.id
        wishlist_item.delete()
        return Response(
            {
                "message": "Product removed from wishlist successfully!",
                "wishlist_item": {
                    "id": deletedID,
                    "variant": ProductVariantSerializer(variant).data,
                    "user": UserSerializer(user).data,
                },
            },
            status=HTTP_200_OK,
        )
    except Wishlist.DoesNotExist:
        return Response(
            {"error": "Wishlist item not found."}, status=HTTP_400_BAD_REQUEST
        )


@api_view(["POST"])
def empty_wishlist(request):
    """Vider la liste de souhaits d’un utilisateur spécifique."""
    user_id = request.data.get("user_id")
    try:
        user = User.objects.get(pk=user_id)
        Wishlist.objects.filter(user=user).delete()
        return Response(
            {"message": "Wishlist emptied successfully!"}, status=HTTP_200_OK
        )
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def add_to_cart(request):
    """Ajoute un produit au panier."""
    user_id = request.data.get("user_id")
    variant_id = request.data.get("variant_id")
    quantity = request.data.get("quantity", 1)
    size_id = request.data.get("size_id") if request.data.get("size_id") else None
    created_at = timezone.now()
    updated_at = timezone.now()
    # Vérifier que les champs sont remplis
    if not user_id or not variant_id:
        return Response(
            {"error": "User ID and variant ID are required."},
            status=HTTP_400_BAD_REQUEST,
        )
    # Vérifier que l’utilisateur existe
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({"error": "User not found."}, status=HTTP_400_BAD_REQUEST)
    # Vérifier que la variante existe
    try:
        variant = ProductVariant.objects.get(pk=variant_id)
    except ProductVariant.DoesNotExist:
        return Response({"error": "Variant not found."}, status=HTTP_400_BAD_REQUEST)
    if size_id:
        try:
            size = ProductVariantSize.objects.get(pk=size_id)
        except ProductVariantSize.DoesNotExist:
            return Response({"error": "Size not found."}, status=HTTP_400_BAD_REQUEST)
    # Vérifier si l’élément est déjà dans le panier
    try:
        cart_items = Cart.objects.filter(user=user, variant=variant)
        if size_id:
            cart_items = cart_items.filter(size=size)
        if cart_items.exists():
            # Si des éléments existent, mettez à jour le premier
            cart_item = cart_items.first()
            cart_item.quantity += quantity
            cart_item.updated_at = updated_at
            cart_item.save()
        else:
            # Sinon, créez un nouvel élément de panier
            cart_item = Cart.objects.create(
                user=user,
                variant=variant,
                quantity=quantity,
                size=size if size_id else None,
                created_at=created_at,
                updated_at=updated_at,
            )
    except Exception as e:
        return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)
    return Response(
        {
            "message": "Product added to cart successfully!",
            "cart_item": {
                "user_id": user_id,
                "user": UserSerializer(user).data,
                "variant_id": variant_id,
                "quantity": quantity,
                "size": ProductVariantSizeSerializer(size).data if size_id else None,
                "variant": ProductVariantSerializer(
                    variant
                ).data,  # Sérialiser l'objet variant
                "created_at": created_at,
                "updated_at": updated_at,
            },
        },
        status=HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def empty_cart(request):
    """Vider le panier d’un utilisateur spécifique."""
    user = request.user
    Cart.objects.filter(user=user).delete()
    return Response({"message": "Cart emptied successfully!"}, status=HTTP_200_OK)


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def update_cart(request):
    """Modifier la quantité d’un produit dans le panier."""
    user = request.user  # Utilisateur authentifié
    variant_id = request.data.get("variant_id")
    size_id = request.data.get("size_id") if request.data.get("size_id") else None
    quantity = request.data.get("quantity")
    updated_at = timezone.now()
    # Vérifier que les champs sont remplis
    if not variant_id or quantity is None:
        return Response(
            {"error": "variant ID, and quantity are required."},
            status=HTTP_400_BAD_REQUEST,
        )
    # Vérifier que la variante existe
    try:
        variant = ProductVariant.objects.get(pk=variant_id)
    except ProductVariant.DoesNotExist:
        return Response({"error": "Variant not found."}, status=HTTP_400_BAD_REQUEST)
    size = None
    if size_id:
        try:
            size = ProductVariantSize.objects.get(pk=size_id)
        except ProductVariantSize.DoesNotExist:
            return Response({"error": "Size not found."}, status=HTTP_400_BAD_REQUEST)
    # Vérifier si l’élément est déjà dans le panier
    try:
        cart_items = Cart.objects.filter(user=user, variant=variant)
        # Si la taille est spécifiée, vérifiez également si elle correspond
        if size_id:
            cart_items = cart_items.filter(size=size)
        if cart_items.exists():
            # Si des éléments existent, mettez à jour le premier
            cart_item = cart_items.first()
            cart_item.quantity = quantity
            cart_item.updated_at = updated_at
            cart_item.save()
            return Response(
                {
                    "message": "Cart updated successfully!",
                    "cart_item": {
                        "user_id": user.id,
                        "user": UserSerializer(user).data,
                        "variant_id": variant_id,
                        "size": (
                            ProductVariantSizeSerializer(size).data if size_id else None
                        ),
                        "size_id": size_id,
                        "variant": ProductVariantSerializer(variant).data,
                        "quantity": quantity,
                        "updated_at": updated_at,
                    },
                },
                status=HTTP_200_OK,
            )
        else:
            # Si l’élément n’existe pas, retournez une erreur
            return Response(
                {"error": "Cart item not found."}, status=HTTP_400_BAD_REQUEST
            )
    except Exception as e:
        return Response({"error": str(e)}, status=HTTP_400_BAD_REQUEST)


@permission_classes([IsAuthenticated])
@api_view(["POST"])
def remove_from_cart(request):
    """Supprime un produit du panier."""
    user = request.user  # Utilisateur authentifié
    variant_id = request.data.get("variant_id")
    size_id = request.data.get("size_id") if request.data.get("size_id") else None
    # Vérifier que les champs sont remplis
    if not variant_id:
        return Response(
            {"error": "variant ID is required."},
            status=HTTP_400_BAD_REQUEST,
        )
    # Vérifier que la variante existe
    try:
        variant = ProductVariant.objects.get(pk=variant_id)
    except ProductVariant.DoesNotExist:
        return Response({"error": "Variant not found."}, status=HTTP_400_BAD_REQUEST)
    if size_id:
        try:
            size = ProductVariantSize.objects.get(pk=size_id)
        except ProductVariantSize.DoesNotExist:
            return Response({"error": "Size not found."}, status=HTTP_400_BAD_REQUEST)
    # Vérifier si l’élément est déjà dans le panier
    try:
        queryset = Cart.objects.filter(user=user, variant=variant)
        # Si la taille est spécifiée, vérifiez également si elle correspond
        if size_id:
            queryset = queryset.filter(size=size)
        cart_item = (
            queryset.first()
        )  # ou .get() si tu es sûr qu'il n'y a qu'un seul résultat
        if not cart_item:
            return Response(
                {"error": "Cart item not found."}, status=HTTP_400_BAD_REQUEST
            )
        # Si l’élément est trouvé, supprimez-le du panier
        deletedID = cart_item.id
        cart_item.delete()
        return Response(
            {
                "message": "Product removed from cart successfully!",
                "cart_item": {
                    "user_id": user.id,
                    "deletedID": deletedID,
                    "variant_id": variant_id,
                    "size": (
                        ProductVariantSizeSerializer(size).data if size_id else None
                    ),
                    "variant": ProductVariantSerializer(variant).data,
                },
            },
            status=HTTP_200_OK,
        )
    except Cart.DoesNotExist:
        return Response({"error": "Cart item not found."}, status=HTTP_400_BAD_REQUEST)
