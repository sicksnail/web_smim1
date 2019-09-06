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
#from .forms import *    #引用form便于在视图使用modelform
from .models import *   #引用已定义的models

# Create your views here.
'''==================================================================================
函数optsuccess，简单的提示信息，协助类视图的处理
==================================================================================='''
def optsuccess(request):
    return render(request, 'addeditsuccess.html')
#================================================================================
#ppcmetXXX是用于处理PPC会议纪要相关功能的页面
#ppcmetlist是调用主界面metsmy-list显示全部内容,使用了基于函数的视图
#Tastk_listview也是调用tasklist，使用了基于类的视图
#task_feedback是调用页面task_feedback来实现任务详情的查看
#taskitem_addview 和Taskitem_editview是基于类的视图，调用页面taskitem-addedit_form来实现任务的增加和编辑功能
#taskfb_addview 和Taskfb_editview是基于类的视图，调用页面taskfb-addedit_form来实现任务的增加和编辑功能
#articleDel是处理删除请求的函数
#================================================================================
'''==================================================================================
函数ppcmetlist，向前端反馈全部会议信息
==================================================================================='''
@login_required
def ppcmetlist(request):
    if request.method == 'GET':
        meets=METSMY_ppc.objects.all() #其他会议时修改点1
        myhead='PPC会议纪要' #其他会议时修改点2
        mytit='ppc_' #其他会议时修改点3
        return render(request, 'metsmy-list.html',{'meets':meets,'Myhead':myhead,'mytit':mytit})
    #meets是查询到的会议，myhead是调用页面时的标题，mytit是调用增删改操作时的值实现一个temple用于多对象


'''==================================================================================
函数ppcgetmetcode，向前端反馈全部会议编号
==================================================================================='''
@login_required
def ppcgetmetcode(request):
    if request.method == 'POST':
        mycode=request.POST.get('yearcode','')
        meets=METSMY_ppc.objects.filter(meetcode__istartswith=('PPC'+mycode)).order_by('-meetcode')#.first()
        #获取同意年份现有最大编号
        if meets.count()<1:
            mycode='PPC'+mycode+'001'
        else:
            mymeet=meets.first()
            mycode='PPC'+str(int(mymeet.meetcode[3:])+1)
        return HttpResponse(mycode)
    #meets是查询到的会议，myhead是调用页面时的标题，mytit是调用增删改操作时的值实现一个temple用于多对象

'''==================================================================================
函数ppc_metquery，向前端反馈筛选会议纪要信息
==================================================================================='''
@login_required
def ppc_metquery(request):
    if request.method == 'POST':
       myid = request.POST.get('qid', '-1')
       #根据qid数值不同进行查找，1是条件筛选，0是全选，-1是参数错误
       if -1==myid:
           return HttpResponse("服务器消息：参数错误，查询不成功！")  # 服务器消息：记录删除成功！
       else :
           mytype=int(request.POST.get('qtype', ''))
           mydmin=request.POST.get('qdmin', '')
           mydmax = request.POST.get('qdmax', '')
           mydesc = request.POST.get('qdesc', '')
           meets = METSMY_ppc.objects.all()
           #return render(request, 'taskitem-listform.html', {'mytasks': tasks})
           #根据type参数筛选
           if -1>mytype:#不筛选<-1
               meets1=meets
           #elif 3==mytype:#完成或取消即结束=3
           #    meets1 = meets.filter(task_status__gt=0)
           else:
               meets1 = meets.filter(meettype=mytype)

           #根据到期下限筛选：
           if len(mydmin)<6:
               meets2= meets1
           else:
               meets2 = meets1.filter(meetdate__gte=mydmin)

            #根据到期上限筛选：
           if len(mydmax)<6:
               meets3= meets2
           else:
               meets3 = meets2.filter(meetdate__lte=mydmax)

            #根据描述筛选
           if len(mydesc) < 1:
               meets4 = meets3
           else:
               meets4 = meets3.filter(title__icontains=mydesc)

           return render(request, 'metsmy-listform.html',
                         {'meets':meets4,'mytit':'ppc_','Myid':myid,'Mydmin':mydmin,'Mydmax':mydmax,'Mydesc':mydesc,'Mytype':int(mytype)})


'''==================================================================================
类视图Metsmy_ppc_editview，应用类视图快速实现任务添加处理
此处涉及在form_valid函数重写过程中处理特殊字段值
==================================================================================='''
class Metsmy_ppc_editview(PermissionRequiredMixin,generic.UpdateView):
    model = METSMY_ppc
    template_name = 'metsmy-addedit_form.html'
    #fields = '__all__' #在createview中必须设置这个函数
    form_class = Metsmy_ppcForm
    context_object_name = 'Mymetsmys'
    success_url = '../../success/'
    #必须给post执行成功一个反馈,这个基础是当前URL.因为updete用的url更深，因此需要多返回一层。
    # 通过重写form_valid(self, form)过程实现从表添加时关系主表的更新，此处处理editby
    def form_valid(self, form):
        if self.request.method == 'POST':
            form.instance.editby_id = int(self.request.user.id)
        return super().form_valid(form)

    # 以下为权限控制的代码，基于AccessMixin类
    # 目前只是实现了没有权限的显示403页面，还需继续优化
    permission_required = 'METSMY.change_metsmy_ppc'
    raise_exception = True
    def get_permission_denied_message(self):
        self.permission_denied_message = '您没有编辑PPC会议纪要的权限！'
        return self.permission_denied_message

