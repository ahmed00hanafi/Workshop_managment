from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('customers/', views.customer_list, name='customer_list'),
    path('cars/', views.car_list, name='car_list'),
    path('workorders/', views.workorder_list, name='workorder_list'),
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('technicians/', views.technician_list, name='technician_list'),
    path('expenses/', views.expense_list, name='expense_list'),
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('create-workorder/', views.create_workorder, name='create_workorder'),
]