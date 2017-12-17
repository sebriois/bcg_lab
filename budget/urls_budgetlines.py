from django.urls import path

from budget.views_budgetlines import index, item, delete, export_to_xls

app_name = 'budget_line'
urlpatterns = [
    path('<int:bl_id>/delete/', delete, name = "delete"),
    path('<int:bl_id>/', item, name = "item"),
    path('export-to-xls/', export_to_xls, name = "export"),
    path('', index, name = "list")
]
