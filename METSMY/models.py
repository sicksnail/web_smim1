from django.db import models
from django.contrib.auth.models import Permission,User
from django.forms import ModelForm
from django import forms
from FileManage.models import RefFiles

# Create your models here.
# ===============================================================================
# METSMY是代表会议纪要的模型，后缀代表了编号首字母
# ===============================================================================
class METSMY_ppc(models.Model):
    MTYPE=(
        (0,'周例会'),
        (1,'专题会'),
    )
    id = models.AutoField(primary_key=True)
    meetcode = models.CharField(verbose_name='会议编号', max_length=30, unique=True)#会议编号有唯一性
    title = models.CharField(verbose_name='会议主题', max_length=100)
    abstract = models.TextField(verbose_name='会议备注',default='无备注说明')
    meetdate = models.DateField(verbose_name='会议日期',blank=True, null=True)
    recorder = models.CharField('记录人', max_length=30, null=True)
    moderator = models.CharField('主持人', max_length=30, null=True)
    codenum = models.IntegerField(verbose_name='编号数值',blank=True,null=True)
    #codenum = models.DecimalField(max_digits=8, decimal_places=2)
    meetfile = models.ForeignKey('FileManage.RefFiles', verbose_name="纪要文件", blank=True, null=True, on_delete=models.SET_NULL)
    meettype=models.IntegerField(verbose_name='会议类型', choices=MTYPE)
    editby = models.ForeignKey('auth.User', verbose_name='最后编辑',blank=True,null=True,on_delete=models.SET_NULL )
    edittime = models.DateTimeField(auto_now=True)  # 更新时间
    hasread = models.ManyToManyField('auth.User', verbose_name='已读人员', blank=True, related_name="person_read")
    class Meta:
        ordering = ['-meetcode'] #按会议编号降序排列
        verbose_name = "PPC会议纪要"

    def __str__(self):
        return self.meetcode+self.title

#TaskitemForm 是一基于类的表单，为便于使用编辑功能，取消外键editby======================================
class Metsmy_ppcForm(ModelForm):
    class Meta:
        model=METSMY_ppc
        exclude=['editby','edittime','codenum','hasread','meetfile']
        #前台表单不显编辑人信息、关联文件和已读情况
        labels={"title":"PPC会议主题",
                "meetcode":"会议编号（只读）",
                }
        #widgets={
        #    'hasread':forms.CheckboxSelectMultiple,
        #}

    def __init__(self, *args, **kwargs):
    #通过重定义init过程，将任务状态修改为只读形式，因为Modelform没有继承form的disable参数
        super(Metsmy_ppcForm, self).__init__(*args, **kwargs)
        #self.fields['hasread'].queryset = User.objects.all() #此处需添加已读人的信息
        #if not self.instance: #判断是否为空白的form，对于空form禁止编辑状态
        #    self.fields['task_status'].widget.attrs['onchange']="this.selectedIndex=this.defaultIndex;"
        self.fields['meetcode'].widget.attrs['readonly'] = True
        self.fields['meetdate'].widget.attrs['onblur'] = "getMeetcode('ppc_getmetcode')"

