from django.shortcuts import render,redirect,reverse,HttpResponse
from django.contrib.auth.decorators import login_required,permission_required #基于函数的验证
from django.contrib.auth.mixins import PermissionRequiredMixin #基于视图的验证
from django.views.generic.edit import FormMixin #通用视图直接用form必须引用
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Permission,User
from django.shortcuts import get_object_or_404
from django.contrib import messages #进入消息处理
from django.utils import timezone #引入时间处理
from django.views import generic #引入通用视图
from .forms import *    #引用form便于在视图使用modelform
from .models import *   #引用已定义的models
from django.db import transaction #在http响应中使用事务控制
import os
import xlwt,xlrd #导出excel文件必须使用
from datetime import datetime #使用时间信息必须使用
from io import StringIO,BytesIO #处理excel文件需要内存操作

# Create your views here.
#================================================================================
#taskXXX是用于处理待办任务的页面
#tasklist是调用主界面task-list显示全部内容,使用了基于函数的视图
#Tastk_listview也是调用tasklist，使用了基于类的视图
#task_feedback是调用页面task_feedback来实现任务详情的查看
#taskitem_addview 和Taskitem_editview是基于类的视图，调用页面taskitem-addedit_form来实现任务的增加和编辑功能
#taskfb_addview 和Taskfb_editview是基于类的视图，调用页面taskfb-addedit_form来实现任务的增加和编辑功能
#articleDel是处理删除请求的函数
#================================================================================
'''==================================================================================
函数tasklist，向前端反馈待办任务列表信息，20190902更新时启用此list方法替代listview方法
20190902为实现模板页面复用，向前台提供tasktype参数，如下
    tasktype： 0 ， 1 ,
    相关项目： PPC, MNG,
20190902增加“mng-值班改善项目”,tasktype=1；
==================================================================================='''
@login_required(login_url='/login/')
def tasklist(request):
    if request.method == 'GET':
        tasks=Taskitem.objects.all()
        #20190904加入myself处理，用于核实是否有超级编辑权限=============
        if request.user.has_perm('taskmanage.superedit_taskitem'):
            myself = 'all'
        else:
            myself = request.user.first_name + request.user.last_name

        return render(request, 'taskitem-list.html',{'Mytasks':tasks,'tasktype':0,'myself':myself})


#20190902添加的mng项目---------------------------------------------------------------------
@login_required(login_url='/login/')
def tasklist_mng(request):
    if request.method == 'GET':
        tasks=Taskitem_mng.objects.all()
        # 20190904加入myself处理，用于核实是否有超级编辑权限=============
        if request.user.has_perm('taskmanage.superedit_taskitem'):
            myself = 'all'
        else:
            myself = request.user.first_name + request.user.last_name

        return render(request, 'taskitem-list.html',{'Mytasks':tasks,'tasktype':1,'myself': myself})

'''==================================================================================
函数taskquery，向前端反馈待办任务筛选的结果
#20190905添加标记，将myid用于任务类型识别
==================================================================================='''
@login_required(login_url='/login/')
def taskquery(request):
    if request.method == 'POST':
       myid = int(request.POST.get('qid', '-1')) #20190905添加标记，将myid用于任务类型识别
       #根据qid数值不同查找不同任务，-1是参数错误，0是生产任务，1是值班领导任务20190905
       if -1==myid:
           return HttpResponse("服务器消息：参数错误，查询不成功！")  # 服务器消息：记录删除成功！
       else :
           mytype=int(request.POST.get('qtype', ''))
           mydmin=request.POST.get('qdmin', '')
           mydmax = request.POST.get('qdmax', '')
           mydesc = request.POST.get('qdesc', '')
           #20190905添加-根据myid的值从不同类型任务取数据
           if 0 == myid:
               tasks = Taskitem.objects.all()
           elif 1 == myid:
               tasks = Taskitem_mng.objects.all()
           else:
               tasks = Taskitem.objects.all()

           #根据type参数筛选
           if -5>mytype:#不筛选<-5
               tasks1=tasks
           elif -3==mytype:#未启动=-3
               tasks1=tasks.filter(task_status__lt=0)
           elif 3==mytype:#完成或取消即结束=3
               tasks1=tasks.filter(task_status__gt=0)
           else:
                tasks1 = tasks.filter(task_status=mytype)

           #根据到期下限筛选：
           if len(mydmin)<6:
               tasks2= tasks1
           else:
               tasks2=tasks1.filter(due_date__gte=mydmin)

            #根据到期上限筛选：
           if len(mydmax)<6:
               tasks3= tasks2
           else:
               tasks3=tasks2.filter(due_date__lte=mydmax)

            #根据描述筛选
           if len(mydesc) < 1:
               tasks4 = tasks3
           else:
               tasks4 = tasks3.filter(taskdesc__icontains=mydesc)

            # 20190904加入myself处理，用于核实是否有超级编辑权限=============
           if request.user.has_perm('taskmanage.superedit_taskitem'):
                myself = 'all'
           else:
                myself = request.user.first_name + request.user.last_name

           return render(request, 'taskitem-listform.html',
                         {'Mytasks':tasks4,'Myid':myid,'Mydmin':mydmin,'Mydmax':mydmax,'Mydesc':mydesc,
                          'Mytype':int(mytype),'myself':myself,'tasktype':myid})

