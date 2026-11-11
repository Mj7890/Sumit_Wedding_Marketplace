from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Restrict Django admin to staff only
admin.site.login_url = '/login/'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('cards.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = 'cards.views.custom_403'
handler404 = 'cards.views.custom_404'
