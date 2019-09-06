from django.forms import ModelForm
from django import forms
from fltdatas.models import *

#TaskitemForm 是一基于类的表单，为便于使用编辑功能，取消外键editby======================================
class AirplanForm(ModelForm):
    class Meta:
        model=Airplan
        #fields=['parent_category','title','slug','useicon','name','ctgtype']
        exclude = ['id','editby','update_time']
        #labels={"parent_category":"主级目录",}
        #widgets={'refperson':forms.CheckboxSelectMultiple,}
    # 通过重定义init过程，将任务状态修改为只读形式，因为Modelform没有继承form的disable参数
    #def __init__(self, *args, **kwargs):
    #    super(CategoryForm, self).__init__(*args, **kwargs)
    #    if self.fields['slug']: #判断是否为空白的form，对于已填报的栏目禁止编辑SLUG
    #        self.fields['slug'].widget.attrs['readonly'] = True
    #        self.fields['task_status'].widget.attrs['onchange']="this.selectedIndex=this.defaultIndex;"

class FltrcdForm(ModelForm):
    class Meta:
        model=Fltrcd
        #fields=['parent_category','title','slug','useicon','name','ctgtype']
        exclude = ['id','editby','update_time']

    # 通过重定义init过程，将记录识别号改为只读形式
    def __init__(self, *args, **kwargs):
        super(FltrcdForm, self).__init__(*args, **kwargs)
        #if self.fields['flt_identity']:
        self.fields['flt_identity'].widget.attrs['readonly'] = True
        if self.fields['flt_identity']:
            self.fields['fltno'].widget.attrs['readonly'] = True
            self.fields['fltdate'].widget.attrs['readonly'] = True
            self.fields['sta_from'].widget.attrs['readonly'] = True
        self.fields['sta_from'].widget.attrs['onblur'] = "getRcdidc()"#当完成起飞航站编辑后自动生成记录识别号
        #self.fields['task_status'].widget.attrs['onchange']="this.selectedIndex=this.defaultIndex;"