'''==================================================================================
类视图Metsmy_ppc_addview，应用类视图快速实现任务添加处理
此处涉及在form_valid函数重写过程中处理特殊字段值
==================================================================================='''
class Metsmy_ppc_addview(PermissionRequiredMixin,generic.CreateView):
    model = METSMY_ppc
    template_name = 'metsmy-addedit_form.html'
    #fields = '__all__' #在createview中必须设置这个函数
    form_class = Metsmy_ppcForm
    context_object_name = 'Mymetsmys'
    success_url = '../success/'  #必须给post执行成功一个反馈,这个基础是当前URL
    # 通过重写form_valid(self, form)过程实现从表添加时关系主表的更新，此处处理editby
    #对于新建任务来说，还需要处理发起人和任务状态信息
    def form_valid(self, form):
        if self.request.method == 'POST':
            form.instance.editby_id = int(self.request.user.id)
            #form.instance.sender=self.request.user.first_name+self.request.user.last_name
        return super().form_valid(form)

    # 以下为权限控制的代码，基于AccessMixin类
    # 目前只是实现了没有权限的显示403页面，还需继续优化
    permission_required = 'METSMY.add_metsmy_ppc'
    raise_exception = True
    def get_permission_denied_message(self):
        self.permission_denied_message = '您没有添加PPC会议纪要的权限！'
        return self.permission_denied_message


'''==================================================================================
函数ppc_metsmydel，处理前端提交的删除会议纪要请求，反馈不同值代表不同结果：
0=未通过权限检查；1=成功完成了反馈
==================================================================================='''
@login_required
#@permission_required('taskmanage.delete_taskitem',raise_exception=True)#
def ppc_metsmydel(request):
    if not request.user.has_perm('METSMY.delete_metsmy_ppc'):
        #鉴于permisson_required用不明白，暂时用has_perm方法
        return HttpResponse("0")#服务器消息：您没有删除任务的权限！
    if request.method == 'POST':
       myid = request.POST.get('aid', '')
       METSMY_ppc.objects.get(id=myid).delete()
       #注意HttpResponse传回前台的数据，需要由前台的回调函数使用
       return HttpResponse("1")#服务器消息：记录删除成功！


'''==================================================================================
函数ppc_checkfile，处理前端提交的纪要文件验证信息，并反馈结果：
0=未通过权限检查；1=成功完成了反馈
==================================================================================='''
@login_required
#@permission_required('taskmanage.delete_taskitem',raise_exception=True)#
def ppc_checkfile(request):
    if not request.user.has_perm('METSMY.change_metsmy_ppc'):
        #鉴于permisson_required用不明白，暂时用has_perm方法
        return HttpResponse("-1")#服务器消息：您没有删除任务的权限！
    if request.method == 'POST':
       myid = request.POST.get('qid', '')
       myfile=RefFiles.objects.filter(refmodel='METSMY_ppc',refid=myid)
       if myfile.count()>0:
           myfile=myfile.first()
           mysmy=METSMY_ppc.objects.get(id=myid)
           mysmy.meetfile_id=myfile.id
           mysmy.save()
           return HttpResponse("1")     # 服务器消息：已有关联文件！
       else:
           return HttpResponse("0")     #服务器消息：尚无关联文件！


'''==================================================================================
函数ppc_setread，处理前端提交的纪要文件已读标记，并反馈结果：
0=之前未读，此次设置；1=之前已完成已读
20190730 by sicksnail
==================================================================================='''
@login_required
#@permission_required('taskmanage.delete_taskitem',raise_exception=True)#
def ppc_setread(request):
    if request.method == 'POST':
        myid = request.POST.get('aid', 1)
        myuid=request.user.id
        myself=User.objects.get(id=myuid)
        mymeet=METSMY_ppc.objects.get(id=myid)
        myreadflag=0
        for chk in mymeet.hasread.all():
           if myuid== chk.id:
               myreadflag=myreadflag+1
        if myreadflag==0:
            mymeet.hasread.add(myself)
            mymeet.save()
        return HttpResponse(myreadflag)

'''==================================================================================
函数ppc_seeread，向前台反馈当前项目的已读情况：
此处使用的不是form,也不适用类视图
20190730 
==================================================================================='''
@login_required
def ppc_seeread(request):
    if request.method == 'GET':
        myid = request.GET.get('id',0)
        try:
            mytask = METSMY_ppc.objects.get(id=myid)#(id=int(myid))
        except:
            mytask = METSMY_ppc.objects.first()
        myrefps = mytask.hasread.all().order_by('id')
        allrefps = User.objects.all().order_by('id')
            # allrefps和myrefps按统一顺序排列有助于简化前台算法
            # models.Taskfeedbacks.objects.filter(tskid__taskfeedbacks__id=myid)
            # 暂时未实现这种set的查询  mytask.Taskfeedbacks_set.all()问题在于从表小写
        if mytask.hasread.count()>0:
            mytkrf = ''
            for rf in mytask.hasread.all():
                mytkrf = mytkrf + rf.first_name + rf.last_name + ','
        return render(request, 'metsmy_seeread.html', {'mytask': mytask, 'myrefps': myrefps, 'allrefps': allrefps})



