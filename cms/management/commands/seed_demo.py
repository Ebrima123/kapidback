from django.core.management.base import BaseCommand

from cms.models import FAQ, Service, SiteSettings

# Only services the business has shown it offers (interiors, exteriors and new
# builds, commercial work, decorative finishes). Add more from /admin/content/services.
SERVICES = [
    ("Interior Painting", "brush", "Walls, ceilings, trim and doors with crisp lines and durable finishes."),
    ("Exterior & New Builds", "home", "Exterior painting for homes and finishing work on new buildings."),
    ("Commercial Painting", "building", "Painting for offices, shops and other business premises."),
    ("Decorative Finishes", "sparkles", "Feature walls, textures and accent colours for a distinctive look."),
]

FAQS = [
    ("Do you offer free quotes?", "Yes. Send us the details through the quote form and we'll get back to you with a free quote."),
    ("Do you paint new buildings?", "Yes. We handle interior and exterior finishing on new builds."),
]

# No projects or testimonials are seeded: those must be real jobs and real
# customer words, added in /admin/content/projects and /admin/content/testimonials.


class Command(BaseCommand):
    help = "Load starter website content (safe to run more than once)."

    def handle(self, *args, **options):
        SiteSettings.load()
        for i, (title, icon, summary) in enumerate(SERVICES):
            Service.objects.get_or_create(
                title=title, defaults={"icon": icon, "summary": summary, "order": i}
            )
        for i, (q, a) in enumerate(FAQS):
            FAQ.objects.get_or_create(question=q, defaults={"answer": a, "order": i})
        self.stdout.write(self.style.SUCCESS("Starter content loaded."))
