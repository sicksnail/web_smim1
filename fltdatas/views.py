from django.shortcuts import render,redirect,reverse,HttpResponse,render_to_response
from django.contrib.auth.decorators import login_required,permission_required #基于函数的验证
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import PermissionRequiredMixin #基于视图的验证
#from django.views.generic.edit import FormMixin #通用视图直接用form必须引用
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Permission,User
from django.shortcuts import get_object_or_404
from django.contrib import messages #进入消息处理
from django.utils import timezone #引入时间处理
from django.http import FileResponse,JsonResponse
from django.views import generic #引入通用视图
from .forms import *    #引用form便于在视图使用modelform
from .models import *   #引用已定义的models
import xlwt,xlrd #导出excel文件必须使用
from django.db import transaction #在http响应中使用事务控制
import os
from datetime import datetime #使用时间信息必须使用
from io import StringIO,BytesIO #处理excel文件需要内存操作



# Create your views here.


'''==================================================================================
函数editsuccess，简单的提示信息，协助类视图的处理
==================================================================================='''
def editsuccess(request):
    return render(request, 'addeditsuccess.html')

'''==================================================================================
函数airplanlist，向前端反馈飞机列表信息
==================================================================================='''
def airplanlist(request):
    if request.method == 'GET':
        airplans=Airplan.objects.all()
        return render(request, 'airplan-list.html',{'Myaps':airplans})


'''==================================================================================
函数dlaclist，向前端提供aclist文件下载
==================================================================================='''
def dlaclist(request):
    if request.method == 'GET':
        filename = request.GET.get("filename", None)
        filepath = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aclistfile/'+filename)
        file = open(filepath, 'rb')
        response = FileResponse(file)
        #response = StreamingHttpResponse(file_iterator(the_file_name))
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachement;filename='+filename #os.path.basename(filepath)
        return response

'''==================================================================================
函数airplanexcelin打开飞机数据excel导入页面
==================================================================================='''
@csrf_exempt
def airplanexcelin(request):
    if request.method == 'GET':
        #filename = request.GET.get("filename", None)
        return  render_to_response('airplan-excelin.html')
    else:
        f = request.FILES.get("my_excel",None)
        type_excel = f.name.split('.')[1]
        if 'xls' in type_excel:#判断确认必须是xls或者xlsx文件
            wb = xlrd.open_workbook(filename=None, file_contents=f.read())  # 关键点在于这里
            table = wb.sheets()[0]
            nrows = table.nrows  # 行数
            ncole = table.ncols  # 列数
            try:
                with transaction.atomic():
                    for i in range(1, nrows):#从这里开始就是真正的数据处理了
                        rowValues = table.row_values(i)  # 一行的数据
                        #acmodel = Airplan.objects.filter(apmodel=rowValues[1])
                        Airplan.objects.create(apmodel=rowValues[1],apgroup=rowValues[2],identity=rowValues[3],
                                               anchor_date=rowValues[4],anchor_tsn=float(rowValues[5]),
                                               anchor_csn=int(rowValues[6]),editby_id=int(request.user.id),apl_status=1
                                               )
            except Exception as e:
                return JsonResponse({'msg': '出现错误....'})
            return redirect('../success/') #JsonResponse({'msg': 'ok'})
        return JsonResponse({'msg': '上传文件格式不是xls或者xlsx'})


