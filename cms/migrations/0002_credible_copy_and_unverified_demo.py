"""
Replace the original placeholder copy with clearer, verifiable wording and
unpublish seeded demo content that was never confirmed by the business.

Each change only applies while the value still equals what was seeded, so
anything already edited in the dashboard is left alone. Unpublished rows are
kept, not deleted, and can be re-published from /admin.
"""

from django.db import migrations

OLD_ABOUT_BODY = (
    "Kapid Painting Company is a Gambian painting and decorating team. From fresh "
    "interiors to the exterior finish on new multi-storey buildings, our crews bring careful "
    "prep, clean lines and the latest decorative styles to every job.\n\n"
    "Excellence isn't built in one coat, so we take the time to do it properly."
)

NEW_HERO_TITLE = "Professional painting for homes, businesses and new builds"
NEW_HERO_SUBTITLE = (
    "Interior and exterior painting and decorative finishes across The Gambia. "
    "Tell us about your project and we'll prepare a free, itemised quote."
)
NEW_ABOUT_TITLE = "About Kapid Painting Company"
NEW_ABOUT_BODY = (
    "Kapid Painting Company is a painting and decorating business in The Gambia. We paint "
    "interiors and exteriors for homeowners, businesses and new-build projects, and offer "
    "decorative finishes for clients who want more than a plain wall.\n\n"
    "Our motto is simple: excellence isn't built in one coat."
)

SETTINGS_UPDATES = {
    "hero_title": ("For all the latest decorations.", NEW_HERO_TITLE),
    "hero_subtitle": (
        "Painting and decorating for homes, new builds and businesses across The Gambia, inside and out.",
        NEW_HERO_SUBTITLE,
    ),
    "about_title": ("Kapid Company, the only solution", NEW_ABOUT_TITLE),
    "about_body": (OLD_ABOUT_BODY, NEW_ABOUT_BODY),
}

SEEDED_PROJECTS = [
    "New Build Exterior Finish",
    "Modern Living Room Refresh",
    "Office Repaint",
    "Decorative Feature Wall",
]

UNVERIFIED_FAQS = [
    ("How long does a typical room take?", "Most rooms are finished in one to two days including prep."),
    ("Do I need to move my furniture?", "We move and cover furniture for you and protect floors."),
]

FREE_QUOTE_FAQ = (
    "Do you offer free quotes?",
    "Yes. Request a quote online and we'll arrange a free visit.",
    "Yes. Send us the details through the quote form and we'll get back to you with a free quote.",
)

UNVERIFIED_SERVICES = ["Surface Repair & Prep", "Cabinet & Door Refinishing"]


def forwards(apps, schema_editor):
    SiteSettings = apps.get_model("cms", "SiteSettings")
    Project = apps.get_model("cms", "Project")
    FAQ = apps.get_model("cms", "FAQ")
    Service = apps.get_model("cms", "Service")

    s = SiteSettings.objects.filter(pk=1).first()
    if s:
        changed = []
        for field, (old, new) in SETTINGS_UPDATES.items():
            if getattr(s, field) == old:
                setattr(s, field, new)
                changed.append(field)
        if changed:
            s.save(update_fields=changed)

    # Placeholder portfolio entries with no photo or description are not real jobs.
    Project.objects.filter(title__in=SEEDED_PROJECTS, cover_image="", description="").update(is_published=False)

    for question, answer in UNVERIFIED_FAQS:
        FAQ.objects.filter(question=question, answer=answer).update(is_published=False)
    q, old, new = FREE_QUOTE_FAQ
    FAQ.objects.filter(question=q, answer=old).update(answer=new)

    Service.objects.filter(title__in=UNVERIFIED_SERVICES, description="", image="").update(is_published=False)


class Migration(migrations.Migration):
    dependencies = [("cms", "0001_initial")]

    operations = [migrations.RunPython(forwards, migrations.RunPython.noop)]
