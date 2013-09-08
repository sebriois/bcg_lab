from xml.etree.ElementTree import Element, SubElement, tostring
import commands
import json
from urllib import urlencode
from urllib2 import Request, urlopen, HTTPError

from django.conf import settings

def send_request( url, args ):
    req = Request( url, urlencode(args) )
    
    try:
        f = urlopen( req )
        return f.read()
    except HTTPError as error:
        print error.code, error.reason
        return False


class Solr(object):
    def __init__(self, url = settings.SOLR_URL + 'collection1/select' ):
        self.url = url
        self.solr_params = {
            'wt': 'python',
            'fl': 'id',
            'rows': settings.PAGINATION_ROWS
        }
    
    def query(self, query_dict):    
        self.solr_params.update( query_dict )
        
        if 'page' in query_dict:
            start = (int(query_dict.get('page', 1)) - 1) * self.solr_params['rows']
            self.solr_params['start'] = start
        
        self._response = eval( send_request(self.url, self.solr_params) )
    
    def response(self):
        return self._response
    
    def docs(self):
        return self._response['response']['docs']
    
    def numFound(self):
        return self._response['response']['numFound']
    
    def suggestions(self):
        if self._response:
            return self._response['spellcheck']['suggestions']
        else:
            return []
    
    def facet_fields(self, field = None):
        if self._response:
            if field:
                return self._response['facet_counts']['facet_fields'][field]
            else:
                return self._response['facet_counts']['facet_fields']
        else:
            return []
        
    def post( self, data_dict = {} ):
        if not data_dict:
            raise "doc to post is empty"
        
        json_doc = json.dumps([ data_dict ])
        
        update_url = settings.SOLR_URL + 'update/'
        command = "curl %s -H 'Content-type:application/json' -d '%s'" % ( update_url, json_doc )
        commands.getoutput(command)
        
        command = "curl %s?commit=true" % update_url
        commands.getoutput(command)
    