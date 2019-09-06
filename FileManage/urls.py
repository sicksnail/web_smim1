from django.urls import path,re_path
from FileManage import views

urlpatterns = [
    #本模块上级目录filemng
    #path('list/', views.Task_listview.as_view(), name="task_list"),
    #path('task_feedback/', views.task_feedback, name="task_feedback"),
    #re_path(r'^edit/(?P<pk>\w+)/$', views.Taskitem_editview.as_view(), name="taskitem_edit"),
    path('rfflist/',views.Reffilelist, name="rfflist"),     #参考文件清单
    path('rfflst/',views.AReffilelist, name="rfflst"),      #参考文件全部清单
    path('rfadd/',views.Reffile_addview.as_view(), name="rfadd"), #添加关联文件
    path('dlreff/',views.downloadrff, name="dlreff"),       #get方法调用下载文件
    path('delrff/',views.deleterff, name="delrff"),       #删除文件和记录
    #re_path(r'^dlrff/(?P<pk>\w+)/$', views.downloadrff, name="dlrff"),  #下载关联文件
]