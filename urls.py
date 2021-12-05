import views
from henango.urls.pattern import URLPattern

url_patterns = {
    URLPattern("/now", views.now),
    URLPattern("/show_request", views.show_request),
    URLPattern("/parameters", views.parameters),
    URLPattern("/user/<user_id>/profile", views.user_profile)
}
