# coding: utf-8
import sys

reload(sys)
sys.setdefaultencoding('utf8')

from django.shortcuts import render_to_response
from django.template import RequestContext
from ldapperm.models import *
from django.db.models import Q
from ldapserver.api import *

def asset_cmd_groups_get(asset_groups_select='', cmd_groups_select=''):       
    asset_groups_select_list = []
    cmd_groups_select_list = []

    for asset_group_id in asset_groups_select:
        asset_groups_select_list.extend(BisGroup.objects.filter(id=asset_group_id))  

    for cmd_group_id in cmd_groups_select:
        cmd_groups_select_list.extend(CmdGroup.objects.filter(id=cmd_group_id))

    return asset_groups_select_list, cmd_groups_select_list

@require_admin
def perm_add(request):
    header_title, path1, path2 = u'主机授权添加', u'授权管理', u'授权添加'

    if request.method == 'GET':
        user_groups = UserGroup.objects.filter(id__gt=2)
        asset_groups = BisGroup.objects.all()

    else:
        name = request.POST.get('name', '')
        user_groups_select = request.POST.getlist('user_groups_select')
        asset_groups_select = request.POST.getlist('asset_groups_select')
        comment = request.POST.get('comment', '')

        user_groups, asset_groups = user_asset_cmd_groups_get(user_groups_select, asset_groups_select, '')[0:2]

        perm = Perm(name=name, comment=comment)
        perm.save()

        perm.user_group = user_groups
        perm.asset_group = asset_groups
        msg = '添加成功'
    return render_to_response('perm_add.html', locals(), context_instance=RequestContext(request))

def dept_add_asset(dept_id, asset_list):
    dept = DEPT.objects.filter(id=dept_id)
    if dept:
        dept = dept[0]
        new_perm_asset = []
        for asset_id in asset_list:
            asset = Asset.objects.filter(id=asset_id)
            new_perm_asset.extend(asset)

        dept.asset_set.clear()
        dept.asset_set = new_perm_asset

@require_super_user
def dept_perm_edit(request):
    header_title, path1, path2 = u'部门授权添加', u'授权管理', u'部门授权添加'
    if request.method == 'GET':
        dept_id = request.GET.get('id', '')
        dept = DEPT.objects.filter(id=dept_id)
        if dept:
            dept = dept[0]
            asset_all = Asset.objects.all()
            asset_select = dept.asset_set.all()
            assets = [asset for asset in asset_all if asset not in asset_select]
    else:
        dept_id = request.POST.get('dept_id')
        asset_select = request.POST.getlist('asset_select')
        dept_add_asset(dept_id, asset_select)
        return HttpResponseRedirect('/ldapperm/dept_perm_list/')
    return render_to_response('dept_perm_edit.html', locals(), context_instance=RequestContext(request))

@require_super_user
def perm_list(request):
    header_title, path1, path2 = u'小组授权', u'授权管理', u'授权详情'
    keyword = request.GET.get('search', '')
    uid = request.GET.get('uid', '')
    agid = request.GET.get('agid', '')
    if keyword:
        contact_list = UserGroup.objects.filter(Q(name__icontains=keyword) | Q(comment__icontains=keyword))
    else:
        contact_list = UserGroup.objects.all().order_by('name')

    if uid:
        user = User.objects.filter(id=uid)
        print user
        if user:
            user = user[0]
            contact_list = contact_list.filter(user=user)

    if agid:
        contact_list_confirm = []
        asset_group = BisGroup.objects.filter(id=agid)
        if asset_group:
            asset_group = asset_group[0]
            for user_group in contact_list:
                if asset_group in user_group_perm_asset_group_api(user_group):
                    contact_list_confirm.append(user_group)
            contact_list = contact_list_confirm

    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(contact_list, request)
    return render_to_response('perm_list.html', locals(), context_instance=RequestContext(request))

