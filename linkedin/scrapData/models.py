from django.db import models


# Create your models here.
class Companies(models.Model):
    name = models.CharField(max_length=255, default="NA")
    tagline = models.CharField(max_length=255, default="NA")
    industry = models.CharField(max_length=255, default="NA")
    location = models.CharField(max_length=255, default="NA")
    followers = models.CharField(max_length=255, default="NA")
    employees = models.CharField(max_length=255, default="NA")
    linkedin_url = models.CharField(max_length=255, unique=True)
    domain = models.CharField(max_length=255, default="NA")
    data_scrapped = models.CharField(max_length=50, default="No")

    class Meta:
        verbose_name_plural = "Companies Data"

    def __str__(self):
        return "{}".format(self.name)


class UsersData(models.Model):
    company = models.ForeignKey(Companies, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, default="NA")
    title = models.CharField(max_length=255, default="NA")
    location = models.CharField(max_length=255, default="NA")
    linkedin_url = models.CharField(max_length=255, unique=True)
    valid_emails = models.TextField(default="NA")
    exported = models.CharField(max_length=255, default="NA")

    class Meta:
        verbose_name_plural = "Users Data"

    def __str__(self):
        return "{}".format(self.name)
