import io
from unittest import mock

import cloudinary
from django.core.files.base import ContentFile
from django.core.files.storage import storages
from django.test import TestCase, override_settings
from PIL import Image

from cms.models import Project, ProjectImage
from config.storage import CloudinaryMediaStorage

CLOUDINARY_STORAGES = {
    "default": {"BACKEND": "config.storage.CloudinaryMediaStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


def png_bytes():
    buf = io.BytesIO()
    Image.new("RGB", (8, 8), "#b8501f").save(buf, "PNG")
    return buf.getvalue()


def fake_upload(file, public_id, **kwargs):
    """Mimic Cloudinary's response: it echoes the public_id and reports the format."""
    return {"public_id": public_id, "format": "png", "secure_url": f"https://res.cloudinary.com/test/{public_id}.png"}


@override_settings(STORAGES=CLOUDINARY_STORAGES)
class CloudinaryMediaStorageTests(TestCase):
    """Uploads are stubbed, so these run offline without real credentials."""

    def setUp(self):
        cloudinary.config(cloud_name="kapid-test", api_key="k", api_secret="s", secure=True)
        storages._storages = {}  # pick up the overridden STORAGES

    def test_save_keeps_folder_and_extension_and_makes_names_unique(self):
        storage = CloudinaryMediaStorage(folder="kapid")
        with mock.patch("cloudinary.uploader.upload", side_effect=fake_upload) as upload:
            first = storage.save("projects/kitchen.png", ContentFile(png_bytes()))
            second = storage.save("projects/kitchen.png", ContentFile(png_bytes()))

        self.assertRegex(first, r"^projects/kitchen_[0-9a-f]{8}\.png$")
        self.assertNotEqual(first, second)
        self.assertTrue(upload.call_args.kwargs["public_id"].startswith("kapid/projects/kitchen_"))
        self.assertEqual(upload.call_args.kwargs["resource_type"], "image")

    def test_url_is_a_secure_cloudinary_delivery_url(self):
        url = CloudinaryMediaStorage(folder="kapid").url("projects/kitchen_abcd1234.png")
        # The SDK adds a /v1/ version segment for public IDs inside folders.
        self.assertRegex(url, r"^https://res\.cloudinary\.com/kapid-test/image/upload/(v\d+/)?kapid/projects/kitchen_abcd1234\.png$")

    def test_delete_destroys_the_cloudinary_asset(self):
        with mock.patch("cloudinary.uploader.destroy") as destroy:
            CloudinaryMediaStorage(folder="kapid").delete("site/hero_abcd1234.jpg")
        destroy.assert_called_once_with("kapid/site/hero_abcd1234", resource_type="image", invalidate=True)

    def test_model_image_fields_upload_through_cloudinary(self):
        project = Project.objects.create(title="Storage test", category="interior")
        with mock.patch("cloudinary.uploader.upload", side_effect=fake_upload):
            project.cover_image.save("cover.png", ContentFile(png_bytes()), save=True)
            photo = ProjectImage.objects.create(project=project, image=ContentFile(png_bytes(), name="room.png"))

        project.refresh_from_db()
        self.assertRegex(project.cover_image.name, r"^projects/cover_[0-9a-f]{8}\.png$")
        self.assertRegex(project.cover_image.url, r"^https://res\.cloudinary\.com/kapid-test/image/upload/(v\d+/)?kapid/projects/cover_")
        self.assertRegex(photo.image.name, r"^projects/room_[0-9a-f]{8}\.png$")
