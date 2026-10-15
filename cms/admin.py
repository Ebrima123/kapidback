from django.contrib import admin

from .models import FAQ, Project, ProjectImage, Service, SiteSettings, Testimonial


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["title", "category", "is_featured", "is_published", "order"]
    inlines = [ProjectImageInline]


admin.site.register([SiteSettings, Service, Testimonial, FAQ])
