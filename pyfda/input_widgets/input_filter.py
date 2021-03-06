# -*- coding: utf-8 -*-
"""
input_filter.py
---------------
Subwidget for selecting the filter, consisting of combo boxes for:
- Response Type (LP, HP, Hilbert, ...)
- Filter Type (IIR, FIR, CIC ...)
- Design Method (Butterworth, ...)

@author: Julia Beike, Christian Münker, Michael Winkler
Datum: 4.12.2014
"""
from __future__ import print_function, division, unicode_literals, absolute_import
import sys
from PyQt4 import QtGui
from PyQt4.QtCore import pyqtSignal

import pyfda.filterbroker as fb
import pyfda.pyfda_rc as rc

# TODO: set_response_type is called 3 times by inputSpecs.loadAllSpecs every time 
#       filter is changed - why? Eliminating set_response_type gives errors when
#       changing the response type of FIR filters

class InputFilter(QtGui.QWidget):
    """
    Construct combo boxes for selecting the filter, consisting of:
      - Response Type (LP, HP, Hilbert, ...)
      - Filter Type (IIR, FIR, CIC ...)
      - DesignMethod (Butterworth, ...)
    """

    sigFiltChanged = pyqtSignal()

    def __init__(self, DEBUG=False):
        super(InputFilter, self).__init__()

        self.DEBUG = DEBUG

        self.dm_last = '' # design method from last call

        self.init_UI()

        self.set_response_type() # first time initialization

    def init_UI(self):
        """
        Initialize UI with comboboxes for selecting filter
        """
#-----------------------------------------------------------------------------
#        see filterbroker.py for structure and content of "filterTree" dict
#-----------------------------------------------------------------------------

        #----------------------------------------------------------------------
        # Create combo boxes
        # - cmbResponseType for selecting response type rt (LP, HP, ...)
		# - cmbFilterType for selection of filter type (IIR, FIR, ...)
		# - cmbDesignMethod for selection of design method (Chebychev, ...)
		# and populate them from the "filterTree" dict either directly or by
		# calling set_response_type() :
        print("\n\ninitialize InputFilter!\n\n")

        self.cmbResponseType = QtGui.QComboBox(self)
        self.cmbResponseType.setToolTip("Select filter response type.")
        self.cmbFilterType = QtGui.QComboBox(self)
        self.cmbFilterType.setToolTip("Select the kind of filter (recursive, transversal, ...).")
        self.cmbDesignMethod = QtGui.QComboBox(self)
        self.cmbDesignMethod.setToolTip("Select the actual filter design method.")

        # Adapt combobox size dynamically to largest element
        self.cmbResponseType.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        self.cmbFilterType.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)
        self.cmbDesignMethod.setSizeAdjustPolicy(QtGui.QComboBox.AdjustToContents)

        #----------------------------------------------------------------------
        # Populate combo box with initial settings from fb.fil_tree
        #----------------------------------------------------------------------
        # Translate short response type ("LP") to displayed names ("Lowpass")
        # (correspondence is defined in pyfda_rc.py) and populate rt combo box
        #
        # In Python 3, python objects are automatically converted to QVariant
        # when stored as "data" e.g. in a QComboBox and converted back when
        # retrieving. In Python 2, QVariant is returned when itemData is retrieved.
        # This is first converted from the QVariant container format to a
        # QString, next to a "normal" non-unicode string
        for rt in fb.fil_tree:
            self.cmbResponseType.addItem(rc.rt_names[rt], rt)
        idx = self.cmbResponseType.findData('LP') # find index for 'LP'

        if idx == -1: # Key 'LP' does not exist, use first entry instead
            idx = 0

        self.cmbResponseType.setCurrentIndex(idx) # set initial index
        rt = self.cmbResponseType.itemData(idx)
        if not isinstance(rt, str):
            rt = str(rt.toString()) # needed for Python 2.x

        for ft in fb.fil_tree[rt]:
            self.cmbFilterType.addItem(rc.ft_names[ft], ft)
        self.cmbFilterType.setCurrentIndex(0) # set initial index
        ft = self.cmbFilterType.itemData(0)
        if not isinstance(ft, str):
            ft = str(ft.toString()) # needed for Python 2.x
            
        for dm in fb.fil_tree[rt][ft]:
            self.cmbDesignMethod.addItem(fb.dm_names[dm], dm)
        self.cmbDesignMethod.setCurrentIndex(0) # set initial index

        #----------------------------------------------------------------------
        # LAYOUT
        #----------------------------------------------------------------------
        # see Summerfield p. 278
        self.layHDynWdg = QtGui.QHBoxLayout() # for additional dynamic subwidgets
        self.frmDynWdg = QtGui.QFrame() # collect subwidgets in frame (no border)
        self.frmDynWdg.setObjectName("wdg_frmDynWdg")
        self.frmDynWdg.setSizePolicy(QtGui.QSizePolicy.MinimumExpanding, 
                                     QtGui.QSizePolicy.Minimum)

        #Debugging: enable next line to show border of frmDnyWdg
        #self.frmDynWdg.setFrameStyle(QtGui.QFrame.StyledPanel|QtGui.QFrame.Raised)

        self.frmDynWdg.setLayout(self.layHDynWdg)

        layHStdWdg = QtGui.QHBoxLayout() # container for standard subwidgets

        spacer = QtGui.QSpacerItem(1, 0, QtGui.QSizePolicy.Expanding,
                                         QtGui.QSizePolicy.Fixed)

        layHStdWdg.addWidget(self.cmbResponseType)# QtCore.Qt.AlignLeft)

        layHStdWdg.addItem(spacer)

        layHStdWdg.addWidget(self.cmbFilterType)

        layHStdWdg.addItem(spacer)

        layHStdWdg.addWidget(self.cmbDesignMethod)

        # stack standard + dynamic subwidgets vertically:
        layVAllWdg = QtGui.QVBoxLayout()

        layVAllWdg.addLayout(layHStdWdg)
        layVAllWdg.addWidget(self.frmDynWdg)


        self.frmMain = QtGui.QFrame()
        self.frmMain.setFrameStyle(QtGui.QFrame.StyledPanel|QtGui.QFrame.Sunken)
        self.frmMain.setLayout(layVAllWdg)

        layHMain = QtGui.QHBoxLayout()
        layHMain.addWidget(self.frmMain)
        layHMain.setContentsMargins(0, 0, 0, 0)

        self.setLayout(layHMain)
