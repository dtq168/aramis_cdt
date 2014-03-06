#-------------------------------------------------------------------------------
#
# Copyright (c) 2013
# IMB, RWTH Aachen University,
# ISM, Brno University of Technology
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in the AramisCDT top directory "license.txt" and may be
# redistributed only under the conditions described in the aforementioned
# license.
#
# Thanks for using Simvisage open source!
#
#-------------------------------------------------------------------------------
# from traits.etsconfig.api import ETSConfig
# ETSConfig.toolkit = 'qt4'

from etsproxy.traits.api import \
    HasTraits, Instance, on_trait_change, Button, Directory, Event

from etsproxy.traits.ui.api import UItem, View, Tabbed, Group, Item, RangeEditor, VGroup, HSplit
from util.traits.editors.mpl_figure_editor import MPLFigureEditor
from matplotlib.figure import Figure
import os
import sys

import platform
import time
if platform.system() == 'Linux':
    sysclock = time.time
elif platform.system() == 'Windows':
    sysclock = time.clock

from aramis_info import AramisInfo
from aramis_data import AramisData
from aramis_cdt import AramisCDT
from aramis_view2d import AramisPlot2D
from aramis_view3d import AramisView3D
from aramis_remote import AramisRemote


class AramisUI(HasTraits):
    '''This class is managing all the parts of the CDT and enable to create
    simple user interface.
    '''

    data_dir = Directory(auto_set=False, enter_set=True)
    '''Directory of data files (*.txt) exported by Aramis Software.
    '''

    aramis_info = Instance(AramisInfo, ())

    aramis_data = Instance(AramisData)
    def _aramis_data_default(self):
        return AramisData(aramis_info=self.aramis_info)

    aramis_remote = Instance(AramisRemote)
    def _aramis_remote_default(self):
        return AramisRemote(aramis_info=self.aramis_info)

    aramis_cdt = Instance(AramisCDT)
    def _aramis_cdt_default(self):
        return AramisCDT(aramis_info=self.aramis_info,
                          aramis_data=self.aramis_data)

    aramis_view2d = Instance(AramisPlot2D)
    def _aramis_view2d_default(self):
        return AramisPlot2D(aramis_info=self.aramis_info,
                            aramis_data=self.aramis_data,
                            aramis_cdt=self.aramis_cdt,
                            figure=self.figure)

    aramis_view3d = Instance(AramisView3D)
    def _aramis_view3d_default(self):
        return AramisView3D(aramis_data=self.aramis_data,
                            aramis_cdt=self.aramis_cdt)

    figure = Instance(Figure)
    def _figure_default(self):
        figure = Figure(tight_layout=True)
        # figure.add_subplot(111)
        # figure.add_axes([0.15, 0.15, 0.75, 0.75])
        return figure

    load_data = Button()
    def _load_data_fired(self):
        self.aramis_info.data_dir = self.data_dir

    set_dir = Button
    def _set_dir_fired(self):
        self.data_dir = os.path.join(self.aramis_remote.local_dir,
                                                 self.aramis_remote.aramis_file_selected)

    view = View(HSplit(
                    Group(
                        UItem('aramis_info@'),
                        UItem('aramis_data@'),
                        Tabbed(
                               Group(
                                UItem('aramis_remote'),
                               UItem('set_dir', label='Use directory from remote'),
                              'data_dir',
                              UItem('load_data'),
                              label='Load data',
                              id='aramisCDT.tabbed.remote',
                              ),
                               UItem('aramis_cdt@'),
                                UItem('aramis_view2d@'),
                                UItem('aramis_view3d@'),
                                id='aramisCDT.tabbed',
                                ),
                          id='aramisCDT.control',
                          ),
                    Group(
                            Item('figure', editor=MPLFigureEditor(),
                            show_label=False),
                            label='Plot sheet',
                            id='aramisCDT.figure',
                            dock='tab',
                            ),
                       id='aramisCDT.hsplit',
                       ),
                title='Aramis CDT',
                id='aramis_CDT.main_window',
                resizable=True,
                # width=0.2,
                )


if __name__ == '__main__':

    from os.path import expanduser
    home = expanduser("~")

    data_dir = os.path.join(home, '.simdb_cache', 'aramis', 'TTb-4c-2cm-0-TU-V1_bs4-Xf19s15-Yf19s15')

    AI = AramisInfo(data_dir=data_dir)
    # AI = AramisInfo()
    AUI = AramisUI(aramis_info=AI)
    AUI.configure_traits()
