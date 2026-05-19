from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Customer, Car, WorkOrder, Invoice, Technician, Expense, InventoryItem
from .forms import CustomerForm, CarForm, WorkOrderForm, InvoiceForm, TechnicianForm, ExpenseForm, InventoryItemForm

def create_workorder(request):
    if request.method == 'POST':
        # استلام بيانات النماذج من POST
        customer_form = CustomerForm(request.POST, prefix='customer')
        car_form = CarForm(request.POST, prefix='car')
        workorder_form = WorkOrderForm(request.POST, prefix='workorder')
        
        # استلام بيانات قطع الغيار والمصنعيات من حقول مخفية (JSON string)
        spare_parts_json = request.POST.get('spare_parts_data', '[]')
        labor_items_json = request.POST.get('labor_items_data', '[]')
        
        try:
            spare_parts = json.loads(spare_parts_json)
            labor_items = json.loads(labor_items_json)
        except:
            spare_parts = []
            labor_items = []
        
        # حساب الإجماليات
        total_spare_cost = sum(float(item['price']) * int(item['quantity']) for item in spare_parts)
        total_labor_cost = sum(float(item['price']) for item in labor_items)
        
        if customer_form.is_valid() and car_form.is_valid() and workorder_form.is_valid():
            with transaction.atomic():
                # حفظ العميل (إذا كان جديداً) أو استخدام عميل موجود؟ سنستخدم العميل الجديد دائماً.
                # يمكن التعديل لاحقاً للبحث عن عميل موجود
                customer = customer_form.save()
                
                # حفظ السيارة وربطها بالعميل
                car = car_form.save(commit=False)
                car.customer = customer
                car.save()
                
                # حفظ أمر الشغل
                workorder = workorder_form.save(commit=False)
                workorder.customer = customer
                workorder.car = car
                # سنضبط المصنعيات وقطع الغيار من الإجماليات
                workorder.labor_costs = total_labor_cost
                workorder.spare_parts = total_spare_cost
                workorder.materials = 0  # سنتركها صفراً أو نجمع من جدول ثالث
                workorder.save()
                
                # هنا يمكن حفظ تفاصيل قطع الغيار والمصنعيات في نماذج منفصلة إذا أردنا (اختياري)
                
                messages.success(request, 'تم إنشاء أمر الشغل بنجاح')
                return redirect('workorder_list')
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء في النموذج')
    else:
        customer_form = CustomerForm(prefix='customer')
        car_form = CarForm(prefix='car')
        workorder_form = WorkOrderForm(prefix='workorder')
    
    technicians = Technician.objects.all()
    return render(request, 'create_workorder.html', {
        'customer_form': customer_form,
        'car_form': car_form,
        'workorder_form': workorder_form,
        'technicians': technicians,
    })

def index(request):
    # حساب متوسط السيارات يومياً (آخر 30 يوم)
    last_30_days = timezone.now() - timedelta(days=30)
    cars_last_30_days = Car.objects.filter(date__gte=last_30_days).count()
    avg_cars_per_day = round(cars_last_30_days / 30, 1) if cars_last_30_days > 0 else 0

    # حالات السيارات من اوامر الشغل
    workorders = WorkOrder.objects.all()
    under_repair = workorders.filter(status='repair').count()
    waiting_parts = workorders.filter(status='waiting_parts').count()
    ready = workorders.filter(status='ready').count()
    delivered = workorders.filter(status='delivered').count()

    context = {
        'avg_cars_per_day': avg_cars_per_day,
        'under_repair': under_repair,
        'waiting_parts': waiting_parts,
        'ready': ready,
        'delivered': delivered,
    }
    return render(request, 'index.html', context)

def customer_list(request):
    customers = Customer.objects.all().order_by('name')
    return render(request, 'customers.html', {'customers': customers})

def car_list(request):
    cars = Car.objects.select_related('customer').all()
    return render(request, 'cars.html', {'cars': cars})

def workorder_list(request):
    workorders = WorkOrder.objects.select_related('customer', 'car', 'technician').all()
    return render(request, 'workorders.html', {'workorders': workorders})

def invoice_list(request):
    invoices = Invoice.objects.select_related('work_order__car', 'work_order__customer').all()
    # اجمالى ايرادات الفواتير اعلى الجدول
    total_revenue = sum(inv.total_after_discount() for inv in invoices)
    return render(request, 'invoices.html', {'invoices': invoices, 'total_revenue': total_revenue})

def technician_list(request):
    technicians = Technician.objects.all()
    return render(request, 'technicians.html', {'technicians': technicians})

def expense_list(request):
    expenses = Expense.objects.all().order_by('-date')
    total_expenses = sum(exp.total_expense() for exp in expenses)
    return render(request, 'expenses.html', {'expenses': expenses, 'total_expenses': total_expenses})

def inventory_list(request):
    items = InventoryItem.objects.all()
    return render(request, 'inventory.html', {'items': items})

# دوال الإضافة والتعديل والحذف (اختصاراً نعرض نماذج بسيطة)
def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'customer_form.html', {'form': form})