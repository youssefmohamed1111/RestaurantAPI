from django.shortcuts import render
from rest_framework import generics, status
from .models import *
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser 
from .serializers import *
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from decimal import Decimal

# Create your views here.

#Menu Views
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    ordering_fields = ['price']
    search_fields = ['title']
    def get_permissions(self):
        if self.request.method =='POST':
            return [IsAdminUser]
        return [AllowAny]

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    def get_permissions(self):
        if self.request.method =="GET":
            return [AllowAny]
        return [IsAdminUser]


 #Orders View
class OrderView(generics.ListAPIView):
    queryset = Order.objects.all()
    serializer_class = OrdersSerializer
    permission_class = [IsAuthenticated]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]

    def perform_create(self, serializer):
        cart_items = Cart.objects.filter(user = self.request.user)
        total = self.calculate_total(cart_items)
        order = serializer.save(user = self.request.user,total=total)

        for cart_item in cart_items:
            OrderItems.objects.create(menuitem =cart_item.menuitem,quantity = cart_item.quantity, unit_price = cart_item.unit_price, price =cart_item.price, order = order)
            cart_item.delete()
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name= 'manager').exist():
            return Order.objects.all()

        return Order.objects.filter(user=user)
    
    def calculate_total(self,cart_items):
        total = Decimal(0)
        for item in cart_items:
            total+=items.price

        return total

class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class= OrdersSerializer
    permission_class = [IsAuthenticated]
    def get_queryset(self):
        return Order.objects.filter(user=user)
class CartView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class= CartSerializer
    permission_class = [IsAuthenticated]
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='manager').exists():
            return Cart.objects.all()
        return Cart.objects.filter(user=user)
    def perform_create(self,serializer):
        menuitem = self.request.data.get('menuitem')
        quantity = self.request.data.get('quantity')
        unit_price = MenuItem.objects.get(pk=menuitem).price
        quantity = int(quantity)
        price = quantity * unit_price
        serializer.save(user=self.request.user, price=price)
    def delete(self, request):
        user = self.request.user
        Cart.objects.filter(user=user).delete()
        return Response(status=204)



#User Groups View

class ManagersView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        # Get the 'manager' group
        manager_group = Group.objects.get(name='manager')
        # Get the users in the 'manager' group
        queryset = User.objects.filter(groups=manager_group)
        return queryset

    def perform_create(self, serializer):
        # Assign the user to the 'manager' group
        manager_group = Group.objects.get(name='manager')
        user = serializer.save()
        user.groups.add(manager_group)


class ManagerSingleView(generics.RetrieveDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        # Get the 'manager' group
        manager_group = Group.objects.get(name='manager')
        # Get the users in the 'manager' group
        queryset = User.objects.filter(groups=manager_group)
        return queryset


class DeliveryCrewView(generics.ListCreateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        delivery_group = Group.objects.get(name='delivery crew')
        queryset = User.objects.filter(groups=delivery_group)
        return queryset

    def perform_create(self, serializer):
        delivery_group = Group.objects.get(name='delivery crew')
        user = serializer.save()
        user.groups.add(delivery_group)


class DeliveryCrewSingleView(generics.RetrieveDestroyAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        delivery_group = Group.objects.get(name='delivery crew')
        queryset = User.objects.filter(groups=delivery_group)
        return queryset
class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_class = [AllowAny]

    
