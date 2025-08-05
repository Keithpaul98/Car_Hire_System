from django.urls import path
from . import views

app_name = 'vehicles'

urlpatterns = [
    # Main vehicle endpoints
    path('', views.VehicleListView.as_view(), name='vehicle-list'),
    path('<uuid:id>/', views.VehicleDetailView.as_view(), name='vehicle-detail'),
    path('search/', views.VehicleSearchView.as_view(), name='vehicle-search'),
    path('statistics/', views.vehicle_statistics, name='vehicle-statistics'),
    path('<uuid:vehicle_id>/availability/', views.vehicle_availability_check, name='vehicle-availability'),
    
    # Vehicle categories
    path('categories/', views.VehicleCategoryListView.as_view(), name='category-list'),
    
    # Vehicle brands
    path('brands/', views.VehicleBrandListView.as_view(), name='brand-list'),
    
    # Vehicle models
    path('models/', views.VehicleModelListView.as_view(), name='model-list'),
    
    # Vehicle features
    path('features/', views.VehicleFeatureListView.as_view(), name='feature-list'),
    
    # Vehicle images
    path('<uuid:vehicle_id>/images/', views.VehicleImageListView.as_view(), name='vehicle-images'),
    
    # Vehicle maintenance records
    path('<uuid:vehicle_id>/maintenance/', views.VehicleMaintenanceListView.as_view(), name='vehicle-maintenance'),
] 