from django.contrib import admin
from budget.models import Budget, BudgetLine

class BudgetAdmin(admin.ModelAdmin):
  list_display = ('team', 'name', 'budget_type', 'default_origin', 'default_nature', 'tva_code', 'domain', 'is_active')
  list_display_links = ('name',)
admin.site.register(Budget, BudgetAdmin)

class BudgetLineAdmin(admin.ModelAdmin):
  list_display = ('team', 'date', 'budget', 'number', 'budget_type', 'nature', 'product', 'quantity', 'credit', 'debit')
  list_display_links = ('date',)
admin.site.register(BudgetLine, BudgetLineAdmin)