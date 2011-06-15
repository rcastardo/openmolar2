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
Provides the TreatmentItem Class
'''

import re
import types

from PyQt4 import QtSql, QtCore

from lib_openmolar.common.classes import proc_codes
from insertable_record import InsertableRecord

PROCEDURE_CODES = proc_codes.ProcedureCodes()

class TreatmentItem(object):
    '''
    this custom data object represents an item of treatment.
    the underlying procedure code can be accessed with TreatmentItem.code
    '''
    SIMPLE = proc_codes.ProcCode.SIMPLE
    TOOTH = proc_codes.ProcCode.TOOTH
    ROOT = proc_codes.ProcCode.ROOT
    FILL = proc_codes.ProcCode.FILL
    CROWN = proc_codes.ProcCode.CROWN
    BRIDGE = proc_codes.ProcCode.BRIDGE
    PROSTHETICS = proc_codes.ProcCode.PROSTHETICS
    OTHER = proc_codes.ProcCode.OTHER

    def __init__(self, param):
        '''

        *overloaded function*

        TreatmentItem.__init__(self, QtSql.QSqlRecord)
            will load values from the Record

        TreatmentItem.__init__(self, string)
            string should be of the form "A01"
            ie. uniquely identify a proc code

        TreatmentItem.__init__(self, ProcCode)
            pass in a :class:`ProcCode` object directly
        '''

        if type(param) == QtSql.QSqlRecord:
            self.qsql_record = param
            param = str(param.value("om_code").toString())
        else:
            self.qsql_record = None

        if type(param) == types.StringType:
            self.code = PROCEDURE_CODES[param]
        else:
            self.code = param

        ## copy some properties from the underlying code
        self.type = self.code.type
        self.is_tooth = self.code.is_tooth
        self.is_fill = self.code.is_fill
        self.is_crown = self.code.is_crown
        self.is_bridge = self.code.is_bridge
        self.is_prosthetics = self.code.is_prosthetics
        self.is_root = self.code.is_root
        self.category = self.code.category
        self.description = self.code.description
        self.further_info_needed = self.code.further_info_needed
        self.pontics_required = self.code.pontics_required
        self.total_span = self.code.total_span
        self.surfaces_required = self.code.surfaces_required
        self.no_surfaces = self.code.no_surfaces
        self.description_required = self.code.description_required
        #self.pontics_required = self.code.pontics_required

        self._px_clinician = None
        self._tx_clinician = None
        self._cmp_date = None
        self.user_description = ""
        self.is_completed = False
        self.tooth = None
        self.pontics = []
        self.teeth = []
        self.surfaces = ""

        if self.in_database:
            self._from_record()

    def _from_record(self):
        '''
        An extension of __init__, loading data from the database
        when initiated by a QSqlRecord.
        '''

        self.set_tooth(self.qsql_record.value("tooth").toInt()[0])
        self.set_surfaces(str(self.qsql_record.value("surfaces").toString()))
        self.set_completed(self.qsql_record.value("completed").toBool())
        self.set_px_clinician(self.qsql_record.value("px_clinician").toInt()[0])
        tx_clinician, valid = self.qsql_record.value("tx_clinician").toInt()
        if valid and tx_clinician !=0 :
            self.set_tx_clinician(tx_clinician)
        tx_date = self.qsql_record.value("tx_date").toDate()
        if tx_date:
            self.set_cmp_date(tx_date)

    def set_cmp_date(self, arg):
        '''
        TreatmentItem.set_cmp_date(self, date)
            sets the item as completed, on date date
        '''
        self.set_completed()
        self._cmp_date = arg

    @property
    def in_database(self):
        '''
        returns true if the item is in the database
        if it is, then it will have a valid qsql_record.
        '''
        return self.qsql_record != None

    @property
    def cmp_date(self):
        '''
        (date) TreatmentItem.cmp_date
        ..note::
            date the item was completed (returns None if tx incomplete)
        '''
        return self._cmp_date

    @property
    def tooth_required(self):
        '''
        returns True if this code is a tooth treatment
        '''
        return (self.code.tooth_required or self.tooth != None)

    def set_tooth(self, tooth):
        '''
        TreatmentItem.set_tooth(self, int)
            int should comply with openmolar's tooth notation
        '''
        if self.tooth_required:
            self.tooth = tooth

    def set_teeth(self, teeth):
        '''
        TreatmentItem.set_teeth(self, [int, int...])
            all ints should comply with openmolar's tooth notation
        '''
        print "setting teeth", teeth
        if self.allow_multiple_teeth:
            self.teeth = teeth

    def set_surfaces(self, surfaces):
        '''
        TreatmentItem.set_surfaces(self, string)
            set the surfaces for a restoration
        ..note::
            an exception will be raised if surfaces are invalid
        '''
        print "setting surfaces", surfaces
        if self.surfaces_required:
            surf = surfaces.replace("I","O")
            surf = surf.replace("P","L")

            if not re.match("[MODBL]{1,5}$", surf) or len(set(surf)) != len(surf):
                raise Exception("INVALID SURFACES", surfaces)
            else:
                self.surfaces = surf

    def set_pontics(self, pontics):
        '''
        TreatmentItem.set_pontics(self, [int, int...])
            all ints should comply with openmolar's tooth notation
        '''
        print "setting pontics %s"% pontics
        if self.pontics_required:
            self.pontics = pontics

    def set_description(self, description):
        '''
        TreatmentItem.set_description(self, string)
        '''
        self.user_description = description


    def set_completed(self, arg=True):
        '''
        TreatmentItem.set_completed(self, arg=True)
        '''
        self.is_completed = arg

    def set_px_clinician(self, arg):
        '''
        TreatmentItem.set_px_clinician(self, int)
        ..note::
            who prescribed this treatment
            int should be the unique id of a clinician
        '''
        self._px_clinician = arg

    def set_tx_clinician(self, arg):
        '''
        TreatmentItem.set_tx_clinician(self, int)
        ..note:
            who performed this treatment
            int should be the unique id of a clinician
        '''
        self._tx_clinician = arg

    @property
    def px_clinician(self):
        '''
        (int) TreatmentItem.px_clinician
        (the unique id of a clinician who prescribed the treatment)
        '''
        return self._px_clinician

    @property
    def tx_clinician(self):
        '''
        (int) TreatmentItem.px_clinician
        (the unique id of a clinician who performed the treatment)
        '''
        return self._tx_clinician

    @property
    def allow_multiple_teeth(self):
        '''
        (bool) TreatmentItem.allow_multiple_teeth
        True if this treatment can related to multiple teeth

        ..note::
            an example would be a periodontal splint
        '''
        return self.is_bridge or self.is_prosthetics

    @property
    def bridge_span(self):
        '''
        (int) TreatmentItem.bridge_span

        '''
        print "checking bridge span", self.pontics, self.teeth
        return len(self.pontics) + len(self.teeth)

    @property
    def is_valid(self):
        return self.check_valid()[0]

    def check_valid(self):
        '''
        TreatmentItem.check_valid(self)

        returns a tuple (valid, errors),
        where valid is a boolean, and errors a list of errors

        check to see that the item has all the attributes required by the
        underlying procedure code

        .. note::
            our 3 surface filling will need to know tooth and surfaces
            returns a tuple (valid, errors),
            where valid is a boolean, and errors a list of errors
        '''
        errors = []
        if self.tooth_required and self.tooth == None:
            errors.append(_("No Tooth Selected"))

        if self.pontics_required and self.pontics == []:
            errors.append(_("No Pontics Selected"))

        if self.is_bridge:
            expected_span = str(self.total_span)
            n = re.match("\d+", expected_span)
            if n:
                span_no = int(n.group())
                entered_span = self.bridge_span

                if not (span_no == entered_span or
                ("+" in expected_span and entered_span > span_no)):
                    errors.append(u"%s (%s %s - %s %s)"% (
                        _("Incorrect Bridge Span"),
                        expected_span, _("units required"),
                        entered_span, _("entered")))

        if self.surfaces_required:
            expected_surfaces = self.no_surfaces
            n = re.match("\d+", expected_surfaces)
            if n:
                no_surfaces = int(n.group())
                surfs_entered = len(self.surfaces)
                if not (no_surfaces == surfs_entered or
                ("+" in expected_surfaces and surfs_entered > no_surfaces)):
                    errors.append(u"%s (%s %s)"% (
                        _("Incorrect number of surfaces entered"),
                        expected_surfaces, _("required")))

        if self.description_required and self.user_description == "":
            errors.append(_("A description is required"))

        return (errors==[], errors)

    def commit_to_db(self, database):
        '''
        :param: database

        write this item to the database

        will raise an exception if item is not :func:`is_valid`

        '''

        valid, reason = self.check_valid()
        if not valid:
            raise Exception, "Invalid Treatment Item <hr />%s"% reason

        record = InsertableRecord(database, "treatments")

        record.setValue("patient_id", SETTINGS.current_patient.patient_id)
        record.setValue("om_code", self.code.code)
        record.setValue("completed", self.is_completed)
        record.setValue("px_clinician", self.px_clinician)
        record.setValue("tx_clinician", self.tx_clinician)
        record.setValue("px_date", QtCore.QDate.currentDate())
        record.setValue("tx_date", self.cmp_date)
        record.setValue("added_by", SETTINGS.user)

        query, values = record.insert_query

        q_query = QtSql.QSqlQuery(database)
        q_query.prepare(query+ " returning ix")
        for value in values:
            q_query.addBindValue(value)
        q_query.exec_()

        if q_query.lastError().isValid():
            error = q_query.lastError()
            database.emit_caught_error(error)
            return False

        q_query.first()
        ix = q_query.value(0).toInt()[0]

        if self.is_tooth:
            record = common_db_orm.InsertableRecord(database, "treatment_teeth")

            record.setValue("treatment_id", ix)

            if self.allow_multiple_teeth:
                teeth = self.teeth
            else:
                teeth = [self.tooth]
            for tooth in teeth:
                record.setValue("tooth", tooth)

                query, values = record.insert_query

                q_query = QtSql.QSqlQuery(database)
                q_query.prepare(query + "returning ix")
                for value in values:
                    q_query.addBindValue(value)
                q_query.exec_()

                if q_query.lastError().isValid():
                    error = q_query.lastError()
                    database.emit_caught_error(error)
                    return False


            if self.is_fill:
                q_query.first()
                ix = q_query.value(0).toInt()[0]

                record = common_db_orm.InsertableRecord(database, "treatment_fills")

                record.setValue("tooth_tx_id", ix)
                record.setValue("surfaces", self.surfaces)
                record.setValue("material", "AM") #self.material)

                query, values = record.insert_query

                q_query = QtSql.QSqlQuery(database)
                q_query.prepare(query)
                for value in values:
                    q_query.addBindValue(value)
                q_query.exec_()

                if q_query.lastError().isValid():
                    error = q_query.lastError()
                    database.emit_caught_error(error)
                    return False

        return True


    def __repr__(self):
        return u"TreatmentItem '%s' completed=%s in_db=%s date=%s"% (
            self.code, self.is_completed, self.in_database, self.cmp_date)

    def __cmp__(self, other):
        try:
            return cmp(self.code, other.code)
        except AttributeError as e:
            return -1

def _test_module():
    '''
    the test for this module
    '''
    from lib_openmolar.common import SETTINGS

    for proc_code in SETTINGS.PROCEDURE_CODES:
        item = TreatmentItem(proc_code)
        print item, item.check_valid()
        #print "   in database?", item.in_database

if __name__ == "__main__":

    _test_module()

