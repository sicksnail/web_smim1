from django.db import models

#=============================================================================
#Article是用来测试功能的一个模板
#=============================================================================
class Article(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    aid = models.AutoField(primary_key=True) #id如果没有models.AutoField，默认会创建一个id的自增列
    title = models.CharField(max_length=100, blank=True, default='资讯标题')        #标题
    category = models.CharField(max_length=30,default='行业动态')                   #分类
    source = models.CharField(max_length=30,default='H-ui')                        #来源
    update_time = models.DateTimeField(auto_now=True)                              #更新时间
    abstract = models.TextField(default='本文摘要不应少于10个字。')                 #摘要
    see_times = models.IntegerField(default=1111)                                  #浏览次数
    publish_status = models.IntegerField(default=0)     #发布状态: 0未发布 1已发布 2草稿

    class Meta:
        ordering = ['created']
        verbose_name = "文章"

    def __str__(self):
        return self.title


# ===============================================================================
# SMIMCategory是用来实现动态树状目录的一个模型
# ===============================================================================
class SMIMCategory(models.Model):
    CTYPE=(
        (0,'父栏目'),
        (1,'子栏目'),
    )
    id = models.AutoField(primary_key=True)
    title = models.CharField('分类标题', max_length=30, unique=True)
    name = models.CharField('分类名', max_length=30, unique=True)
    slug = models.SlugField('slug', max_length=40, blank=True, null=True)
    uslug = models.SlugField('上级slug', max_length=40, blank=True, null=True) #为支持跨app的业务目录
    useicon=models.CharField('父类图标', max_length=30, null=True)#, unique=True表示具备独特性
    parent_category = models.ForeignKey('self', verbose_name="父级分类", blank=True, null=True, on_delete=models.CASCADE)
    ctgtype=models.IntegerField(verbose_name='标签类型',blank=True, null=True,choices=CTYPE)
    viewperm=models.CharField('查看权限',max_length=40, blank=True, null=True)
    class Meta:
        ordering = ['name']
        verbose_name = "分类"

    def __str__(self):
        return self.title
"""
from slugify import slugify
#这里记录的是slug数据自动处理，需要安装slugify文件，暂时取消啦
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super(SMIMCategory, self).save(*args, **kwargs)

"""
# ===============================================================================
# FLTOBJ是用来记录飞行对象的一个模型
# ===============================================================================
class Fltobj(models.Model):
    id = models.AutoField(primary_key=True) #id如果没有models.AutoField，默认会创建一个id的自增列
    category = models.CharField(max_length=10,default='AC')                   #对象分类
    identity = models.CharField(max_length=30)                                #来源
    update_time = models.DateTimeField(auto_now=True)                         #更新时间
    abstract = models.TextField(default='无备注说明')                          #备注说明
    anchor_date = models.DateField(blank=True, null=True)                     # 锚定日期
    anchor_tsn = models.DecimalField(max_digits=8, decimal_places=2)          # 锚定使用时间 时.分
    csn = models.IntegerField(default=4)                                      # 锚定使用循环
    obj_status = models.IntegerField(default=0)     #发布状态: 0使用中 1已停用 2未启用

    class Meta:
        ordering = ['category']
        verbose_name = "飞行对象"

    def __str__(self):
        return self.identity

# ===============================================================================
# FLTDATA是用来记录对象每日飞行时间的一个模型
# ===============================================================================
class Fltdata(models.Model):
    id = models.AutoField(primary_key=True) #id如果没有models.AutoField，默认会创建一个id的自增列
    objid =models.ForeignKey('Fltobj', verbose_name="对象", on_delete=models.CASCADE) # 对象
    flt_date = models.DateField()                                                     # 飞行日期
    sta_from = models.CharField(max_length=10,default='TSN')                          # 出港站
    time_from = models.DateTimeField(blank=True, null=True)                           # 出港时间
    sta_end = models.CharField(max_length=10, default='TSN')                          # 航后站
    time_end = models.DateTimeField(blank=True, null=True)                            # 航后时间
    time_air = models.DecimalField(max_digits=4, decimal_places=2)                    # 空中时间 时.分
    time_opt = models.DecimalField(max_digits=4, decimal_places=2)                    # 空地时间 时.分
    cyc_nml = models.IntegerField(default=4)                                          # 正常起落
    cyc_ctn = models.IntegerField(default=4)                                          # 连续起落
    tsn = models.DecimalField(max_digits=8, decimal_places=2)                         # 总飞行时间
    csn = models.IntegerField(default=4)                                              # 总使用循环
    update_time = models.DateTimeField(auto_now=True)                                 # 更新时间
    identity = models.CharField(max_length=30)                                        # 识别编号
    note = models.TextField(default='无备注信息')                                      # 摘要

    class Meta:
        ordering = ['identity']
        verbose_name = "飞行数据日报"

    def __str__(self):
        return self.identity