'''==================================================================================
函数taskquerym，向前端反馈当前用户参与的待办任务列表信息
20190905添加标记，将myid用于任务类型的识别
==================================================================================='''
@login_required(login_url='/login/')
def taskquerym(request):
    if request.method == 'POST':
       myid = int(request.POST.get('qid', '-1')) #20190905添加标记，将myid用于任务类型识别
       myuser=User.objects.get(id=request.user.id)
       #根据qid数值不同进行查找，1是条件筛选，0是全选，-1是参数错误
       if -1==myid:
           return HttpResponse("服务器消息：参数错误，查询不成功！")  # 服务器消息：记录删除成功！
       else :
           mytype=int(request.POST.get('qtype', ''))
           mydmin=request.POST.get('qdmin', '')
           mydmax = request.POST.get('qdmax', '')
           mydesc = request.POST.get('qdesc', '')
           if 0==myid:
               tasks = myuser.person_onti.all()
           elif 1==myid:
               tasks = myuser.person_onmng.all()
           else:
               tasks = Taskitem.objects.all()

           #根据type参数筛选
           if -5>mytype:#不筛选<-5
               tasks1=tasks
           elif -3==mytype:#未启动=-3
               tasks1=tasks.filter(task_status__lt=0)
           elif 3==mytype:#完成或取消即结束=3
               tasks1=tasks.filter(task_status__gt=0)
           else:
                tasks1 = tasks.filter(task_status=mytype)

           #根据到期下限筛选：
           if len(mydmin)<6:
               tasks2= tasks1
           else:
               tasks2=tasks1.filter(due_date__gte=mydmin)

            #根据到期上限筛选：
           if len(mydmax)<6:
               tasks3= tasks2
           else:
               tasks3=tasks2.filter(due_date__lte=mydmax)

            #根据描述筛选
           if len(mydesc) < 1:
               tasks4 = tasks3
           else:
               tasks4 = tasks3.filter(taskdesc__icontains=mydesc)

           myname=myuser.first_name+myuser.last_name
           # 20190904加入myself处理，用于核实是否有超级编辑权限=============
           if request.user.has_perm('taskmanage.superedit_taskitem'):
                myself = 'all'
           else:
                myself = request.user.first_name + request.user.last_name

           return render(request, 'taskitem-listform.html',{'Mytasks':tasks4,'Myid':myid,'Mydmin':mydmin,
                            'Mydmax':mydmax,'Mydesc':mydesc,'Mytype':int(mytype),'Myname':myname,
                            'myself':myself,'tasktype':myid})




'''==================================================================================
函数taskDelete，处理前端提交的删除任务请求，反馈不同值代表不同结果：
0=未通过权限检查；1=成功完成了反馈
20090904添加tasktype参数，实现本函数对多个类型任务的处理能力
==================================================================================='''
#@permission_required('taskmanage.delete_taskitem',raise_exception=True)#
def taskDelete(request):
    if request.method == 'POST':
       myid = request.POST.get('aid', '')
       mytype = request.POST.get('tty', '')
       if 0 == int(mytype):
           if not request.user.has_perm('Taskmanage.delete_taskitem'):
               return HttpResponse("0")  # 服务器消息：您没有删除任务的权限！
           Taskitem.objects.get(id=myid).delete()
           return HttpResponse("1")  # 服务器消息：记录删除成功！
       elif 1 == int(mytype):
           if not request.user.has_perm('Taskmanage.delete_taskitem_mng'):
               return HttpResponse("0")  # 服务器消息：您没有删除任务的权限！
           Taskitem_mng.objects.get(id=myid).delete()
           return HttpResponse("1")  # 服务器消息：记录删除成功！
       else:
           return HttpResponse("2")#服务器消息：任务类型不支持！

