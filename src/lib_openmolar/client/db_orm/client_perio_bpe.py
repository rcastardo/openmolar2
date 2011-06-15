#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2010, Neil Wallace <rowinggolfer@googlemail.com>               ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

'''
Provides Perio_BpeDB class
'''

from PyQt4 import QtSql
from lib_openmolar.common import common_db_orm

TABLENAME = "perio_bpe"

class NewPerioBPERecord(common_db_orm.InsertableRecord):
    def __init__(self):
        common_db_orm.InsertableRecord.__init__(
            self, SETTINGS.database, TABLENAME)

    @property
    def comment(self):
        return unicode(self.value('comment').toString())

    def commit(self):
        self.remove(self.indexOf("checked_date"))
        query, values = self.insert_query

        q_query = QtSql.QSqlQuery(SETTINGS.database)
        q_query.prepare(query)
        for value in values:
            q_query.addBindValue(value)
        if not q_query.exec_():
            print q_query.lastError().text()
            SETTINGS.database.emit_caught_error(q_query.lastError())


class PerioBpeDB(object):
    '''
    class to get static chart information
    '''
    def __init__(self, serialno):
        self.record_list = []

        query = '''select checked_date, values, comment, checked_by
        from %s where patient_id=? order by checked_date desc'''% TABLENAME

        q_query = QtSql.QSqlQuery(SETTINGS.database)
        q_query.prepare(query)
        q_query.addBindValue(serialno)
        q_query.exec_()
        while q_query.next():
            record = q_query.record()
            self.record_list.append(record)

    @property
    def records(self):
        '''
        returns a list of all records (type QtSql.QSqlRecords) found
        '''
        records = []
        for record in self.record_list:
            yield ( record.value("checked_date").toDate(),
                    record.value("checked_by").toString(),
                    record.value("values").toString(),
                    record.value("comment").toString())

    @property
    def current_bpe(self):
        if self.record_list == []:
            return None
        current = self.record_list[0]
        return (    current.value("checked_date").toDate(),
                    current.value("checked_by").toString(),
                    current.value("values").toString(),
                    current.value("comment").toString())

if __name__ == "__main__":

    from lib_openmolar.client.connect import ClientConnection
    cc = ClientConnection()
    cc.connect()

    obj = PerioBpeDB(1)
    bpes = obj.records

    print "%d records"% len(obj.records)

    for record in obj.records:
        print record.value("checked_date").toString(),
        print record.value("checked_by").toString(),
        print record.value("values").toString(),
        print record.value("comments").toString()

    print obj.current_bpe