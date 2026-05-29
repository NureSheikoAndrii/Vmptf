from django.urls import path
from . import views

urlpatterns = [
    path('', views.transaction_list, name='transaction_list'),
    path('add/', views.add_transaction, name='add_transaction'),
    path('category/<int:category_id>/', views.transactions_by_category, name='transactions_by_category'),
]