'''==================================================================================
类视图Task_listview，向前端反馈待办任务列表信息,可替代函数tasklist
20190902更新时放弃了适用此办法，因为需要增加一个tasktype参数
==================================================================================='''
class Task_listview(generic.ListView):
    model = Taskitem
    template_name = 'taskitem-list.html'
    context_object_name = 'Mytasks'

'''==================================================================================
函数task_feedback，向前台反馈当前任务以及所有的相关反馈
此处涉及一对多关系的主从表显示
20190902增加了tasktype识别的不同任务对象处理,增加了login_required
20190905将tasktype推送给前端，让进展和反馈页面可以根据此参数进行相关处理
==================================================================================='''
@login_required(login_url='/login/')
def task_feedback(request):
    if request.method == 'GET':
        myid = int(request.GET.get('id', 0))
        mytasktype = int(request.GET.get('type'))
        #根据任务类型和id获取相关任务和反馈数据---------------------------
        if 0 == mytasktype:
            mytask=Taskitem.objects.get(id=myid)
            myfeedbacks=mytask.taskfeedbacks_set.all().order_by('-update_time')
            if request.user.has_perm('Taskmanage.can_superedit_taskitem'):
                myname = 'super'
            else:
                myname = request.user.first_name + request.user.last_name

            # 暂时未使用models.Taskfeedbacks.objects.filter(tskid__taskfeedbacks__id=myid)这种关联查询法
        elif 1 == mytasktype:
            mytask = Taskitem_mng.objects.get(id=myid)
            myfeedbacks = mytask.taskfeedbacks_mng_set.all().order_by('-update_time')
            if request.user.has_perm('Taskmanage.can_superedit_taskitem_mng'):
                myname = 'super'
            else:
                myname = request.user.first_name + request.user.last_name
        else:
            return HttpResponse('对不起，当前任务类型无效！type='+str(mytasktype))
        #查询当前任务的参与人并反馈给前端--------------------------------------------
        mytkrf=''#实际反馈给前端的是参与人的姓名字符串，注意人员姓名不能修改
        for rf in mytask.refperson.all():
            mytkrf=mytkrf+rf.first_name+rf.last_name+','

        return render(request, 'task-feedback.html',{'mytask':mytask , 'myfeedbacks':myfeedbacks,
                        'mytkrf':mytkrf,'mytasktype':mytasktype,'myname':myname})

'''==================================================================================
类视图Taskitem_addview，应用类视图快速实现任务添加处理
此处涉及在form_valid函数重写过程中处理特殊字段值
20190902添加了分项_mng
==================================================================================='''
#Taskitem_addview是针对生产待办任务taskitem的基础项目，新功能务必先在此实现
class Taskitem_addview(PermissionRequiredMixin,generic.CreateView):
    model = Taskitem
    template_name = 'taskitem-addedit_form.html'
    #fields = '__all__' #在createview中必须设置这个函数
    form_class = TaskitemForm
    context_object_name = 'Mytaskitem'
    success_url = '../success/'  #必须给post执行成功一个反馈,这个基础是当前URL
    # 通过重写form_valid(self, form)过程实现从表添加时关系主表的更新，此处处理editby
    #对于新建任务来说，还需要处理发起人和任务状态信息
    def form_valid(self, form):
        if self.request.method == 'POST':
            form.instance.editby_id = int(self.request.user.id)
            form.instance.task_status=0
            form.instance.sender=self.request.user.first_name+self.request.user.last_name
        return super().form_valid(form)

    def form_invalid(self, form):  # 定义表对象没有添加失败后跳转到的页面。
        return HttpResponse("错误信息提示：表格提交无效，未完成添加操作. this is just an HttpResponse object")

    # 以下为权限控制的代码，基于AccessMixin类
    # 目前只是实现了没有权限的显示403页面，还需继续优化
    permission_required = 'Taskmanage.add_taskitem'
    raise_exception = True
    def get_permission_denied_message(self):
        self.permission_denied_message = '您没有添加任务反馈的权限！'
        return self.permission_denied_message

