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

from traits.api import \
    HasTraits, Float, Bool, Trait, Instance, Button, WeakRef

from traitsui.api import  UItem, View, Item

import numpy as np
# import etsproxy.mayavi.mlab as m

import platform
import time
if platform.system() == 'Linux':
    sysclock = time.time
elif platform.system() == 'Windows':
    sysclock = time.clock

import os
from mayavi.tools.mlab_scene_model import MlabSceneModel

from aramis_info import AramisInfo
from aramis_data import AramisFieldData
from aramis_cdt import AramisCDT


class AramisView3D(HasTraits):
    '''This class manages 3D views for AramisCDT variables
    '''

    aramis_data = Instance(AramisFieldData)

    aramis_cdt = Instance(AramisCDT)

    scene = Instance(MlabSceneModel)

    plot_title = Bool(True)

    plot3d_var = Trait('07 d_ux [-]', {'01 x_arr [mm]':['aramis_data', 'x_arr_0'],
                                            '02 y_arr [mm]':['aramis_data', 'y_arr_0'],
                                            '03 z_arr [mm]':['aramis_data', 'z_arr_0'],
                                            '04 ux_arr [mm]':['aramis_data', 'ux_arr'],
                                            '05 uy_arr [mm]':['aramis_data', 'uy_arr'],
                                            '06 uz_arr [mm]':['aramis_data', 'uz_arr'],
                                            '07 d_ux [-]':['aramis_data', 'd_ux'],
                                            '08 crack_filed_arr [mm]': ['aramis_cdt', 'crack_field_arr'],
                                            '09 delta_ux_arr [mm]': ['aramis_data', 'delta_ux_arr'],
                                            '10 delta_uy_arr [mm]': ['aramis_data', 'delta_uy_arr']
                                            })

    plot3d_points_flat = Button
    def _plot3d_points_flat_fired(self):
        '''Plot array of variable using colormap
        '''
        # m.figure(fgcolor=(0, 0, 0), bgcolor=(1, 1, 1) , size=(900, 600))
        # engine = m.get_engine()
        # scene = engine.scenes[0]
        self.scene.mlab.clf()
        m = self.scene.mlab
        m.fgcolor = (0, 0, 0)
        m.bgcolor = (1, 1, 1)
        self.scene.scene.disable_render = True

        plot3d_var = getattr(getattr(self, self.plot3d_var_[0]), self.plot3d_var_[1])

        mask = np.logical_or(np.isnan(self.aramis_data.x_arr_0),
                             self.aramis_data.x_0_mask[0, :, :])
        mask = None
        m.points3d(self.aramis_data.x_arr_0[mask],
                   self.aramis_data.y_arr_0[mask],
                   self.aramis_data.z_arr_0[mask],
                   plot3d_var[mask],
                   mode='cube',
                   scale_mode='none', scale_factor=1)
        m.view(0, 0)
        self.scene.scene.parallel_projection = True
        self.scene.scene.disable_render = False

        if self.plot_title:
            m.title('step no. %d' % self.aramis_data.current_step, size=0.3)

        m.scalarbar(orientation='horizontal', title=self.plot3d_var_[1])

        # plot axes
        m.axes()

    glyph_x_length = Float(0.200)
    glyph_y_length = Float(0.200)
    glyph_z_length = Float(0.000)

    glyph_x_length_cr = Float(3.000)
    glyph_y_length_cr = Float(0.120)
    glyph_z_length_cr = Float(0.120)

    warp_factor = Float(0.0)

    plot3d_points = Button
    def _plot3d_points_fired(self):
        '''Plot arrays of variables in 3d relief
        '''
        aramis_cdt = self.aramis_cdt
        # m.figure(fgcolor=(0, 0, 0), bgcolor=(1, 1, 1), size=(900, 600))

        #
        # scene = engine.scenes[0]
        self.scene.mlab.clf()
        m = self.scene.mlab
        m.fgcolor = (0, 0, 0)
        m.bgcolor = (1, 1, 1)
        self.scene.scene.disable_render = True

        #-----------------------------------
        # plot crack width ('crack_field_w')
        #-----------------------------------

        z_arr = np.zeros_like(self.aramis_data.z_arr_0)

        plot3d_var = getattr(getattr(self, self.plot3d_var_[0]), self.plot3d_var_[1])
        m.points3d(z_arr, self.aramis_data.x_arr_0, self.aramis_data.y_arr_0, plot3d_var,
                   mode='cube', colormap="blue-red", scale_mode='scalar')

        # scale glyphs
        #
        glyph = self.scene.engine.scenes[0].children[0].children[0].children[0]
        glyph.glyph.glyph_source.glyph_position = 'tail'
        glyph.glyph.glyph_source.glyph_source.x_length = self.glyph_x_length_cr
        glyph.glyph.glyph_source.glyph_source.y_length = self.glyph_y_length_cr
        glyph.glyph.glyph_source.glyph_source.z_length = self.glyph_z_length_cr

        #-----------------------------------
        # plot displacement jumps ('d_ux_w')
        #-----------------------------------

        plot3d_var = getattr(getattr(self, self.plot3d_var_[0]), self.plot3d_var_[1])
        m.points3d(z_arr, self.aramis_data.x_arr_0, self.aramis_data.y_arr_0, plot3d_var, mode='cube',
                   colormap="blue-red", scale_mode='none')

        glyph1 = self.scene.engine.scenes[0].children[1].children[0].children[0]
