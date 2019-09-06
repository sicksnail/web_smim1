from django.urls import path,re_path
from fltdatas import views

urlpatterns = [
    #本模块上级目录fltdata
    #path('list/', views.Task_listview.as_view(), name="task_list"),
    #path('task_feedback/', views.task_feedback, name="task_feedback"),
    #注意updateview的使用需要调用re_path进行带正则表达式的匹配
    #re_path(r'^edit/(?P<pk>\w+)/$', views.Taskitem_editview.as_view(), name="taskitem_edit"),
    #以下为针对飞机对象Airplan的显示和处理相关页面
    path('airplans/', views.airplanlist, name="aplist"),
    path('apadd/', views.Airplan_addview.as_view(), name="apadd"),
    path('apdel/', views.airplanDelete, name="apdel"),
    re_path(r'^apedit/(?P<pk>\w+)/$', views.Airplan_editview.as_view(), name="apedit"),
    path('excel_aclist/', views.excelaclistout, name='excel_aclist'),#aclist形成excel
    path('getaclist/',views.dlaclist,name='getaclist'),#下载aclist的excel文件
    path('excelin_aclist/', views.airplanexcelin, name='excelin_aclist'),#从excel文件内导入ac数据
    path('success/', views.editsuccess, name="success"),
    path('fltrcds/', views.Fltrcdlist, name="fltrcdlist"),
    path('getfltidentity/',views.getFltcode,name="getfltidentity"),
    path('fltrcdadd/', views.Fltrcd_addview.as_view(), name="fltrcdadd"),
    re_path(r'^fltrcdedit/(?P<pk>\w+)/$', views.Fltrcd_editview.as_view(), name="fltrcdedit"),
    #newtest是专门用于调用前台新设计功能测试的
    #path('newtest/',views.Checkperson, name="newtest"),
]