@require_admin
def perm_list_adm(request):
    header_title, path1, path2 = u'小组授权', u'授权管理', u'授权详情'
    keyword = request.GET.get('search', '')
    uid = request.GET.get('uid', '')
    agid = request.GET.get('agid', '')
    user, dept = get_session_user_dept(request)
    contact_list = dept.usergroup_set.all().order_by('name')
    if keyword:
        contact_list = contact_list.filter(Q(name__icontains=keyword) | Q(comment__icontains=keyword))

    if uid:
        user = User.objects.filter(id=uid)
        print user
        if user:
            user = user[0]
            contact_list = contact_list.filter(user=user)

    if agid:
        contact_list_confirm = []
        asset_group = BisGroup.objects.filter(id=agid)
        if asset_group:
            asset_group = asset_group[0]
            for user_group in contact_list:
                if asset_group in user_group_perm_asset_group_api(user_group):
                    contact_list_confirm.append(user_group)
            contact_list = contact_list_confirm

    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(contact_list, request)
    return render_to_response('perm_list.html', locals(), context_instance=RequestContext(request))

@require_super_user
def dept_perm_list(request):
    header_title, path1, path2 = '查看部门', '授权管理', '部门授权'
    keyword = request.GET.get('search')
    if keyword:
        contact_list = DEPT.objects.filter(Q(name__icontains=keyword) | Q(comment__icontains=keyword)).order_by('name')
    else:
        contact_list = DEPT.objects.filter(id__gt=2)

    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(contact_list, request)

    return render_to_response('dept_perm_list.html', locals(), context_instance=RequestContext(request))

def perm_group_update(user_group_id, asset_groups_id_list):
    user_group = UserGroup.objects.filter(id=user_group_id)
    if user_group:
        user_group = user_group[0]
        old_asset_group = [perm.asset_group for perm in user_group.perm_set.all()]
        new_asset_group = []

        for asset_group_id in asset_groups_id_list:
            new_asset_group.extend(BisGroup.objects.filter(id=asset_group_id))

        del_asset_group = [asset_group for asset_group in old_asset_group if asset_group not in new_asset_group]
        add_asset_group = [asset_group for asset_group in new_asset_group if asset_group not in old_asset_group]

        for asset_group in del_asset_group:
            Perm.objects.filter(user_group=user_group, asset_group=asset_group).delete()

        for asset_group in add_asset_group:
            Perm(user_group=user_group, asset_group=asset_group).save()

@require_super_user
def perm_edit(request):
    if request.method == 'GET':
        header_title, path1, path2 = u'编辑授权', u'授权管理', u'授权编辑'
        user_group_id = request.GET.get('id', '')
        user_group = UserGroup.objects.filter(id=user_group_id)
        if user_group:
            user_group = user_group[0]
            asset_groups_all = BisGroup.objects.all()
            asset_groups_select = [perm.asset_group for perm in user_group.perm_set.all()]
            asset_groups = [asset_group for asset_group in asset_groups_all if asset_group not in asset_groups_select]
    else:
        user_group_id = request.POST.get('user_group_id')
        asset_group_id_list = request.POST.getlist('asset_groups_select')
        perm_group_update(user_group_id, asset_group_id_list)

        return HttpResponseRedirect('/ldapperm/perm_list/')
    return render_to_response('perm_edit.html', locals(), context_instance=RequestContext(request))

@require_admin
def perm_edit_adm(request):
    if request.method == 'GET':
        header_title, path1, path2 = u'编辑授权', u'授权管理', u'授权编辑'
        user_group_id = request.GET.get('id', '')
        user_group = UserGroup.objects.filter(id=user_group_id)
        user, dept = get_session_user_dept(request)
        if user_group:
            user_group = user_group[0]
            asset_groups_all = dept.bisgroup_set.all()
            asset_groups_select = [perm.asset_group for perm in user_group.perm_set.all()]
            asset_groups = [asset_group for asset_group in asset_groups_all if asset_group not in asset_groups_select]
    else:
        user_group_id = request.POST.get('user_group_id')
        asset_group_id_list = request.POST.getlist('asset_groups_select')
        print user_group_id, asset_group_id_list
        if not validate(request, user_group=[user_group_id], asset_group=asset_group_id_list):
            return HttpResponseRedirect('/')
        perm_group_update(user_group_id, asset_group_id_list)

        return HttpResponseRedirect('/ldapperm/perm_list/')
    return render_to_response('perm_edit.html', locals(), context_instance=RequestContext(request))

