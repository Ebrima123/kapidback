from django.core.management.base import BaseCommand

from cms.models import FAQ, Project, Service, SiteSettings, Testimonial

SERVICES = [
    ("Interior Painting", "brush", "Walls, ceilings, trim and doors with crisp lines and durable finishes."),
    ("Exterior Painting", "home", "Weather-resistant coatings that protect and refresh your home's exterior."),
    ("Commercial Painting", "building", "Offices, shops and rentals painted with minimal disruption to business."),
    ("Cabinet Refinishing", "layers", "Give kitchens a new look without the cost of new cabinets."),
    ("Wallpaper & Decorating", "sparkles", "Wallpaper hanging, removal and feature walls."),
    ("Surface Repair & Prep", "wrench", "Plaster patching, crack filling and sanding for a flawless base."),
]

PROJECTS = [
    ("Modern Living Room Refresh", "interior", "Riverside", True),
    ("Victorian Facade Restoration", "exterior", "Old Town", True),
    ("Open-Plan Office Repaint", "commercial", "Business Park", True),
    ("Shaker Kitchen Cabinets", "cabinets", "Hillview", False),
]

TESTIMONIALS = [
    ("Sarah M.", "Riverside", "Spotless work and they left the house cleaner than they found it."),
    ("James O.", "Old Town", "On time, on budget and the exterior looks brand new. Highly recommended."),
    ("Amina K.", "Hillview", "Our kitchen cabinets look like they came straight from the showroom."),
]

FAQS = [
    ("Do you offer free quotes?", "Yes. Request a quote online and we'll arrange a free visit."),
    ("How long does a typical room take?", "Most rooms are finished in one to two days including prep."),
    ("Do I need to move my furniture?", "We move and cover furniture for you and protect floors."),
    ("Are you insured?", "Yes, we are fully insured and all work is guaranteed."),
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
                name=name, defaults={"location": loc, "quote": quote, "order": i}
            )
        for i, (q, a) in enumerate(FAQS):
            FAQ.objects.get_or_create(question=q, defaults={"answer": a, "order": i})
        self.stdout.write(self.style.SUCCESS("Demo content loaded."))
