from django.forms import ModelForm
from django import forms
from FileManage.models import *

#ReffileForm 是一基于类的表单，为便于使用编辑功能，取消外键editby======================================
class ReffileForm(ModelForm):
    class Meta:
        model=RefFiles
        #fields=['parent_category','title','slug','useicon','name','ctgtype']
        exclude = ['editby','update_time','filesize']
        labels={"filename":"文件名(不支持中文)",}
        #widgets={'filename':forms.CheckboxSelectMultiple,}
        widgets = {'filename': forms.FileInput(attrs={'accept':'image/jpeg,application/pdf,application/msword,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,application/vnd.openxmlformats-officedocument.wordprocessingml.document '}), }
    # 通过重定义init过程，将任务状态修改为只读形式，因为Modelform没有继承form的disable参数

    #def __init__(self, *args, **kwargs):
    #    super(ReffileForm, self).__init__(*args, **kwargs)
    #    self.fields['filename'].widget.attrs['accept'] = "image/jpeg,application/pdf,application/msword,application/vnd.ms-excel,application/vnd.openxmlformats-officedocument"
    #    if self.fields['slug']: #判断是否为空白的form，对于已填报的栏目禁止编辑SLUG
    #        self.fields['slug'].widget.attrs['readonly'] = True
    #    self.fields['task_status'].widget.attrs['onchange']="this.selectedIndex=this.defaultIndex;"