@require_admin
def perm_detail(request):
    header_title, path1, path2 = u'授权管理', u'小组管理', u'授权详情'
    group_id = request.GET.get('id')
    user_group = UserGroup.objects.filter(id=group_id)
    if user_group:
        user_group = user_group[0]
        users = user_group.user_set.all()
        group_user_num = len(users)
        perms = user_group.perm_set.all()
        asset_groups = [perm.asset_group for perm in perms]
    return render_to_response('perm_detail.html', locals(), context_instance=RequestContext(request))

@require_admin
def perm_del(request):
    perm_id = request.GET.get('id')
    perm = Perm.objects.filter(id=perm_id)
    if perm:
        perm = perm[0]
        perm.delete()
    return HttpResponseRedirect('/ldapperm/perm_list/')

@require_admin
def perm_asset_detail(request):
    header_title, path1, path2 = u'用户授权主机', u'权限管理', u'用户主机详情'
    user_id = request.GET.get('id')
    user = User.objects.filter(id=user_id)
    if user:
        user = user[0]
        assets_list = user_perm_asset_api(user.username)
    return render_to_response('perm_asset_detail.html', locals(), context_instance=RequestContext(request))

def unicode2str(unicode_list):
    return [str(i) for i in unicode_list]

def sudo_ldap_add(user_group, user_runas, asset_groups_select,
                  cmd_groups_select):
    if not LDAP_ENABLE:
        return True
    
    assets = []
    cmds = []
    user_runas = user_runas.split(',')
    if len(asset_groups_select) == 1 and asset_groups_select[0].name == 'ALL':
        asset_all = True
    else:
        asset_all = False
        for asset_group in asset_groups_select:
            assets.extend(asset_group.asset_set.all())

    if user_group.name == 'ALL':
        user_all = True
        users = []
    else:
        user_all = False
        users = user_group.user_set.all()

    for cmd_group in cmd_groups_select:
        cmds.extend(cmd_group.cmd.split(','))

    if user_all:
        users_name = ['ALL']
    else:
        users_name = list(set([user.username for user in users]))

    if asset_all:
        assets_ip = ['ALL']
    else:
        assets_ip = list(set([asset.ip for asset in assets]))

    name = 'sudo%s' % user_group.id
    sudo_dn = 'cn=%s,ou=Sudoers,%s' % (name, LDAP_BASE_DN)
    sudo_attr = {'objectClass': ['top', 'sudoRole'],
                 'cn': ['%s' % name],
                 'sudoCommand': unicode2str(cmds),
                 'sudoHost': unicode2str(assets_ip),
                 'sudoOption': ['!authenticate'],
                 'sudoRunAsUser': unicode2str(user_runas),
                 'sudoUser': unicode2str(users_name)}
    ldap_conn.delete(sudo_dn)
    ldap_conn.add(sudo_dn, sudo_attr)


def sudo_update(user_group, user_runas, asset_groups_select, cmd_groups_select, comment):
    asset_groups_select_list, cmd_groups_select_list = \
        asset_cmd_groups_get(asset_groups_select, cmd_groups_select)
    sudo_perm = user_group.sudoperm_set.all()
    if sudo_perm:
        sudo_perm.update(user_runas=user_runas, comment=comment)
        sudo_perm = sudo_perm[0]
        sudo_perm.asset_group = asset_groups_select_list
        sudo_perm.cmd_group = cmd_groups_select_list
    else:
        sudo_perm = SudoPerm(user_group=user_group, user_runas=user_runas, comment=comment)
        sudo_perm.save()
        sudo_perm.asset_group = asset_groups_select_list
        sudo_perm.cmd_group = cmd_groups_select_list

    sudo_ldap_add(user_group, user_runas, asset_groups_select_list, cmd_groups_select_list)