# Taskitem_addview_mng是针对领导值班提升项目建立的分项,20190902添加============
class Taskitem_addview_mng(PermissionRequiredMixin,generic.CreateView):
    model = Taskitem_mng #此处是分项修改参数
    template_name = 'taskitem-addedit_form.html'
    #fields = '__all__' #在createview中必须设置这个函数
    form_class = TaskitemForm_mng
    context_object_name = 'Mytaskitem'
    success_url = '../success/'  #必须给post执行成功一个反馈,这个基础是当前URL
    # 通过重写form_valid(self, form)过程实现从表添加时关系主表的更新，此处处理editby
    #对于新建任务来说，还需要处理发起人和任务状态信息
    def form_valid(self, form):
        if self.request.method == 'POST':
            form.instance.editby_id = int(self.request.user.id)
            form.instance.task_status=0
            form.instance.sender=self.request.user.first_name+self.request.user.last_name
        return super().form_valid(form)

    def form_invalid(self, form):  # 定义表对象没有添加失败后跳转到的页面。
        return HttpResponse("错误：表格提交无效，未完成添加操作. this is just an HttpResponse object")

    # 以下为权限控制的代码，基于AccessMixin类
    # 目前只是实现了没有权限的显示403页面，还需继续优化
    permission_required = 'Taskmanage.add_taskitem_mng'#&&分项编写更新点
    raise_exception = True
    def get_permission_denied_message(self):
        self.permission_denied_message = '您没有添加任务反馈的权限！'
        return self.permission_denied_message

'''==================================================================================
类视图Taskitem_editview，应用类视图快速实现任务添加处理
此处涉及在form_valid函数重写过程中处理特殊字段值
20190904添加了分项_mng
==================================================================================='''
class Taskitem_editview(PermissionRequiredMixin,generic.UpdateView):
    model = Taskitem
    template_name = 'taskitem-addedit_form.html'
    #fields = '__all__' #在createview中必须设置这个函数
    form_class = TaskitemForm
    context_object_name = 'Mytaskitem'
    success_url = '../../success/'
    #必须给post执行成功一个反馈,这个基础是当前URL.因为updete用的url更深，因此需要多返回一层。
    #当然，这个success_url如果在model定义中有一些安排，这里就不用再搞了，回头研究
    # 通过重写form_valid(self, form)过程实现从表添加时关系主表的更新，此处处理editby
    def form_valid(self, form):
        if self.request.method == 'POST':
            form.instance.editby_id = int(self.request.user.id)
        return super().form_valid(form)

    # 以下为权限控制的代码，基于AccessMixin类
    # 目前只是实现了没有权限的显示403页面，还需继续优化
    permission_required = 'Taskmanage.change_taskitem'
    raise_exception = True
    def get_permission_denied_message(self):
        self.permission_denied_message = '您没有编辑任务的权限！'
        return self.permission_denied_message

#分项MNG，20190904添加=========================================================
class Taskitem_editview_mng(PermissionRequiredMixin,generic.UpdateView):
    model = Taskitem_mng
    template_name = 'taskitem-addedit_form.html'
    #fields = '__all__' #在createview中必须设置这个函数
    form_class = TaskitemForm_mng
    context_object_name = 'Mytaskitem'
    success_url = '../../success/'
    #必须给post执行成功一个反馈,这个基础是当前URL.因为updete用的url更深，因此需要多返回一层。
    #当然，这个success_url如果在model定义中有一些安排，这里就不用再搞了，回头研究
    # 通过重写form_valid(self, form)过程实现从表添加时关系主表的更新，此处处理editby
    def form_valid(self, form):
        if self.request.method == 'POST':
            form.instance.editby_id = int(self.request.user.id)
        return super().form_valid(form)

    # 以下为权限控制的代码，基于AccessMixin类
    # 目前只是实现了没有权限的显示403页面，还需继续优化
    permission_required = 'Taskmanage.change_taskitem_mng'
    raise_exception = True
    def get_permission_denied_message(self):
        self.permission_denied_message = '您没有编辑任务的权限！'
        return self.permission_denied_message



