from django.db import models

class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')  # This saves files in `media/uploads/`
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file.name