@require_super_user
def sudo_list(request):
    header_title, path1, path2 = u'Sudo授权', u'权限管理', u'Sudo权限详情'
    keyword = request.GET.get('search', '')
    contact_list = UserGroup.objects.all().order_by('name')
    if keyword:
        contact_list = contact_list.filter(Q(name__icontains=keyword) | Q(comment__icontains=keyword))

    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(contact_list, request)
    return render_to_response('sudo_list.html', locals(), context_instance=RequestContext(request))

@require_admin
def sudo_list_adm(request):
    header_title, path1, path2 = u'Sudo授权', u'权限管理', u'Sudo权限详情'
    keyword = request.GET.get('search', '')
    user, dept = get_session_user_dept(request)
    contact_list = dept.usergroup_set.all().order_by('name')
    if keyword:
        contact_list = contact_list.filter(Q(name__icontains=keyword) | Q(comment__icontains=keyword))

    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(contact_list, request)
    return render_to_response('sudo_list.html', locals(), context_instance=RequestContext(request))

@require_super_user
def sudo_edit(request):
    header_title, path1, path2 = u'Sudo授权', u'授权管理', u'Sudo授权'

    if request.method == 'GET':
        user_group_id = request.GET.get('id', '0')
        user_group = UserGroup.objects.filter(id=user_group_id)
        asset_group_all = BisGroup.objects.filter()
        cmd_group_all = CmdGroup.objects.all()
        if user_group:
            user_group = user_group[0]
            sudo_perm = user_group.sudoperm_set.all()
            if sudo_perm:
                sudo_perm = sudo_perm[0]
                asset_group_permed = sudo_perm.asset_group.all()
                cmd_group_permed = sudo_perm.cmd_group.all()
                user_runas = sudo_perm.user_runas
                comment = sudo_perm.comment
            else:
                asset_group_permed = []
                cmd_group_permed = []

            asset_groups = [asset_group for asset_group in asset_group_all if asset_group not in asset_group_permed]
            cmd_groups = [cmd_group for cmd_group in cmd_group_all if cmd_group not in cmd_group_permed]

    else:
        user_group_id = request.POST.get('user_group_id', '')
        users_runas = request.POST.get('runas') if request.POST.get('runas') else 'root'
        asset_groups_select = request.POST.getlist('asset_groups_select')
        cmd_groups_select = request.POST.getlist('cmd_groups_select')
        comment = request.POST.get('comment', '')
        user_group = UserGroup.objects.filter(id=user_group_id)
        if user_group:
            user_group = user_group[0]
            if LDAP_ENABLE:
                sudo_update(user_group, users_runas, asset_groups_select, cmd_groups_select, comment)
                msg = '修改成功'

        return HttpResponseRedirect('/ldapperm/sudo_list/')
    return render_to_response('sudo_edit.html', locals(), context_instance=RequestContext(request))

