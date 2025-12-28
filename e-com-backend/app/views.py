from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import filters
from .serializers import ProductSerializer, CartSerializer, OrderSerializer, CartItemSerializer,RegisterSerializer,CategorySerializer
from .models import Product, Cart, CartItem, Order,Category
from rest_framework.permissions import AllowAny,IsAuthenticated,IsAdminUser,BasePermission
from rest_framework import status,generics


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        return request.user and request.user.is_staff

# Registration 
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    # permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data= request.data)
        if serializer.is_valid():
            serializer.save()
            return Response('User is Register Successfully',status=status.HTTP_201_CREATED)
        raise serializers.ValidationError('Invalid credentials',status=status.HTTP_400_BAD_REQUEST)

# Product ViewSet
class ProductView(ModelViewSet):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'price', 'name']  # exact match filters
    search_fields = ['name', 'description']         # partial match filters
    ordering_fields = ['price', 'name', 'id'] 

    @action(detail=True, methods=['post'], url_path='publish', url_name='publish', permission_classes = [IsAdminUser])
    def publish(self, request, pk=None):
        product = self.get_object()
        product.status = 'published'  # must match your model choices
        product.save()
        return Response({'message': 'Product is published'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='upload_image', url_name='upload_image',permission_classes= [IsAdminUser])
    def upload_image(self, request, pk=None):
        product = self.get_object()
        image = request.FILES.get('image')
        if not image:
            return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)
        product.image = image
        product.save()
        return Response({'message': 'Image updated'}, status=status.HTTP_200_OK)

# Cart ViewSet
class CartView(ModelViewSet):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='add_item', url_name='add_item')
    def add_item(self, request, pk=None):
        cart = self.get_object()
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))
        if not product_id:
            return Response({'error': 'Product ID required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            cart_item = CartItem.objects.get(cart=cart, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            return Response({'message': 'Item quantity updated', 'quantity': cart_item.quantity}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            data = {
                "cart": cart.id,
                "product_id": product_id,  # <-- change here if your serializer expects product_id
                "quantity": quantity,
            }
            serializer = CartItemSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'message': 'Item added to cart'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='remove_item', url_name='remove_item')
    def remove_item(self, request, pk=None):
        item_id = request.data.get('item_id')
        if not item_id:
            return Response({'error': 'Item ID required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            item = CartItem.objects.get(id=item_id, cart_id=pk)
            item.delete()
            return Response({'message': 'Item removed'}, status=status.HTTP_200_OK)
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)
    @action(detail=True, methods=['patch'], url_path='update_item')
    def update_item(self, request, pk=None):
     cart = self.get_object()
     item_id = request.data.get('item_id')
     new_quantity = request.data.get('quantity')
 
     if item_id is None or new_quantity is None:
         return Response({'error': 'item_id and quantity are required'}, status=status.HTTP_400_BAD_REQUEST)
 
     try:
         item = CartItem.objects.get(id=item_id, cart=cart)
         if int(new_quantity) <= 0:
             item.delete()
         else:
             item.quantity = int(new_quantity)
             item.save()
         serializer = self.get_serializer(cart)
         return Response(serializer.data, status=status.HTTP_200_OK)
     except CartItem.DoesNotExist:
         return Response({'error': 'Item not found in cart'}, status=status.HTTP_404_NOT_FOUND)
     except Exception as e:
         print("Update item error:", e)
         return Response({'error': 'Internal server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

    @action(detail=True, methods=['post'], url_path='checkout', url_name='checkout')
    def checkout(self, request, pk=None):
        cart = self.get_object()
        cart.status = 'checked_out'
        cart.save()
        return Response({'message': 'Checkout successful'}, status=status.HTTP_200_OK)

# Order ViewSet
class OrderView(ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(cart__user=self.request.user)

    @action(detail=False, methods=['get'], url_path='my_order')
    def my_order(self, request):
        orders = self.get_queryset()
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='cancel', url_name='cancel')
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status in ['paid', 'shipped', 'delivered']:
            return Response({'error': 'Cannot cancel a processed order'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'cancelled'
        order.save()
        return Response({'message': 'Order cancelled'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='finalize', url_name='finalize')
    def finalize(self, request, pk=None):
        order = self.get_object()
        if order.status != 'pending':
            return Response({'error': 'Only pending orders can be finalized'}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'paid'
        order.save()
        return Response({'message': 'Order finalized and marked as paid'}, status=status.HTTP_200_OK)
    # views.py
class CategoryView(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
