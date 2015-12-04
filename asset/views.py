# coding:utf-8

import ast  

from django.db.models import Q
from django.template import RequestContext
from django.shortcuts import get_object_or_404

from asset.models import *
from yunwei.models import *
from ldapperm.models import *
from ldapserver.api import *

cryptor = PyCrypt(KEY)

class RaiseError(Exception):
    pass

def my_render(template, data, request):
    return render_to_response(template, data, context_instance=RequestContext(request))

def get_host_groups(groups):
    ret = []
    for group_id in groups:
        group = BisGroup.objects.filter(id=group_id)
        if group:
            group = group[0]
            ret.append(group)
    group_all = get_object_or_404(BisGroup, name='ALL')
    ret.append(group_all)
    return ret

def get_host_depts(depts):
    ret = []
    for dept_id in depts:
        dept = DEPT.objects.filter(id=dept_id)
        if dept:
            dept = dept[0]
            ret.append(dept)
    return ret

def get_host_usergroups(usergroups):
    ret = []
    for usergroup_id in usergroups:
        usergroup = UserGroup.objects.filter(id=usergroup_id)
        if usergroup:
            usergroup = usergroup[0]
            ret.append(usergroup)
    return ret

@require_admin
def group_add(request):
    header_title, path1, path2 = u'添加主机组', u'资产管理', u'添加主机组'
    if is_super_user(request):
        posts = Asset.objects.all()
        edept = DEPT.objects.all()
    elif is_group_admin(request):
        dept_id = get_user_dept(request)
        dept = DEPT.objects.get(id=dept_id)
        posts = Asset.objects.filter(dept=dept)
        edept = get_session_user_info(request)[5]

    if request.method == 'POST':
        j_group = request.POST.get('j_group', '')
        j_dept = request.POST.get('j_dept', '')
        j_hosts = request.POST.getlist('j_hosts', '')
        j_comment = request.POST.get('j_comment', '')

        try:
            if is_group_admin(request) and not validate(request, asset=j_hosts, edept=[j_dept]):
                emg = u'添加失败, 您无权操作!'
                raise RaiseError

            elif BisGroup.objects.filter(name=j_group):
                emg = u'添加失败, 该主机组已存在!'
                raise RaiseError

        except RaiseError:
            pass

        else:
            j_dept = DEPT.objects.filter(id=j_dept)[0]
            group = BisGroup.objects.create(name=j_group, dept=j_dept, comment=j_comment)
            for host in j_hosts:
                g = Asset.objects.get(id=host)
                group.asset_set.add(g)
            smg = u'主机组 %s 添加成功' % j_group

    return my_render('asset_group_add.html', locals(), request)

@require_admin
def group_list(request):
    header_title, path1, path2 = u'查看主机组', u'资产管理', u'查看主机组'
    dept_id = get_user_dept(request)
    dept = DEPT.objects.get(id=dept_id)
    keyword = request.GET.get('keyword', '')
    gid = request.GET.get('gid')
    sid = request.GET.get('sid')
    if gid:
        if is_common_user(request):
            return httperror(request, u'您无权查看!')

        elif is_group_admin(request) and not validate(request, user_group=[gid]):
            return httperror(request, u'您无权查看!')

        posts = []
        user_group = UserGroup.objects.filter(id=gid)
        if user_group:
            user_group = user_group[0]
            perms = Perm.objects.filter(user_group=user_group)
            for perm in perms:
                posts.append(perm.asset_group)

    elif sid:
        if is_common_user(request):
            return httperror(request, u'您无权查看!')

        elif is_group_admin(request) and not validate(request, user_group=[sid]):
            return httperror(request, u'您无权查看!')

        posts = []
        user_group = UserGroup.objects.filter(id=sid)
        if user_group:
            user_group = user_group[0]
            for perm in user_group.sudoperm_set.all():
                posts.extend(perm.asset_group.all())
            posts = list(set(posts))
        else:
            return httperror(request, u'没有此sudo授权!')

    else:
        if is_super_user(request):
            if keyword:
                posts = BisGroup.objects.exclude(name='ALL').filter(
                    Q(name__contains=keyword) | Q(comment__contains=keyword))
            else:
                posts = BisGroup.objects.exclude(name='ALL').order_by('id')
        elif is_group_admin(request):
            if keyword:
                posts = BisGroup.objects.filter(Q(name__contains=keyword) | Q(comment__contains=keyword)).filter(
                    dept=dept)
            else:
                posts = BisGroup.objects.filter(dept=dept).order_by('id')
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)
    return my_render('asset_group_list.html', locals(), request)


