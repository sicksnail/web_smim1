from django.db import models
from django.contrib.auth.models import Permission,User

# Create your models here.
# ===============================================================================
# Taskitem是用来任务项目的一个模型
# ===============================================================================
class Taskitem(models.Model):
    #choise选项，第一个数据库内的值，第二个是页面显示的值
    ITEM_STATUS=(
        (0,'推进中'),
        (1,'已完成'),
        (2,'已取消'),
        (-1,'暂停中'),
        (-2,'未启动'),
    )

    CHARACTERS = (
        (0, '主责人'),
        (1, '执行人'),
        (2, '监督人'),
    )

    id = models.AutoField(primary_key=True) #id如果没有models.AutoField，默认会创建一个id的自增列
    duegroup = models.CharField(max_length=10,verbose_name="职责组",default='计划组')  #负责工作组，便于查找
    taskdesc = models.CharField(max_length=300,verbose_name="描述")             #任务描述不超过300字
    update_time = models.DateTimeField(verbose_name="更新时间",auto_now=True)   #更新时间，自动更新
    abstract = models.TextField(verbose_name="备注", default='无备注说明')        #备注说明
    start_date = models.DateField(verbose_name="开始日期", blank=True, null=True) #开始日期
    due_date = models.DateField(verbose_name="到期日期", blank=True, null=True)   #完成期限日期
    fbdays = models.IntegerField(verbose_name="反馈周期", default=7)              #进度反馈周期
    sender = models.CharField(verbose_name="发起人", max_length=30)               #任务发起人
    task_status = models.IntegerField(verbose_name="任务状态",choices=ITEM_STATUS, default=0)  # 任务状态
    #anchor_tsn = models.DecimalField(max_digits=8, decimal_places=2)          # 锚定使用时间 时.分
    editby = models.ForeignKey('auth.User',verbose_name='最后编辑', blank=True,null=True,
                               on_delete=models.SET_NULL) #最后编辑，外键与用户关联
    #refguys = models.ManyToManyField('auth.User', verbose_name='参与人员', blank=True, related_name="person_onti",through="Personontask")  # 参与人员
    #在加入了through后，直接在编辑中处理参与人信息报错，后续再研究吧
    refperson = models.ManyToManyField('auth.User', verbose_name='参与人员', blank=True, related_name="person_onti")
    class Meta:
        ordering = ['due_date']
        verbose_name = "待办任务"
        permissions=(
            ("can_change_status","can 调整项目状态"),
            ("can_superedit_taskitem", "can 项目超级管理"),
        )

    def __str__(self):
        return self.taskdesc

# ===============================================================================
# Personontask是用来记录参与任务的人员，暂时未启用
# ===============================================================================
class Personontask(models.Model):
    CHARACTERS = (
        (0, '主责人'),
        (1, '执行人'),
        (2, '监督人'),
    )
    tskid =models.ForeignKey('Taskitem', on_delete=models.CASCADE) # 任务
    pid =models.ForeignKey('auth.User', on_delete=models.CASCADE,related_name="person_ontask",) # 人员
    # 以下为附加的衍生信息字段
    jointime = models.DateTimeField (verbose_name="加入时间", blank=True)
    character = models.IntegerField(verbose_name="角色",choices=CHARACTERS, blank=True)
    #editby = models.ForeignKey('auth.User',verbose_name='编辑人', blank=True,on_delete=models.CASCADE,related_name="edit_taskreperson",)
    update_time = models.DateTimeField(verbose_name="更新时间", auto_now=True)  # 更新时间，自动更新

# ===============================================================================
# Taskfeedbacks是用来记录任务回复的对象
# ===============================================================================
class Taskfeedbacks(models.Model):
    ITEM_STATUS = (
        (0, '推进中'),
        (1, '已完成'),
        (2, '已取消'),
        (-1, '暂停中'),
        (-2, '未启动'),
    )

    id = models.AutoField(primary_key=True) #id如果没有models.AutoField，默认会创建一个id的自增列
    tskid =models.ForeignKey('Taskitem', verbose_name="任务", on_delete=models.CASCADE) # 任务
    update_time = models.DateTimeField(verbose_name="更新时间", auto_now=True)  # 更新时间，自动更新
    feedback = models.CharField(verbose_name="反馈信息", max_length=300)        # 反馈信息
    status2be = models.IntegerField(verbose_name="状态变更",choices=ITEM_STATUS, default=0) # 状态变更
    editby = models.ForeignKey('auth.User', verbose_name='最后编辑', null=True, blank=True,
                               on_delete=models.SET_NULL)  #最后编辑，外键与用户关联
    # #tsn = models.DecimalField(max_digits=8, decimal_places=2)                       # 总飞行时间
    #csn = models.IntegerField(default=4)                                              # 总使用循环
    note = models.TextField(default='无备注信息')                                      # 摘要

    class Meta:
        ordering = ['tskid']
        verbose_name = "任务反馈记录"

    def __str__(self):
        return str(self.id)