@require_admin
def sudo_edit_adm(request):
    header_title, path1, path2 = u'Sudo授权', u'授权管理', u'Sudo授权'
    user, dept = get_session_user_dept(request)
    if request.method == 'GET':
        user_group_id = request.GET.get('id', '0')
        if not validate(request, user_group=[user_group_id]):
            return render_to_response('/ldapperm/sudo_list/')
        user_group = UserGroup.objects.filter(id=user_group_id)
        asset_group_all = dept.bisgroup_set.all()
        cmd_group_all = dept.cmdgroup_set.all()
        if user_group:
            user_group = user_group[0]
            sudo_perm = user_group.sudoperm_set.all()
            if sudo_perm:
                sudo_perm = sudo_perm[0]
                asset_group_permed = sudo_perm.asset_group.all()
                cmd_group_permed = sudo_perm.cmd_group.all()
                user_runas = sudo_perm.user_runas
                comment = sudo_perm.comment
            else:
                asset_group_permed = []
                cmd_group_permed = []

            asset_groups = [asset_group for asset_group in asset_group_all if asset_group not in asset_group_permed]
            cmd_groups = [cmd_group for cmd_group in cmd_group_all if cmd_group not in cmd_group_permed]

    else:
        user_group_id = request.POST.get('user_group_id', '')
        users_runas = request.POST.get('runas', 'root')
        asset_groups_select = request.POST.getlist('asset_groups_select')
        cmd_groups_select = request.POST.getlist('cmd_groups_select')
        comment = request.POST.get('comment', '')
        user_group = UserGroup.objects.filter(id=user_group_id)
        if not validate(request, user_group=[user_group_id], asset_group=asset_groups_select):
            return render_to_response('/ldapperm/sudo_list/')
        if user_group:
            user_group = user_group[0]
            if LDAP_ENABLE:
                sudo_update(user_group, users_runas, asset_groups_select, cmd_groups_select, comment)
                msg = '修改成功'

        return HttpResponseRedirect('/ldapperm/sudo_list/')
    return render_to_response('sudo_edit.html', locals(), context_instance=RequestContext(request))

@require_admin
def sudo_detail(request):
    header_title, path1, path2 = u'Sudo授权详情', u'授权管理', u'授权详情'
    user_group_id = request.GET.get('id')
    user_group = UserGroup.objects.filter(id=user_group_id)
    if user_group:
        asset_groups = []
        cmd_groups = []
        user_group = user_group[0]
        users = user_group.user_set.all()
        group_user_num = len(users)

        for perm in user_group.sudoperm_set.all():
            asset_groups.extend(perm.asset_group.all())
            cmd_groups.extend(perm.cmd_group.all())
        print asset_groups
    return render_to_response('sudo_detail.html', locals(), context_instance=RequestContext(request))

@require_admin
def sudo_refresh(request):
    sudo_perm_all = SudoPerm.objects.all()
    for sudo_perm in sudo_perm_all:
        user_group = sudo_perm.user_group
        user_runas = sudo_perm.user_runas
        asset_groups_select = sudo_perm.asset_group.all()
        cmd_groups_select = sudo_perm.cmd_group.all()
        sudo_ldap_add(user_group, user_runas, asset_groups_select, cmd_groups_select)
    return HttpResponse('刷新sudo授权成功')

@require_super_user
def cmd_add(request):
    header_title, path1, path2 = u'sudo命令添加', u'授权管理', u'命令组添加'
    dept_all = DEPT.objects.all()

    if request.method == 'POST':
        name = request.POST.get('name')
        dept_id = request.POST.get('dept_id')
        cmd = ','.join(request.POST.get('cmd').split('\n'))
        comment = request.POST.get('comment')
        dept = DEPT.objects.filter(id=dept_id)

        try:
            if CmdGroup.objects.filter(name=name):
                error = '%s 命令组已存在'
                raise ServerError(error)

            if not dept:
                error = u"部门不能为空"
                raise ServerError(error)
        except ServerError, e:
            pass
        else:
            dept = dept[0]
            CmdGroup.objects.create(name=name, dept=dept, cmd=cmd, comment=comment)
            msg = u'命令组添加成功'
            return HttpResponseRedirect('/ldapperm/cmd_list/')

    return render_to_response('sudo_cmd_add.html', locals(), context_instance=RequestContext(request))

