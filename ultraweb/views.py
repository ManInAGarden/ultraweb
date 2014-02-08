# -*- coding: utf8 -*-

from pyramid.view import view_config
import datetime as dt
import sqlitemeasures as sqm

import pygal

SQM_DB_FILE = '/home/tiger/ultrapy.db'

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


@view_config(route_name='series_view', renderer='templates/series_view.pt')
class SeriesActionResponse:
    def __init__(self, request):
        print('Init SeriesResponse - view',  request.matchdict['id'])
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
        valsets = []
        heading = '???'
        series = sqm.Series.select(whereClause="Id='" + self.id + "'")
                
        values = sqm.Value.select(whereClause="SeriesId='" + str(self.id) + "'", orderBy='Created')
        valsets = self.get_values(values)
        heading = u'Messwerte der Serie ' + series[0].Name + ' vom ' + str(series[0].Created)

        self.response['heading'] = heading
        self.response['valuesets'] = valsets
        self.response['msg_title'] = self.msg_title
        self.response['message'] = self.message
        self.response['graphics'] = self.render_graphics(self.id, values)
        return self.response

    def get_values(self, vals, do_units=True):
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
            
            if do_units==True:
                unit = val.resolve('UnitId')
                unitstr = ''
                if unit != None:
                    unitstr = unit.Name
                
                setattr(val_set, val.Name,
                    self.format_value(val.Name, val.Value, unitstr))
            else:
                setattr(val_set, val.Name, val.Value)
                
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

    def render_graphics(self, id, values):
        filename = str(id) + '.svg'

        line_c = pygal.Line(disable_xml_declaration = True, x_title='t/s',
                            x_label_rotation=90, x_labels_major_every=3,
                            show_minor_x_labels=False)
        line_c.title = 'Lade-/Entladediagramm'

        maxsec = 0
        lines = {'Ladung': [],
                 'Strom' : [],
                 'Spannung' : [],
                 'Spannung_1': [],
                 'Spannung_2': [],
                 'Spannung_3': [],
                 'Spannung_4': [],
                 'Spannung_5': [],
                 'Spannung_6': [],
                 'Spannung_7': [],
                 'Spannung_8': [],
                 'Spannung_9': [],
                 'Spannung_10': [],
                 'Spannung_11': [],
                 'Spannung_12': []}
        
        x_axis = []

        do_disp = {}
        units = {}
        for key in lines.keys():
            do_disp[key] = False
            units[key] = None
        
        old_time = None
        curr_secs = 0
        start_time = None
        for val in values:
            if start_time == None:
                start_time = val.t
                
            if val.t != old_time:
                old_time = val.t
                currsecs = (old_time - start_time).total_seconds()
                x_axis.append(currsecs)
         
            if val.Name in lines:
                lines[val.Name].append(val.Value)
                if val.Value != 0.0:
                    do_disp[val.Name] = True
                    
                if units[val.Name] == None:
                    erg = sqm.Unit.select(whereClause="Id='" + str(val.UnitId) + "'")
                    if len(erg)==1:
                        units[val.Name] = erg[0].Name
                    
        for key in lines.keys():
            if do_disp[key] == True:
                if key.startswith('Spannung'):
                    sec = True
                else:
                    sec = False

                name = self.get_line_name(key)
                line_c.add(name + '/' + units[key], lines[key], secondary=sec)
            

        line_c.x_labels = map(str, x_axis)
        
        return line_c.render()
        
    def get_line_name(self, key):
        name = key
        if key.startswith('Spannung'):
            if key=='Spannung':
                name = 'Uges'
            else:
                name = key.replace('Spannung_', 'U')
        elif key=='Strom':
            name = 'Iges'
            
        return name