'''==================================================================================
函数taskref_edit实现任务相关人的，向前台反馈当前任务以及所有的相关反馈
函数taskref_chg则实现相关人员的变更，edit与chg协同处理，实现了对参与人员的编辑管理
完成功能调试 20190722 by sicksnail
20190904 by sicksnail 加入了tasktype实现多多种任务的支持
==================================================================================='''
def taskref_edit(request):
    if request.method == 'GET':
        myid=request.GET.get('id',0)
        mytype=request.GET.get('type','')
        if mytype=='0':
            mytask=Taskitem.objects.get(id=int(myid))
            allrefps = User.objects.filter(groups__name='staff_ppc').order_by('id')
        elif mytype=='1':
            mytask = Taskitem_mng.objects.get(id=int(myid))
            allrefps = User.objects.filter(groups__name='staff_mng').order_by('id')
        else:
            mytask=Taskitem.objects.get(id=0)
            allrefps = User.objects.get(id=0)
        myrefps=mytask.refperson.all().order_by('id')
        #20190826修订，通过group设定来实现备选参与人信息，替代User.objects.all().order_by('id')
        #allrefps和myrefps按统一顺序排列有助于简化前台算法
        #models.Taskfeedbacks.objects.filter(tskid__taskfeedbacks__id=myid)
        #暂时未实现这种set的查询  mytask.Taskfeedbacks_set.all()问题在于从表小写
        mytkrf=''
        for rf in mytask.refperson.all():
            mytkrf=mytkrf+rf.first_name+rf.last_name+','
        return render(request, 'taskitem_refeditn.html',{'mytask':mytask , 'myrefps':myrefps,
                                    'mytype':mytype,'allrefps':allrefps})

def taskref_chg(request):
    if request.method == 'POST':
        myid=request.POST.get('tid',0)
        mytype=request.POST.get('tasktype','')
        if mytype == '0':
            mytask = Taskitem.objects.get(id=myid)
        elif mytype =='1':
            mytask = Taskitem_mng.objects.get(id=myid)
        else:
            mytask = Taskitem.objects.get(id=0)
        refparr=request.POST.get('refparr','')
        refparr=refparr.split(',')#将前台传输过来的字符串改为列表，才能使用set功能
        #refpcnt = request.POST.get('refpcnt', 0)
        mytask.refperson.set(refparr)
        return HttpResponse("参与人员信息更新完毕"+','.join(refparr))

'''==================================================================================
函数taskmnt_edit与taskref_chg配合实现监控人员的变更，分别处理同一个页面的GET和POST
20190905 完成功能测试 by sickssnail
==================================================================================='''
def taskmnt_edit(request):
    if request.method == 'GET':
        myid=request.GET.get('id',0)         #myid是任务的id
        mytype=request.GET.get('type','')   #mytype是任务类型
        if mytype=='0':
            mytask=Taskitem.objects.get(id=int(myid))
            allrefps = User.objects.filter(groups__name='staff_ppc').order_by('id')
        elif mytype=='1':
            mytask = Taskitem_mng.objects.get(id=int(myid))
            allrefps = User.objects.filter(groups__name='staff_mng').order_by('id')
        else:
            mytask=Taskitem.objects.get(id=0)
            allrefps = User.objects.get(id=0)
        mymntp=mytask.sender
        return render(request, 'taskitem_mntedit.html',{'mytask':mytask , 'mymntp':mymntp,
                                    'mytype':mytype,'allrefps':allrefps})


def taskmnt_chg(request):
    if request.method == 'POST':
        myid=request.POST.get('tid',0)
        mytype=request.POST.get('tasktype','')
        mysender = request.POST.get('newsender', '')
        if mytype == '0':
            mytask = Taskitem.objects.get(id=myid)
        elif mytype =='1':
            mytask = Taskitem_mng.objects.get(id=myid)
        else:
            mytask = Taskitem.objects.get(id=0)

        mytask.sender = mysender
        mytask.save()
        return HttpResponse("监控人员信息更新为"+mysender+'!')


'''==================================================================================
类视图Taskref_editview，应用类视图快速实现任务添加参与人处理
此处涉及在form_valid函数重写过程中处理特殊字段值
20190904目前未使用本方法----------------------------------
==================================================================================='''
class Taskref_editview(PermissionRequiredMixin,generic.UpdateView):
    model = Taskitem
    template_name = 'taskitem-refedit.html'
    #fields = '__all__' #在createview中必须设置这个函数
    form_class = TaskrefForm
    context_object_name = 'Mytaskitem'
    success_url = '../../success/'
    #必须给post执行成功一个反馈,这个基础是当前URL.因为updete用的url更深，因此需要多返回一层。
    #当然，这个success_url如果在model定义中有一些安排，这里就不用再搞了，回头研究
    # 通过重写form_valid(self, form)过程实现从表添加时关系主表的更新，此处处理editby
    def form_valid(self, form):
        if self.request.method == 'POST':
            form.instance.editby_id = int(self.request.user.id)
        return super().form_valid(form)

    # 以下为权限控制的代码，基于AccessMixin类
    # 目前只是实现了没有权限的显示403页面，还需继续优化
    permission_required = 'Taskmanage.change_taskitem'
    raise_exception = True
    def get_permission_denied_message(self):
        self.permission_denied_message = '您没有编辑任务参与人的权限！'
        return self.permission_denied_message

