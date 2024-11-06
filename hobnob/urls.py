"""hobnob URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from schema_graph.views import Schema
from django.conf.urls.static import static
from django.utils.translation import ugettext_lazy as _

admin.site.site_header = _('HOBNOB')
admin.site.site_title = _('HOBNOB')
admin.autodiscover()
admin.site.enable_nav_sidebar = False


urlpatterns = [
#    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path('dashboard/', admin.site.urls),
    path('profile/', include('userprofile.urls')),
    path('events/', include('events.urls')),
    path('match/', include('matching.urls')),
    path('chat/', include('chatting.urls')),
    path('notifications/', include('notifications.urls')),
    path('silk/', include('silk.urls', namespace='silk')),
    path('api_doc', include('api_doc.urls')),
    path("schema", Schema.as_view()),

    path('v1/profile/', include('userprofile.urls', namespace="v1")),
    path('v1/events/', include('events.urls', namespace="v1")),
    path('v1/match/', include('matching.urls', namespace="v1")),
    path('v1/chat/', include('chatting.urls', namespace="v1")),
    path('v1/notifications/', include('notifications.urls', namespace="v1")),
]
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL,
                          document_root=settings.STATIC_ROOT)
