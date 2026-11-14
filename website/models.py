from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
from django.conf import settings


# Utility
def get_current_time():
    return timezone.now().time()


# ==================== EMPLOYEE & MANAGER ====================
class EmployeeManager(BaseUserManager):
    def create_user(self, email, phone, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not phone:
            raise ValueError("Phone number is required")

        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, phone, password, **extra_fields)


class Employee(AbstractBaseUser, PermissionsMixin):
    employee_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=255)
    dob = models.DateField()
    designation = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True, null=True)
    address = models.TextField()
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = EmployeeManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["phone", "name"]

    def __str__(self):
        return self.name


# ==================== VEGETABLE & RELATED FORMS ====================
class Vegetable(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Batch(models.Model):
    # vegetable = models.ForeignKey(Vegetable, on_delete=models.PROTECT, related_name="batches")
    vegetable = models.ForeignKey(Vegetable, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Batch {self.id} - {self.vegetable.name}"


class InputForm(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="input_forms")
    date = models.DateField(default=timezone.now)
    name_of_rm = models.CharField(max_length=255, default="Unknown Raw Material")
    vehicle_number = models.CharField(max_length=50, default="UNKNOWN_VEHICLE")
    lot_number = models.CharField(max_length=255, default="DEFAULT_LOT_NUMBER")
    vendor_name = models.CharField(max_length=255, default="Unknown")
    place_from = models.CharField(max_length=255, default="Unknown")
    wt_supplier = models.FloatField(default=0.0)
    wt_ours = models.FloatField(default=0.0)
    slip_number = models.CharField(max_length=50, default="UNKNOWN_SLIP")
    rate = models.FloatField(default=0.0)
    is_filled = models.BooleanField(default=False)
    filled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='input_forms_filled')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='input_forms_approved')

    def __str__(self):
        return f"InputForm {self.id} - Batch {self.batch.id}"


class VegetableForm(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="vegetable_forms")
    date = models.DateField(default=timezone.now)
    color = models.CharField(max_length=100, default="Unknown")
    texture = models.CharField(max_length=100, default="Unknown")
    size = models.CharField(max_length=100, default="Unknown")
    maturity = models.CharField(max_length=100, default="Unknown")
    aroma = models.CharField(max_length=100, default="Unknown")
    appearance = models.CharField(max_length=255, default="Unknown")
    is_filled = models.BooleanField(default=False)
    filled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='inspection_forms_filled')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='inspection_forms_approved')

    def __str__(self):
        return f"VegetableForm {self.id} - Batch {self.batch.id}"


class WashingForm(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="washing_forms")
    date = models.DateField(default=timezone.now)
    input_quantity = models.FloatField(default=0.0)
    output_quantity = models.FloatField(default=0.0)
    waste = models.FloatField(default=0.0)
    is_filled = models.BooleanField(default=False)
    filled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='washing_forms_filled')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='washing_forms_approved')

    def __str__(self):
        return f"WashingForm {self.id} - Batch {self.batch.id}"


class BlanchingForm(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="blanching_forms")
    date = models.DateField(default=timezone.now)
    time = models.TimeField(default=get_current_time)

    blancher_belt_speed = models.FloatField(default=0.0)
    blancher_temperature = models.FloatField(default=0.0)
    cooler_belt_speed = models.FloatField(default=0.0)
    cooler_temperature = models.FloatField(default=0.0)

    spray_nozzle_washer = models.CharField(max_length=100, default="Not Specified")
    spray_nozzle_blancher = models.CharField(max_length=100, default="Not Specified")
    spray_nozzle_cooler = models.CharField(max_length=100, default="Not Specified")
    spray_nozzle_precooler = models.CharField(max_length=100, default="Not Specified")

    belt_speed_1 = models.FloatField(default=0.0)
    belt_speed_2 = models.FloatField(default=0.0)

    iqf_air_temperature = models.FloatField(default=0.0)
    iqf_coil_temperature = models.FloatField(default=0.0)
    iqf_product_temperature = models.FloatField(default=0.0)

    bag_number = models.IntegerField(default=0)
    total_bag = models.IntegerField(default=0)
    waste_blancing = models.IntegerField(default=0)

    is_filled = models.BooleanField(default=False)
    filled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='blancing_forms_filled')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='blancing_forms_approved')

    def __str__(self):
        return f"BlanchingForm {self.id} - Batch {self.batch.id}"


class OutputForm(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name="output_forms")
    date = models.DateField(default=timezone.now)
    final_bags = models.IntegerField(default=0)
    final_recovery = models.FloatField(default=0.0)
    packing = models.CharField(max_length=255, default="Not Specified")
    wasteWeighted = models.FloatField(default=0.0)
    is_filled = models.BooleanField(default=False)
    filled_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='output_forms_filled')
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='output_forms_approved')

    def __str__(self):
        return f"OutputForm {self.id} - Batch {self.batch.id}"


class PieChartData(models.Model):
    vegetable_id = models.ForeignKey(Vegetable, on_delete=models.CASCADE, related_name="pie_chart_data", default=1)
    date = models.DateField(default=timezone.now)
    data = models.IntegerField(default=0)
    waste_pie = models.FloatField(default=0.0)
