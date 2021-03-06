#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2010-2012, Neil Wallace <neil@openmolar.com>                   ##
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

from PyQt4 import QtCore, QtGui

from lib_openmolar.common.qt4.widgets.closeable_tab_widget \
    import ClosableTabWidget
from lib_openmolar.admin.qt4.classes.known_server_widget \
    import KnownServerWidget

class AdminTabWidget(ClosableTabWidget):
    '''
    a minor re-implementation of the closeabletabwidget from openmolar common
    uses a toolbutton as the right widget, and has some custom signals
    '''
    def __init__(self, parent=None):
        ClosableTabWidget.__init__(self, parent)

        self.currentChanged.connect(self._tab_changed)

        self.known_server_widget = KnownServerWidget()
        self.addTab(self.known_server_widget, _("Known Servers"))

    def closeAll(self):
        '''
        re-implement the base class method
        '''
        result = self.count() <= 1
        if self.count() > 1:
            result = ClosableTabWidget.closeAll(self,
                _("End All Postgres Sessions and"))
            if result:
                self.addTab(self.known_server_widget, _("Known Servers"))
                LOGGER.debug("emitting end_pg_session signal")
                self.emit(QtCore.SIGNAL("end_pg_session"))
        return result

    def _tab_changed(self, i):
        try:
            ## if the current widget is a query tool, the query history
            ## may have been updated by another instance
            self.widget(i).get_history()
        except AttributeError:
            ## fail quietly!
            pass

    def new_query(self):
        LOGGER.debug("%s new_query called"% self)
        try:
            tool = self.currentWidget()
            tool.add_query_editor()
            tool.set_session(tool.pg_session)
        except AttributeError:
            LOGGER.debug("cannot add a new query to %s"% tool)

    def new_table(self):
        LOGGER.debug("%s new_table called"% self)
        try:
            tool = self.currentWidget()
            tool.add_table()
            tool.set_session(tool.pg_session)
        except AttributeError:
            LOGGER.debug("cannot add a new table to %s"% tool)

    def addTab(self, *args):
        ClosableTabWidget.addTab(self, *args)
        self.setCurrentIndex(self.count()-1)


def _test():
    import gettext
    gettext.install("")

    app = QtGui.QApplication([])
    mw = QtGui.QMainWindow()

    atw = AdminTabWidget()

    label1 = QtGui.QLabel("Placeholder1")
    label2 = QtGui.QLabel("Placeholder2")
    atw.addTab(label1, "one")
    atw.addTab(label2, "two")

    mw.setCentralWidget(atw)
    mw.show()
    app.exec_()

if __name__ == "__main__":
    _test()