#        layHMain.setSizeConstraint(QtGui.QLayout.SetFixedSize)

        #------------------------------------------------------------
        # SIGNALS & SLOTS
        #------------------------------------------------------------
        # Connect comboBoxes and setters, generate the signal sigFiltChanged
        # every time a combo box is changed
        self.cmbResponseType.currentIndexChanged.connect(self.set_response_type) # 'LP'
        self.cmbResponseType.currentIndexChanged.connect(self.sigFiltChanged.emit)
        self.cmbFilterType.currentIndexChanged.connect(self.set_filter_type) #'IIR'
        self.cmbFilterType.currentIndexChanged.connect(self.sigFiltChanged.emit)
        self.cmbDesignMethod.currentIndexChanged.connect(self.set_design_method) #'cheby1'
        self.cmbDesignMethod.currentIndexChanged.connect(self.sigFiltChanged.emit)
        #------------------------------------------------------------


#------------------------------------------------------------------------------
    def load_entries(self):
        """
        Reload comboboxes from filter dictionary to update changed settings
        e.g. by loading filter design
        """
        idx_rt = self.cmbResponseType.findData(fb.fil[0]['rt']) # find index for 'LP'
        self.cmbResponseType.setCurrentIndex(idx_rt)
        self.set_response_type()


#------------------------------------------------------------------------------
    def set_response_type(self):
        """
        Triggered when cmbResponseType (LP, HP, ...) is changed:
        Copy selection to self.rt and fb.fil[0] and reconstruct filter type combo

        If previous filter type (FIR, IIR, ...) exists for new rt, set the
        filter type combo box to the old setting
        """
        # Read out current setting of comboBox and convert to string (see init_UI)
        rt_idx = self.cmbResponseType.currentIndex()
        self.rt = self.cmbResponseType.itemData(rt_idx)

        if not isinstance(self.rt, str):
            self.rt = str(self.rt.toString()) # needed for Python 2
        fb.fil[0]['rt'] = self.rt # copy selected rt setting to filter dict

        # Get list of available filter types for new rt
        ft_list = list(fb.fil_tree[self.rt].keys()) # explicit list() needed for Py3

        #---------------------------------------------------------------
        # Rebuild filter type combobox entries for new rt setting
        self.cmbFilterType.blockSignals(True) # don't fire when changed programmatically
        self.cmbFilterType.clear()
        for ft in fb.fil_tree[self.rt]:
            self.cmbFilterType.addItem(rc.ft_names[ft], ft)

        # Is current filter type (e.g. IIR) in list for new rt?
        if fb.fil[0]['ft'] in ft_list:
            ft_idx = self.cmbFilterType.findText(fb.fil[0]['ft'])
            self.cmbFilterType.setCurrentIndex(ft_idx) # yes, set same ft as before
        else:
            self.cmbFilterType.setCurrentIndex(0)     # no, set index 0
            
        self.cmbFilterType.blockSignals(False)
        #---------------------------------------------------------------

        self.set_filter_type()

