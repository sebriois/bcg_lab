# -*- coding : utf8 -*-
from xml.etree.ElementTree import Element, SubElement, tostring
import commands
import json

from urllib2 import Request, urlopen, HTTPError

from django.conf import settings
from django.utils.http import urlencode

def send_request( url, args ):
    req = Request( url, urlencode(args) )
    
    try:
        f = urlopen( req )
        return f.read()
    except HTTPError as error:
        print error.code, error.reason
        return False


class Solr(object):
    def __init__(self, url = settings.SOLR_URL + '/select' ):
        self.url = url
        self.solr_params = {
            'wt': 'json',
            'fl': 'id',
            'rows': settings.PAGINATION_ROWS
        }
    
    def query(self, query_dict):    
        self.solr_params.update( query_dict )
        
        if 'page' in query_dict:
            start = (int(query_dict.get('page', 1)) - 1) * self.solr_params['rows']
            self.solr_params['start'] = start
        
        json_response = send_request(self.url, self.solr_params)
        self._response = json.loads( json_response )
    
    def response(self, field = None):
        if not field:
            return self._response
        
        return self._response[field]
    
    def docs(self):
        return self._response['response']['docs']
    
    def numFound(self):
        return self._response['response']['numFound']
    
    def suggestion(self):
        suggestion = None
        if self._response and 'spellcheck' in self._response:
            spellcheck = self._response['spellcheck']['suggestions']
            spellcheck = dict(zip(spellcheck[0::2], spellcheck[1::2]))
            if not spellcheck['correctlySpelled'] and 'collation' in spellcheck:
                suggestion = spellcheck['collation'][1]
        
        return suggestion
    
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
            raise Exception("doc to post is empty")
        
        json_doc = json.dumps([ data_dict ])
        
        update_url = settings.SOLR_URL + '/update/json'
        args = { 'stream.body': json_doc }
        
        if not send_request( update_url, args ):
            print "Failed to update solr with", data_dict

        command = "curl %s?commit=true" % update_url
        commands.getoutput(command)
    
