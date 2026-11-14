from django.urls import path, include
from rest_framework.routers import DefaultRouter

from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

router = DefaultRouter()


from django.urls import path
from .views import (InputFormDetailView, VegetableListCreateAPIView, VegetableRetrieveDestroyAPIView, 
                    BatchListForVegetableAPIView, InputFormCreateWithVegetableAPIView,
                    FormDetailCreateAPIView,CombinedFormListView,CombinedBlanchingFormListView,CombinedFormDashboardView,RecentVegetableEntriesView,PieChartDataView,
                    AllDataView,LineGraphView,create_employee,fetch_employees,delete_employee,login_user,get_logged_in_user,delete_vegetable,delete_batch,approve_forms)


urlpatterns = [
    path('users/employee/add', create_employee, name='create-employee'),
    path('users/employee/fetch', fetch_employees, name='fetch-employees'),
    path('users/employee/delete/<uuid:employee_id>', delete_employee, name='delete-employee'),
    path('users/employee/login', login_user, name='login-user'),
    path('users/employee/profile', get_logged_in_user, name='login-user-deatils'),
    
    path('vegetables/', VegetableListCreateAPIView.as_view(), name='vegetable-list-create'),
    path('vegetables/<int:pk>/', VegetableRetrieveDestroyAPIView.as_view(), name='vegetable-retrieve-destroy'),
    path('vegetables/<int:vegetable_id>/batches/', BatchListForVegetableAPIView.as_view(), name='batch-list-for-vegetable'),
    path('vegetables/<int:vegetable_id>/input-form/', InputFormCreateWithVegetableAPIView.as_view(), name='inputform-create'),
    path('batches/<int:batch_id>/<str:form_type>/', FormDetailCreateAPIView.as_view(), name='form-detail-create'),
    path('batches/input-form/<int:batch_id>/', InputFormDetailView.as_view(), name='inputform-detail'),
    path('vegetables/<int:batch_id>/combined-form/', CombinedFormListView.as_view(), name='combined-form-data-in-outputform-for-batch-data'),
    path('vegetables/<int:vegetable_id>/combined-blanching/', CombinedBlanchingFormListView.as_view(), name='combined-blanching-form-detail-for-processParamterTable'),
    path('vegetables/recent-vegetable/', RecentVegetableEntriesView.as_view(), name='combined-form-detail-recent-for-dailyProductionTable'),
    path('vegetables/output/by-date/', PieChartDataView.as_view(), name='output-by-date-for-outputform'),
    path('vegetables/per-day-data/', AllDataView.as_view(), name='per-day-data-for-pieChart'),    
    path('vegetables/<int:vegetable_id>/combined-bargraph/', CombinedFormDashboardView.as_view(), name='combined-form-detail'),
    path('vegetables/line-graph/', LineGraphView.as_view(), name='line-graph-data-for-lineGraph'),
    path('delete-vegetable/<int:vegetable_id>/', delete_vegetable, name='delete_vegetable'),
    path('delete-batch/<int:batch_id>/', delete_batch, name='delete_batch'),
    path('batches/<str:form_type>/<int:batch_id>/approve/', approve_forms, name='approve_forms'),
]