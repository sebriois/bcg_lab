from haystack import indexes
from product.models import Product

class ProductIndex(indexes.RealTimeSearchIndex, indexes.Indexable):
	text = indexes.CharField(document=True, use_template=True)
	provider = indexes.CharField(model_attr='provider')
	reference = indexes.CharField(model_attr='reference')
	packaging = indexes.CharField(model_attr='packaging', null = True)
#	offer_nb = indexes.CharField(model_attr='offer_nb', null = True)
	
	def get_model(self):
		return Product
	
	def index_queryset(self):
		return self.get_model().objects.all()