# ===============================================================================
# Taskitem_mng和Taskfeedbacks_mng是用来推进工程部值班领导问题跟踪的任务项目的两个模型
# ===============================================================================
class Taskitem_mng(models.Model):
    #choise选项，第一个数据库内的值，第二个是页面显示的值
    ITEM_STATUS=(
        (0,'推进中'),
        (1,'已完成'),
        (2,'已取消'),
        (-1,'暂停中'),
        (-2,'未启动'),
    )

    CHARACTERS = (
        (0, '主责人'),
        (1, '执行人'),
        (2, '监督人'),
    )

    id = models.AutoField(primary_key=True) #id如果没有models.AutoField，默认会创建一个id的自增列
    duegroup = models.CharField(max_length=10,verbose_name="职责组",default='计划组')  #负责工作组，便于查找
    taskdesc = models.CharField(max_length=300,verbose_name="描述")             #任务描述不超过300字
    update_time = models.DateTimeField(verbose_name="更新时间",auto_now=True)   #更新时间，自动更新
    abstract = models.TextField(verbose_name="备注", default='无备注说明')        #备注说明
    start_date = models.DateField(verbose_name="开始日期", blank=True, null=True) #开始日期
    due_date = models.DateField(verbose_name="到期日期", blank=True, null=True)   #完成期限日期
    fbdays = models.IntegerField(verbose_name="反馈周期", default=7)              #进度反馈周期
    sender = models.CharField(verbose_name="发起人", max_length=30)               #任务发起人
    task_status = models.IntegerField(verbose_name="任务状态",choices=ITEM_STATUS, default=0)  # 任务状态
    #anchor_tsn = models.DecimalField(max_digits=8, decimal_places=2)          # 锚定使用时间 时.分
    editby = models.ForeignKey('auth.User',verbose_name='最后编辑',null=True, blank=True,
                               on_delete=models.SET_NULL) #最后编辑，外键与用户关联
    refperson = models.ManyToManyField('auth.User', verbose_name='参与人员', blank=True, related_name="person_onmng")
    refstaff = models.CharField(verbose_name="参与群组", max_length=30,default="staff_mng") #用于甄别不同类型任务的参与全体
    class Meta:
        ordering = ['due_date']
        verbose_name = "领导提问跟踪"
        permissions=(
            ("can_change_status_mng","can 调整领导提问项目状态"),
            ("can_superedit_taskitem_mng", "can 项目超级管理"),
        )

    def __str__(self):
        return self.taskdesc


class Taskfeedbacks_mng(models.Model):
    ITEM_STATUS = (
        (0, '推进中'),
        (1, '已完成'),
        (2, '已取消'),
        (-1, '暂停中'),
        (-2, '未启动'),
    )

    id = models.AutoField(primary_key=True) #id如果没有models.AutoField，默认会创建一个id的自增列
    tskid =models.ForeignKey('Taskitem_mng', verbose_name="任务", on_delete=models.CASCADE) # 任务
    update_time = models.DateTimeField(verbose_name="更新时间", auto_now=True)  # 更新时间，自动更新
    feedback = models.CharField(verbose_name="反馈信息", max_length=300)        # 反馈信息
    status2be = models.IntegerField(verbose_name="状态变更",choices=ITEM_STATUS, default=0) # 状态变更
    editby = models.ForeignKey('auth.User', verbose_name='最后编辑', null=True, blank=True,
                               on_delete=models.SET_NULL)  # 最后编辑，外键与用户关联
    #tsn = models.DecimalField(max_digits=8, decimal_places=2)                         # 总飞行时间
    #csn = models.IntegerField(default=4)                                              # 总使用循环
    note = models.TextField(default='无备注信息')                                      # 摘要

    class Meta:
        ordering = ['tskid']
        verbose_name = "mng任务反馈记录"

    def __str__(self):
        return str(self.id)
