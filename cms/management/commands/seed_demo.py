from django.core.management.base import BaseCommand

from cms.models import FAQ, Project, Service, SiteSettings, Testimonial

SERVICES = [
    ("Interior Painting", "brush", "Walls, ceilings, trim and doors with crisp lines and durable finishes."),
    ("Exterior & New Builds", "home", "Weather-resistant finishes for homes and new multi-storey buildings."),
    ("Commercial Painting", "building", "Offices, shops and compounds painted with minimal disruption."),
    ("Decorative Finishes", "sparkles", "The latest decorative styles: feature walls, textures and accent colours."),
    ("Surface Repair & Prep", "wrench", "Plaster patching, crack filling and sanding for a flawless base."),
    ("Cabinet & Door Refinishing", "layers", "Give kitchens and doors a new look without replacing them."),
]

# Placeholder portfolio entries; replace with real jobs and photos in /admin/content/projects.
PROJECTS = [
    ("New Build Exterior Finish", "exterior", "", True),
    ("Modern Living Room Refresh", "interior", "", True),
    ("Office Repaint", "commercial", "", True),
    ("Decorative Feature Wall", "other", "", False),
]

# Sample reviews for layout only: seeded hidden so invented quotes never go live.
TESTIMONIALS = [
    ("Sarah M.", "", "Spotless work and they left the house cleaner than they found it."),
    ("James O.", "", "On time, on budget and the exterior looks brand new. Highly recommended."),
    ("Amina K.", "", "Our kitchen cabinets look like they came straight from the showroom."),
]

FAQS = [
    ("Do you offer free quotes?", "Yes. Request a quote online and we'll arrange a free visit."),
    ("How long does a typical room take?", "Most rooms are finished in one to two days including prep."),
    ("Do I need to move my furniture?", "We move and cover furniture for you and protect floors."),
    ("Do you paint new buildings?", "Yes. We handle interior and exterior finishing on new builds of every size."),
]


class Command(BaseCommand):
    help = "Load demo website content (safe to run more than once)."

    def handle(self, *args, **options):
        SiteSettings.load()
        for i, (title, icon, summary) in enumerate(SERVICES):
            Service.objects.get_or_create(
                title=title, defaults={"icon": icon, "summary": summary, "order": i}
            )
        for i, (title, cat, loc, featured) in enumerate(PROJECTS):
            Project.objects.get_or_create(
                title=title,
                defaults={"category": cat, "location": loc, "is_featured": featured, "order": i},
            )
        for i, (name, loc, quote) in enumerate(TESTIMONIALS):
            Testimonial.objects.get_or_create(
                name=name, defaults={"location": loc, "quote": quote, "order": i, "is_published": False}
            )
        for i, (q, a) in enumerate(FAQS):
            FAQ.objects.get_or_create(question=q, defaults={"answer": a, "order": i})
        self.stdout.write(self.style.SUCCESS("Demo content loaded."))
