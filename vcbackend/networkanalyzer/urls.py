"""vcbackend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path, re_path
from rest_framework import routers, permissions
from networkanalyzer import views
from django.conf import settings
from rest_framework_jwt.views import obtain_jwt_token
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
      title="Citel NAP API",
      default_version='v1',
      description="Test description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

router = routers.DefaultRouter()
router.register('users', views.UserViewSet)
router.register('GetStoreData', views.RDSEdgesViewSet)
router.register('edges', views.RDSEdgesViewSet)
router.register('links', views.LinksViewSet)
router.register('GetEvents', views.EventsViewSet)
router.register('GetSiteData', views.SitesViewSet)
router.register('Database3', views.Database3ViewSet)
API_ROOT = f"api/{settings.API_VERSION}"
app_name = 'api'
urlpatterns = [
    path("", include(router.urls)),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path(r'api-token-auth/', obtain_jwt_token),
    path("hello/", views.hello), #a view for testing
    path(f'api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
