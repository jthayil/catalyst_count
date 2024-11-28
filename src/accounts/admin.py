from django.contrib import admin
from accounts.models import Company


class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "domain",
        "year_founded",
        "industry",
        "size_range",
        "city",
        "state",
        "country",
        "linkedin_url",
        "current_employee_estimate",
        "total_employee_estimate",
    )
    list_filter = ["year_founded", "country", "city","state",]
    search_fields = ["name"]


admin.site.register(Company, CompanyAdmin)
