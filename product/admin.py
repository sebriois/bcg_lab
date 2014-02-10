from django.contrib import admin
from product.models import Product
from product.models import ProductCode
from product.models import ProductType
from product.models import ProductSubType


class ProductAdmin(admin.ModelAdmin):
  date_hierarchy = 'last_change'
  list_display = ('provider', 'name', 'packaging', 'reference', 'price', 'offer_nb', 'nomenclature')
  list_display_links = ('name',)
  list_filter = ('provider',)
  
  search_fields = ('name',)
  
  fieldsets = (
    ( None, {
      'fields' : ('provider', 'name', 'reference', 'price')
    }),
    ( 'Options', {
      'fields': ( 'packaging', 'offer_nb', 'nomenclature' )
    })
  )

class ProductCodeAdmin(admin.ModelAdmin):
    list_display  = ('code', 'title')
    list_display_links  = ('code',)
    search_fields = ('code','title')

admin.site.register(Product, ProductAdmin)
admin.site.register(ProductCode, ProductCodeAdmin)
admin.site.register(ProductType)
admin.site.register(ProductSubType)