@require_admin
def group_edit(request):
    header_title, path1, path2 = u'编辑主机组', u'资产管理', u'编辑主机组'
    group_id = request.GET.get('id', '')
    group = BisGroup.objects.filter(id=group_id)
    if group:
        group = group[0]
    else:
        httperror(request, u'没有这个主机组!')

    host_all = Asset.objects.all()
    dept_id = get_session_user_info(request)[3]
    eposts = Asset.objects.filter(bis_group=group)

    if is_group_admin(request) and not validate(request, asset_group=[group_id]):
        return httperror(request, '编辑失败, 您无权操作!')
    dept = DEPT.objects.filter(id=group.dept.id)
    if dept:
        dept = dept[0]
    else:
        return httperror(request, u'没有这个部门!')

    all_dept = dept.asset_set.all()
    posts = [g for g in all_dept if g not in eposts]

    if request.method == 'POST':
        j_group = request.POST.get('j_group', '')
        j_hosts = request.POST.getlist('j_hosts', '')
        j_dept = request.POST.get('j_dept', '')
        j_comment = request.POST.get('j_comment', '')

        j_dept = DEPT.objects.filter(id=int(j_dept))
        j_dept = j_dept[0]

        group.asset_set.clear()
        for host in j_hosts:
            g = Asset.objects.get(id=host)
            group.asset_set.add(g)
        BisGroup.objects.filter(id=group_id).update(name=j_group, dept=j_dept, comment=j_comment)
        smg = u'主机组%s修改成功' % j_group
        return HttpResponseRedirect('/asset/group_list')

    return my_render('asset_group_edit.html', locals(), request)

@require_admin
def group_detail(request):
    header_title, path1, path2 = u'主机组详情', u'资产管理', u'主机组详情'
    login_types = {'L': 'LDAP', 'M': 'MAP'}
    dept = get_session_user_info(request)[5]
    group_id = request.GET.get('id', '')
    group = BisGroup.objects.get(id=group_id)
    if is_super_user(request):
        posts = Asset.objects.filter(bis_group=group).order_by('ip')

    elif is_group_admin(request):
        if not validate(request, asset_group=[group_id]):
            return httperror(request, u'您无权查看!')
        posts = Asset.objects.filter(bis_group=group).filter(dept=dept).order_by('ip')

    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)
    return my_render('asset_group_detail.html', locals(), request)

@require_admin
def group_del_host(request):
    if request.method == 'POST':
        group_id = request.POST.get('group_id')
        offset = request.GET.get('id', '')
        group = BisGroup.objects.get(id=group_id)
        if offset == 'group':
            len_list = request.POST.get("len_list")
            for i in range(int(len_list)):
                key = "id_list[" + str(i) + "]"
                jid = request.POST.get(key)
                g = Asset.objects.get(id=jid)
                group.asset_set.remove(g)

    else:
        offset = request.GET.get('id', '')
        group_id = request.GET.get('gid', '')
        group = BisGroup.objects.get(id=group_id)
        g = Asset.objects.get(id=offset)
        group.asset_set.remove(g)

    return HttpResponseRedirect('/asset/group_detail/?id=%s' % group.id)

@require_admin
def group_del(request):
    offset = request.GET.get('id', '')
    if offset == 'multi':
        len_list = request.POST.get("len_list")
        for i in range(int(len_list)):
            key = "id_list[" + str(i) + "]"
            gid = request.POST.get(key)
            if is_group_admin(request) and not validate(request, asset_group=[gid]):
                return httperror(request, '删除失败, 您无权删除!')
            BisGroup.objects.filter(id=gid).delete()
    else:
        gid = int(offset)
        if is_group_admin(request) and not validate(request, asset_group=[gid]):
            return httperror(request, '删除失败, 您无权删除!')
        BisGroup.objects.filter(id=gid).delete()
    return HttpResponseRedirect('/asset/group_list/')

