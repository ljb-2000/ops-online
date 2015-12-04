from django.db import models

class AppInfor(models.Model):
    appname = models.CharField(max_length=50)
    appip = models.CharField(max_length=50)
    livever = models.CharField(max_length=50)
    lastver = models.CharField(max_length=50)

    def __unicode__(self):
        return self.appname

class Host(models.Model):
    vendor = models.CharField(max_length=50,null=True) 
    sn = models.CharField(max_length=50,null=True)
    product = models.CharField(max_length=50,null=True)
    cpu_model = models.CharField(max_length=50,null=True) 
    cpu_num = models.CharField(max_length=5,null=True)
    memory_size = models.CharField(max_length=50,null=True) 
    device_size = models.CharField(max_length=50,null=True)
    network =  models.CharField(max_length=50,null=True)
    ipaddr = models.CharField(max_length=50,null=True)
    mac = models.CharField(max_length=50,null=True)
    mask = models.CharField(max_length=50,null=True)
    osver = models.CharField(max_length=50,null=True) 
    os_release = models.CharField(max_length=50,null=True)
    hostname = models.CharField(max_length=50,null=True)
    position = models.CharField(max_length=50,null=True)
    iloip = models.IPAddressField(max_length=50,null=True)
    netport = models.CharField(max_length=15,null=True)
    manageport = models.CharField(max_length=15,null=True)
    datastorageport = models.CharField(max_length=15,null=True)

    def __unicode__(self):
        return self.hostname
		
class HostGroup(models.Model):
    groupname = models.CharField(max_length=50)
    members = models.ManyToManyField(Host)

class ServerAppCateg(models.Model):
    id = models.IntegerField(primary_key=True, db_column='ID') 
    server_categ_id = models.IntegerField()
    app_categ_name = models.CharField(max_length=90)
    class Meta:
        db_table = u'yunwei_server_app_categ'

class ServerFunCateg(models.Model):
    id = models.IntegerField(primary_key=True, db_column='ID') 
    server_categ_name = models.CharField(max_length=60)
    class Meta:
        db_table = u'yunwei_server_fun_categ'

class ServerList(models.Model):
    server_name = models.CharField(max_length=39, primary_key=True)
    server_lip = models.CharField(max_length=36)
    server_op = models.CharField(max_length=30)
    server_app_id = models.IntegerField()
    class Meta:
        db_table = u'yunwei_server_list'

class ModuleList(models.Model):
    id = models.IntegerField(primary_key=True, db_column='ID') 
    module_name = models.CharField(max_length=60)
    module_caption = models.CharField(max_length=765)
    module_extend = models.CharField(max_length=6000)
    class Meta:
        db_table = u'yunwei_module_list'


