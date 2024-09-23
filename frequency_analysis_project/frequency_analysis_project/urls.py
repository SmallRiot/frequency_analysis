from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('analysis/', include('analysis.urls')),  
    path('', lambda request: HttpResponseRedirect('analysis/')),  # Редирект с главной страницы на /analysis/
]



if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