@require_admin
def dept_host_ajax(request):
    dept_id = request.GET.get('id', '')
    if dept_id not in ['1', '2']:
        dept = DEPT.objects.filter(id=dept_id)
        if dept:
            dept = dept[0]
            hosts = dept.asset_set.all()
    else:
        hosts = Asset.objects.all()

    return my_render('dept_host_ajax.html', locals(), request)

def show_all_ajax(request):
    env = request.GET.get('env', '')
    get_id = request.GET.get('id', '')
    host = Asset.objects.filter(id=get_id)
    if host:
        host = host[0]
    return my_render('show_all_ajax.html', locals(), request)

@require_login
def host_search(request):
    keyword = request.GET.get('keyword')
    login_types = {'L': 'LDAP', 'M': 'MAP'}
    dept = get_session_user_info(request)[5]
    post_all = Asset.objects.filter(Q(ip__contains=keyword) |
                                    Q(idc__name__contains=keyword) |
                                    Q(bis_group__name__contains=keyword) |
                                    Q(comment__contains=keyword)).distinct().order_by('ip')
    if is_super_user(request):
        posts = post_all

    elif is_group_admin(request):
        posts = post_all.filter(dept=dept)

    elif is_common_user(request):
        user_id, username = get_session_user_info(request)[0:2]
        post_perm = user_perm_asset_api(username)
        posts = list(set(post_all) & set(post_perm))
    contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)

    return my_render('host_search.html', locals(), request)

@require_login
def host_list(request):
    keyword = request.GET.get('keyword', '')
    dept_id = get_session_user_info(request)[3]
    dept = DEPT.objects.get(id=dept_id)
    did = request.GET.get('did', '')
    gid = request.GET.get('gid', '')
    sid = request.GET.get('sid', '')
    user_id = get_session_user_info(request)[0]
    post_all = Asset.objects.all().order_by('ip')
    post_keyword_all = Asset.objects.filter(Q(ip__contains=keyword) |
                                            Q(idc__name__contains=keyword) |
                                            Q(bis_group__name__contains=keyword) |
                                            Q(comment__contains=keyword)).distinct().order_by('ip')
    if did:
        if is_common_user(request):
            return httperror(request, u'您无权查看!')
        if is_group_admin(request):
            user, dept = get_session_user_dept(request)
        else:
            dept = DEPT.objects.get(id=did)
        posts = dept.asset_set.all()
        return my_render('host_list_nop.html', locals(), request)

    elif gid:
        if is_common_user(request):
            return httperror(request, u'您无权查看!')

        elif is_group_admin(request) and not validate(request, user_group=[gid]):
            return httperror(request, u'您无权查看!')

        posts = []
        user_group = UserGroup.objects.filter(id=gid)
        if user_group:
            perms = Perm.objects.filter(user_group=user_group)
            for perm in perms:
                for post in perm.asset_group.asset_set.all():
                    posts.append(post)
            posts = list(set(posts))     
        else:
            return httperror(request, u'没有这个小组!')
        return my_render('host_list_nop.html', locals(), request)

    elif sid:
        if is_common_user(request):
            return httperror(request, u'您无权查看!')

        elif is_group_admin(request) and not validate(request, user_group=[sid]):
            return httperror(request, u'您无权查看!')

        posts, asset_groups = [], []
        user_group = UserGroup.objects.filter(id=int(sid))
        if user_group:
            user_group = user_group[0]
            for perm in user_group.sudoperm_set.all():
                asset_groups.extend(perm.asset_group.all())
            for asset_group in asset_groups:
                posts.extend(asset_group.asset_set.all())
            posts = list(set(posts))
        else:
            return httperror(request, u'没有这个sudo授权!')
        return my_render('host_list_nop.html', locals(), request)

    else:
        if is_super_user(request):
            if keyword:
                posts = post_keyword_all
            else:
                posts = post_all
            contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)
            return my_render('host_list.html', locals(), request)

        elif is_group_admin(request):
            if keyword:
                posts = post_keyword_all.filter(dept=dept)
            else:
                posts = post_all.filter(dept=dept)

            contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)
            return my_render('host_list.html', locals(), request)

        elif is_common_user(request):
            user_id, username = get_session_user_info(request)[0:2]
            posts = user_perm_asset_api(username)
            contact_list, p, contacts, page_range, current_page, show_first, show_end = pages(posts, request)
            return my_render('host_list_common.html', locals(), request)