'''==================================================================================
函数excelaclistout，向前端导出excel文件
==================================================================================='''
def excelaclistout(request):
    #第一步是获取对象数据
    if request.method == 'GET':
        mytp = request.GET.get('actypev', '0')
    else:
        mytp = request.POST.get('actypev', '0')
    mytpn = request.POST.get('actypen', '')
    if '0' == mytp:
        myacs1 = Airplan.objects.all()
    else:
        myacs1 = Airplan.objects.filter(apmodel=mytpn)
    #myacs1 = getaclist(request)

    #第二步准备excel文件
    # 创建一个文件对象
    fname = 'aclist_opt_' + datetime.now().strftime('%y%m%d%H%M%S') + '.xls'
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
    sheet.write(0, 0, 'ID', style_heading)
    sheet.write(0, 1, '机型', style_heading)
    sheet.write(0, 2, '构型', style_heading)
    sheet.write(0, 3, '注册号', style_heading)
    sheet.write(0, 4, '锚定日期', style_heading)
    sheet.write(0, 5, '锚定TSN', style_heading)
    sheet.write(0, 6, '锚定CSN', style_heading)

    #第三歩，将数据写入excel中，for循环
    data_row = 1
    for myac1 in myacs1:
    #myac1=Airplan.objects.all().first()
        pri_time = myac1.anchor_date.strftime('%Y-%m-%d')
        sheet.write(data_row, 0, myac1.id,style_body)
        sheet.write(data_row, 1, myac1.apmodel,style_body)
        sheet.write(data_row, 2, myac1.apgroup,style_body)
        sheet.write(data_row, 3, myac1.identity,style_body)
        sheet.write(data_row, 4, pri_time,style_body)
        sheet.write(data_row, 5, myac1.anchor_tsn,style_body)
        sheet.write(data_row, 6, myac1.anchor_csn,style_body)
        data_row=data_row+1

    # 第一方案：生成的文件直接存储到服务器指定目录下,即本APP下aclistfile文件，反馈给前台文件名
    # 前台收到反馈后，在页面生成一个文件的下载链接
    # 该方案的优点是容易将文件下载与文件生成分步骤进行，容易处理复杂查询，不足在于服务器安全受影响
    wb.save(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aclistfile/' + fname))
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

'''==================================================================================
类视图airplan_addview，应用类视图快速实现任务添加处理
此处涉及在form_valid函数重写过程中处理特殊字段值
==================================================================================='''
class Airplan_addview(PermissionRequiredMixin,generic.CreateView):
    model = Airplan
    template_name = 'airplan-addedit_form.html'
    #fields = '__all__' #在createview中必须设置这个函数
    form_class = AirplanForm
    context_object_name = 'Myairplan'
    success_url = '../../success/'  #此处使用根目录下的成功返回页面
    # 通过重写form_valid(self, form)过程实现从表添加时关系主表的更新，此处处理editby
    #对于新建任务来说，还需要处理编辑人信息
    def form_valid(self, form):
        if self.request.method == 'POST':
            form.instance.editby_id = int(self.request.user.id)
        return super().form_valid(form)

    # 以下为权限控制的代码，基于AccessMixin类
    # 目前只是实现了没有权限的显示403页面，还需继续优化
    permission_required = 'fltdatas.add_airplan'
    raise_exception = True
    def get_permission_denied_message(self):
        self.permission_denied_message = '您没有添加飞机信息的权限！'
        return self.permission_denied_message

'''==================================================================================
类视图Airplan_editview，应用类视图快速实现任务添加处理
此处涉及在form_valid函数重写过程中处理特殊字段值
==================================================================================='''
class Airplan_editview(PermissionRequiredMixin,generic.UpdateView):
    model = Airplan
    template_name = 'airplan-addedit_form.html'
    #fields = '__all__' #在createview中必须设置这个函数
    form_class = AirplanForm
    context_object_name = 'Myairplan'
    success_url = '../../../success/' #此处使用项目根目录下的编辑成功反馈页
    #必须给post执行成功一个反馈,这个基础是当前URL.因为updete用的url更深，因此需要多返回一层。
    # 通过重写form_valid(self, form)过程实现从表添加时关系主表的更新，此处处理editby
    def form_valid(self, form):
        if self.request.method == 'POST':
            form.instance.editby_id = int(self.request.user.id)
        return super().form_valid(form)

    # 以下为权限控制的代码，基于AccessMixin类
    # 目前只是实现了没有权限的显示403页面，还需继续优化
    permission_required = 'fltdatas.change_airplan'
    raise_exception = True
    def get_permission_denied_message(self):
        self.permission_denied_message = '您没有编辑飞机信息的权限！'
        return self.permission_denied_message

'''==================================================================================
函数airplanDelete，处理前端提交的删除任务请求，反馈不同值代表不同结果：
0=未通过权限检查；1=成功完成了反馈
==================================================================================='''
#@permission_required('taskmanage.delete_taskitem',raise_exception=True)#
def airplanDelete(request):
    if not request.user.has_perm('fltdatas.delete_airplan'):
        #鉴于permisson_required用不明白，暂时用has_perm方法
        return HttpResponse("0")#服务器消息：您没有删除任务的权限！
    if request.method == 'POST':
       myid = request.POST.get('aid', '')
       Airplan.objects.get(id=myid).delete()
       #注意HttpResponse传回前台的数据，需要由前台的回调函数使用
       return HttpResponse("1")#服务器消息：记录删除成功！


'''==================================================================================================
以下view处理为针对Fltrcd（飞行记录）进行的处理===========================================================
===================================================================================================='''

'''==================================================================================
函数Fltrcdlist，向前端反馈飞行记录的列表信息，同时也反馈飞机信息
==================================================================================='''
def Fltrcdlist(request):
    if request.method == 'GET':
        airplanes=Airplan.objects.all()
        fltrcds=Fltrcd.objects.all()
        return render(request, 'fltrcd-list.html',{'Myacs':airplanes,'Myrcds':fltrcds})

'''==================================================================================
函数getFltcode，向前端反馈自动生成的飞行记录编号
==================================================================================='''
@login_required
def getFltcode(request):
    if not request.user.has_perm('fltdatas.add_fltrcd'):
        #鉴于permisson_required用不明白，暂时用has_perm方法
        return HttpResponse("0")#服务器消息：您没有添加飞行记录的权限！
    if request.method == 'POST':
        myac=request.POST.get('myac','')
        mydate = request.POST.get('mydate', '')
        myflt = request.POST.get('myflt', '')
        mysta = request.POST.get('mysta', '')
        mycode=myac+'D'+datetime.strptime(mydate,'%Y-%m-%d').strftime('%Y%m%d')+myflt+mysta
        myfltrcds=Fltrcd.objects.filter(flt_identity=mycode)
        if myfltrcds.count()>0:
            return HttpResponse("1")  # 服务器消息：发现飞行记录重号！
        else:
            return HttpResponse(mycode)
    #meets是查询到的会议，myhead是调用页面时的标题，mytit是调用增删改操作时的值实现一个temple用于多对象

'''==================================================================================
类视图Fltrcd_addview，应用类视图快速实现飞行数据添加处理
此处涉及在form_valid函数重写过程中处理特殊字段值
==================================================================================='''
class Fltrcd_addview(PermissionRequiredMixin,generic.CreateView):
    model = Fltrcd
    template_name = 'fltrcd-addedit_form.html'
    #fields = '__all__' #在createview中必须设置这个函数
    form_class = FltrcdForm
    context_object_name = 'Myfltrcds'
    success_url = '../../success/'  #此处使用根目录下的成功返回页面
    # 通过重写form_valid(self, form)过程实现从表添加时关系主表的更新，此处处理editby
    #对于新建任务来说，还需要处理编辑人信息
    def form_valid(self, form):
        if self.request.method == 'POST':
            form.instance.editby_id = int(self.request.user.id)
        return super().form_valid(form)

    # 以下为权限控制的代码，基于AccessMixin类
    # 目前只是实现了没有权限的显示403页面，还需继续优化
    permission_required = 'fltdatas.add_fltrcd'
    raise_exception = True
    def get_permission_denied_message(self):
        self.permission_denied_message = '您没有添加飞行记录的权限！'
        return self.permission_denied_message

'''==================================================================================
类视图Fltrcd_editview，应用类视图快速实现飞行数据编辑处理
此处涉及在form_valid函数重写过程中处理特殊字段值
==================================================================================='''
class Fltrcd_editview(PermissionRequiredMixin,generic.UpdateView):
    model = Fltrcd
    template_name = 'fltrcd-addedit_form.html'
    #fields = '__all__' #在createview中必须设置这个函数
    form_class = FltrcdForm
    context_object_name = 'Myfltrcds'
    success_url = '../../../success/' #此处使用项目根目录下的编辑成功反馈页
    #必须给post执行成功一个反馈,这个基础是当前URL.因为updete用的url更深，因此需要多返回一层。
    # 通过重写form_valid(self, form)过程实现从表添加时关系主表的更新，此处处理editby
    def form_valid(self, form):
        if self.request.method == 'POST':
            form.instance.editby_id = int(self.request.user.id)
        return super().form_valid(form)

    # 以下为权限控制的代码，基于AccessMixin类
    # 目前只是实现了没有权限的显示403页面，还需继续优化
    permission_required = 'fltdatas.change_fltrcd'
    raise_exception = True
    def get_permission_denied_message(self):
        self.permission_denied_message = '您没有编辑飞行数据的权限！'
        return self.permission_denied_message

'''==================================================================================
函数Fltrcd_delete，处理前端提交的删除飞行数据请求，反馈不同值代表不同结果：
0=未通过权限检查；1=成功完成了反馈
==================================================================================='''
#@permission_required('taskmanage.delete_taskitem',raise_exception=True)#
def Fltrcd_delete(request):
    if not request.user.has_perm('fltdatas.delete_fltrcd'):
        return HttpResponse("0")#服务器消息：您没有删除任务的权限！
    if request.method == 'POST':
       myid = request.POST.get('id', '')
       Fltrcd.objects.get(id=myid).delete()
       #注意HttpResponse传回前台的数据，需要由前台的回调函数使用
       return HttpResponse("1")#服务器消息：记录删除成功！

