#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2011, Neil Wallace <rowinggolfer@googlemail.com>               ##
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
A simple application with a shrinkable menu bar.
(similar functionality to firefox4)

At any point either the tiny menu or menubar should be visible.
Therefore if the toolbar is hidden, the menu will re-appear.

to experience this... either

    click View>Tiny Menu or hit ctrl M
'''

from PyQt4 import QtGui, QtCore

class DockableMenuBar(QtGui.QMenuBar):
    def __init__(self, parent=None):
        QtGui.QMenuBar.__init__(self, parent)

        self._menu_button = None

        self.toggleViewAction = QtGui.QAction(_("Tiny &Menu"), parent)
        self.toggleViewAction.setShortcut('ctrl+M')
        self.toggleViewAction.setCheckable(True)
        self.toggleViewAction.triggered.connect(self.toggle_visability)

        self.menu_view = QtGui.QMenu(_("&View"), self)
        self.menu_view.addAction(self.toggleViewAction)
        self.addMenu(self.menu_view)


    @property
    def menu_button(self):
        self._menu_button = QtGui.QToolButton()
        self._menu_button.setPopupMode(QtGui.QToolButton.InstantPopup)
        self._menu_button.setText(_("Menu"))
        self._menu_button.setMenu(self.mini_menu)
        self._menu_button.setToolButtonStyle(
            QtCore.Qt.ToolButtonFollowStyle)
        return self._menu_button

    @property
    def mini_menu(self):
        self._mini_menu = QtGui.QMenu()
        for action in self.actions():
            self._mini_menu.addAction(action)
        return self._mini_menu

    def refresh_mini_menu(self):
        '''
        called when an item is added to the menuBar
        '''
        if self._menu_button:
            self._menu_button.setMenu(self.mini_menu)

    def addViewOption(self, action):
        '''
        add an action to the 'view' category of the toolbar
        '''
        self.menu_view.addAction(action)

    def addMenu(self, *args):
        try:
            retval = self.insertMenu(self.actions()[-1], *args)
        except IndexError:
            retval = QtGui.QMenuBar.addMenu(self, *args)

        self.refresh_mini_menu()
        return retval

    def addAction(self, *args):
        try:
            retval = self.insertAction(self.actions()[-1], *args)
        except IndexError:
            retval = QtGui.QMenuBar.addAction(self, *args)
        self.refresh_mini_menu()
        return retval


    def toggle_visability(self, set_visible):
        self.setVisible(not set_visible)
        if set_visible:
            self.emit(QtCore.SIGNAL("mini menu required"), self.menu_button)
        else:
            self.emit(QtCore.SIGNAL("hide mini menu"), True)

    def setNotVisible(self, menu_bar_visible):
        '''
        make sure that we don't end up with neither menu visible!
        '''
        if not menu_bar_visible:
            self.setVisible(True)
            self.toggleViewAction.setChecked(False)

class DockAwareToolBar(QtGui.QToolBar):
    def __init__(self, parent=None):
        QtGui.QToolBar.__init__(self, parent)
        self.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.setObjectName("DockAwareToolbar") #for QSettings

        # this should happen by default IMO.
        self.toggleViewAction().setText(_("&ToolBar"))
        self.toggleViewAction().triggered.connect(self.clear_mini_menu)
        self._menu_button = None

    def add_mini_menu(self, menu_button):
        if not self._menu_button is None:
            self.clear_mini_menu(True)
        self._menu_button = menu_button
        if self.actions():
            self.insertWidget(self.actions()[0], menu_button)
        else:
            self.addWidget(menu_button)
        self.show()

    def clear_mini_menu(self, clear=False):
        if clear:
            self._menu_button.hide()
            self._menu_button.setParent(None)
            self._menu_button.deleteLater()
            self._menu_button = None

class TestMainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        ## initiate instances of our classes

        self.toolbar = DockAwareToolBar()
        menu_bar = DockableMenuBar(self)

        ## the menu bar needs this action adding
        menu_bar.addViewOption(self.toolbar.toggleViewAction())

        ## add them to the app
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolbar)
        self.setMenuBar(menu_bar)

        ## make them aware of one another
        self.connect(self.menuBar(), QtCore.SIGNAL("mini menu required"),
            self.toolbar.add_mini_menu)
        self.connect(self.menuBar(), QtCore.SIGNAL("hide mini menu"),
            self.toolbar.clear_mini_menu)
        self.toolbar.toggleViewAction().triggered.connect(
            self.menuBar().setNotVisible)

        ## some arbitrary stuff to make the app more realistic
        file_action = QtGui.QAction("&File", self)
        self.menuBar().addAction(file_action)

        edit_action = QtGui.QAction("&Edit", self)
        self.menuBar().addAction(edit_action)

        line_edit = QtGui.QLineEdit("http://google.com")
        self.toolbar.addWidget(line_edit)

        go_but = QtGui.QPushButton("Go!")
        go_but.setFixedWidth(60)
        self.toolbar.addWidget(go_but)

        te = QtGui.QTextEdit()
        self.setCentralWidget(te)
        te.setText(__doc__)


if __name__ == "__main__":
    import gettext
    gettext.install("")

    app = QtGui.QApplication([])
    mw = TestMainWindow()
    mw.show()
    app.exec_()
