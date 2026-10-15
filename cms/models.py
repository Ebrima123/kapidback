from django.core.validators import RegexValidator
from django.db import models
from django.utils.text import slugify


class Orderable(models.Model):
    order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["order", "id"]


class SlugMixin(models.Model):
    slug = models.SlugField(max_length=140, unique=True, blank=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:120] or "item"
            slug, n = base, 2
            while type(self).objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug, n = f"{base}-{n}", n + 1
            self.slug = slug
        super().save(*args, **kwargs)


class SiteSettings(models.Model):
    """Singleton holding editable site-wide copy and contact details."""

    company_name = models.CharField(max_length=120, default="Kapid Painting Company")
    tagline = models.CharField(max_length=200, default="Excellence isn't built in one coat")
    hero_title = models.CharField(
        max_length=200, default="Professional painting for homes, businesses and new builds"
    )
    hero_subtitle = models.TextField(
        default="Interior and exterior painting and decorative finishes across The Gambia. "
        "Tell us about your project and we'll prepare a free, itemised quote."
    )
    hero_image = models.ImageField(upload_to="site/", blank=True)
    about_title = models.CharField(max_length=200, default="About Kapid Painting Company")
    about_body = models.TextField(
        default="Kapid Painting Company is a painting and decorating business in The Gambia. We paint "
        "interiors and exteriors for homeowners, businesses and new-build projects, and offer "
        "decorative finishes for clients who want more than a plain wall.\n\n"
        "Our motto is simple: excellence isn't built in one coat."
    )
    about_image = models.ImageField(upload_to="site/", blank=True)
    phone = models.CharField(max_length=40, blank=True)
    whatsapp_number = models.CharField(
        max_length=30,
        blank=True,
        validators=[
            RegexValidator(
                r"^\+?[\d\s()-]{7,}$",
                "Enter a phone number using digits, spaces, dashes or a leading +.",
            )
        ],
        help_text="Shown as a WhatsApp chat button on the website. Leave blank to hide it.",
    )
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    service_area = models.CharField(max_length=255, blank=True, default="The Gambia")
    opening_hours = models.CharField(max_length=255, blank=True)
    facebook_url = models.URLField(blank=True, default="https://www.facebook.com/kaddijatou.sbah.3")
    instagram_url = models.URLField(blank=True)
    tiktok_url = models.URLField(blank=True, default="https://www.tiktok.com/@kapidpaints")
    # 0 hides the stat on the homepage until real figures are entered.
    years_experience = models.PositiveIntegerField(default=0)
    projects_completed = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "site settings"
        verbose_name_plural = "site settings"

    def __str__(self):
        return "Site settings"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class Service(SlugMixin, Orderable):
    title = models.CharField(max_length=120)
    summary = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=40, blank=True, help_text="Icon name used by the frontend")
    image = models.ImageField(upload_to="services/", blank=True)

    class Meta(Orderable.Meta):
        pass

    def __str__(self):
        return self.title


class Project(SlugMixin, Orderable):
    class Category(models.TextChoices):
        INTERIOR = "interior", "Interior"
        EXTERIOR = "exterior", "Exterior"
        COMMERCIAL = "commercial", "Commercial"
        NEW_BUILD = "new_build", "New build"
        CABINETS = "cabinets", "Cabinets"
        OTHER = "other", "Other"

    title = models.CharField(max_length=140)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.INTERIOR)
    location = models.CharField(max_length=140, blank=True)
    description = models.TextField(blank=True)
    scope_of_work = models.TextField(
        blank=True, help_text="Work carried out on this job, one item per line"
    )
    cover_image = models.ImageField(upload_to="projects/", blank=True)
    completed_on = models.DateField(null=True, blank=True)
    is_featured = models.BooleanField(default=False)

    class Meta(Orderable.Meta):
        pass

    def __str__(self):
        return self.title


class ProjectImage(models.Model):
    project = models.ForeignKey(Project, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="projects/")
    caption = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]


class Testimonial(Orderable):
    name = models.CharField(max_length=120)
    location = models.CharField(max_length=120, blank=True)
    quote = models.TextField()
    rating = models.PositiveSmallIntegerField(default=5)

    class Meta(Orderable.Meta):
        pass

    def __str__(self):
        return f"{self.name}: {self.quote[:40]}"


class FAQ(Orderable):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    class Meta(Orderable.Meta):
        verbose_name = "FAQ"

    def __str__(self):
        return self.question
