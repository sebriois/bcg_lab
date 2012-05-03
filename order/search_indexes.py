from haystack import indexes
from order.models import OrderItem

class OrderItemIndex(indexes.SearchIndex, indexes.Indexable):
	text = indexes.CharField(document=True, use_template=True)
	
	def get_model(self):
		return OrderItem
	
	def index_queryset(self):
		return self.get_model().objects.all()

