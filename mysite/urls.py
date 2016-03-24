from django.conf.urls import patterns, include, url
from django.contrib import admin
from mysite.views import home

urlpatterns = patterns('',
    # Examples:
   
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', home, name = 'home'),
    url(r'^lists/', include('lists.urls', namespace="lists")),
 #   url(r'^admin/', include(admin.site.urls)),
    
    
)