from django.db import models

class GuideCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Guide(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(GuideCategory, on_delete=models.CASCADE)
    file = models.FileField(upload_to='guides')
    created = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ('-created', '-id')