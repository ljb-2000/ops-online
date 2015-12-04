# coding:utf-8
from django.conf.urls import patterns, include, url
from asset.views import *

urlpatterns = patterns('',
    url(r"^dept_host_ajax/$", dept_host_ajax),
    url(r"^show_all_ajax/$", show_all_ajax),
    url(r'^group_add/$', group_add),
    url(r'^group_edit/$', group_edit),
    url(r'^group_list/$', group_list),
    url(r'^group_detail/$', group_detail),
    url(r'^group_del_host/$', group_del_host),
    url(r'^group_del/$', group_del),
    url(r'^host_list/$', host_list),
)

