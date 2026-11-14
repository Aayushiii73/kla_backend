from rest_framework import serializers
from .models import Vegetable,Employee,PieChartData, Batch, InputForm, VegetableForm, WashingForm, BlanchingForm, OutputForm
from django.utils import timezone
from django.contrib.auth import authenticate


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = '__all__'

    def create(self, validated_data):
        employee = Employee.objects.create_user(**validated_data)
        return employee

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'name', 'email']  # Add more fields as needed

# Serializer for Login
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid email or password")
        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["name", "email", "phone", "dob", "designation", "department", "address", "date_joined"]

class InputFormSerializer(serializers.ModelSerializer):
    filled_by = UserSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)
    class Meta:
        model = InputForm
        fields = ['id', 'batch', 'date', 'name_of_rm', 'vehicle_number', 'lot_number', 'vendor_name', 'place_from', 'wt_supplier', 'wt_ours', 'slip_number', 'rate', 'is_filled','filled_by','approved_by']

class PieChartDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PieChartData
        fields = ['id', 'vegetable_id', 'date', 'data','waste_pie']

        
        
class VegetableFormSerializer(serializers.ModelSerializer):
    filled_by = UserSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)
    class Meta:
        model = VegetableForm
        fields = ['id', 'batch','date', 'color', 'texture', 'size', 'maturity', 'aroma', 'appearance', 'is_filled','filled_by','approved_by']
        

class WashingFormSerializer(serializers.ModelSerializer):
    filled_by = UserSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)
    class Meta:
        model = WashingForm
        fields = ['id', 'batch','date', 'input_quantity', 'output_quantity', 'waste', 'is_filled','filled_by','approved_by']

class BlanchingFormSerializer(serializers.ModelSerializer):
    filled_by = UserSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)
    class Meta:
        model = BlanchingForm
        fields = ['id', 'batch','date', 'blancher_belt_speed', 'blancher_temperature', 'cooler_belt_speed', 'cooler_temperature', 'spray_nozzle_washer', 'spray_nozzle_blancher', 'spray_nozzle_cooler', 'spray_nozzle_precooler', 'belt_speed_1', 'belt_speed_2', 'iqf_air_temperature', 'iqf_coil_temperature', 'iqf_product_temperature', 'bag_number', 'total_bag','waste_blancing','is_filled','filled_by','approved_by']
        

class OutputFormSerializer(serializers.ModelSerializer):
    filled_by = UserSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)
    class Meta:
        model = OutputForm
        fields = ['id','batch','date', 'final_bags', 'final_recovery', 'packing','wasteWeighted', 'is_filled','filled_by','approved_by']
        

class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = '__all__'


class VegetableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vegetable
        fields = '__all__'

class CombinedFormSerializerfordp(serializers.Serializer):
    product_name = serializers.SerializerMethodField()
    vendor_name = serializers.CharField(source='input_form.vendor_name', allow_null=True, default="N/A")
    vehicle_no = serializers.CharField(source='input_form.vehicle_number', allow_null=True, default="N/A")
    raw_material_wt = serializers.FloatField(source='input_form.wt_ours', allow_null=True, default=0.0)
    final_bags = serializers.IntegerField(source='output_form.final_bags', allow_null=True, default=0)
    final_recovery = serializers.FloatField(source='output_form.final_recovery', allow_null=True, default=0.0)
    lot_no = serializers.CharField(source='input_form.lot_number', allow_null=True, default="N/A")
    packing = serializers.CharField(source='output_form.packing', allow_null=True, default="N/A")
    date = serializers.DateField(source='output_form.date', default=timezone.now),
    waste_blanching = serializers.FloatField(source='blanching_form.waste_blancing', allow_null=True, default=0.0)

    def get_product_name(self, obj):
        return obj.get('input_form').name_of_rm if obj.get('input_form') else "Unknown Product"

    class Meta:
        fields = ['product_name', 'vendor_name', 'vehicle_no', 'raw_material_wt', 
                  'final_bags', 'final_recovery', 'lot_no', 'packing','date', 'waste_blanching']
