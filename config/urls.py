
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from boutique.admin import tableau_de_bord

urlpatterns = [
    path(
    'admin/tableau-de-bord/',
    admin.site.admin_view(tableau_de_bord),
    name='admin_tableau_de_bord'
),
    path('admin/', admin.site.urls),
    path('', include('boutique.urls')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
