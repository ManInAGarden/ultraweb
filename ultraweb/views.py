# -*- coding: utf8 -*-

from pyramid.view import view_config
import datetime as dt
import sqlitemeasures as sqm

SQM_DB_FILE = '/home/pi/ultrapy.db'

@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    return {'project': 'ultraweb'}


@view_config(route_name='series', renderer='templates/series.pt')
class SeriesResponse:
    def __init__(self, request):
        print('Init SeriesResponse', request)
        sqm.Series.initialize(SQM_DB_FILE)
        self.request = request
        self.response = {}
        
        
    def __call__(self):
        series = sqm.Series.select()
        self.response['heading'] = u'Gespeicherte Messungen'
        self.response['items'] = series
        return self.response

class ValueSet:
    def __init__(self):
        self.Spannung = 0.0
        self.t = 0
        self.Strom = 0
        self.Ladung = 0
        self.Spannung_1 = 0.0
        self.Spannung_2 = 0.0
        self.Spannung_3 = 0.0
        self.Spannung_4 = 0.0
        self.Spannung_5 = 0.0
        self.Spannung_6 = 0.0
        self.Spannung_7 = 0.0
        self.Spannung_8 = 0.0
        self.Spannung_9 = 0.0
        self.Spannung_10 = 0.0
        self.Spannung_11 = 0.0
        self.Spannung_12 = 0.0


@view_config(route_name='series_action', renderer='templates/series_action.pt')
class SeriesActionResponse:
    def __init__(self, request):
        print('Init SeriesResponse', request.matchdict['action'], request.matchdict['id'])
        sqm.Series.initialize(SQM_DB_FILE)
        sqm.Value.initialize(SQM_DB_FILE)
        sqm.Unit.initialize(SQM_DB_FILE)
        self.request = request
        self.action = request.matchdict['action']
        self.id = request.matchdict['id']
        self.response = {}
        
        
    def __call__(self):
        series = sqm.Series.select(whereClause="Id='" + self.id + "'")
        values = sqm.Value.select(whereClause="SeriesId='" + str(series[0].Id) + "'", orderBy='Created')

        self.response['heading'] = u'Messwerte der Serie ' + series[0].Name + ' vom ' + str(series[0].Created)
        self.response['valuesets'] = self.get_values(values)
        return self.response

    def get_values(self, vals):
        answ = []
        old_time = None
        val_set = None
        for val in vals:
            if val.t != old_time:
                old_time = val.t
                if val_set != None:
                    #print('appending val_set')
                    answ.append(val_set)

                #print('creating new valset')
                val_set = ValueSet()
                val_set.t = '{0:%H:%M:%S}'.format(val.t)
            
            #print("adding <" + val.Name + "> = <" + str(val.Value) + ">")
            unit = val.resolve('UnitId')
            unitstr = ''
            if unit != None:
                unitstr = unit.Name
                
            setattr(val_set, val.Name,
                    self.format_value(val.Name, val.Value, unitstr))
                
        return answ


    def format_value(self, name, value, unit_str):
        vals = ""
        t = type(value)
        if t == dt.datetime:
            vals = '{0:%Y.%m.%d %H:%M:%S}'.format(value)
        elif t == float:
            vals = '{0:.2f}{1}'.format(value, unit_str)
        elif t == int:
            if unit_str != 'mA' and unit_str != 'mAh':
                vals = '{0:.2f}{1}'.format(float(value), unit_str)
            else:
                vals = '{0:d}{1}'.format(value, unit_str)
        else:
            print(type(value))
            vals = str(value)


        return vals
