from django.contrib import admin
from .models import Vegetable,Employee,PieChartData, Batch, InputForm, WashingForm, BlanchingForm, OutputForm, VegetableForm


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'name', 'email', 'phone', 'date_joined')
    search_fields = ('name', 'email', 'phone')
    ordering = ('-date_joined',)


class VegetableAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    list_filter = ('name',)

class BatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'vegetable', 'created_at')
    search_fields = ('vegetable__name',)  # Allows searching by vegetable name
    list_filter = ('vegetable', 'created_at')

class InputFormAdmin(admin.ModelAdmin):
    list_display = ('id', 'batch', 'date', 'name_of_rm', 'vehicle_number', 'is_filled','filled_by')
    search_fields = ('batch__vegetable__name', 'name_of_rm', 'vehicle_number')
    list_filter = ('is_filled', 'date')

class WashingFormAdmin(admin.ModelAdmin):
    list_display = ('id', 'batch','date', 'input_quantity', 'output_quantity', 'waste', 'is_filled','filled_by')
    search_fields = ('batch__vegetable__name',)
    list_filter = ('is_filled',)

class BlanchingFormAdmin(admin.ModelAdmin):
    list_display = ('id', 'batch','date', 'blancher_belt_speed', 'blancher_temperature', 'cooler_temperature','waste_blancing','filled_by')
    search_fields = ('batch__vegetable__name',)
    list_filter = ('is_filled','blancher_temperature', 'cooler_temperature')

class VegetableFormAdmin(admin.ModelAdmin):
    list_display = ('id', 'batch','date','color', 'texture', 'size', 'maturity', 'aroma', 'appearance','filled_by')
    search_fields = ('batch__vegetable__name', 'color', 'texture', 'size')
    list_filter = ('is_filled','color', 'texture', 'size')

class OutputFormAdmin(admin.ModelAdmin):
    list_display = ('id', 'batch', 'date','final_bags', 'final_recovery', 'packing','wasteWeighted','filled_by')
    search_fields = ('batch__vegetable__name',)
    list_filter = ('is_filled','final_recovery','date',)


class PieChartAdmin(admin.ModelAdmin):
    list_display = ("id", "vegetable_id", "data", "date",'waste_pie')  # Correct field name
    search_fields = ("vegetable_id",)  # Ensure this field exists in the model
    list_filter = ("date",)  # Ensure this is a DateField for filtering
    

# Register models with their respective admin classes
admin.site.register(Vegetable, VegetableAdmin)
admin.site.register(Batch, BatchAdmin)
admin.site.register(InputForm, InputFormAdmin)
admin.site.register(WashingForm, WashingFormAdmin)
admin.site.register(BlanchingForm, BlanchingFormAdmin)
admin.site.register(VegetableForm, VegetableFormAdmin)
admin.site.register(OutputForm, OutputFormAdmin)
admin.site.register(PieChartData, PieChartAdmin)
