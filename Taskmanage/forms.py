from django.forms import ModelForm,forms
from django import forms
from django.contrib.auth.models import Permission,User
from Taskmanage.models import *

#TaskfbForm 是一个从表表单，为便于使用编辑功能，取消外键======================================
class TaskfbForm(ModelForm):
    class Meta:
        model = Taskfeedbacks
        fields = ['id','feedback', 'note', 'status2be']  # 前台表单不显示主表依附和编辑人信息
        labels = {"feedback": "反馈内容", }
        widgets = {
            'feedback': forms.Textarea,
            'note': forms.TextInput,
        }
    def __init__(self, *args, **kwargs):
    #通过重定义init过程，将任务状态修改为只读形式，因为Modelform没有继承form的disable参数
        super(TaskfbForm, self).__init__(*args, **kwargs)

#TaskitemForm 是一基于类的表单，为便于使用编辑功能，取消外键editby======================================
#20190829取消了参与人的添加编辑框显示==================================================================
class TaskitemForm(ModelForm):
    class Meta:
        model=Taskitem
        exclude=['editby', 'refperson']  #前台表单不显示主表依附和编辑人信息
        labels={"task_status":"任务状态",
                "fbdays":"反馈周期（天）",
                "sender":"发起人（编辑时只读）",
                }
        #widgets={
        #    'refperson':forms.CheckboxSelectMultiple,
        #}

    def __init__(self, *args, **kwargs):
    #通过重定义init过程，将任务状态修改为只读形式，因为Modelform没有继承form的disable参数
        super(TaskitemForm, self).__init__(*args, **kwargs)
        #self.fields['refperson'].queryset = User.objects.all()
        if not self.instance: #判断是否为空白的form，对于空form禁止编辑状态
            self.fields['task_status'].widget.attrs['onchange']="this.selectedIndex=this.defaultIndex;"
        #self.fields['duegroup'].widget.attrs['readonly'] = True
        self.fields['start_date'].widget.attrs['onfocus'] = "WdatePicker()"
        self.fields['start_date'].widget.attrs['class'] = "input-text Wdate"
        self.fields['due_date'].widget.attrs['onfocus'] = "WdatePicker()"
        self.fields['due_date'].widget.attrs['class'] = "input-text Wdate"

#TaskrefForm 是一基于类的表单，为便于使用前台处理多对多参与人信息，专门建立=================================
#此表目前还是基于taskitem模型，后续应改为独立多对多Personontask并考虑用set=================================
class TaskrefForm(ModelForm):
    class Meta:
        model=Taskitem
        fields=['taskdesc','refperson']  #前台表单不显示主表依附和编辑人信息
        labels = {"taskdesc": "任务标题（只读）",}
        widgets={
            'refperson':forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
    #通过重定义init过程，将任务状态修改为只读形式，因为Modelform没有继承form的disable参数
        super(TaskrefForm, self).__init__(*args, **kwargs)
        #if not self.instance: #判断是否为空白的form，对于空form禁止编辑状态
            #self.fields['task_status'].widget.attrs['onchange']="this.selectedIndex=this.defaultIndex;"
        self.fields['taskdesc'].widget.attrs['readonly'] = True

#=====================================================================================
#mng_*** 是一组基于待办任务Taskitem_mng的form定义
#包括TaskitemForm，TaskfbForm，TaskrefForm三种form
#20190829 add by sicksnail
#=====================================================================================
class TaskitemForm_mng(ModelForm):
    class Meta:
        model=Taskitem_mng
        exclude=['editby', 'refperson','refstaff','duegroup']  #前台表单不显示主表依附和编辑人信息
        labels={"task_status":"任务状态",
                "fbdays":"建议周期（天）",
                "sender":"发起人（只读）",
                }

    def __init__(self, *args, **kwargs):
    #通过重定义init过程，将任务状态修改为只读形式，因为Modelform没有继承form的disable参数
        super(TaskitemForm_mng, self).__init__(*args, **kwargs)
        if not self.instance: #判断是否为空白的form，对于空form禁止编辑状态
            self.fields['task_status'].widget.attrs['onchange']="this.selectedIndex=this.defaultIndex;"
        self.fields['start_date'].widget.attrs['onfocus'] = "WdatePicker()"
        self.fields['start_date'].widget.attrs['class'] = "input-text Wdate"
        self.fields['due_date'].widget.attrs['onfocus'] = "WdatePicker()"
        self.fields['due_date'].widget.attrs['class'] = "input-text Wdate"


class TaskrefForm_mng(ModelForm):
    class Meta:
        model=Taskitem_mng
        fields=['taskdesc','refperson']  #前台表单不显示主表依附和编辑人信息
        labels = {"taskdesc": "任务标题（只读）",}
        widgets={
            'refperson':forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
    #通过重定义init过程，将任务状态修改为只读形式，因为Modelform没有继承form的disable参数
        super(TaskrefForm_mng, self).__init__(*args, **kwargs)
        self.fields['taskdesc'].widget.attrs['readonly'] = True

class TaskfbForm_mng(ModelForm):
    class Meta:
        model = Taskfeedbacks_mng
        fields = ['id','feedback', 'note', 'status2be']  # 前台表单不显示主表依附和编辑人信息
        labels = {"feedback": "反馈内容", }
        widgets = {
            'feedback': forms.Textarea,
            'note': forms.TextInput,
        }
    def __init__(self, *args, **kwargs):
    #通过重定义init过程，将任务状态修改为只读形式，因为Modelform没有继承form的disable参数
        super(TaskfbForm_mng, self).__init__(*args, **kwargs)