#       # switch order of the scale_factor corresponding to the order of the
        glyph1.glyph.glyph_source.glyph_source.x_length = self.glyph_z_length
        glyph1.glyph.glyph_source.glyph_source.y_length = self.glyph_x_length
        glyph1.glyph.glyph_source.glyph_source.z_length = self.glyph_y_length

        # rotate scene
        #
        # scene = engine.scenes[0]
        self.scene.scene.parallel_projection = True
        m.view(0, 90)

        glyph.glyph.glyph_source.glyph_position = 'head'
        glyph.glyph.glyph_source.glyph_position = 'tail'

        module_manager = self.scene.engine.scenes[0].children[1].children[0]
        module_manager.scalar_lut_manager.show_scalar_bar = True
        module_manager.scalar_lut_manager.show_legend = True
        module_manager.scalar_lut_manager.scalar_bar.orientation = 'horizontal'
        module_manager.scalar_lut_manager.scalar_bar.title = self.plot3d_var_[1]
        module_manager.scalar_lut_manager.scalar_bar_representation.position = (0.10, 0.05)
        module_manager.scalar_lut_manager.scalar_bar_representation.position2 = (0.8, 0.15)
        self.scene.scene.disable_render = False

        if self.plot_title:
            m.title('step no. %d' % self.aramis_data.current_step, size=0.3)

        # m.scalarbar(orientation='horizontal', title=self.plot3d_var_[1])

        # plot axes
        #
        m.axes()

    plot3d_cracks = Button
    def _plot3d_cracks_fired(self):
        '''Plot cracks in 3D
        '''
        aramis_cdt = self.aramis_cdt
        # m.figure(fgcolor=(0, 0, 0), bgcolor=(1, 1, 1), size=(900, 600))

        # engine = m.get_engine()
        # scene = engine.scenes[0]
        self.scene.mlab.clf()
        m = self.scene.mlab
        m.fgcolor = (0, 0, 0)
        m.bgcolor = (1, 1, 1)
        self.scene.scene.disable_render = True

        #-----------------------------------
        # plot crack width ('crack_field_w')
        #-----------------------------------

        z_arr = np.zeros_like(self.aramis_data.z_arr_0)

        plot3d_var = aramis_cdt.crack_field_arr

        m.points3d(z_arr,
                   self.aramis_data.x_arr_0 + self.aramis_data.ux_arr * self.warp_factor,
                   self.aramis_data.y_arr_0 + self.aramis_data.uy_arr * self.warp_factor,
                   plot3d_var,
                   mode='cube', colormap="blue-red", scale_mode='scalar', scale_factor=1.0)

        # scale glyphs
        #
        glyph = self.scene.engine.scenes[0].children[0].children[0].children[0]
        glyph.glyph.glyph_source.glyph_position = 'tail'
        glyph.glyph.glyph_source.glyph_source.x_length = self.glyph_x_length_cr
        glyph.glyph.glyph_source.glyph_source.y_length = self.glyph_y_length_cr
        glyph.glyph.glyph_source.glyph_source.z_length = self.glyph_z_length_cr

        #-----------------------------------
        # plot crack_field_arr
        #-----------------------------------

        m.points3d(z_arr,
                   self.aramis_data.x_arr_0 + self.aramis_data.ux_arr * self.warp_factor,
                   self.aramis_data.y_arr_0 + self.aramis_data.uy_arr * self.warp_factor,
                   plot3d_var,
                   mode='cube', colormap="blue-red", scale_mode='none', scale_factor=1)

        glyph1 = self.scene.engine.scenes[0].children[1].children[0].children[0]
