#coding:utf-8
from django.http import HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required,permission_required
from django.shortcuts import render_to_response
from django.contrib import auth
from django.shortcuts import render
from django.utils.log import logging
from django.conf import settings
from django.template import RequestContext   
from django.db.models import Q     
from subprocess import Popen,PIPE
from Crypto.PublicKey import RSA
from ldapserver.api import *
from yunwei.models import *
from ldapuser.models import *
from ldapperm.models import *
import random
import crypt
import re
import time
import MySQLdb
import json
import paramiko

def login(request):
    #return render_to_response("login.html",{})
    #return render_to_response("dept_add.html",{})
    return render_to_response("index.html",{})
@require_login
def index(request):
    return render_to_response('index.html')
@require_login
def index_cu(request):
    user_id = request.session.get('user_id')
    print user_id
    user = User.objects.filter(id=user_id)
    if user:
        user = user[0]
    user_id = request.session.get('user_id')
    username = User.objects.get(id=user_id).username
    posts = user_perm_asset_api(username)
    host_count = len(posts)
    new_posts = []
    post_five = []
    for post in posts:
        if len(post_five) < 5:
            post_five.append(post)
        else:
            new_posts.append(post_five)
            post_five = []
    new_posts.append(post_five)
    return render_to_response('index_cu.html', locals(), context_instance=RequestContext(request))
def account_login(request):
#    print request.POST
#    username = request.POST.get('username')
#    password = request.POST.get('password')
#    user = auth.authenticate(username=username,password=password)
#    if user is not None:
#        auth.login(request,user)
#        return HttpResponseRedirect('/dashboard/')
#    else:
#        return render_to_response('index.html',{'login_err':"Wrong username and password!"})
    if request.session.get('username'):
        return HttpResponseRedirect('/dashboard/')
    if request.method == 'GET':
        return render_to_response('index.html')
    else:
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_filter = User.objects.filter(username=username)
        if user_filter:
            user = user_filter[0]
            if md5_crypt(password) == user.password:
                request.session['user_id'] = user.id
                user_filter.update(last_login=datetime.datetime.now())
                if user.role == 'SU':
                    request.session['role_id'] = 2
                elif user.role == 'DA':
                    request.session['role_id'] = 1
                else:
                    request.session['role_id'] = 0
                response = HttpResponseRedirect('/dashboard/', )
                response.set_cookie('username', username, expires=604800)
                response.set_cookie('seed', md5_crypt(password), expires=604800)
                return response
            else:
                error = '密码错误，请重新输入。'
        else:
            error = '用户不存在。'
    return render_to_response('index.html', {'error': error})
def logout(request):
    request.session.delete()
    return render_to_response('index.html')
#@login_required
def dashboard(request):
    #username = request.session.get('username')
    #return render_to_response('dashboard.html',{'user':request.user})
    #return render_to_response('dashboard.html',{'username':username})

    if is_common_user(request):
        return index_cu(request)
    username = request.session.get('username')
    return render_to_response('dashboard.html',{'username':username})
#@login_required
def tcloudvm(request):
    return render_to_response('tcloudvm.html',{})
def create_vm(request):
    print request.POST
    tcloudvm_conf = '/root/ops/static/scripts/tcloudvm.conf'
    vm_list = '/root/ops/static/scripts/vmlist'
    rsync_cmd = 'prsync -arzv -H root@124.251.36.114 %s /root/python/server_info.py' %(tcloudvm_conf)
    createvm_cmd = 'pssh -H root@124.251.36.114 -P "source tcloud-openrc.sh;python /root/2.py"'
    msg = None
    servername = request.POST.get('servername')
    owner = request.POST.get('owner')
    security = request.POST.get('security')
    type = request.POST.get('type')
    publicip = request.POST.get('publicip')
    disknum = request.POST.get('disknum')
    disksize = request.POST.get('disksize')
    software = request.POST.get('software')
    print software
    list = ['security','type','publicip','disknum','disksize','software','owner']
    list1 = [str(security),str(type),str(publicip),str(disknum),str(disksize),str(software),str(owner)]    
    print list1
    vm_add = dict(zip(list,list1))
    print vm_add
    a = 'server_info = { \'%s\':%s,\n} '
    if servername:
        with open(vm_list) as fp:
            vm_exist = fp.read()
            if servername not in vm_exist:
                with open(tcloudvm_conf,'w') as fp:
                    fp.write(a % (servername,vm_add))
                    fp.flush()
                    p1 = Popen(rsync_cmd,shell=True,stdout=PIPE,stderr=PIPE)
                    p2 = Popen(createvm_cmd,shell=True,stdout=PIPE,stderr=PIPE)
                    if p1.wait() == 0 and p2.wait() == 0:
                        msg = u'createvm sucessed!'
                        with open(vm_list,'a+') as fp:
                            fp.write(str(servername)+'\n')
                    else:
                        msg = u'createvm failed!'
            else:
                msg = u'vm is exists!'
    else:
        msg = u'input error!'
    return render(request,'tcloudvm.html',{'msg':msg})
#@login_required
def codedeploy(request):
    names = AppInfor.objects.all()
    return render(request,'codedeploy.html',{'user':request.user,'names':names})
