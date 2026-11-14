from rest_framework import generics, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Vegetable,Employee, Batch, InputForm, WashingForm, BlanchingForm, OutputForm, VegetableForm,PieChartData
from .serializers import (EmployeeSerializer,ProfileSerializer,VegetableSerializer, BatchSerializer, BlanchingFormSerializer, VegetableFormSerializer,
                          InputFormSerializer, WashingFormSerializer, OutputFormSerializer,CombinedFormSerializerfordp,PieChartDataSerializer)
from rest_framework.views import APIView
from datetime import date
from datetime import datetime
from collections import defaultdict
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.hashers import check_password


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_employee(request):
    serializer = EmployeeSerializer(data=request.data)
    if serializer.is_valid():
        employee = serializer.save()
        return Response({
            "employee_id": employee.employee_id,
            "temporary_password": request.data.get("password", "Not Provided")
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def fetch_employees(request):       
        
    print("Authenticated User:", request.user)  # Debugging Line
    
    if not request.user.is_authenticated:
        return Response({"detail": "User not authenticated"}, status=status.HTTP_401_UNAUTHORIZED)
    
    employees = Employee.objects.all()
    serializer = EmployeeSerializer(employees, many=True)
    
    return Response({"data": serializer.data}, status=status.HTTP_200_OK)

# Delete Employee
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_employee(request, employee_id):
    try:
        employee = Employee.objects.get(employee_id=employee_id)
        employee.delete()
        return Response({"message": "Employee deleted successfully"}, status=status.HTTP_200_OK)
    except Employee.DoesNotExist:
        return Response({"error": "Employee not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    email = request.data.get("email")
    password = request.data.get("password")

    if not email or not password:
        return Response({"error": "Email and password are required"}, status=400)

    try:
        user = Employee.objects.get(email=email)
    except Employee.DoesNotExist:
        return Response({"error": "Invalid credentials"}, status=401)

    # 🔹 Check the hashed password
    if not check_password(password, user.password):
        return Response({"error": "Invalid credentials"}, status=401)

    # 🔹 Generate JWT token
    refresh = RefreshToken.for_user(user)
    return Response({
        "success": True,
        "token": str(refresh.access_token),
        "refresh": str(refresh),
        "role": user.designation,
        "name":user.name
    }, status=200)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_logged_in_user(request):
    user = request.user  # The authenticated user
    serializer = ProfileSerializer(user)
    return Response(serializer.data)

  
from django.views.decorators.http import require_http_methods

@csrf_exempt
@require_http_methods(["DELETE"])
def delete_vegetable(request, vegetable_id):
    try:
        vegetable = get_object_or_404(Vegetable, id=vegetable_id)
        vegetable.delete()
        return JsonResponse({'message': f'Vegetable with ID {vegetable_id} has been deleted.'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
@require_http_methods(["DELETE"])
@permission_classes([IsAuthenticated])
def delete_batch(request, batch_id):
    try:
        batch = get_object_or_404(Batch, id=batch_id)
        batch.delete()
        return JsonResponse({'message': f'Batch with ID {batch_id} has been deleted.'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
      
# Vegetable Views
@permission_classes([IsAuthenticated])
class VegetableListCreateAPIView(generics.ListCreateAPIView):
    queryset = Vegetable.objects.all()
    serializer_class = VegetableSerializer

@permission_classes([IsAuthenticated])
class VegetableRetrieveDestroyAPIView(generics.RetrieveDestroyAPIView):
    queryset = Vegetable.objects.all()
    serializer_class = VegetableSerializer


# Batch Views
@permission_classes([IsAuthenticated])
class BatchListForVegetableAPIView(generics.ListAPIView):
    serializer_class = BatchSerializer

    def get_queryset(self):
        vegetable_id = self.kwargs.get('vegetable_id')
        selected_date = self.request.query_params.get('date')

        if selected_date:
            return Batch.objects.filter(
                vegetable_id=vegetable_id,
                input_forms__date=selected_date  # <-- CORRECT related name
            ).distinct()
        return Batch.objects.filter(vegetable_id=vegetable_id)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def approve_forms(request, form_type, batch_id):
    try:
        batch = Batch.objects.get(id=batch_id)

        # Get the appropriate form model based on form_type
        if form_type == 'washing':
            form = WashingForm.objects.get(batch=batch)
        elif form_type == 'blanching':
            form = BlanchingForm.objects.get(batch=batch)
        elif form_type == 'output':
            form = OutputForm.objects.get(batch=batch)
        elif form_type == 'vegetable':
            form = VegetableForm.objects.get(batch=batch)
        elif form_type == 'input':
            form = InputForm.objects.get(batch=batch)
        else:
            return Response({"error": "Invalid form type"}, status=status.HTTP_400_BAD_REQUEST)

        form.approved_by = request.user
        form.save()
        return Response({"approved_by": request.user.name}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
@permission_classes([IsAuthenticated])
class InputFormCreateWithVegetableAPIView(generics.CreateAPIView):
    serializer_class = InputFormSerializer

    def create(self, request, *args, **kwargs):
        vegetable_id = self.kwargs.get('vegetable_id')
        vegetable = get_object_or_404(Vegetable, pk=vegetable_id)

        # Create a new batch for the vegetable
        batch = Batch.objects.create(vegetable=vegetable)

        # Extract the input form data from the request
        data = {
            'batch': batch.id,
            'date': date.today(),
            'name_of_rm': request.data.get('name_of_rm'),
            'vehicle_number': request.data.get('vehicle_number'),
            'lot_number': request.data.get('lot_number'),
            'vendor_name': request.data.get('vendor_name'),
            'place_from': request.data.get('place_from'),
            'wt_supplier': request.data.get('wt_supplier'),
            'wt_ours': request.data.get('wt_ours'),
            'slip_number': request.data.get('slip_number'),
            'rate': request.data.get('rate'),
            'is_filled': True,
            # 'filled_by':request.user.id
        }

        # Create the InputForm and associate it with the new batch
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        
        serializer.instance.filled_by = request.user
        serializer.instance.save()
        
        
        # Initialize WashingForm, BlanchingForm, VegetableForm, and OutputForm for the new batch
        WashingForm.objects.create(
            batch=batch,
            input_quantity=request.data.get('wt_ours'),
            output_quantity=0,
            waste=0,
            is_filled=False,
            filled_by = None,
            approved_by=None
        )

        BlanchingForm.objects.create(
            batch=batch,
            blancher_belt_speed=0,
            blancher_temperature=0,
            cooler_belt_speed=0,
            cooler_temperature=0,
            spray_nozzle_washer="",
            spray_nozzle_blancher="",
            spray_nozzle_cooler="",
            spray_nozzle_precooler="",
            belt_speed_1=0,
            belt_speed_2=0,
            iqf_air_temperature=0,
            iqf_coil_temperature=0,
            iqf_product_temperature=0,
            bag_number=0,
            total_bag=0,
            is_filled=False,
            filled_by=None,
            approved_by=None
        )

        VegetableForm.objects.create(
            batch=batch,
            color="",
            texture="",
            size="",
            maturity="",
            aroma="",
            appearance="",
            is_filled=False,
            filled_by=None,
            approved_by=None
        )

        OutputForm.objects.create(
            batch=batch,
            final_bags=0,
            final_recovery=0,
            packing="",
            wasteWeighted=0,
            is_filled=False,
            filled_by=None,
            approved_by=None
        )

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

@permission_classes([IsAuthenticated])
class FormDetailCreateAPIView(generics.GenericAPIView):
        
    def get_object(self):
        form_type = self.kwargs.get('form_type')
        batch_id = self.kwargs.get('batch_id')

        if form_type == 'washing':
            return get_object_or_404(WashingForm, batch_id=batch_id)
        elif form_type == 'blanching':
            return get_object_or_404(BlanchingForm, batch_id=batch_id)
        elif form_type == 'output':
            return get_object_or_404(OutputForm, batch_id=batch_id)
        elif form_type == 'vegetable':
            return get_object_or_404(VegetableForm, batch_id=batch_id)
        return None

    def get_serializer_class(self):
        form_type = self.kwargs.get('form_type')
        if form_type == 'washing':
            return WashingFormSerializer
        elif form_type == 'blanching':
            return BlanchingFormSerializer
        elif form_type == 'output':
            return OutputFormSerializer
        elif form_type == 'vegetable':
            return VegetableFormSerializer
        return None

    def get(self, request, *args, **kwargs):
        """Retrieve the form data if already filled."""
        form = self.get_object()
        serializer = self.get_serializer(form)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        """Update the form data if it's not filled or modify existing data."""
        form = self.get_object()
        serializer = self.get_serializer(form, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        # Update the form and mark it as filled
        serializer.save(filled_by = request.user, is_filled=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

@permission_classes([IsAuthenticated])
class InputFormDetailView(APIView):
    def get(self, request, batch_id):
        try:
            batch = Batch.objects.get(id=batch_id)
            input_form = InputForm.objects.get(batch=batch)

            # Serialize the input form data
            serializer = InputFormSerializer(input_form)  # Ensure serializer_class is set correctly
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Batch.DoesNotExist:
            return Response({'detail': 'Batch not found.'}, status=status.HTTP_404_NOT_FOUND)
        except InputForm.DoesNotExist:
            return Response({'detail': 'Input form not found for this batch.'}, status=status.HTTP_404_NOT_FOUND)

@permission_classes([IsAuthenticated])
class CombinedFormListView(APIView):
    def get(self, request, batch_id):
        try:
            # Get the batch with the given batch_id
            batch = Batch.objects.filter(id=batch_id).first()

            if not batch:
                return Response({'detail': 'Batch not found.'}, status=status.HTTP_404_NOT_FOUND)

            # Fetch associated forms
            input_form = InputForm.objects.filter(batch=batch).first()
            output_form = OutputForm.objects.filter(batch=batch).first()
            blanching_form = BlanchingForm.objects.filter(batch=batch).first()

            if not input_form or not output_form:
                return Response({'detail': 'Input or Output form not found for this batch.'}, status=status.HTTP_404_NOT_FOUND)

            # Prepare combined data
            data = {
                'input_form': input_form,
                'output_form': output_form,
                'blanching_form': blanching_form
            }

            serializer = CombinedFormSerializerfordp(data)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@permission_classes([IsAuthenticated])
class CombinedBlanchingFormListView(APIView):
    def get(self, request, vegetable_id):
        try:
            # Get the date filter from query params
            date_filter = request.query_params.get('date', None)

            if date_filter:
                parsed_date = parse_date(date_filter)
                if not parsed_date:
                    return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Filter batches by vegetable_id and created_at date
                batches = Batch.objects.filter(vegetable_id=vegetable_id, created_at__date=parsed_date)
            else:
                # Get all batches for the vegetable if no date is provided
                batches = Batch.objects.filter(vegetable_id=vegetable_id)

            if not batches.exists():
                return Response({'detail': 'No batches found for this vegetable on the given date.'}, status=status.HTTP_404_NOT_FOUND)

            combined_data = []

            for batch in batches:
                # Fetch all blanching records for the batch
                blanching_records = BlanchingForm.objects.filter(batch=batch)

                # Prepare blanching records data
                for record in blanching_records:
                    data = {
                        'time': record.time.strftime("%I:%M %p"),  # Format time as required
                        'blancher': {
                            'beltSpeed': f"{record.blancher_belt_speed} m/min",
                            'temperature': f"{record.blancher_temperature}°C"
                        },
                        'cooler': {
                            'beltSpeed': f"{record.cooler_belt_speed} m/min",
                            'temperature': f"{record.cooler_temperature}°C"
                        },
                        'sprayNozzle': {
                            'blancher': record.spray_nozzle_blancher,
                            'cooler': record.spray_nozzle_cooler
                        },
                        'meshCleaning': {
                            'preCooler': record.spray_nozzle_precooler,
                            'beltSpeed1': f"{record.belt_speed_1} m/min",
                            'beltSpeed2': f"{record.belt_speed_2} m/min"
                        },
                        'iqf': {
                            'airTemp': f"{record.iqf_air_temperature}°C",
                            'coilTemp': f"{record.iqf_coil_temperature}°C",
                            'productTemp': f"{record.iqf_product_temperature}°C"
                        },
                        'bagNo': f"B{record.bag_number:03}",  # Format bag number as "B001"
                        'totalBag': record.total_bag
                    }

                    combined_data.append(data)

            if not combined_data:
                return Response({'detail': 'No blanching records found for the given vegetable and date.'}, status=status.HTTP_404_NOT_FOUND)

            return Response(combined_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

@permission_classes([IsAuthenticated])
class CombinedFormDashboardView(APIView):
    def get(self, request, vegetable_id):
        try:
            # Get the date parameter from the request
            date_str = request.query_params.get('date', None)
            if not date_str:
                return Response({'detail': 'Date parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # Convert date string to a datetime object
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return Response({'detail': 'Invalid date format. Use YYYY-MM-DD.'}, status=status.HTTP_400_BAD_REQUEST)

            # Fetch all batches for the given vegetable_id and date
            batches = Batch.objects.filter(vegetable_id=vegetable_id, created_at__date=date_obj).order_by('-created_at')

            if not batches.exists():
                return Response({'detail': 'No batches found for this vegetable on the given date.'}, status=status.HTTP_404_NOT_FOUND)

            # Iterate over each batch and get the associated forms
            batch_data_list = []

            for batch in batches:
                try:
                    input_form = InputForm.objects.get(batch=batch)
                    washing_form = WashingForm.objects.get(batch=batch)
                    blanching_form = BlanchingForm.objects.get(batch=batch)
                    output_form = OutputForm.objects.get(batch=batch)

                    batch_data = {
                        'batch_id': batch.id,
                        'created_at': batch.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                        'date': input_form.date.strftime("%Y-%m-%d"),
                        'name_of_raw_material': input_form.name_of_rm,
                        'lot_number': input_form.lot_number,
                        'wt_supplier': input_form.wt_supplier,
                        'wt_ours': input_form.wt_ours,
                        'waste': washing_form.waste,
                        'final_bags': output_form.final_bags,
                        'waste_blanching': blanching_form.waste_blancing,
                        'final_recovery': output_form.final_recovery,
                    }

                    batch_data_list.append(batch_data)

                except InputForm.DoesNotExist:
                    logger.warning(f"Input form missing for batch {batch.id}")
                except WashingForm.DoesNotExist:
                    logger.warning(f"Washing form missing for batch {batch.id}")
                except BlanchingForm.DoesNotExist:
                    logger.warning(f"Blanching form missing for batch {batch.id}")
                except OutputForm.DoesNotExist:
                    logger.warning(f"Output form missing for batch {batch.id}")

            if not batch_data_list:
                return Response({'detail': 'No complete data found for the given date and vegetable.'}, status=status.HTTP_404_NOT_FOUND)

            return Response(batch_data_list, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in CombinedFormDashboardView: {str(e)}", exc_info=True)
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

from django.utils.dateparse import parse_date
@permission_classes([IsAuthenticated])
class RecentVegetableEntriesView(APIView):
    """
    API View to get all batch entries for each vegetable on a specific date.
    - If no date is provided, returns all batches.
    - Sorted by vegetable_id (ascending)
    - Inside each vegetable, batches are sorted by created_at (descending)
    """

    def get(self, request):
        try:
            # Get the date filter from query params
            date_filter = request.query_params.get('date', None)

            # Filter batches by date if provided
            if date_filter:
                try:
                    parsed_date = parse_date(date_filter)
                    if not parsed_date:
                        return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Filter batches created on the given date
                    vegetable_batches = Batch.objects.filter(created_at__date=parsed_date)
                except ValueError:
                    return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Get all batches if no date is provided
                vegetable_batches = Batch.objects.all()

            vegetable_batches = vegetable_batches.order_by('vegetable_id', '-created_at')

            if not vegetable_batches.exists():
                return Response({'detail': 'No data available.'}, status=status.HTTP_404_NOT_FOUND)

            # Group batches under their vegetable_id
            recent_entries = defaultdict(list)

            for batch in vegetable_batches:
                # Fetch related forms
                input_form = InputForm.objects.filter(batch=batch).first()
                washing_form = WashingForm.objects.filter(batch=batch).first()
                blanching_form = BlanchingForm.objects.filter(batch=batch).first()
                output_form = OutputForm.objects.filter(batch=batch).first()

                # Prepare response data
                data = {
                    "batch_id": batch.id,
                    "created_at": batch.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                    "date": input_form.date.strftime("%Y-%m-%d") if input_form else None,
                    "name_of_raw_material": input_form.name_of_rm if input_form else None,
                    "lot_number": input_form.lot_number if input_form else None,
                    "wt_supplier": input_form.wt_supplier if input_form else None,
                    "wt_ours": input_form.wt_ours if input_form else None,
                    "waste": washing_form.waste if washing_form else None,
                    "final_bags": output_form.final_bags if output_form else None,
                    "waste_blanching": blanching_form.waste_blancing if blanching_form else None,
                    "vendor_name": input_form.vendor_name if input_form else None,
                    "final_recovery": output_form.final_recovery if output_form else None,
                    "packing": output_form.packing if output_form else None,
                    "vehicle_number": input_form.vehicle_number if input_form else None
                }

                # Append batch data under its respective vegetable_id
                recent_entries[batch.vegetable_id].append(data)

            if not recent_entries:
                return Response({'detail': 'No complete entries found.'}, status=status.HTTP_404_NOT_FOUND)

            # Convert defaultdict to a sorted dictionary
            sorted_entries = {
                vegetable_id: sorted(batches, key=lambda x: x["created_at"], reverse=True)
                for vegetable_id, batches in sorted(recent_entries.items())  # Sort vegetable_id (ascending)
            }

            return Response(sorted_entries, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in RecentVegetableEntriesView: {str(e)}", exc_info=True)
            return Response({'error': 'Internal Server Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.utils.decorators import method_decorator
from django.views import View

@method_decorator(csrf_exempt, name='dispatch')
@permission_classes([IsAuthenticated])
class AllDataView(APIView):
    def get(self, request):
        """Retrieve all PieChartData records for a given date"""
        date = request.query_params.get('date')  # ✅ Use query_params for GET request

        if not date:
            return Response({"error": "Date parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pie_chart_data = PieChartData.objects.filter(date=date)
            if not pie_chart_data.exists():  # ✅ Check if data exists
                return Response({"message": "Data not found"}, status=status.HTTP_404_NOT_FOUND)

            serializer = PieChartDataSerializer(pie_chart_data, many=True)  # ✅ Serialize multiple objects
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@permission_classes([IsAuthenticated])
class PieChartDataView(APIView):
    def get(self, request):
        vegetable_id = request.query_params.get('vegetable_id')
        date = request.query_params.get('date')

        if not vegetable_id or not date:
            return Response({"error": "vegetable_id and date are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pie_chart_data = PieChartData.objects.get(vegetable_id=vegetable_id, date=date)
            serializer = PieChartDataSerializer(pie_chart_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PieChartData.DoesNotExist:
            return Response({"message": "Data not found"}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        vegetable_id = request.data.get('vegetable_id')
        date = request.data.get('date')
        data = request.data.get('data', 0)
        waste_pie = request.data.get('waste_pie', 0)  # ✅ Read waste_pie
        
        if not vegetable_id or not date:
            return Response({"error": "vegetable_id and date are required"}, status=status.HTTP_400_BAD_REQUEST)

        pie_chart_data, created = PieChartData.objects.get_or_create(
            vegetable_id=Vegetable.objects.get(id=vegetable_id),
            date=date,
            defaults={'data': data,'waste_pie': waste_pie}
        )

        if not created:
            pie_chart_data.data = data
            pie_chart_data.waste_pie = waste_pie
            pie_chart_data.save()

        serializer = PieChartDataSerializer(pie_chart_data)
        return Response(serializer.data, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)
    
    

@permission_classes([IsAuthenticated])
class LineGraphView(APIView):
    def get(self, request):
        vegetable_id = request.query_params.get('vegetable_id')
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')

        if not vegetable_id or not from_date or not to_date:
            return Response({"error": "vegetable_id, from_date, and to_date are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            pie_chart_data = PieChartData.objects.filter(vegetable_id=vegetable_id, date__range=[from_date, to_date])
            
            if not pie_chart_data.exists():
                return Response({"message": "No data found for the given range"}, status=status.HTTP_404_NOT_FOUND)

            serializer = PieChartDataSerializer(pie_chart_data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)