#       # switch order of the scale_factor corresponding to the order of the
        glyph1.glyph.glyph_source.glyph_source.x_length = self.glyph_z_length
        glyph1.glyph.glyph_source.glyph_source.y_length = self.glyph_x_length
        glyph1.glyph.glyph_source.glyph_source.z_length = self.glyph_y_length

        # rotate scene
        #
        scene = self.scene.engine.scenes[0]
        scene.scene.parallel_projection = True
        m.view(0, 90)
        glyph.glyph.glyph_source.glyph_position = 'head'
        glyph.glyph.glyph_source.glyph_position = 'tail'

        module_manager = self.scene.engine.scenes[0].children[1].children[0]
        module_manager.scalar_lut_manager.show_scalar_bar = True
        module_manager.scalar_lut_manager.show_legend = True
        module_manager.scalar_lut_manager.scalar_bar.orientation = 'horizontal'
        module_manager.scalar_lut_manager.scalar_bar.title = 'delta_ux [mm]'
        module_manager.scalar_lut_manager.scalar_bar_representation.position = (0.10, 0.05)
        module_manager.scalar_lut_manager.scalar_bar_representation.position2 = (0.8, 0.15)
        scene.scene.disable_render = False

        if self.plot_title:
            m.title('step no. %d' % self.aramis_data.current_step, size=0.2)

        # set scalar bar to start at zero and format values in font style 'times'
        print 'np.max(plot3d_var)', np.max(plot3d_var)
        wr_max = module_manager.scalar_lut_manager.data_range[1]
#         wr_max = 6.90  # [mm] set fixed ranges
        module_manager.scalar_lut_manager.data_range = np.array([0., wr_max])

        # format scalar bar in font style 'times'
        module_manager.scalar_lut_manager.label_text_property.font_family = 'times'
        module_manager.scalar_lut_manager.label_text_property.italic = False
        module_manager.scalar_lut_manager.label_text_property.bold = False
        module_manager.scalar_lut_manager.label_text_property.font_size = 25

        # title font of scalar bar
        module_manager.scalar_lut_manager.title_text_property.font_family = 'times'
        module_manager.scalar_lut_manager.title_text_property.bold = True
        module_manager.scalar_lut_manager.title_text_property.italic = False
        module_manager.scalar_lut_manager.title_text_property.font_size = 25


        # title font of plot (step no)
        text = scene.children[1].children[0].children[1]
        text.property.font_size = 25
        text.property.font_family = 'times'
        text.property.bold = True
        text.property.italic = False

        # use white background for plots
#         scene.scene.foreground = (0.0, 0.0, 0.0)
#         scene.scene.background = (1.0, 1.0, 1.0)

        # m.scalarbar(orientation='horizontal', title='crack_field')

        # plot axes
        #
        # m.axes()



    plot3d_var_deformed = Button
    def _plot3d_var_deformed_fired(self):
        '''Plot 3D variable in deformed configuration
        '''
        aramis_cdt = self.aramis_cdt

        self.scene.mlab.clf()
        m = self.scene.mlab
#         m.fgcolor = (0, 0, 0)
#         m.bgcolor = (1, 1, 1)
        m.fgcolor = (1, 1, 1)
        m.bgcolor = (0, 0, 0)
        self.scene.scene.disable_render = True

        #-----------------------------------
        # plot displacement jumps)
        #-----------------------------------

        z_arr = np.zeros_like(self.aramis_data.z_arr_0)

        plot3d_var = getattr(getattr(self, self.plot3d_var_[0]), self.plot3d_var_[1])
