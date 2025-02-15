from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from django.views.generic import RedirectView
from django.conf.urls.static import static
from drf_yasg import openapi
from core.views import index, menu, CustomLoginView, home2
from django.conf import settings

schema_view = get_schema_view(
    openapi.Info(
        title="API Documentation",
        default_version="v1",
        description="Documentation interactive de l'API Double Codification",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="razanajatovocela@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.DjangoModelPermissionsOrAnonReadOnly,),#IsAuthenticated
)
urlpatterns = [
    path('', RedirectView.as_view(url='/login/', permanent=False), name='index'),
    path('home/', index, name='home'),
     path('consolidation/', home2, name='consolidationedit'),
    path('menu/', menu, name='selectouvrage'),
    path('admin/', admin.site.urls),
    path('swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),    
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('login/', CustomLoginView.as_view(template_name='registration/login.html'), name='login'),
    path('api/', include('core.urls')),     
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
