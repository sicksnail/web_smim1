from django.shortcuts import render,redirect,reverse
from django.contrib.auth.decorators import login_required,permission_required #基于函数的验证
from django.contrib.auth.models import User,Group #用于编辑个人信息
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password #用于前台修改密码
from django.views.decorators.csrf import csrf_exempt,csrf_protect
from django.http import HttpResponse
from django.contrib.auth.mixins import PermissionRequiredMixin #基于视图的验证
from django.views import generic #引入通用视图
from datetime import *  #引用时间处理函数
from .models import *    #引用自建的model
from .forms import *


# ================================================================================
# loginUser是前台登录页面
# 20181129加入了动态目录部分
# ================================================================================
def loginUser(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    else:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request,username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                request.session.set_expiry(0)   # 设置浏览器关闭之后就过期
                #return redirect(reverse('web_smim'))#前端是ajax不支持重定向
                return HttpResponse('{"status":"success", "msg":"登录成功"}', content_type="application/json")
            else:
                return HttpResponse('{"status":"unsuccess", "msg":"用户名或密码错误"}', content_type="application/json")
                #return render(request, 'login.html', {'errmsg': 'disabled account'})
                # Return a 'disabled account' error message
        else:
            return HttpResponse('{"status":"err", "msg":"用户名或密码错误"}', content_type="application/json")

# ================================================================================
# logoutUser是前台退出
# 重新定位到login页面
# ================================================================================
def logoutUser(request):
    logout(request)
    return redirect('../login/')

#================================================================================
#web_smim是主页面的显示，调用了hui的index文件
#20181129加入了动态目录部分
#================================================================================
@login_required(login_url='/login/')
def web_smim(request):
    categoryPs = SMIMCategory.objects.filter(parent_category = None).order_by('id')
    #20190816加入用户目录管理代码======================================
    myctitems=[]
    for myp in categoryPs:
        myctcs=SMIMCategory.objects.filter(parent_category = myp).order_by('id')
        myinflag = 0  # 标记当前父目录下有无已入选子目录
        myctcts = []
        for myc in myctcs:
            if request.user.has_perm(myc.viewperm):
                if myinflag==0:
                    myitem={'title':myp.title,'icon':myp.useicon} #父目录取标题和图标
                    myctcts.append(myitem)
                    myinflag = 1
                myitem2 = {'title': myc.title, 'slug': myc.uslug+'/'+myc.slug} #子目录取标题和slug
                myctcts.append(myitem2)
        if myinflag>0:  #如果有目录符合，则加入目录数组
            myctitems.append(myctcts)
    # 20190828加入用户默认页面管理代码======================================
    #gps=Group.objects.all()
    gps = Group.objects.filter(user=request.user)
    mygroup={'title':"欢迎使用",'url':"../welcome/"}
    for mygp in gps:
        if 'staff_mng' == mygp.name :
            mygroup = {'title': "值班改善项目", 'url': "../taskmng/list_mng/"}
            break
        elif  'staff_ppc' == mygp.name :
            mygroup = {'title': "生产待办任务", 'url': "../taskmng/list/"}
            break
        else:
            mygroup={'title':"欢迎使用",'url':"../welcome/"}
    return render(request,
                  'index.html',
                  {'username': request.user.username ,
                   'myself':request.user,
                   'myitems':myctitems,#二维数组表示的目录，第一个为父目录，后面的用冒号拆开
                   'mygroup':mygroup
                   }
                  )

#================================================================================
#welcome是无任务分组(staff_xxx)用户登录时显示的页面
#================================================================================
def welcome(request):
    if request.method == 'GET':
        categorys = SMIMCategory.objects.exclude(parent_category = None).order_by('parent_category')
        return render(request, 'welcome.html',{'myself':request.user,'categorys':categorys})

#================================================================================
#userlist是用户页面的显示，调用了hui的user-list文件
#================================================================================
def userlist(request):
    if request.method == 'GET':
        return render(request,
                      'user-list.html',
                      {'username': request.user.username,
                       'myself': request.user}
                      )

#================================================================================
#categoryXXX是目录管理的相关处理
#categorylist是获取并反馈父一级目录的函数
#articladd是调用页面article-add来实现增加功能
#articleEdit是调用页面article-edit来实现编辑功能
#articleDel是处理删除请求的函数
#================================================================================
'''============================================================================
函数categorylist用于处理栏目清单的请求
============================================================================='''
def categorylist(request):
    if request.method == 'GET':
        mycategorys = SMIMCategory.objects.all()
        return render(request, 'category-list.html',{'Myctgs':mycategorys})

'''==================================================================================
类视图Category_editview，应用类视图快速实现任务添加参与人处理
此处涉及在form_valid函数重写过程中处理特殊字段值
==================================================================================='''
class Category_editview(PermissionRequiredMixin,generic.UpdateView):
    model = SMIMCategory
    template_name = 'category-addedit_form.html'
    form_class = CategoryForm
    context_object_name = 'Mycategory'
    success_url = '../../success/'
    #必须给post执行成功一个反馈,这个基础是当前URL.因为updete用的url更深，因此需要多返回一层。
    # 通过重写form_valid(self, form)过程实现从表添加时关系主表的更新，此处处理editby
    #def form_valid(self, form):
    #    if self.request.method == 'POST':
    #        form.instance.editby_id = int(self.request.user.id)
    #    return super().form_valid(form)
    # 以下为权限控制的代码，基于AccessMixin类------------------------------
    # 目前只是实现了没有权限的显示403页面，还需继续优化
    permission_required = 'newsmim.change_SMIMCategory'
    raise_exception = True
    def get_permission_denied_message(self):
        self.permission_denied_message = '您没有编辑栏目信息的权限！'
        return self.permission_denied_message

'''==================================================================================
类视图Category_addview，应用类视图快速实现任务添加参与人处理
此处涉及在form_valid函数重写过程中处理特殊字段值
==================================================================================='''
class Category_addview(PermissionRequiredMixin,generic.CreateView):
    model = SMIMCategory
    template_name = 'category-addedit_form.html'
    form_class = CategoryForm
    context_object_name = 'Mycategory'
    success_url = '../success/'
    #必须给post执行成功一个反馈,这个基础是当前URL.因为updete用的url更深，因此需要多返回一层。
    # 通过重写form_valid(self, form)过程实现从表添加时关系主表的更新，此处处理editby
    #def form_valid(self, form):
    #    if self.request.method == 'POST':
    #        form.instance.editby_id = int(self.request.user.id)
    #    return super().form_valid(form)
    # 以下为权限控制的代码，基于AccessMixin类------------------------------
    # 目前只是实现了没有权限的显示403页面，还需继续优化
    permission_required = 'newsmim.add_SMIMCategory'
    raise_exception = True
    def get_permission_denied_message(self):
        self.permission_denied_message = '您没有添加编辑栏目信息的权限！'
        return self.permission_denied_message

'''============================================================================
函数categoryDelete用于处理栏目删除的请求
============================================================================='''
@login_required(login_url='/login/')
def categoryDelete(request):
    if not request.user.has_perm('newsmim.delete_smimcategory'):
        #鉴于permisson_required用不明白，暂时用has_perm方法
        return HttpResponse("服务器消息：您没有删除任务的权限！")#服务器消息：您没有删除任务的权限！
    if request.method == 'POST':
       myid = request.POST.get('cid', '')
       SMIMCategory.objects.get(id=myid).delete()
       return HttpResponse("删除任务成功!")


'''==================================================================================
函数Userinfo_edit用于更新用户的个人信息，包括邮箱和姓名
函数Password_chg用于更新用户的密码
==================================================================================='''
@login_required(login_url='/login/')
def Userinfo_edit(request):
    if request.method == 'GET':
        myid=request.user.id
        myinfo=User.objects.get(id=myid)
        return render(request, 'userinfo_edit.html', {'myinfo': myinfo})
    elif request.method == 'POST':
        obj=User.objects.get(id=request.user.id)
        obj.first_name = request.POST.get('first_name', '')
        obj.last_name = request.POST.get('last_name', '')
        obj.email= request.POST.get('email', '')
        obj.save()
        return HttpResponse("个人信息修改成功！")

@login_required(login_url='/login/')
def password_chg(request):
    if request.method == 'POST':
        obj=User.objects.get(id=request.user.id)
        mypwo = request.POST.get('password', '')
        mypwn = request.POST.get('password2', '')
        if obj.check_password(mypwo):
            obj.password = make_password(mypwn)
            obj.save()
            return HttpResponse('{"status":"success", "msg":"修改成功"}', content_type="application/json")
        else:
            return HttpResponse('{"status":"fail", "msg":"原始密码错误"}', content_type="application/json")

#================================================================================
#articleXXX是测试页面的显示，用于验证可以打开子页面
#articlelist是调用主界面article-list显示全部内容
#articladd是调用页面article-add来实现增加功能
#articleEdit是调用页面article-edit来实现编辑功能
#articleDel是处理删除请求的函数
#================================================================================
def articlelist(request):
    if request.method == 'GET':
        articles=models.Article.objects.all()
        return render(request, 'article-list.html',{'articles':articles})

def articleAdd(request):
    if request.method == 'GET':
        return render(request, 'article-add.html')
    elif request.method == 'POST':
        '''
        #测试是查看提交的请求数据
        return HttpResponse(request.body)
        '''
        thecategory = request.POST.get('category', '')
        thesource = request.POST.get('source', '')
        thetitle = request.POST.get('title', '')
        theabstract=request.POST.get('abstract', '')
        theupdatetime = request.POST.get('update_time', '')
        Article.objects.create(title=thetitle,
                                      category=thecategory,
                                      source=thesource,
                                      abstract=theabstract,
                                      update_time=theupdatetime)
        return HttpResponse("<p>wiew消息：新记录添加成功！<p>",content_type="text/plain")

def articleEdit(request):
    if request.method == 'GET':
        myid=request.GET.get('aid',1)
        myart=Article.objects.get(aid=myid)
        return render(request, 'article-edit.html', {'myart': myart})
    elif request.method == 'POST':
        obj=Article.objects.get(aid=request.POST['aid'])
        obj.category = request.POST.get('category', '')
        obj.source = request.POST.get('source', '')
        obj.title = request.POST.get('title', '')
        obj.abstract=request.POST.get('abstract', '对象没有取到')
        obj.save()
        return HttpResponse("记录添加成功！")


def articleDelete(request):
    if request.method == 'POST':
       myid = request.POST.get('aid', '')
       Article.objects.get(aid=myid).delete()
       return HttpResponse("记录删除成功！")

'''==================================================================================
函数editsuccess，简单的提示信息，协助类视图的处理
==================================================================================='''
def editsuccess(request):
    return render(request, 'addeditsuccess.html')


