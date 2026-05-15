from django.db import models

# Create your models here.
class Job(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class Candidate(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='candidates')
    name = models.CharField(max_length=200)
    emal = models.EmailField()
    resume_text = models.TextField(blank=True)
    summary = models.TextField(blank=True)
    score = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.job.title}"