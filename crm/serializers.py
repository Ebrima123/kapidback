from django.db import transaction
from rest_framework import serializers

from .models import Customer, Estimate, EstimateItem, Job, Lead, Note


class NoteSerializer(serializers.ModelSerializer):
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = ["id", "customer", "lead", "job", "body", "author", "author_name", "created_at"]
        read_only_fields = ["author", "created_at"]

    def get_author_name(self, obj):
        if not obj.author:
            return ""
        return obj.author.get_full_name() or obj.author.get_username()

    def validate(self, attrs):
        if not any(attrs.get(k) for k in ("customer", "lead", "job")) and not self.instance:
            raise serializers.ValidationError("A note must belong to a customer, lead or job.")
        return attrs


class CustomerSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(read_only=True)
    job_count = serializers.IntegerField(read_only=True, required=False)

    class Meta:
        model = Customer
        fields = "__all__"


class LeadSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.full_name", read_only=True, default="")

    class Meta:
        model = Lead
        fields = "__all__"


class PublicQuoteRequestSerializer(serializers.ModelSerializer):
    """Fields a website visitor may submit; everything else is staff-only."""

    # Honeypot: real visitors never fill this hidden field.
    website = serializers.CharField(required=False, allow_blank=True, write_only=True)

    class Meta:
        model = Lead
        fields = [
            "name",
            "email",
            "phone",
            "address",
            "service",
            "property_type",
            "message",
            "preferred_date",
            "website",
        ]

    def validate_website(self, value):
        if value:
            raise serializers.ValidationError("Invalid submission.")
        return value

    def create(self, validated_data):
        validated_data.pop("website", None)
        return Lead.objects.create(source="website", **validated_data)


class JobSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)

    class Meta:
        model = Job
        fields = "__all__"


class EstimateItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)
    line_total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = EstimateItem
        fields = ["id", "description", "quantity", "unit_price", "order", "line_total"]


class EstimateSerializer(serializers.ModelSerializer):
    items = EstimateItemSerializer(many=True, required=False)
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    tax = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    customer_name = serializers.CharField(source="customer.full_name", read_only=True, default="")
    lead_name = serializers.CharField(source="lead.name", read_only=True, default="")

    class Meta:
        model = Estimate
        fields = "__all__"
        read_only_fields = ["number"]

    @transaction.atomic
    def create(self, validated_data):
        items = validated_data.pop("items", [])
        estimate = Estimate.objects.create(**validated_data)
        self._save_items(estimate, items)
        return estimate

    @transaction.atomic
    def update(self, instance, validated_data):
        items = validated_data.pop("items", None)
        instance = super().update(instance, validated_data)
        if items is not None:
            self._save_items(instance, items)
        return instance

    def _save_items(self, estimate, items):
        # Replace the full item list: simplest consistent semantics for an editor UI.
        estimate.items.all().delete()
        EstimateItem.objects.bulk_create(
            EstimateItem(
                estimate=estimate,
                description=item["description"],
                quantity=item.get("quantity", 1),
                unit_price=item.get("unit_price", 0),
                order=item.get("order", idx),
            )
            for idx, item in enumerate(items)
        )
