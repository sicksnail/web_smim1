from django.db import models

# Create your models here.

# ===============================================================================
# Airplan是用来记录飞机对象的一个模型
# ===============================================================================
class Airplan(models.Model):
    C_APMODEL = (
        ('B737NG', 'B737NG'),
        ('B737CL','B737CL'),
        ('B737MAX', 'B737MAX'),
        ('B787', 'B787'),
        ('A320', 'A320'),
    )

    C_APGROUP = (
        ('739A', '739A'),
        ('738B', '738B'),
        ('738C', '738C'),
        ('738D', '738D'),
        ('738E', '738E'),
        ('738F', '738F'),
        ('73MA', '73MA'),
    )

    C_APSTATUS=(
        (1,'使用中'),
        (2,'封存中'),
        (0,'已退出'),

    )
    id = models.AutoField(primary_key=True) #id如果没有models.AutoField，默认会创建一个id的自增列
    category = models.CharField(verbose_name="类别",max_length=10,default='AC')                   #对象分类
    apmodel=models.CharField(verbose_name="机型",max_length=10,choices=C_APMODEL)                 #机型
    apgroup=models.CharField(verbose_name="构型组",max_length=10,choices=C_APGROUP)                 #飞机构型
    identity = models.CharField(verbose_name="识别",max_length=30)                                #识别号，注册号
    abstract = models.TextField(verbose_name="说明",default='无备注说明')                          #备注说明
    anchor_date = models.DateField(verbose_name="锚定日期",blank=True, null=True)                     # 锚定日期
    anchor_tsn = models.DecimalField(verbose_name="锚定TSN",max_digits=8, decimal_places=2)          # 锚定使用时间 时.分
    anchor_csn = models.IntegerField(verbose_name="锚定CSN",default=4)                               # 锚定使用循环
    apl_status = models.IntegerField(verbose_name='飞机状态',choices=C_APSTATUS)
    update_time = models.DateTimeField(verbose_name="更新时间",auto_now=True)  # 更新时间
    editby = models.ForeignKey('auth.User', verbose_name='最后编辑', blank=True, on_delete=models.CASCADE)  # 最后编辑，外键与用户关联

    class Meta:
        ordering = ['identity']
        verbose_name = "飞机信息"
        permissions = (
            ("can_change_status", "can 调整飞机状态"),
        )

    def __str__(self):
        return self.identity


# ===============================================================================
# Fltrcd是FLB中飞行数据记录模型
# ===============================================================================
class Fltrcd(models.Model):
    C_FLTCTG = (
        ('YY', '营运'),
        ('XL', '训练'),
        ('DJ', '调机'),
        ('QT', '其他'),
    )

    id = models.AutoField(primary_key=True) #id如果没有models.AutoField，默认会创建一个id的自增列
    flt_identity=models.CharField(verbose_name="飞机记录识别号",max_length=30) # 由飞机号+航班号+起飞站组成null=True
    airplane=models.ForeignKey('Airplan',verbose_name="注册号",on_delete=models.CASCADE)   #飞机号关联外键
    category = models.CharField(verbose_name="飞行类别",max_length=10,choices=C_FLTCTG,default='YY')
    fltno=models.CharField(verbose_name="航班号",max_length=10,blank=True, null=True)
    fltdate=models.DateField(verbose_name="起飞日期")
    sta_from = models.CharField(verbose_name="起飞航站", max_length=10)
    sta_to=models.CharField(verbose_name="着陆航站", max_length=10)
    time_run = models.DecimalField(verbose_name="开车时间", max_digits=8, decimal_places=2, null=True)
    time_sd = models.DecimalField(verbose_name="关车时间", max_digits=8, decimal_places=2, null=True)
    time_takeoff = models.DecimalField(verbose_name="起飞时间", max_digits=8, decimal_places=2)
    time_land = models.DecimalField(verbose_name="着陆时间", max_digits=8, decimal_places=2)
    time_inair = models.DecimalField(verbose_name="空中时间", max_digits=8, decimal_places=2)
    time_opr = models.DecimalField(verbose_name="空地时间", max_digits=8, decimal_places=2)
    cyc_nml=models.IntegerField(verbose_name="正常起落",default=1)
    cyc_ctn=models.IntegerField(verbose_name="连续起落",default=0)
    ENG1=models.CharField(verbose_name="1发序号", max_length=10)
    ENG2=models.CharField(verbose_name="2发序号", max_length=10)
    APU=models.CharField(verbose_name="APU序号", max_length=10)
    APU_runtime=models.DecimalField(verbose_name="APU运行时间", max_digits=8, decimal_places=2)
    #以下为更新人员信息及备注信息
    update_time = models.DateTimeField(verbose_name="更新时间",auto_now=True)  # 更新时间
    editby = models.ForeignKey('auth.User', verbose_name='最后编辑', blank=True, null=True, on_delete=models.SET_NULL)  # 最后编辑，外键与用户关联
    abstract = models.TextField(verbose_name='备注说明', default='无备注说明')  # 备注说明

    class Meta:
        ordering = ['-fltdate','airplane_id']
        verbose_name = "飞行记录信息"
        #permissions = ( ("can_change_status", "can 调整飞机状态"),   )

    def __str__(self):
        return self.airplane.identity+str(self.fltdate)+self.fltno+self.sta_from



