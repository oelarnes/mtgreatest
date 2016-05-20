import MySQLdb
import re

from db_params import params  
from datetime import datetime

def connect():
    return MySQLdb.connect(user=params['user'],passwd=params['passwd'],db=params['db'])

def serialize(el, _type):
    if type(el) is unicode:
        el = el.replace(u'\xa0', u' ')
        el = el.encode('utf-8')
    if type(el) is str and _type.startswith('int'):
        el = re.match('^[0-9]*', el).group()
    if type(el) is str and _type.startswith('varchar'):
        return "'{}'".format(el.replace("'", "\\'"))
    if el == None or el == '':
        return 'NULL'
    if type(el) is datetime:
        return "'{}'".format(el.isoformat()[:10])
    return str(el)

def names_from_data_table(data_table):
    return list(set().union(*[row.keys() for row in data_table]))

def insert_statement(table_name, data_table, types):
    statement = 'INSERT INTO {} '.format(table_name)
    if not len(data_table):
        statement += '() VALUES ()'
        return statement
    
    names = names_from_data_table(data_table)
    statement += '({}) VALUES '.format(str.join(',', names))

    values = []
    for row in data_table:
        content = str.join(',', [serialize(row.get(name, None), types[name]) for name in names])
        values.append('({})'.format(content))

    statement += str.join(',', values)
    return statement

class Cursor:
    def __init__(self):
        self.__db = connect()
        self.__cursor = self.__db.cursor()
    
    def insert(self, table_name, data_table, verbose=True):
        types = self.get_types(table_name)
        statement = insert_statement(table_name, data_table, types)
        self.execute(statement, verbose=verbose)
        return self

    def execute(self, statement, verbose=False):
        if verbose:
            print 'executing statement: {}'.format(statement)
        self.__cursor.execute(statement)
        return self.__cursor.fetchall()

    def close(self, commit=True):
        if commit:
            self.__db.commit()
        self.__cursor.close()
        self.__db.close()

    def get_types(self, table_name):
        return dict(self.execute("select column_name, data_type from information_schema.columns where table_name = '{}'".format(table_name)))


