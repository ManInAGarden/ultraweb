# -*- coding: utf8 -*-

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
import datetime as dt
import sqlitemeasures as sqm

SQM_DB_FILE = '/home/tiger/ultrapy.db'


@view_config(route_name='series_delete', renderer='templates/series_delete.pt')
class SeriesDeleteResponse:
    def __init__(self, request):
        print('Init SeriesResponse - delete',  request.matchdict['id'])
        sqm.Series.initialize(SQM_DB_FILE)
        sqm.Value.initialize(SQM_DB_FILE)
        sqm.Unit.initialize(SQM_DB_FILE)
        self.request = request
        self.id = request.matchdict['id']
        self.msg_title = ''
        self.message = ''
        self.response = {}
        

    def show_message(self, title, message):
        self.msg_title = title
        self.message = message

    def __call__(self):
        if self.request.method == 'GET':
            heading = '???'
            series = sqm.Series.select(whereClause="Id='" + self.id + "'")
            values = sqm.Value.select(whereClause="SeriesId='" + str(series[0].Id) + "'", orderBy='Created')
            
            heading = u'Löschen der Serie ' + series[0].Name + ' vom ' + str(series[0].Created)
            
            self.response['heading'] = heading
            self.response['series'] = series[0]
            self.response['datacount'] = len(values)
            self.response['msg_title'] = self.msg_title
            self.response['message'] = self.message
            return self.response
        elif self.request.method == 'POST':
            print('In POST')
            params = self.request.params
            self.delete_series(params['Id'])
            url = self.request.route_url('series') 
            return HTTPFound(location=url)
            
    def delete_series(self, id):
        sqm.Value.delete(whereClause="SeriesId='" + id + "'")
        sqm.Series.delete(whereClause="Id='" + id + "'")
