from rest_framework import generics, permissions, viewsets
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from .models import FAQ, Project, ProjectImage, Service, SiteSettings, Testimonial
from .serializers import (
    FAQSerializer,
    ProjectImageSerializer,
    ProjectSerializer,
    ServiceSerializer,
    SiteSettingsSerializer,
    TestimonialSerializer,
)

PARSERS = [JSONParser, MultiPartParser, FormParser]


# ---- Public, read-only content for the website ----


class PublicMixin:
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    pagination_class = None


class PublicSettingsView(PublicMixin, generics.RetrieveAPIView):
    serializer_class = SiteSettingsSerializer

    def get_object(self):
        return SiteSettings.load()


class PublicServiceList(PublicMixin, generics.ListAPIView):
    queryset = Service.objects.filter(is_published=True)
    serializer_class = ServiceSerializer


class PublicServiceDetail(PublicMixin, generics.RetrieveAPIView):
    queryset = Service.objects.filter(is_published=True)
    serializer_class = ServiceSerializer
    lookup_field = "slug"


class PublicProjectList(PublicMixin, generics.ListAPIView):
    queryset = Project.objects.filter(is_published=True).prefetch_related("images")
    serializer_class = ProjectSerializer
    filterset_fields = ["category", "is_featured"]


class PublicProjectDetail(PublicMixin, generics.RetrieveAPIView):
    queryset = Project.objects.filter(is_published=True).prefetch_related("images")
    serializer_class = ProjectSerializer
    lookup_field = "slug"


class PublicTestimonialList(PublicMixin, generics.ListAPIView):
    queryset = Testimonial.objects.filter(is_published=True)
    serializer_class = TestimonialSerializer


class PublicFAQList(PublicMixin, generics.ListAPIView):
    queryset = FAQ.objects.filter(is_published=True)
    serializer_class = FAQSerializer


# ---- Staff CMS management ----


class SettingsAdminView(generics.RetrieveUpdateAPIView):
    serializer_class = SiteSettingsSerializer
    parser_classes = PARSERS

    def get_object(self):
        return SiteSettings.load()


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer
    parser_classes = PARSERS
    search_fields = ["title", "summary"]


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all().prefetch_related("images")
    serializer_class = ProjectSerializer
    parser_classes = PARSERS
    filterset_fields = ["category", "is_featured", "is_published"]
    search_fields = ["title", "location"]


class ProjectImageViewSet(viewsets.ModelViewSet):
    queryset = ProjectImage.objects.all()
    serializer_class = ProjectImageSerializer
    parser_classes = PARSERS
    filterset_fields = ["project"]


class TestimonialViewSet(viewsets.ModelViewSet):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer
    search_fields = ["name", "quote"]


class FAQViewSet(viewsets.ModelViewSet):
    queryset = FAQ.objects.all()
    serializer_class = FAQSerializer
    search_fields = ["question"]
