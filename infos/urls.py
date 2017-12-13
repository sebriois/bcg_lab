from django.urls import path

from infos.views import index, new, delete, item

urlpatterns = [
	path('<int:info_id>/delete$', delete, name="info_delete"),
	path('<int:info_id>/$', item, name="info_item"),
    path('add-info/$', new, name="info_new"),
    path('$', index, name="info_index")
]