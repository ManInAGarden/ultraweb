# -*- coding: utf8 -*-

from pyramid.view import view_config
from pyramid.httpexceptions import HTTPFound
import datetime as dt
import sqlitemeasures as sqm

SQM_DB_FILE = '/home/tiger/ultrapy.db'


@view_config(route_name='series_edit', renderer='templates/series_edit.pt')
class SeriesEditResponse:
    def __init__(self, request):
        print('Init SeriesResponse - edit',  request.matchdict['id'])
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
            
            heading = u'Bearbeiten der Serie ' + series[0].Name + ' vom ' + str(series[0].Created)
            if len(series)>0:
                self.series = series[0]
            else:
                self.series = None
                
            self.response['heading'] = heading
            self.response['series'] = self.series
            self.response['msg_title'] = self.msg_title
            self.response['message'] = self.message
            
            return self.response
            
        elif self.request.method == 'POST':
            print('In POST')
            params = self.request.params
            self.update_series(params)
            url = self.request.route_url('series') 
            return HTTPFound(location=url)

    def update_series(self, params):
        id = params['Id']
        erg = sqm.Series.select(whereClause="[Id]='" + id + "'")
        if len(erg)==1:
            series = erg[0]
            series.Name = unicode(params['Name'])
            series.Mode = unicode(params['Mode'])
            series.Description = unicode(params['Description'])
            series.flush()
        else:
            print('Häh!')
