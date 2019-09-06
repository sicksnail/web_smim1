"""web_smim URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include,re_path
from newsmim import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.loginUser,name="loginuser"),
    path('logout/', views.logoutUser,name="logoutuser"),
    path('web_smim/', views.web_smim,name="web_smim"),
    path('welcome/', views.welcome,name="welcome"), #20190828增加
    path('success/', views.editsuccess, name="success"),
    path('userlist/', views.userlist,name="userlist"),
    path('userinfoedit/', views.Userinfo_edit,name="userinfoedit"), #20190711增加个人信息编辑功能
    path('password_chg/', views.password_chg,name="password_chg"), #20190711增加密码修改功能
    path('ctglist/', views.categorylist,name="ctglist"),
    path('ctgadd/', views.Category_addview.as_view(),name="ctgadd"),
    re_path(r'^ctgedit/(?P<pk>\w+)/$', views.Category_editview.as_view(), name="ctgedit"),
    path('ctgdel/', views.categoryDelete,name="ctgdel"),
    path('articlelist/', views.articlelist,name="articlelist"),
    path('articleadd/', views.articleAdd,name="articleadd"),
    path('articleedit/', views.articleEdit,name="articleedit"),
    path('articledel/', views.articleDelete,name="articledel"),
    #自此以下为应用项目
    path('filemng/', include('FileManage.urls')), #文件管理，其中reffile相关未公共需要
    path('taskmng/', include('Taskmanage.urls')),
    path('fltdata/', include('fltdatas.urls')),
    path('metsmy/', include('METSMY.urls')),  #会议纪要模块，20190801
]
