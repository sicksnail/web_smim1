from django.urls import path,re_path
from METSMY import views

urlpatterns = [
    #本模块上级目录taskmng
    path('success/', views.optsuccess, name="optsuccess"),#常用模块，提示更新成功
    #path('ppc_list/', views.Task_listview.as_view(), name="ppc_list"),
    #以下9个函数调用时每个会议纪要管理都会用到的，具备复用性
    path('ppc_list/', views.ppcmetlist, name="ppc_list"),                   #查看纪要清单
    path('ppc_add/', views.Metsmy_ppc_addview.as_view(), name="ppc_add"),   #增加纪要项目
    path('ppc_del/',views.ppc_metsmydel,name="ppc_del"),                    #删除纪要项目，注意，已上传的文件不会删除
    path('ppc_listquery/',views.ppc_metquery, name="ppc_listquery"),        #筛选纪要项目
    path('ppc_getmetcode/',views.ppcgetmetcode, name="ppc_getmetcode"),     #根据会议日期自动生成会议纪要编号
    path('ppc_checkfile/',views.ppc_checkfile, name="ppc_checkfile"),       #检查当前纪要项目是否已经上传了纪要文件
    path('ppc_seeread/',views.ppc_seeread, name="ppc_seeread"),             #查看会议纪要已读人员
    path('ppc_setread/',views.ppc_setread, name="ppc_setread"),             #设置当前用户已读此文件
    re_path(r'^ppc_edit/(?P<pk>\w+)/$', views.Metsmy_ppc_editview.as_view(), name="ppc_edit"),  #编辑纪要项目
]

