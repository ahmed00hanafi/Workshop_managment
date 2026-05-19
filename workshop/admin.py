from django.contrib import admin
from .models import Customer, Technician, Car, WorkOrder, Invoice, Expense, InventoryItem

admin.site.register(Customer)
admin.site.register(Technician)
admin.site.register(Car)
admin.site.register(WorkOrder)
admin.site.register(Invoice)
admin.site.register(Expense)
admin.site.register(InventoryItem)