@require_admin
def cmd_add_adm(request):
    header_title, path1, path2 = u'sudo命令添加', u'授权管理', u'命令组添加'
    user, dept = get_session_user_dept(request)

    if request.method == 'POST':
        name = request.POST.get('name')
        cmd = ','.join(request.POST.get('cmd').split('\n'))
        comment = request.POST.get('comment')

        try:
            if CmdGroup.objects.filter(name=name):
                error = '%s 命令组已存在'
                raise ServerError(error)
        except ServerError, e:
            pass
        else:
            CmdGroup.objects.create(name=name, dept=dept, cmd=cmd, comment=comment)
            return HttpResponseRedirect('/ldapperm/cmd_list/')

        return HttpResponseRedirect('/ldapperm/cmd_list/')

    return render_to_response('sudo_cmd_add.html', locals(), context_instance=RequestContext(request))

@require_admin
def cmd_edit(request):
    header_title, path1, path2 = u'sudo命令修改', u'授权管理管理', u'命令组修改'

    cmd_group_id = request.GET.get('id')
    cmd_group = CmdGroup.objects.filter(id=cmd_group_id)
    dept_all = DEPT.objects.all()

    if cmd_group:
        cmd_group = cmd_group[0]
        cmd_group_id = cmd_group.id
        dept_id = cmd_group.dept.id
        name = cmd_group.name
        cmd = '\n'.join(cmd_group.cmd.split(','))
        comment = cmd_group.comment

    if request.method == 'POST':
        cmd_group_id = request.POST.get('cmd_group_id')
        name = request.POST.get('name')
        dept_id = request.POST.get('dept_id')
        cmd = ','.join(request.POST.get('cmd').split('\n'))
        comment = request.POST.get('comment')
        cmd_group = CmdGroup.objects.filter(id=cmd_group_id)

        dept = DEPT.objects.filter(id=dept_id)
        try:
            if not dept:
                error = '没有该部门'
                raise ServerError(error)

            if not cmd_group:
                error = '没有该命令组'
        except ServerError, e:
            pass
        else:
            cmd_group.update(name=name, cmd=cmd, dept=dept[0], comment=comment)
            return HttpResponseRedirect('/ldapperm/cmd_list/')
    return render_to_response('sudo_cmd_add.html', locals(), context_instance=RequestContext(request))

@require_admin
def cmd_list(request):
    header_title, path1, path2 = u'sudo命令查看', u'权限管理', u'Sudo命令添加'

    if is_super_user(request):
        cmd_groups = contact_list = CmdGroup.objects.all()
    else:
        user, dept = get_session_user_dept(request)
        cmd_groups = contact_list = dept.cmdgroup_set.all()
    p = paginator = Paginator(contact_list, 10)

    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    try:
        contacts = paginator.page(page)
    except (EmptyPage, InvalidPage):
        contacts = paginator.page(paginator.num_pages)
    return render_to_response('sudo_cmd_list.html', locals(), context_instance=RequestContext(request))

@require_admin
def cmd_del(request):
    cmd_group_id = request.GET.get('id')
    cmd_group = CmdGroup.objects.filter(id=cmd_group_id)

    if cmd_group:
        cmd_group[0].delete()
    return HttpResponseRedirect('/ldapperm/cmd_list/')

@require_admin
def cmd_detail(request):
    cmd_ids = request.GET.get('id').split(',')
    cmds = []
    if len(cmd_ids) == 1:
        if cmd_ids[0]:
            cmd_id = cmd_ids[0]
        else:
            cmd_id = 1
        cmd_group = CmdGroup.objects.filter(id=cmd_id)
        if cmd_group:
            cmd_group = cmd_group[0]
            cmds.extend(cmd_group.cmd.split(','))
            cmd_group_name = cmd_group.name
    else:
        cmd_groups = []
        for cmd_id in cmd_ids:
            cmd_groups.extend(CmdGroup.objects.filter(id=cmd_id))
        for cmd_group in cmd_groups:
            cmds.extend(cmd_group.cmd.split(','))

    cmds_str = ', '.join(cmds)

    return render_to_response('sudo_cmd_detail.html', locals(), context_instance=RequestContext(request))