'''==================================================================================
函数tasksuccess，简单的提示信息，协助类视图的处理
==================================================================================='''
def tasksuccess(request):
    return render(request, 'addeditsuccess.html')

'''==================================================================================
类视图Taskfb_addview，应用类视图快速实现任务反馈的添加处理
此处涉及在form_valid函数重写过程中处理特殊字段值，以及权限控制403
20190905创建分享-mng
==================================================================================='''
#基于类的视图不能用上述方法，得用minin
class Taskfb_addview(PermissionRequiredMixin,generic.CreateView):
    model = Taskfeedbacks
    template_name = 'taskfb-addedit_form.html'
    fields = ['id', 'feedback','status2be']
    labels = {"feedback": "反馈内容", }
    widgets = {
        'feedback': forms.Textarea,
        'note': forms.TextInput,
    }
    context_object_name = 'Myfeedback'
    success_url = '../success/'  #必须给post执行成功一个反馈,这个基础是当前URL
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            mytask = self.request.GET.get('id', 0)
            mytype = self.request.GET.get('type', -1)
            context['ntskid'] = mytask  #通过get方法传递任务编号
            context['ntskty'] = mytype  # 通过get方法传递任务类型
        context['now']=timezone.now() #只有这行代码有用
        return context

    # 通过重写form_valid(self, form)过程实现从表添加时关系主表的更新
    def form_valid(self, form):
        if self.request.method == 'POST':
            form.instance.tskid_id = int(self.request.POST['task_id'])
            form.instance.editby_id = int(self.request.user.id)
        return super().form_valid(form)

    # 以下为权限控制的代码，基于AccessMixin类
    # 目前只是实现了没有权限的显示403页面，还需继续优化
    permission_required = 'Taskmanage.add_taskfeedbacks'
    raise_exception = True
    def get_permission_denied_message(self):
        self.permission_denied_message = '您没有添加生产任务反馈的权限！'
        return self.permission_denied_message


#以下为20190905添加的-mng分项函数
class Taskfb_addview_mng(PermissionRequiredMixin,generic.CreateView):
    model = Taskfeedbacks_mng
    template_name = 'taskfb-addedit_form.html'
    fields = ['id', 'feedback','status2be']
    labels = {"feedback": "反馈内容", }
    widgets = {
        'feedback': forms.Textarea,
        'note': forms.TextInput,
    }
    context_object_name = 'Myfeedback'
    success_url = '../success/'  #必须给post执行成功一个反馈,这个基础是当前URL
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'GET':
            mytask = self.request.GET.get('id', 0)
            mytype = self.request.GET.get('type', -1)
            context['ntskid'] = mytask  #通过get方法传递任务编号
            context['ntskty'] = mytype  # 通过get方法传递任务类型
        context['now']=timezone.now()
        return context

    # 通过重写form_valid(self, form)过程实现从表添加时关系主表的更新
    def form_valid(self, form):
        if self.request.method == 'POST':
            form.instance.tskid_id = int(self.request.POST['task_id'])
            form.instance.editby_id = int(self.request.user.id)
        return super().form_valid(form)

    # 以下为权限控制的代码，基于AccessMixin类
    # 目前只是实现了没有权限的显示403页面，还需继续优化
    permission_required = 'Taskmanage.add_taskfeedbacks_mng'
    raise_exception = True
    def get_permission_denied_message(self):
        self.permission_denied_message = '您没有添加任务反馈的权限！'
        return self.permission_denied_message


