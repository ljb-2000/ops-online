from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()
from yunwei.views import *

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ops.views.home', name='home'),
    # url(r'^ops/', include('ops.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
       (r'^login/$', 'yunwei.views.login'),
       (r'^$',index),
       (r'^account_login/$',account_login),
       (r'^logout/$',logout),
       (r'^dashboard/$',dashboard),
       (r'^tcloudvm/$','yunwei.views.tcloudvm'),
      #(r'^create_vm/$',create_vm),
       (r'^codedeploy/$','yunwei.views.codedeploy'),
       (r'^code/$',code),
       (r'^cmdbsubmit/$',cmdbsubmit),
       (r'^collect/$',collect),
       (r'^getjson/$',getjson),
       (r'^cmdb/$','yunwei.views.cmdb'),
       (r'^index_cu/$', index_cu),
       (r'^upload/$', upload),
       (r'^saltstack/$',saltstack),
       (r'^operation/$',operation),
       (r'^ldapperm/',include('ldapperm.urls')),
       (r'^ldapuser/',include('ldapuser.urls')),
       (r'^asset/',include('asset.urls')),
)
