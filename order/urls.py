from django.urls import path

from order.views import order_detail, orderitem_detail, orderitem_disjoin, order_delete, order_export
from order.views import set_budget
from order.views import add_orderitem, orderitem_delete
from order.views import add_credit, add_debit
from order.views import cart_add, set_item_quantity
from order.views import set_notes, set_number, set_team
from order.views import set_is_urgent, set_has_problem
from order.views import tab_cart, tab_orders, tab_validation

from order.views_ajax import autocomplete_order_number

from order.views_reception import tab_reception, tab_reception_local_provider
from order.views_reception import do_reception

from order.views_order_status import set_next_status

app_name = 'order'
urlpatterns = [
    # Order
    path('<int:order_id>/delete/', order_delete, name="delete"),
    path('<int:order_id>/set-next-status/', set_next_status, name="set_next_status"),
    path('<int:order_id>/set-team/', set_team, name="set_team"),
    path('<int:order_id>/set-budget/', set_budget, name="set_budget"),
    path('<int:order_id>/set-notes/', set_notes, name="set_notes"),
    path('<int:order_id>/set-number/', set_number, name="set_number"),
    path('<int:order_id>/toggle-urgent/', set_is_urgent, name="set_is_urgent"),
    path('<int:order_id>/toggle-problem/', set_has_problem, name="set_has_problem"),
    path('<int:order_id>/view-in-excel/', order_export, name="export_xls"),
    path('<int:order_id>/add-credit/', add_credit, name="add_credit"),
    path('<int:order_id>/add-debit/', add_debit, name="add_debit"),
    path('<int:order_id>/add-item/', add_orderitem, name="add_orderitem"),
    path('<int:order_id>/', order_detail, name="detail"),

    # Order Items
    path('<int:orderitem_id>/del-item/', orderitem_delete, name="item_delete"),
    path('<int:orderitem_id>/disjoin-item/', orderitem_disjoin, name="item_disjoin"),
    path('<int:orderitem_id>/edit/', orderitem_detail, name="item_detail"),
    path('set-item-quantity/', set_item_quantity, name="set_item_quantity"),

    # Cart
    path('add-to-cart/', cart_add, name="cart_add"),

    # Autocomplete
    path('autocomplete/number/', autocomplete_order_number, name="autocomplete_number"),

    # Tabs
    path('validation/', tab_validation, name="tab_validation"),
    path('cart/', tab_cart, name="tab_cart"),
    path('reception-list/', tab_reception, name="tab_reception"),
    path('do-reception/', do_reception, name="do_reception"),
    path('reception-local-provider/', tab_reception_local_provider, name="tab_reception_local_provider"),
    path('', tab_orders, name="tab_orders")
]
