from django.contrib import admin
from product.models import Product, ProductType, ProductSubType

class ProductTypeAdmin(admin.ModelAdmin):
	list_display = ("name",)
admin.site.register(ProductType, ProductTypeAdmin)

class ProductSubTypeAdmin(admin.ModelAdmin):
	list_display = ("name","category")
admin.site.register(ProductSubType, ProductSubTypeAdmin)

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
admin.site.register(Product, ProductAdmin)