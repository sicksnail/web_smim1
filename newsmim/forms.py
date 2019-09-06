from django.forms import ModelForm,forms
from django import forms
from newsmim.models import *

#TaskitemForm 是一基于类的表单，为便于使用编辑功能，取消外键editby======================================
class CategoryForm(ModelForm):
    class Meta:
        model=SMIMCategory
        fields=['parent_category','title','slug','uslug','viewperm','useicon','name','ctgtype']  #前台表单不显示主表依附和编辑人信息
        labels={"parent_category":"主级目录",
                "slug":"SLUG描述",
                "title":"标题",
                "useicon": "图标",
                'name':"栏目说明",
                }
        #widgets={'refperson':forms.CheckboxSelectMultiple,}
    # 通过重定义init过程，将任务状态修改为只读形式，因为Modelform没有继承form的disable参数
    #def __init__(self, *args, **kwargs):
    #    super(CategoryForm, self).__init__(*args, **kwargs)
    #    if self.fields['slug']: #判断是否为空白的form，对于已填报的栏目禁止编辑SLUG
    #        self.fields['slug'].widget.attrs['readonly'] = True
    #        self.fields['task_status'].widget.attrs['onchange']="this.selectedIndex=this.defaultIndex;"