#------------------------------------------------------------------------------
    def set_filter_type(self):
        """"
        Triggered when cmbFilterType (IIR, FIR, ...) is changed:
        - read filter type ft and copy it to fb.fil[0]['ft'] and self.ft
        - (re)construct design method combo, adding
          displayed text (e.g. "Chebychev 1") and hidden data (e.g. "cheby1")
        """
        # Read out current setting of comboBox and convert to string (see init_UI)
        ft_idx = self.cmbFilterType.currentIndex()
        self.ft = self.cmbFilterType.itemData(ft_idx)
        
        if not isinstance(self.ft, str):
            self.ft = str(self.ft.toString()) # needed for Python 2.x
        fb.fil[0]['ft'] = self.ft # copy selected ft setting to filter dict

        if self.DEBUG:
            print("InputFilter.set_filter_type triggered:", self.ft)

        #---------------------------------------------------------------
        # Get all available design methods for new ft from fil_tree and
        # - Collect them in list dm_list
        # - Rebuild design method combobox entries for new ft setting:
        #    The combobox is populated with the "long name",
        #    the internal name is stored in comboBox.itemData
        self.cmbDesignMethod.blockSignals(True)
        self.cmbDesignMethod.clear()
        dm_list = []

        for dm in fb.fil_tree[self.rt][self.ft]:
            self.cmbDesignMethod.addItem(fb.dm_names[dm], dm)
            dm_list.append(dm)

        if self.DEBUG:
            print("dm_list", dm_list)
            print(fb.fil[0]['dm'])

        # Does new ft also provide the previous design method (e.g. ellip)?
        # Has filter been instantiated?
        if fb.fil[0]['dm'] in dm_list and fb.fil_inst:
            # yes, set same dm as before
            dm_idx = self.cmbDesignMethod.findText(fb.dm_names[fb.fil[0]['dm']])
            if self.DEBUG:
                print("dm_idx", dm_idx)
            self.cmbDesignMethod.setCurrentIndex(dm_idx)
        else:
            self.cmbDesignMethod.setCurrentIndex(0)     # no, set index 0

        self.cmbDesignMethod.blockSignals(False)
        self.set_design_method()


#------------------------------------------------------------------------------
    def set_design_method(self):
        """
        Triggered when cmbDesignMethod (cheby1, ...) is changed:
        - read design method dm and copy it to fb.fil[0]
        - create / update global filter instance fb.fil_inst of dm class
        - update dynamic widgets (if any)
        - set filter_initialized = True
        """
        dm_idx = self.cmbDesignMethod.currentIndex()
        dm = self.cmbDesignMethod.itemData(dm_idx)
        if not isinstance(dm, str):
            dm = str(dm.toString()) # needed for Python 2.x (see init_UI)
        fb.fil[0]['dm'] = dm
        if dm != self.dm_last: # dm has changed, create new instance
            #-----
            err = fb.fil_factory.create_fil_inst(dm)
            #-----
            if self.DEBUG:
                print("InputFilter.set_design_method triggered:", dm)
    
            # Check whether new design method also provides the old filter order
            # method. If yes, don't change it, else set first available
            # filter order method
            if fb.fil[0]['fo'] not in fb.fil_tree[self.rt][self.ft][dm].keys():
                fb.fil[0].update({'fo':{}})
                fb.fil[0]['fo'] = fb.fil_tree[self.rt][self.ft][dm].keys()[0]
    
            if self.DEBUG:
                print("=== InputFilter.set_design_method ===")
                print("selFilter:", fb.fil[0])
                print("filterTree[dm] = ", fb.fil_tree[self.rt][self.ft][dm])
                print("filterTree[dm].keys() = ", fb.fil_tree[self.rt][self.ft]\
                                                                [dm].keys())
    
            self._update_dyn_widgets() # check for new subwidgets and update if needed
    
#------------------------------------------------------------------------------
    def _update_dyn_widgets(self):
        """
        Delete dynamically (i.e. within filter design routine) created subwidgets
        and create new ones, depending on requirements of filter design algorithm


        This does NOT work when the subwidgets to be deleted and created are
        identical, as the deletion is only performed when the current scope has
        been left (?)! Hence, it is necessary to skip this method when the new
        design method is the same as the old one.
        """
# TODO: see https://www.commandprompt.com/community/pyqt/x3410.htm


        # Find "old" dyn. subwidgets and delete them:
        widgetList = self.frmDynWdg.findChildren(
            (QtGui.QComboBox, QtGui.QLineEdit, QtGui.QLabel, QtGui.QWidget))
#       widgetListNames = [w.objectName() for w in widgetList]

        for w in widgetList:
            self.layHDynWdg.removeWidget(w)   # remove widget from layout
            w.deleteLater()             # tell Qt to delete object when the
                                        # method has completed
#                del w                       # not really needed?

        # Try to create "new" dyn. subwidgets:
        if hasattr(fb.fil_inst, 'wdg'):
            try:
                if 'sf' in fb.fil_inst.wdg:
                    a = getattr(fb.fil_inst, fb.fil_inst.wdg['sf'])
                    self.layHDynWdg.addWidget(a, stretch=1)
                    self.layHDynWdg.setContentsMargins(0, 0, 0, 0)
                    self.frmDynWdg.setVisible(a != None)

            except AttributeError as e:
                print("sf.updateWidgets:", e)
                self.frmDynWdg.setVisible(False)
        else:
            self.frmDynWdg.setVisible(False)

        self.dm_last = fb.fil[0]['dm']


#    def closeEvent(self, event):
#        exit()
#------------------------------------------------------------------------------

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    form = InputFilter()
    form.show()


    app.exec_()

