from django.contrib import admin
from models import Host
from models import HostGroup

class HostAdmin(admin.ModelAdmin):
    list_display = [
                'vendor',
                'sn',
                'product',
                'cpu_model',
                'cpu_num',
                'memory_size',
                'device_size',
                'network',
                'ipaddr',
                'mac',
                'mask',
                'osver',
                'os_release',
                'hostname',
                'position',
                'iloip',
                'netport',
                'manageport',
                'datastorageport',
                ]
 

class HostGroupAdmin(admin.ModelAdmin):
    list_display = ['groupname']
 
admin.site.register(Host,HostAdmin)
admin.site.register(HostGroup,HostGroupAdmin)	

