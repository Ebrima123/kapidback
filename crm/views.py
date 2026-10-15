from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.utils import timezone
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import Customer, Estimate, Job, Lead, Note
from .serializers import (
    CustomerSerializer,
    EstimateSerializer,
    JobSerializer,
    LeadSerializer,
    NoteSerializer,
    PublicQuoteRequestSerializer,
)


class MeView(APIView):
    def get(self, request):
        u = request.user
        return Response(
            {
                "id": u.id,
                "username": u.get_username(),
                "email": u.email,
                "name": u.get_full_name() or u.get_username(),
            }
        )


class PublicQuoteRequestView(generics.CreateAPIView):
    serializer_class = PublicQuoteRequestSerializer
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "quote"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"ok": True}, status=status.HTTP_201_CREATED)


class CustomerViewSet(viewsets.ModelViewSet):
    serializer_class = CustomerSerializer
    filterset_fields = ["source", "city"]
    search_fields = ["first_name", "last_name", "company", "email", "phone"]
    ordering_fields = ["created_at", "last_name"]

    def get_queryset(self):
        return Customer.objects.annotate(job_count=Count("jobs"))


class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.select_related("customer")
    serializer_class = LeadSerializer
    filterset_fields = ["status", "source", "property_type", "customer"]
    search_fields = ["name", "email", "phone", "service", "message"]
    ordering_fields = ["created_at", "status"]

    @action(detail=True, methods=["post"])
    def convert(self, request, pk=None):
        """Create (or reuse by email) a customer for this lead and link it."""
        lead = self.get_object()
        if lead.customer_id:
            return Response(CustomerSerializer(lead.customer).data)
        customer = None
        if lead.email:
            customer = Customer.objects.filter(email__iexact=lead.email).first()
        if customer is None:
            first, _, last = lead.name.partition(" ")
            customer = Customer.objects.create(
                first_name=first or lead.name,
                last_name=last,
                email=lead.email,
                phone=lead.phone,
                address=lead.address,
                source=lead.source,
            )
        lead.customer = customer
        if lead.status == Lead.Status.NEW:
            lead.status = Lead.Status.CONTACTED
        lead.save(update_fields=["customer", "status", "updated_at"])
        return Response(CustomerSerializer(customer).data, status=status.HTTP_201_CREATED)


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.select_related("customer")
    serializer_class = JobSerializer
    filterset_fields = ["status", "customer", "lead"]
    search_fields = ["title", "address", "assigned_to", "customer__first_name", "customer__last_name"]
    ordering_fields = ["start_date", "created_at", "price"]


class EstimateViewSet(viewsets.ModelViewSet):
    queryset = Estimate.objects.select_related("customer", "lead").prefetch_related("items")
    serializer_class = EstimateSerializer
    filterset_fields = ["status", "customer", "lead", "job"]
    search_fields = ["number", "title", "customer__first_name", "customer__last_name", "lead__name"]
    ordering_fields = ["created_at", "issue_date"]


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.select_related("author")
    serializer_class = NoteSerializer
    filterset_fields = ["customer", "lead", "job"]
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class DashboardView(APIView):
    def get(self, request):
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        lead_counts = dict(Lead.objects.order_by().values_list("status").annotate(c=Count("id")))
        job_counts = dict(Job.objects.order_by().values_list("status").annotate(c=Count("id")))
        revenue = Job.objects.filter(
            status=Job.Status.COMPLETED, end_date__gte=month_start.date()
        ).aggregate(s=Sum("price"))["s"] or Decimal("0")
        pipeline = Job.objects.filter(
            status__in=[Job.Status.SCHEDULED, Job.Status.IN_PROGRESS]
        ).aggregate(s=Sum("price"))["s"] or Decimal("0")
        decided = Lead.objects.filter(status__in=[Lead.Status.WON, Lead.Status.LOST])
        won = decided.filter(status=Lead.Status.WON).count()
        upcoming = Job.objects.select_related("customer").filter(
            Q(status=Job.Status.SCHEDULED) | Q(status=Job.Status.IN_PROGRESS),
            start_date__lte=(now + timedelta(days=14)).date(),
        ).order_by("start_date")[:6]

        return Response(
            {
                "leads_by_status": {s: lead_counts.get(s, 0) for s in Lead.Status.values},
                "jobs_by_status": {s: job_counts.get(s, 0) for s in Job.Status.values},
                "new_leads_this_month": Lead.objects.filter(created_at__gte=month_start).count(),
                "customers": Customer.objects.count(),
                "revenue_this_month": str(revenue),
                "open_job_value": str(pipeline),
                "win_rate": round(won / decided.count() * 100) if decided.exists() else None,
                "recent_leads": LeadSerializer(Lead.objects.all()[:6], many=True).data,
                "upcoming_jobs": JobSerializer(upcoming, many=True).data,
            }
        )
