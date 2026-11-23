"""URL configuration for Hotel Booking project."""

from django.contrib import admin
from django.urls import include, path, re_path
from apps.core.views import spa_host_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.core.urls")),
    path("api/auth/", include("apps.accounts.urls")),
    path("api/", include("apps.hotels.urls")),
    path("api/", include("apps.bookings.urls")),
    path("api/", include("apps.reviews.urls")),
    re_path(r"^(?!api/|admin/|static/|media/).*$", spa_host_view, name="spa-host"),
]

handler400 = "apps.core.views.bad_request_view"
handler403 = "apps.core.views.permission_denied_view"
handler404 = "apps.core.views.page_not_found_view"
handler500 = "apps.core.views.server_error_view"
