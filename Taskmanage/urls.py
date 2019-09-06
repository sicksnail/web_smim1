from django.urls import path,re_path
from Taskmanage import views

urlpatterns = [
    #本模块上级目录taskmng
    #path('list/', views.Task_listview.as_view(), name="task_list"),
    path('list/', views.tasklist, name="task_list"),#20190902恢复为函数实现
    path('list_mng/', views.tasklist_mng, name="task_listmng"),#20190902恢复为函数实现

    path('task_feedback/', views.task_feedback, name="task_feedback"),

    path('add/', views.Taskitem_addview.as_view(), name="taskitem_add"),
    path('add_mng/', views.Taskitem_addview_mng.as_view(), name="taskitem_add_mng"),#20190902增加-mng功能分项
    #当需要添加反馈时，首先进入refaddfb进行参与资格检查，通过后跳转调用fbadd或其后缀分项
    path('refaddfb/', views.Checkperson, name="refaddfb"),
    path('fbadd/', views.Taskfb_addview.as_view(), name="taskfb_add"),
    path('fbadd_mng/', views.Taskfb_addview_mng.as_view(), name="taskfb_add_mng"),

    path('del/',views.taskDelete,name="taskitem_del"),#前端ajax推送post请求，实现多种功能
    path('success/', views.tasksuccess, name="tasksuccess"),
    path('listquery/',views.taskquery, name="listquery"),
    path('listmine/',views.taskquerym, name="listmine"),
    path('listexcel/',views.tasklistoutexcel, name="listexcel"),#20190906添加excel筛选导出
    path('taskupdate/', views.Task_update, name="taskupdate"),#20190905加入分项参数type
    path('refedit/',views.taskref_edit,name="taskref_edit"),
    path('prefedit/', views.taskref_chg, name="ptaskref_edit"),
    path('mntedit/',views.taskmnt_edit,name="taskmnt_edit"),
    path('pmntedit/', views.taskmnt_chg, name="ptaskref_edit"),
    #注意updateview的使用需要调用re_path进行带正则表达式的匹配
    re_path(r'^edit/(?P<pk>\w+)/$', views.Taskitem_editview.as_view(), name="taskitem_edit"),
    re_path(r'^edit_mng/(?P<pk>\w+)/$', views.Taskitem_editview_mng.as_view(), name="taskitem_edit_mng"), #20190904添加
    re_path(r'^fbedit/(?P<pk>\w+)/$', views.Taskfb_editview.as_view(), name="taskfb_edit"),
    re_path(r'^fbedit_mng/(?P<pk>\w+)/$', views.Taskfb_editview_mng.as_view(), name="taskfb_edit_mng"),
    #re_path(r'^refedit/(?P<pk>\w+)/$', views.Taskref_editview.as_view(), name="taskref_edit"),#目前未使用
    #re_path(r'^nrefedit/(?P<pk>\w+)/$', views.taskref_edit, name="ntaskref_edit"),20190904换了调用办法


    #newtest是专门用于调用前台新设计功能测试的
    path('newtest/',views.Checkperson, name="newtest"),
]

