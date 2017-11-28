from django.core.management import BaseCommand
from django.conf import settings
from elasticsearch import Elasticsearch, helpers

from product.models import Product


class Command(BaseCommand):
    can_import_settings = True
    help = 'reindex %s products into ElasticSearch' % settings.SITE_NAME

    mappings = {
        "products": {
            "properties": {
                "provider": {"type": "string"},
                "origin":   {"type": "string"},
                "name":     {"type": "string"},
                "reference": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "offer_nb": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "nomenclature": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "category": {
                    "type": "string",
                    "index": "not_analyzed"
                },
                "suggest":  {
                    "type": "completion",
                    "payloads": True
                }
            }
        }
    }

    def handle(self, *args, **options):
        verbose = options.get('verbosity', 0)

        self.index_name = settings.SITE_NAME.lower()

        self.es = Elasticsearch()
        self.delete_index()
        self.create_index()
        self.put_mappings()
        self.before_indexing()
        print(helpers.bulk(
            client = self.es,
            actions = self.iter_products_to_index(),
            stats_only = True
        ))
        self.after_indexing()

    def delete_index(self):
        print("[%s] Deleting index" % self.index_name)
        print(self.es.indices.delete(index = self.index_name, ignore = [400, 404]))

    def create_index(self):
        # ignore 400 cause by IndexAlreadyExistsException when creating an index
        print("[%s] Creating index" % self.index_name)
        print(self.es.indices.create(index = self.index_name, ignore = 400))

    def put_mappings(self):
        print("[%s] PUT mapping" % self.index_name)
        print(self.es.indices.put_mapping(
            "products",
            self.mappings,
            index = self.index_name,
        ))

    def iter_products_to_index(self):
        print("[%s] Indexing %s products" % (self.index_name, Product.objects.all().count()))

        for product in Product.objects.all():
            product_doc = {
                "provider": product.provider.name,
                "name": product.name,
                "suggest": {
                    "output": "%s - %s" % (product.provider.name, product.name),
                    "payload": {"product_id": product.id},
                }
            }
            if product.origin:
                product_doc['origin'] = product.origin
            if product.reference:
                product_doc['reference'] = product.reference
            if product.offer_nb:
                product_doc['offer_nb'] = product.offer_nb
            if product.nomenclature:
                product_doc['nomenclature'] = product.nomenclature
            if product.category:
                product_doc['category'] = product.category.name

            yield {
                '_index': self.index_name,
                '_type': 'products',
                '_id': product.id,
                '_source': product_doc
            }

    def before_indexing(self):
        self.es.indices.put_settings(
            {
                "index": {
                    "refresh_interval": "-1",
                    "number_of_replicas": 0
                }
            },
            index = self.index_name
        )

    def after_indexing(self):
        self.es.indices.put_settings(
            {
                "index": {
                    "refresh_interval": "1s",
                    "number_of_replicas": 0
                }
            },
            index = self.index_name
        )

