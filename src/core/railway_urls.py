"""URLconf for plain Janeway on Railway (no nginx in front).

Stock core.urls plus a /media/ file route. Upstream only serves
MEDIA_ROOT when DEBUG is on because production installs are expected
to serve it from nginx; here gunicorn is the only server, so Django
serves it (low traffic journal site - acceptable).
"""
from django.conf import settings
from django.urls import include, path, re_path
from django.views.static import serve

urlpatterns = [
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    path("", include("core.urls")),
]