#         plot3d_var = aramis_cdt.aramis_data.delta_ux_arr

        m.points3d(z_arr,
                   self.aramis_data.x_arr_0 + self.aramis_data.ux_arr * self.warp_factor,
                   self.aramis_data.y_arr_0 + self.aramis_data.uy_arr * self.warp_factor,
                   plot3d_var,
                   mode='cube', colormap="blue-red", scale_mode='scalar', scale_factor=1.0)

        # scale glyphs
        #
        glyph = self.scene.engine.scenes[0].children[0].children[0].children[0]
        glyph.glyph.glyph_source.glyph_position = 'tail'
        glyph.glyph.glyph_source.glyph_source.x_length = self.glyph_x_length_cr
        glyph.glyph.glyph_source.glyph_source.y_length = self.glyph_y_length_cr
        glyph.glyph.glyph_source.glyph_source.z_length = self.glyph_z_length_cr

        #-----------------------------------
        # plot displacement jumps ('delta_ux_arr')
        #-----------------------------------

        m.points3d(z_arr,
                   self.aramis_data.x_arr_0 + self.aramis_data.ux_arr * self.warp_factor,
                   self.aramis_data.y_arr_0 + self.aramis_data.uy_arr * self.warp_factor,
                   plot3d_var,
                   mode='cube', colormap="blue-red", scale_mode='none', scale_factor=1)

        glyph1 = self.scene.engine.scenes[0].children[1].children[0].children[0]
#       # switch order of the scale_factor corresponding to the order of the
        glyph1.glyph.glyph_source.glyph_source.x_length = self.glyph_z_length
        glyph1.glyph.glyph_source.glyph_source.y_length = self.glyph_x_length
        glyph1.glyph.glyph_source.glyph_source.z_length = self.glyph_y_length

        # rotate scene
        #
        scene = self.scene.engine.scenes[0]
        scene.scene.parallel_projection = True
        m.view(0, 90)
        glyph.glyph.glyph_source.glyph_position = 'head'
        glyph.glyph.glyph_source.glyph_position = 'tail'

        module_manager = self.scene.engine.scenes[0].children[1].children[0]
        module_manager.scalar_lut_manager.show_scalar_bar = True
        module_manager.scalar_lut_manager.show_legend = True
        module_manager.scalar_lut_manager.scalar_bar.orientation = 'horizontal'
        module_manager.scalar_lut_manager.scalar_bar.title = self.plot3d_var_[1]
        scene.scene.disable_render = False

        module_manager.scalar_lut_manager.scalar_bar_representation.position2 = np.array([ 0.7, 0.15])
        module_manager.scalar_lut_manager.scalar_bar_representation.position = np.array([ 0.2, 0.1])

        if self.plot_title:
            m.title('step no. %d' % self.aramis_data.current_step, size=0.2)

        # for scalar bar format values in font style 'times'
        module_manager.scalar_lut_manager.label_text_property.font_family = 'times'
        module_manager.scalar_lut_manager.label_text_property.italic = False
        module_manager.scalar_lut_manager.label_text_property.bold = False

        # title font of scalar bar
        module_manager.scalar_lut_manager.title_text_property.font_family = 'times'
        module_manager.scalar_lut_manager.title_text_property.bold = True
        module_manager.scalar_lut_manager.title_text_property.italic = False

        # title font of plot (step no)
        text = scene.children[1].children[0].children[1]
        text.property.font_size = 25
        text.property.font_family = 'times'
        text.property.bold = True
        text.property.italic = True


    clean_scene = Button
    def _clean_scene_fired(self):
        self.scene.mlab.clf()


    view = View(
                Item('plot3d_var'),
                UItem('plot3d_points_flat'),
                UItem('plot3d_points'),
                UItem('plot3d_cracks'),
                UItem('plot3d_var_deformed'),
                Item('_'),
                Item('warp_factor'),
                UItem('clean_scene'),
                id='aramisCDT.view3d',
               )


