from django.db import models
from django.contrib.auth.models import Permission,User
from django.conf import settings
import os
import uuid

# Create your models here.

# ===============================================================================
# RefFiles是用来记录上传文件与其他业务数据关系的模型
# make_filedir函数是实现上传文件动态目录生成的参数，20190718
# ===============================================================================
def make_filedir(instance,filename):
    #return '/'.join([settings.MEDIA_ROOT,instance.refmodel,str(instance.refid),filename])
    #上面的写法会暴露文件的实际位置，取消掉MEDIA_ROOT也是可以的
    return '/'.join([instance.refmodel, str(instance.refid), filename])

class RefFiles(models.Model):
    #C_APMODEL = (('B737NG', 'B737NG'),)
    #id = models.AutoField(primary_key=True)
    #category = models.CharField(max_length=10,default='AC')
    #anchor_tsn = models.DecimalField(max_digits=8, decimal_places=2)          # 锚定使用时间 时.分
    #update_time = models.DateTimeField(auto_now=True)  # 更新时间
    #editby = models.ForeignKey('auth.User', verbose_name='最后编辑', blank=True, on_delete=models.CASCADE)
    #apl_status = models.IntegerField(verbose_name='飞机状态',choices=C_APSTATUS)
    C_FST = (
        (1, '有效'),
        (0, '失效'),
    )
    id = models.AutoField(primary_key=True) #id如果没有models.AutoField，默认会创建一个id的自增列
    refmodel = models.CharField(verbose_name='相关业务',max_length=30)          #相关模型/业务
    refid = models.IntegerField(verbose_name='相关ID',default=0)                #相关项目编号
    filename = models.FileField(verbose_name='文件名',upload_to=make_filedir)    # 文件名，实际上是存储路径
    filesize=models.DecimalField(verbose_name='文件大小',max_digits=8, decimal_places=2)
    abstract = models.TextField(verbose_name='文件说明',default='无备注说明')    # 备注说明
    filestatus = models.IntegerField(verbose_name='文件状态', choices=C_FST)
    dlcount= models.IntegerField(verbose_name='下载次数',default=0)               #相关项目编号
    update_time = models.DateTimeField(verbose_name='更新时间',auto_now=True)   # 更新时间
    editby = models.ForeignKey('auth.User', verbose_name='最后编辑',
                               blank=True, on_delete=models.CASCADE)            # 最后编辑，外键与用户关联
    class Meta:
        ordering = ['id']
        verbose_name = "相关文件"
        permissions = (
            ("can_change_status", "可以调整文件状态"),
        )

    def __str__(self):
        return self.filename
