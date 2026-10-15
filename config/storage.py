"""
Cloudinary storage for uploaded media (CMS images).

Render's disk is wiped on every deploy, so uploads must live elsewhere. This is a
small Django Storage backend on the official Cloudinary SDK; it is enabled in
settings only when the CLOUDINARY_* environment variables are present, otherwise
uploads fall back to the local MEDIA_ROOT (handy for development).

Stored names keep Django's upload_to folders and the file extension, e.g.
"projects/kitchen_3f9a1c2b.jpg"; the Cloudinary public_id is the same path without
the extension, under CLOUDINARY_FOLDER.
"""

import os
import uuid

import cloudinary
import cloudinary.uploader
import cloudinary.utils
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class CloudinaryMediaStorage(Storage):
    def __init__(self, folder=None):
        self.folder = (folder or os.getenv("CLOUDINARY_FOLDER") or "kapid").strip("/")

    def _public_id(self, name):
        stem, _ext = os.path.splitext(name.replace("\\", "/"))
        return f"{self.folder}/{stem}"

    def _save(self, name, content):
        stem, ext = os.path.splitext(name.replace("\\", "/"))
        # A short random suffix keeps names unique without an extra "exists" API call.
        unique = f"{stem}_{uuid.uuid4().hex[:8]}"
        if hasattr(content, "seek"):
            content.seek(0)
        result = cloudinary.uploader.upload(
            content,
            public_id=self._public_id(unique),
            resource_type="image",
            overwrite=False,
        )
        fmt = result.get("format") or ext.lstrip(".") or "jpg"
        return f"{unique}.{fmt}"

    def url(self, name):
        if not name:
            return ""
        _stem, ext = os.path.splitext(name)
        url, _options = cloudinary.utils.cloudinary_url(
            self._public_id(name),
            resource_type="image",
            format=ext.lstrip(".") or None,
            secure=True,
        )
        return url

    def exists(self, name):
        # Names are made unique in _save, so there is never a clash to avoid.
        return False

    def delete(self, name):
        if name:
            cloudinary.uploader.destroy(self._public_id(name), resource_type="image", invalidate=True)

    def size(self, name):
        return 0

    def path(self, name):
        raise NotImplementedError("Cloudinary files have no local path.")
