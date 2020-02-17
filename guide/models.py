from django.db import models

class GuideCategory(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name='类别名称')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '指南分类'
        verbose_name_plural = '指南分类'

class Guide(models.Model):
    name = models.CharField(max_length=255, verbose_name='服务指南名称')
    category = models.ForeignKey(GuideCategory, on_delete=models.CASCADE, verbose_name='类别')
    file = models.FileField(upload_to='guides', verbose_name='指南文件')
    created = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        ordering = ('-created', '-id')
        verbose_name = '指南文件'
        verbose_name_plural = '指南文件'