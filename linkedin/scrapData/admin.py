from django.contrib import admin
from .models import Companies, UsersData


# Register your models here.
class CompaniesAdmin(admin.ModelAdmin):
    model = Companies

    list_display = ('name', 'industry', 'location', 'employees', 'data_scrapped', 'keyword')

    list_filter = ('data_scrapped', "keyword")


class UsersDataAdmin(admin.ModelAdmin):
    model = UsersData

    list_display = ('company', 'name', 'title', 'location', 'valid_emails', 'keyword', 'exported')

    list_filter = ('keyword', "exported")


admin.site.register(Companies, CompaniesAdmin)
admin.site.register(UsersData, UsersDataAdmin)
