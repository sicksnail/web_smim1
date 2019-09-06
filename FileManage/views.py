from django.shortcuts import render,redirect,reverse,HttpResponse,get_object_or_404
from django.http import FileResponse
from django.contrib.auth.decorators import login_required,permission_required #基于函数的验证
from django.contrib.auth.mixins import PermissionRequiredMixin #基于视图的验证
#from django.views.generic.edit import FormMixin #通用视图直接用form必须引用
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Permission,User
from django.contrib import messages #进入消息处理
from django.utils import timezone #引入时间处理
from django.views import generic #引入通用视图
from django.conf import settings #引用配置参数
import os
import xlwt
from .forms import *    #引用form便于在视图使用modelform
from .models import *   #引用已定义的models


# Create your views here.

'''==================================================================================
函数Reffilelist，向前端反馈待办任务列表信息
==================================================================================='''
@login_required
def Reffilelist(request):
    if request.method == 'GET':
        rmodel = request.GET.get('rmodel', '')
        rid = request.GET.get('rid', '')
        mytitle=request.GET.get('objtitle', '')
        myfiles=RefFiles.objects.filter(refmodel=rmodel,refid=rid).order_by('refid')
        return render(request, 'reffile-list.html',{'myfiles':myfiles,'mytitle':mytitle,'mymodel':rmodel,'myid':rid})

@login_required
def AReffilelist(request):
    if request.method == 'GET':
        myfiles=RefFiles.objects.all()
        return render(request, 'reffile-list.html',{'myfiles':myfiles})

'''==================================================================================
函数downloadrff，向前端提供关联文件的下载服务
==================================================================================='''
def downloadrff(request):
    if request.method == 'GET':
        filename = request.GET.get("filename", None)
        #filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        filepath = settings.MEDIA_ROOT+os.sep+filename
        file = open(filepath, 'rb')
        response = FileResponse(file)
        #response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachement;filename='+os.path.basename(filepath)
        return response

'''==================================================================================
函数deleterff，向前端提供关联文件的删除功能
20190718 by sicksnail
==================================================================================='''
@login_required
def deleterff(request):
    if request.method == 'POST':
        file_id = request.POST.get("id", "")
        assert int(file_id), "网页异常，没有传递有效的文件id"
        #验证文件存在
        my_file=RefFiles.objects.filter(id=file_id)
        if my_file.exists():
            my_file=my_file[0] #从一堆中取第一个，实际上不可能有多个，只是习惯写法
            my_fliename=my_file.filename
            my_fliename=settings.MEDIA_ROOT+os.sep+str(my_fliename) #确定了实际存储路径
            if os.path.exists(my_fliename):
                os.remove(my_fliename)
                result = "文件删除成功。"
            else:
                result="文件不存在，记录已删除"
            my_file.delete()
        else:
            result="文件记录不存在，删除失败，请联系管理员"

        return HttpResponse(result)

'''==================================================================================
函数uploadrff，向前端提供关联文件的上传服务.实际未使用
==================================================================================='''
def uploadrff(request):
    if request.method == 'GET':
        return render(request, 'reffile-addedit_form.html')
    else:
        #myfname=request.POST.get('filename', '')
        obj = request.FILES.get("myfile",None)
        f = open(os.path.join('upload', obj.filename), 'wb')
        for line in obj.chunks():
            f.write(line)
        f.close()
        return HttpResponse('上传成功')


'''==================================================================================
类视图Reffile_addview，应用类视图快速实现相关文件添加处理
此处涉及在form_valid函数重写过程中处理特殊字段值
==================================================================================='''
class Reffile_addview(PermissionRequiredMixin,generic.CreateView):
    model = RefFiles
    template_name = 'reffile-addedit_form.html'
    #fields = '__all__' #在createview中必须设置这个函数
    form_class = ReffileForm
    context_object_name = 'myreffile'
    success_url = '../../success/'  #必须给post执行成功一个反馈,这个基础是当前URL

    # 通过重写get_context_data(self, **kwargs)过程实现实现初始化过程中的
    def get_context_data(self, **kwargs):
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['refid']=self.request.GET.get('id','0')
        kwargs['refmodel'] = self.request.GET.get('model', 'nomodel')
        return super().get_context_data( **kwargs)


    # 通过重写form_valid(self, form)过程实现从表添加时关系主表的更新，此处处理editby
    # 对于此处是需要填写编辑人和文件大小信息
    def form_valid(self, form):
        if self.request.method == 'POST':
            form.instance.editby_id = int(self.request.user.id)
            form.instance.filesize=(self.request.FILES.get('filename').size)/1000
            #20190718加入对于filename的修改，争取将文件放入到特定文件夹下,但是这种方法不对。度娘说要在model里定义动态函数
            #form.instance.filename=self.request.POST.get('refmodel', 'nomodel')+'/'+self.request.POST.get('refid','0')+'/'+self.request.FILES.get('filename').name
    #        form.instance.sender=self.request.user.first_name+self.request.user.last_name
        return super().form_valid(form)
    # 以下为权限控制的代码，基于AccessMixin类
    # 目前只是实现了没有权限的显示403页面，还需继续优化
    permission_required = 'FileManage.add_reffiles'
    raise_exception = True
    def get_permission_denied_message(self):
        self.permission_denied_message = '您没有添加文件关联的权限！'
        return self.permission_denied_message