#通过get_context_data(self, **kwargs):get_queryset(self)和get_object(self, queryset=None)
# 可以传递和修改参数-------------------------------------------------
# def get_context_data(self, **kwargs):
#    context = super().get_context_data(**kwargs)
#    context['now']=timezone.now() #只有这行代码有用
#    return context
#------------------------------------------------------------------
# def get_queryset(self):
#   qs = super().get_queryset() # 调用父类方法
#   return qs.filter(author = self.request.user).order_by('-pub_date')
#--------------------------------------------------------------------
#def get_object(self, queryset=None):
#   obj = super().get_object(queryset=queryset)
#   if obj.author != self.request.user:
#     raise Http404()
#   return obj
#===================================================================
'''==================================================================================
类视图Taskfb_editview，应用类视图快速实现任务反馈的编辑处理
此处涉及在form_valid函数重写过程中处理特殊字段值，以及权限控制403
20190905添加分项-mng
==================================================================================='''
class Taskfb_editview(generic.UpdateView):
    model = Taskfeedbacks
    #permission_request='catalog.make' 百度的权限控制，暂未用
    template_name = 'taskfb-addedit_form.html'
    #template_name_suffix='_addedit_'可实现‘taskmanage/taskitem_addedit_form.html’在使用框架模板时不好用
    fields = ['id', 'feedback', 'status2be'] #在createview中必须设置这个函数
    widgets = {
        'feedback': forms.TextInput,
    }
    context_object_name = 'Myfeedback'
    success_url = '../../success/'
    #必须给post执行成功一个反馈,这个基础是当前URL.因为updete用的url更深，因此需要多返回一层。
    #当然，这个success_url如果在model定义中有一些安排，这里就不用再搞了，回头研究

#20190905添加的--mng分项
class Taskfb_editview_mng(generic.UpdateView):
    model = Taskfeedbacks_mng
    template_name = 'taskfb-addedit_form.html'
    fields = ['id', 'feedback', 'status2be'] #在createview中必须设置这个函数
    widgets = {
        'feedback': forms.Textarea,
    }
    context_object_name = 'Myfeedback'
    success_url = '../../success/'

'''==================================================================================
函数checkperson(tid，chr)用于检查当前用户是否参与某项任务 返回True或者False
20190905添加tasktype参数，实现对多种任务的支持
==================================================================================='''
def Checkperson(request):#,tid,chr
    tid=request.POST.get('tid')
    tty=int(request.POST.get('tty'))
    myid=request.user.id
    if tty == 0:
        intasks= Taskitem.objects.get(id=tid).refperson #.get(username=myid)
    elif tty == 1:
        intasks= Taskitem_mng.objects.get(id=tid).refperson
    else:
        return HttpResponse(-1)#不能匹配正确的任务类型，直接反馈无权限
    myflag=0 #myflag用于记录对比结果，发现相同的则加1，否则加0，如果存在则最终为1
    for guy in intasks.all():
        if myid==guy.id:
            myflag=myflag+1
        else: myflag=myflag+0
    return HttpResponse(myflag)


'''==================================================================================
函数task_update(tid，chr)用于更新详细进展
本函数未进行权限确认，因为前台通过隐藏按钮控制了操作人员
20190905进行了更新，加入了type分项，取消了参与人检查
==================================================================================='''
def Task_update(request):#,tid,chr
    tid=request.POST.get('tid')
    tty=int(request.POST.get('tty','-1'))#注意python类型敏感
    newnote=request.POST.get('newnote')
    if 0 == tty:
        obj = Taskitem.objects.get(id=tid)
        obj.abstract = newnote
        obj.editby_id = request.user.id
        obj.save()
        return HttpResponse(1)
    elif 1 == tty:
        obj = Taskitem_mng.objects.get(id=tid)
        obj.abstract = newnote
        obj.editby_id = request.user.id
        obj.save()
        return HttpResponse(1)
    else:
        return HttpResponse("类型参数错误，无法在本页面编辑进展！！")