def code(request):
    print request.POST
    appname = request.POST.get('app_name')
    version = request.POST.get('deploy_version')
    ip = request.POST.get('deploy_ip')
    id = request.POST.get('deploy_id')
    codedeploy_conf = '/root/ops/static/scripts/codedeploy.conf'
    rsyncd_cmd = 'prsync -arzv -H %s %s /home/work/python/deploy_info.py'%(ip,codedeploy_conf)
    codedeploy_cmd = 'pssh -H %s -P "python /home/work/%s.py"'%(ip,appname)
    msg = None
    list = ['app_name','version','app_ip','app_id']
    list1 = [str(appname),str(version),str(ip),str(id)]
    code_deploy = dict(zip(list,list1))
    a = 'deploy_info = %s'
    with open(codedeploy_conf,'w') as fp:
        fp.write(a % (code_deploy))
        fp.flush()
        p1 = Popen(rsyncd_cmd,shell=True,stdout=PIPE,stderr=PIPE)
        p2 = Popen(codedeploy_cmd,shell=True,stdout=PIPE,stderr=PIPE)
        time.sleep(15)
        if p1.wait() == 0 and p2.wait() == 0:
            msg = u'codedeploy sucessed!'
        else:
            msg = u'codedeploy failed!'
    names = AppInfor.objects.all()
    return render(request,'codedeploy.html', {'msg':msg,'names':names})     
#@login_required
def saltstack(request):
    return render_to_response('saltstack.html',{'user':request.user})
def collect(request):
    global hostname
    if request.POST:
        vendor = request.POST.get('Product_Name')
        sn = request.POST.get('Serial_Number')
        product = request.POST.get('Manufacturer')
        cpu_model = request.POST.get('Model_Name')
        cpu_num = request.POST.get('Cpu_Cores')
        memory_size = request.POST.get('memory_size')
        device_size = request.POST.get('device_size')
        osver = request.POST.get('os_version')
        hostname = request.POST.get('os_name')
        os_release = request.POST.get('os_release')
        ipaddr = request.POST.get('Ipaddr')
        mac = request.POST.get('Mac')
        mask = request.POST.get('Mask')
        network = request.POST.get('Device')
    try:
        host = Host.objects.get(hostname = hostname)
    except:
        host = Host()
        host.hostname = hostname
        host.vendor = vendor
        host.sn = sn
        host.product = product
        host.cpu_model = cpu_model
        host.cpu_num = cpu_num
        host.memory_size = memory_size
        host.device_size = device_size
        host.osver = osver
        host.os_release = os_release
        host.ipaddr = ipaddr
        host.mac = mac
        host.mask = mask
        host.network = network
        host.save()
        return HttpResponse('ok')
    else:
        return HttpResponse('no data,hahahahaha')
def getjson(request):
    d = []
    names = Host.objects.all()
    for a in names:
        b = a.ipaddr
	c = list(eval(b))
	server_lip = c[0]
	e = a.hostname
	f = list(eval(e))
	server_name = f[0]
	g = a.osver
	h = list(eval(g))
        server_op = h[0]
	ret = {'server_name':server_name,'server_lip':server_lip,'server_op':server_op}
        d.append(ret)
    return HttpResponse(json.dumps(d))
#@login_required
def cmdb(request):
    names = Host.objects.all()
    return render(request,'cmdb.html',{'user':request.user,'names':names})
def cmdbsubmit(request):
    position = request.POST.get('position')
    iloip = request.POST.get('iloip')
    netport = request.POST.get('netport')
    manageport = request.POST.get('manageport')
    datastorageport = request.POST.get('datastorageport')
    id = request.POST.get('cmdb_id')
    sn = req.POST.get('serial_number')
    sql='update yunwei_host set position="%s",iloip="%s",netport="%s",manageport="%s",datastorageport="%s" where id="%s"'%(position,iloip,netport,manageport,datastorageport,id)
    conn= MySQLdb.connect(host="localhost" ,user= "root",passwd ="sup@hp123",port=3306,db='tclsupport')
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()
    names = Host.objects.all()
    return render(request,'cmdb.html', {'msg':msg,'names':names})     
#@login_required
def authority(request):
    return render_to_response('authority.html',{'user':request.user})
def operation(request):
    return render_to_response('operation.html',{'user':request.user})
#@login_required
def user(request):
    return render_to_response('user.html',{'user':request.user})
def download(request):
    return render_to_response('download.html', locals(), context_instance=RequestContext(request))
def transfer(sftp, filenames):
    for filename, file_path in filenames.items():
        print filename, file_path
        sftp.put(file_path, '/data/repos/%s' % filename)
    sftp.close()
def upload(request):
    user, dept = get_session_user_dept(request)
    if request.method == 'POST':
        hosts = request.POST.get('hosts')
        upload_files = request.FILES.getlist('file[]', None)
        upload_dir = "/data/repos/%s" % user.username
        is_dir(upload_dir)
        date_now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        hosts_list = hosts.split(',')
        user_hosts = get_user_host(user.username).keys()
        unperm_hosts = []
        filenames = {}
        for ip in hosts_list:
            if ip not in user_hosts:
                unperm_hosts.append(ip)
        if not hosts:
            return HttpResponseNotFound(u'地址不能为空')
        if unperm_hosts:
            print hosts_list
            return HttpResponseNotFound(u'%s 没有权限.' % ', '.join(unperm_hosts))
        for upload_file in upload_files:
            file_path = '%s/%s.%s' % (upload_dir, upload_file.name, date_now)
            filenames[upload_file.name] = file_path
            f = open(file_path, 'w')
            for chunk in upload_file.chunks():
                f.write(chunk)
            f.close()
        sftps = []
        for host in hosts_list:
            username, password, host, port = get_connect_item(user.username, host)
            try:
                t = paramiko.Transport((host, port))
                t.connect(username=username, password=password)
                sftp = paramiko.SFTPClient.from_transport(t)
                sftps.append(sftp)
            except paramiko.AuthenticationException:
                return HttpResponseNotFound(u'%s 连接失败.' % host)
        for sftp in sftps:
            transfer(sftp,filenames)
        return HttpResponse('传送成功')
    return render_to_response('file_upload.html', locals(), context_instance=RequestContext(request))

