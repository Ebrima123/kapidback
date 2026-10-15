from django.contrib import admin

from .models import Customer, Estimate, EstimateItem, Job, Lead, Note


class EstimateItemInline(admin.TabularInline):
    model = EstimateItem
    extra = 1


@admin.register(Estimate)
class EstimateAdmin(admin.ModelAdmin):
    list_display = ["number", "customer", "status", "issue_date"]
    inlines = [EstimateItemInline]


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ["name", "email", "service", "status", "created_at"]
    list_filter = ["status", "source"]


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ["title", "customer", "status", "start_date", "price"]
    list_filter = ["status"]


admin.site.register([Customer, Note])