'''==================================================================================
函数tasklistoutexcel用于导出符合条件的任务进展数据,处理post请休
20190906 by sicksnail
==================================================================================='''
@login_required(login_url='/login/')
def tasklistoutexcel(request):
    #第一步是获取对象数据，20190906直接粘贴了taskquery代码
    if request.method == 'POST':
       myid = int(request.POST.get('qid', '-1')) #20190905添加标记，将myid用于任务类型识别
       #根据qid数值不同查找不同任务，-1是参数错误，0是生产任务，1是值班领导任务20190905
       if -1==myid:
           return HttpResponse("服务器消息：参数错误，查询不成功！")  # 服务器消息：记录删除成功！
       else :
           mytype=int(request.POST.get('qtype', ''))
           mydmin=request.POST.get('qdmin', '')
           mydmax = request.POST.get('qdmax', '')
           mydesc = request.POST.get('qdesc', '')
           #20190905添加-根据myid的值从不同类型任务取数据
           if 0 == myid:
               tasks = Taskitem.objects.all()
           elif 1 == myid:
               tasks = Taskitem_mng.objects.all()
           else:
               tasks = Taskitem.objects.all()

           #根据type参数筛选
           if -5>mytype:#不筛选<-5
               tasks1=tasks
           elif -3==mytype:#未启动=-3
               tasks1=tasks.filter(task_status__lt=0)
           elif 3==mytype:#完成或取消即结束=3
               tasks1=tasks.filter(task_status__gt=0)
           else:
                tasks1 = tasks.filter(task_status=mytype)

           #根据到期下限筛选：
           if len(mydmin)<6:
               tasks2= tasks1
           else:
               tasks2=tasks1.filter(due_date__gte=mydmin)

            #根据到期上限筛选：
           if len(mydmax)<6:
               tasks3= tasks2
           else:
               tasks3=tasks2.filter(due_date__lte=mydmax)

            #根据描述筛选
           if len(mydesc) < 1:
               tasks4 = tasks3
           else:
               tasks4 = tasks3.filter(taskdesc__icontains=mydesc)

    #第二步准备excel文件
    # 创建一个文件对象
    fname = 'tasklist_opt_' + datetime.now().strftime('%y%m%d%H%M%S') + '.xls'
    wb = xlwt.Workbook(encoding='utf8')
    # 创建一个sheet对象
    sheet = wb.add_sheet('sheet01')
    # 设置excel文件的各种样式,这个不是必须的可以根据自己的需求进行更改
    style_heading = xlwt.easyxf("""
                font:
                    name Arial,
                    colour_index white,
                    bold on,
                    height 0xA0;
                align:
                    wrap off,
                    vert center,
                    horiz center;
                pattern:
                    pattern solid,
                    fore-colour 0x21;
                borders:
                    left THIN,
                    right THIN,
                    top THIN,
                    bottom THIN;
                """)

    style_body = xlwt.easyxf("""
            font:
              name Calibri,
              bold off,
              height 0XA0;
            align:
              wrap on,
              vert center,
              horiz left;
            borders:
              left THIN,
              right THIN,
              top THIN,
              bottom THIN;
            """
                             )

    # 写入文件标题
    sheet.write(0, 0, '启动日期', style_heading)
    sheet.write(0, 1, '监控人', style_heading)
    sheet.write(0, 2, '当前状态', style_heading)
    sheet.write(0, 3, '问题描述', style_heading)
    sheet.write(0, 4, '当前进展', style_heading)
    sheet.write(0, 5, '各方反馈', style_heading)
    sheet.write(0, 6, '备注', style_heading)

    #第三歩，将数据写入excel中，for循环
    data_row = 1
    for mytask in tasks4:
        pri_time = mytask.start_date.strftime('%Y-%m-%d')
        sheet.write(data_row, 0, pri_time,style_body)#启动日期
        sheet.write(data_row, 1, mytask.sender,style_body)
        sheet.write(data_row, 2, mytask.task_status,style_body)
        sheet.write(data_row, 3, mytask.taskdesc,style_body)
        sheet.write(data_row, 4, mytask.abstract,style_body)
        if 0 == myid:
            myfbs = mytask.taskfeedbacks_set.all()
        elif 1 == myid:
            myfbs = mytask.taskfeedbacks_mng_set.all()
        else:
            myfbs = mytask.taskfeedbacks_set.all()
        myfbstr='本项目共计有'+str(myfbs.count)+'个反馈：'+'\n'
        for myfb in myfbs:
            myfbstr = myfbstr+myfb.feedback+'. by '+myfb.editby.first_name+ myfb.editby.last_name
            myfbstr = myfbstr  + ',on '+myfb.update_time.strftime('%Y-%m-%d')+';'+'\n'
        sheet.write(data_row, 5, myfbstr,style_body)
        sheet.write(data_row, 6, mytask.id,style_body)
        data_row=data_row+1

    # 第一方案：生成的文件直接存储到服务器指定目录下,即本APP下aclistfile文件，反馈给前台文件名
    # 前台收到反馈后，在页面生成一个文件的下载链接
    # 该方案的优点是容易将文件下载与文件生成分步骤进行，容易处理复杂查询，不足在于服务器安全受影响
    wb.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tasklistfile/' + fname))
    return HttpResponse(fname)
    # 第二方案是直接将生成的文件反馈给前台，由前台直接打开，避免了服务器存储负担但不易处理复杂查询
    # 设置HTTPResponse的类型
    #response = HttpResponse(content_type='application/vnd.ms-excel')
    #response['Content-Disposition'] = 'attachment;filename='+fname
    # 写出到IO
    #output = BytesIO()
    #wb.save(output)
    # 重新定位到开始
    #output.seek(0)
    #response.write(output.getvalue())
    # 最后一步是反馈导出的excel对象
    #return response


