from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("cms/services", views.ServiceViewSet)
router.register("cms/projects", views.ProjectViewSet)
router.register("cms/project-images", views.ProjectImageViewSet)
router.register("cms/testimonials", views.TestimonialViewSet)
router.register("cms/faqs", views.FAQViewSet)

urlpatterns = [
    path("public/settings/", views.PublicSettingsView.as_view()),
    path("public/services/", views.PublicServiceList.as_view()),
    path("public/services/<slug:slug>/", views.PublicServiceDetail.as_view()),
    path("public/projects/", views.PublicProjectList.as_view()),
    path("public/projects/<slug:slug>/", views.PublicProjectDetail.as_view()),
    path("public/testimonials/", views.PublicTestimonialList.as_view()),
    path("public/faqs/", views.PublicFAQList.as_view()),
    path("cms/settings/", views.SettingsAdminView.as_view()),
    path("", include(router.urls)),
]
