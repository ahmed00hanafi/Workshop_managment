from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

class Customer(models.Model):
    phone = models.CharField(max_length=15, primary_key=True, verbose_name="رقم التليفون")
    name = models.CharField(max_length=100, verbose_name="الاسم")
    address = models.TextField(verbose_name="العنوان")
    job = models.CharField(max_length=100, blank=True, null=True, verbose_name="الوظيفة")

    def __str__(self):
        return f"{self.name} - {self.phone}"

    class Meta:
        verbose_name = "عميل"
        verbose_name_plural = "العملاء"

class Technician(models.Model):
    phone = models.CharField(max_length=15, primary_key=True, verbose_name="رقم التليفون")
    name = models.CharField(max_length=100, verbose_name="اسم الفنى")
    address = models.TextField(verbose_name="العنوان")
    national_id = models.CharField(max_length=14, unique=True, verbose_name="الرقم القومى")
    id_card_image = models.ImageField(upload_to='id_cards/', blank=True, null=True, verbose_name="صورة بطاقة الرقم القومى")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "فنى"
        verbose_name_plural = "الفنيين"

class Car(models.Model):
    license_plate = models.CharField(max_length=20, primary_key=True, verbose_name="رقم اللوحة")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='cars', verbose_name="العميل")
    date = models.DateField(default=timezone.now, verbose_name="التاريخ")
    chassis_number = models.CharField(max_length=50, verbose_name="رقم الشاسيه")
    engine_number = models.CharField(max_length=50, verbose_name="رقم المحرك")
    car_type = models.CharField(max_length=50, verbose_name="نوع السيارة")
    manufacture_year = models.IntegerField(verbose_name="سنة الصنع")
    odometer_reading = models.IntegerField(verbose_name="قراءة العداد")
    defects = models.TextField(blank=True, verbose_name="الاعطال")
    notes = models.TextField(blank=True, verbose_name="ملاحظات")

    def __str__(self):
        return f"{self.license_plate} - {self.car_type}"

    class Meta:
        verbose_name = "سيارة"
        verbose_name_plural = "السيارات"

class WorkOrder(models.Model):
    STATUS_CHOICES = [
        ('repair', 'تحت الإصلاح'),
        ('waiting_parts', 'انتظار قطع غيار'),
        ('ready', 'جاهز'),
        ('delivered', 'تم التسليم'),
    ]
    work_order_number = models.AutoField(primary_key=True, verbose_name="رقم امر الشغل")
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='workorders', verbose_name="العميل")
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='workorders', verbose_name="السيارة")
    technician = models.ForeignKey(Technician, on_delete=models.SET_NULL, null=True, related_name='workorders', verbose_name="الفنى")
    defects = models.TextField(verbose_name="الاعطال")
    labor_costs = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="المصنعيات")
    spare_parts = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="قطع الغيار")
    materials = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="الخامات")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='repair', verbose_name="الحالة")
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    def total_cost(self):
        return self.labor_costs + self.spare_parts + self.materials

    def __str__(self):
        return f"امر #{self.work_order_number} - {self.car.license_plate}"

    class Meta:
        verbose_name = "امر شغل"
        verbose_name_plural = "اوامر الشغل"

class Invoice(models.Model):
    invoice_number = models.AutoField(primary_key=True, verbose_name="رقم الفاتورة")
    work_order = models.OneToOneField(WorkOrder, on_delete=models.CASCADE, related_name='invoice', verbose_name="امر الشغل")
    date = models.DateField(default=timezone.now, verbose_name="التاريخ")
    labor_costs = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="المصنعيات")
    spare_parts = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قطع الغيار")
    materials = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="الخامات")
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], verbose_name="خصم (%)")

    def subtotal(self):
        return self.labor_costs + self.spare_parts + self.materials

    def total_after_discount(self):
        discount_amount = self.subtotal() * (self.discount_percent / 100)
        return self.subtotal() - discount_amount

    def __str__(self):
        return f"فاتورة #{self.invoice_number} - {self.work_order.car.license_plate}"

    class Meta:
        verbose_name = "فاتورة"
        verbose_name_plural = "الفواتير"

class Expense(models.Model):
    expense_id = models.AutoField(primary_key=True, verbose_name="امر دفع")
    date = models.DateField(default=timezone.now, verbose_name="التاريخ")
    rent = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="ايجار")
    salaries = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="مرتبات")
    spare_parts_purchases = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="شراء قطع غيار و خامات")
    electricity = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="كهرباء")
    water = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="مياه")
    miscellaneous = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="نثريات")

    def total_expense(self):
        return self.rent + self.salaries + self.spare_parts_purchases + self.electricity + self.water + self.miscellaneous

    def __str__(self):
        return f"مصروف #{self.expense_id} - {self.date}"

    class Meta:
        verbose_name = "مصروف"
        verbose_name_plural = "المصروفات"

class InventoryItem(models.Model):
    name = models.CharField(max_length=100, verbose_name="اسم الصنف")
    quantity = models.IntegerField(default=0, verbose_name="الكمية")
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="سعر الوحدة")
    item_type = models.CharField(max_length=20, choices=[('spare_part', 'قطع غيار'), ('material', 'خامات')], verbose_name="النوع")

    def __str__(self):
        return f"{self.name} - {self.quantity}"

    class Meta:
        verbose_name = "صنف مخزن"
        verbose_name_plural = "المخزن"