from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("crm/customers", views.CustomerViewSet, basename="customer")
router.register("crm/leads", views.LeadViewSet)
router.register("crm/jobs", views.JobViewSet)
router.register("crm/estimates", views.EstimateViewSet)
router.register("crm/notes", views.NoteViewSet)

urlpatterns = [
    path("public/quote-request/", views.PublicQuoteRequestView.as_view()),
    path("crm/dashboard/", views.DashboardView.as_view()),
    path("", include(router.urls)),
]
