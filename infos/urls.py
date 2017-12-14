from django.urls import path

from infos.views import index, new, delete, item

app_name = "infos"
urlpatterns = [
    path('<int:info_id>/delete', delete, name = "delete"),
    path('<int:info_id>/', item, name = "item"),
    path('add-info/', new, name = "new"),
    path('', index, name = "index")
]
