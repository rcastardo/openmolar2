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
Provides the TreatmentWrapper Class -
which uses the virtual treatment table
(a view over several tables)
'''

from PyQt4 import QtCore, QtSql

from lib_openmolar.common.settings import om_types
from lib_openmolar.common import common_db_orm


class TreatmentModel(object):
    def __init__(self, patient_id):
        '''
        :param database: :doc:`ClientConnection`
        :param patient_id: integer
        '''
        self.patient_id = patient_id
        self.get_records()

    def get_records(self):
        '''
        pulls all treatment items in the database
        (for the patient with the id specified at class initiation)
        '''
        self._treatment_items = []

        ## long query - only time will tell if this is a performance hit
        query =    '''select
treatments.ix, patient_id, parent_id, om_code, description,
completed, comment, px_clinician, tx_clinician, tx_date, added_by,
tooth, surfaces, material, type, technition
from treatments
left join procedure_codes on procedure_codes.code = treatments.om_code
left join treatment_teeth on treatments.ix = treatment_teeth.treatment_id
left join treatment_fills  on treatment_fills.tooth_tx_id = treatment_teeth.ix
left join treatment_crowns on treatment_crowns.tooth_tx_id = treatment_teeth.ix
where patient_id = ?
'''

        q_query = QtSql.QSqlQuery(SETTINGS.database)
        q_query.prepare(query)
        q_query.addBindValue(self.patient_id)
        q_query.exec_()
        while q_query.next():
            record = q_query.record()

            treatment_item = common_db_orm.TreatmentItem(record)
            self.add_treatment_item(treatment_item)

    @property
    def treatment_items(self):
        '''
        returns a list of all treatment items in the model
        '''
        return self._treatment_items

    @property
    def isDirty(self):
        '''
        will return True if the model differs from that in the database
        '''
        dirty = False
        for treatment_item in self.treatment_items:
            dirty = dirty or not treatment_item.in_database
        return dirty

    def add_treatment_item(self, treatment_item):
        '''
        add a :doc:`TreatmentItem` Object
        '''
        self._treatment_items.append(treatment_item)

    def commit_changes(self):
        if not self.isDirty:
            return
        print "treatment model, commiting changes"
        result = True
        for item in self.treatment_items:
            if not item.in_database:
                result = result and self.commit_item(item)

        return result

    def commit_item(self, item):
        '''
        Commit the item to the database
        '''

        return item.commit_to_db(SETTINGS.database)

if __name__ == "__main__":



    from lib_openmolar.client.connect import ClientConnection
    from lib_openmolar.client.db_orm import PatientModel

    cc = ClientConnection()
    cc.connect()

    pt = PatientModel(1)

    obj = pt.treatment_model

    for record in obj.treatment_items:
        print record

    SETTINGS.set_current_patient(pt)

    print obj.isDirty
    ti = common_db_orm.TreatmentItem("D01")
    ti.set_px_clinician(1)
    ti.set_tooth(3)
    ti.set_surfaces("O")

    print "adding", ti
    print ti.in_database
    obj.add_treatment_item(ti)
    print obj.isDirty
    print obj.commit_changes()


