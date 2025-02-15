from django.urls import path
from .views import GetCatalogData
from .views import ImportJsonView
from .views import check_code_client_exists
from .views import CheckNameUnicity
from .views import ConsolidatedObjectsView, filtered_objects,update_objects
from .views import AddNewLigneConsolidated, LoadOwnerCodeDetails
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

urlpatterns = [
    path('token', TokenObtainPairView.as_view(), name='get_token'),
    path('token/refresh', TokenRefreshView.as_view(), name='token_refresh'),   
    path('UpdateDatas', ImportJsonView.as_view(), name='loadjsondata'),
    path('CheckOwnerCodeUnicity', check_code_client_exists.as_view(), name='checkunicitycodeclient'),
    path('CheckNameUnicity', CheckNameUnicity.as_view(), name='CheckNameUnicity'),
    path('GetdataConsolided', ConsolidatedObjectsView.as_view(), name='GetConsolidate'),
    path('GetObjectFromCao', filtered_objects, name='getOjectFromcao'),
    path('PutObjectFromCao', update_objects, name='updateFromCao'),
    path('addNewLigneConsolide', AddNewLigneConsolidated.as_view(), name='add-row'),
    path('loadCodeDetails', LoadOwnerCodeDetails.as_view(), name='insertOwnerCode'),
    path('getCatalogue', GetCatalogData.as_view(), name='getcatalogue'),
]