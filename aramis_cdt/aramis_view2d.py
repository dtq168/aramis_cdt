#-------------------------------------------------------------------------
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
#-------------------------------------------------------------------------

import matplotlib

# matplotlib.use('Qt4Agg')
matplotlib.use('WxAgg')

from matplotlib.figure import Figure
import os
import platform
from scipy import stats
import tempfile
import time
from traits.api import \
    HasTraits, Instance, Button, Bool, Directory
from traitsui.api import UItem, View, Group

from aramis_cdt import AramisCDT
from aramis_data import AramisFieldData
from aramis_info import AramisInfo
import matplotlib.pyplot as plt
import numpy as np


if platform.system() == 'Linux':
    sysclock = time.time
elif platform.system() == 'Windows':
    sysclock = time.clock


class AramisPlot2D(HasTraits):

    '''This class manages 2D views for AramisCDT variables
    '''

    aramis_info = Instance(AramisInfo)

    aramis_data = Instance(AramisFieldData)

    aramis_cdt = Instance(AramisCDT)

    figure = Instance(Figure)

    save_plot = Bool(False)

    show_plot = Bool(True)

    save_dir = Directory

    def _save_dir_default(self):
        return os.getcwd()

    temp_dir = Directory

    def _temp_dir_default(self):
        return tempfile.mkdtemp()

    plot2d = Button

    def _plot2d_fired(self):
        aramis_data = self.aramis_data
        aramis_cdt = self.aramis_cdt
        fig = self.figure
        fig.clf()

        ax = fig.add_subplot(2, 2, 1)
        ax.plot(aramis_data.i_cut.T, aramis_data.d_ux.T, color='black')
        ax.plot(
            aramis_data.i_cut[0, :], aramis_data.d_ux_avg, color='red', linewidth=2)
        # for x in aramis_data.d_ux:
        #    ax.plot(aramis_data.i_cut.T, np.convolve(x, np.ones(10) / 10., 'same'), color='green', linewidth=0.3)
        y_max_lim = ax.get_ylim()[-1]
        ax.vlines(aramis_data.i_cut[0, :-1], [0], aramis_cdt.crack_filter_avg * y_max_lim,
                  color='magenta', linewidth=1, zorder=10)
        ax.set_title('d_ux')

        ax2 = fig.add_subplot(2, 2, 2)
        ax2.plot(aramis_data.i_cut.T, aramis_data.ux_arr.T, color='green')
        ax2.plot(
            aramis_data.i_cut[0, :], aramis_data.ux_arr_avg, color='red', linewidth=2)
        y_min_lim = np.min(ax2.get_ylim())
        y_max_lim = np.max(ax2.get_ylim())
        ax2.vlines(aramis_data.i_cut[0, :-1], y_min_lim, aramis_cdt.crack_filter_avg * y_max_lim + ~aramis_cdt.crack_filter_avg * y_min_lim,
                   color='magenta', linewidth=1, zorder=10)
        ax2.set_title('ux')

        ax3 = fig.add_subplot(2, 2, 3)
        ax3.plot(aramis_data.i_cut[0, :], aramis_data.dd_ux_avg, color='black')
        ax3.plot(aramis_data.i_cut[0, :], aramis_data.ddd_ux_avg, color='blue')
        y_max_lim = ax3.get_ylim()[-1]
        ax3.vlines(aramis_data.i_cut[0, :-1], [0], aramis_cdt.crack_filter_avg * y_max_lim,
                   color='magenta', linewidth=1, zorder=10)
        ax3.set_title('dd_ux, ddd_ux')

        ax = fig.add_subplot(2, 2, 4)
        ax.plot(aramis_data.i_cut.T, aramis_data.delta_ux_arr.T, color='black')
        ax.plot(aramis_data.i_cut[
                0, :], aramis_data.delta_ux_arr_avg, color='red', linewidth=2)
        y_max_lim = ax.get_ylim()[-1]
        ax.vlines(aramis_data.i_cut[0, :-1], [0], aramis_cdt.crack_filter_avg * y_max_lim,
                  color='magenta', linewidth=1, zorder=10)
        ax.set_title('delta_ux')


#         ax = fig.add_subplot(2, 2, 4)
#         from aramis_data import get_d
#         ir = aramis_data.integ_radius
#         ax.plot(aramis_data.x_arr_0.T[ir:-ir, :],
#                 (get_d(aramis_data.x_arr_0 + aramis_data.ux_arr, ir).T - get_d(aramis_data.x_arr_0, ir).T)[ir:-ir, :], color='black')
#        ax.plot(aramis_data.x_arr_0.T[ir:-ir, :],
#                 get_d(aramis_data.x_arr_0 + aramis_data.ux_arr, ir).T[ir:-ir, :], color='black')
#         xx = get_d(aramis_data.x_arr_0 + aramis_data.ux_arr, ir)
#         print xx[:, ir]
#         print xx[:, ir][:, None] * np.ones(xx.shape[1])[None, :]
#         ax.plot(aramis_data.x_arr_0.T[ir:-ir, :],
#                 (xx - xx[:, ir][:, None] * np.ones(xx.shape[1])[None, :]).T[ir:-ir, :] * 1000, color='black')

        plt.suptitle(self.aramis_info.specimen_name + ' - %d' %
                     aramis_data.current_step)

        aramis_cdt.crack_spacing_avg

        if self.save_plot:
            fig.savefig(os.path.join(self.save_dir, 'plot2d.png'))

        if self.show_plot:
            fig.canvas.draw()

    plot_crack_hist = Button

    def _plot_crack_hist_fired(self):

        aramis_cdt = self.aramis_cdt
        fig = self.figure
        fig.clf()
        ax = fig.add_subplot(111)

        ax.hist(aramis_cdt.crack_arr.flatten(), bins=40, normed=True)

        ax.set_xlabel('crack_width [mm]')
        ax.set_ylabel('frequency [-]')

        ax2 = ax.twinx()
        ax2.hist(aramis_cdt.crack_arr.flatten(), normed=True,
                 histtype='step', color='black',
                 cumulative=True, bins=40, linewidth=2)
        ax2.set_ylabel('probability [-]')

        ax.set_title(aramis_cdt.aramis_info.specimen_name + ' - %d' %
                     self.aramis_data.current_step)

        mu = float(aramis_cdt.crack_arr.flatten().mean())
        sigma = float(aramis_cdt.crack_arr.flatten().std())
        skew = float(stats.skew(aramis_cdt.crack_arr.flatten()))
        textstr = '$\mu=%.3g$\n$\sigma=%.3g$\n$\gamma_1=%.3g$' % (
            mu, sigma, skew)

        # these are matplotlib.patch.Patch properties
        props = dict(boxstyle='round', facecolor='wheat', alpha=1)

        # place a text box in upper left in axes coords,
        ax.text(0.95, 0.95, textstr, transform=ax.transAxes, fontsize=14,
                verticalalignment='top', horizontalalignment='right', bbox=props)

        if self.save_plot:
            fig.savefig(os.path.join(self.save_dir, 'crack_hist.png'))

        if self.show_plot:
            fig.canvas.draw()

    plot_number_of_cracks_t = Button

    def _plot_number_of_cracks_t_fired(self):

        aramis_cdt = self.aramis_cdt
        fig = self.figure
        fig.clf()
        ax = fig.add_subplot(111)

        ax.plot(aramis_cdt.control_strain_t, aramis_cdt.number_of_cracks_t)

        ax.set_xlabel('control strain')
        ax.set_ylabel('number of cracks')

        if self.show_plot:
            fig.canvas.draw()

    plot_force_step = Button

    def _plot_force_step_fired(self):

        aramis_cdt = self.aramis_cdt
        fig = self.figure
        fig.clf()
        ax = fig.add_subplot(111)

        ax.set_title('')
        ax.plot(self.aramis_info.step_list, self.aramis_data.force)

        ax.set_xlabel('step')
        ax.set_ylabel('force_t [kN]')

        if self.save_plot:
            fig.savefig(os.path.join(self.save_dir, 'force_time.png'))

        if self.show_plot:
            fig.canvas.draw()

    plot_stress_strain = Button

    def _plot_stress_strain_fired(self):

        aramis_cdt = self.aramis_cdt
        fig = self.figure
        fig.clf()
        ax = fig.add_subplot(111)

        ax.set_title('')
        ax.plot(aramis_cdt.control_strain_t, self.aramis_data.stress)

        ax.set_xlabel('control strain [-]')
        ax.set_ylabel('nominal stress [MPa]')

        if self.save_plot:
            fig.savefig(os.path.join(self.save_dir, 'stress_strain.png'))

        if self.show_plot:
            fig.canvas.draw()

    plot_w_strain = Button

    def _plot_w_strain_fired(self):

        aramis_cdt = self.aramis_cdt
        fig = self.figure
        fig.clf()
        ax = fig.add_subplot(111)

        ax.set_title('')
        plt.plot(aramis_cdt.control_strain_t,
                 aramis_cdt.crack_width_avg_t.T)

        ax.set_xlabel('control strain [-]')
        ax.set_ylabel('crack width [mm]')

        if self.save_plot:
            fig.savefig(os.path.join(self.save_dir, 'w_strain.png'))

        if self.show_plot:
            fig.canvas.draw()

    plot_subw_strain = Button

    def _plot_subw_strain_fired(self):

        aramis_cdt = self.aramis_cdt
        fig = self.figure
        fig.clf()
        ax = fig.add_subplot(111)

        ax.set_title('')
        ax.plot(aramis_cdt.control_strain_t,
                aramis_cdt.crack_width_t.T)

        ax.set_xlabel('control strain [-]')
        ax.set_ylabel('subcrack width [mm]')

        if self.save_plot:
            fig.savefig(os.path.join(self.save_dir, 'subw_strain.png'))

        if self.show_plot:
            fig.canvas.draw()

    plot_stress_strain_init = Button

    def _plot_stress_strain_init_fired(self):

        aramis_cdt = self.aramis_cdt
        fig = self.figure
        fig.clf()
        ax = fig.add_subplot(111)

        ax.set_title('')
        ax.plot(aramis_cdt.control_strain_t, self.aramis_data.stress)
        ax.plot(aramis_cdt.control_strain_t[aramis_cdt.init_step_avg_lst],
                self.aramis_data.stress[aramis_cdt.init_step_avg_lst],
                'ro', linewidth=4)
        ax.plot(aramis_cdt.control_strain_t[aramis_cdt.init_step_lst],
                self.aramis_data.stress[aramis_cdt.init_step_lst],
                'kx', linewidth=4)

        ax.set_xlabel('control strain [-]')
        ax.set_ylabel('nominal stress [MPa]')

        if self.save_plot:
            fig.savefig(os.path.join(self.save_dir, 'stress_strain_init.png'))

        if self.show_plot:
            fig.canvas.draw()

    plot_crack_init = Button

    def _plot_crack_init_fired(self):

        aramis_cdt = self.aramis_cdt

        fig = self.figure
        fig.clf()
        ax = fig.add_subplot(111)
        ax.set_title('')
        ax.vlines(np.arange(len(aramis_cdt.init_step_avg_lst)) + 0.5,
                  [0], aramis_cdt.init_step_avg_lst)
        ax.set_xlabel('crack number')
        ax.set_ylabel('initiation step')

        if self.save_plot:
            fig.savefig(os.path.join(self.save_dir, 'crack_init.png'))

        if self.show_plot:
            fig.canvas.draw()

    plot_force_time = Button

    def _plot_force_time_fired(self):
        fig = self.figure
        fig.clf()
        ax = fig.add_subplot(111)

        ax.set_title('')
        ax.plot(self.aramis_data.step_times, self.aramis_data.force)
        ax.set_xlabel('Time')
        ax.set_ylabel('Force')

        if self.show_plot:
            fig.canvas.draw()

    plot_number_of_missing_facets = Button

    def _plot_number_of_missing_facets_fired(self):

        aramis_cdt = self.aramis_cdt
        fig = self.figure
        fig.clf()
        ax = fig.add_subplot(111)

        y = aramis_cdt.number_of_missing_facets_t
        ax.plot(self.aramis_info.step_list, y)

        ax.set_xlabel('step')
        ax.set_ylabel('number of missing facets')
        ax.set_title('missing facets in time')

        if self.save_plot:
            fig.savefig(
                os.path.join(self.save_dir, 'number_of_missing_facets.png'))

        if self.show_plot:
            fig.canvas.draw()

    plot_strain_crack_avg = Button

    def _plot_strain_crack_avg_fired(self):

        aramis_cdt = self.aramis_cdt
        aramis_data = self.aramis_data

        fig = self.figure
        fig.clf()
        ax = fig.add_subplot(111, aspect='equal')
        ax.set_title(aramis_cdt.aramis_info.specimen_name + ' - %d' %
                     self.aramis_data.current_step)

        plot3d_var = getattr(aramis_data, 'd_ux')

        mask = np.logical_or(np.isnan(self.aramis_data.x_arr_0),
                             self.aramis_data.x_0_mask[0, :, :])
        mask = None
#         plt.scatter(aramis_cdt.x_arr_0[mask],
#                    aramis_cdt.y_arr_0[mask], c=plot3d_var[mask], cmap=my_cmap_lin,
#                    marker='s')

        print plot3d_var[mask].shape
        # contour the data, plotting dots at the nonuniform data points.
#         CS = plt.contour(aramis_cdt.x_arr_0[mask][0, :, :],
#                          aramis_cdt.y_arr_0[mask][0, :, :],
#                          plot3d_var[mask][0, :, :], 25, linewidths=.5, colors='k')
        # plotting filled contour
        CS = ax.contourf(self.aramis_data.x_arr_0,
                         self.aramis_data.y_arr_0,
                         plot3d_var, 256, cmap=plt.get_cmap('jet'))

        ax.vlines(self.aramis_data.x_arr_0[0, :][self.aramis_cdt.crack_filter_avg],
                  [0], np.nanmax(self.aramis_data.y_arr_0),
                  color='white', zorder=10, linewidth=2)

        ax.set_xlabel('x [mm]')
        ax.set_ylabel('y [mm]')

        fig.colorbar(CS, orientation='horizontal')

        if self.save_plot:
            fig.savefig(os.path.join(self.save_dir, 'strain_crack_avg.png'))

        if self.show_plot:
            fig.canvas.draw()

    plot_crack_filter_crack_avg = Button

    def _plot_crack_filter_crack_avg_fired(self):
        aramis_cdt = self.aramis_cdt
        aramis_data = self.aramis_data

        fig = self.figure
        fig.clf()
        ax = fig.add_subplot(111, aspect='equal')
        ax.set_title(aramis_cdt.aramis_info.specimen_name + ' - %d' %
                     self.aramis_data.current_step)

        plot3d_var = getattr(aramis_data, 'd_ux')

        mask = np.logical_or(np.isnan(self.aramis_data.x_arr_0),
                             self.aramis_data.x_0_mask[0, :, :])
        mask = None
#         plt.scatter(aramis_cdt.x_arr_0[mask],
#                    aramis_cdt.y_arr_0[mask], c=plot3d_var[mask], cmap=my_cmap_lin,
#                    marker='s')

        print plot3d_var[mask].shape
        # contour the gridded data, plotting dots at the nonuniform data points.
#         CS = plt.contour(aramis_cdt.x_arr_0[mask][0, :, :],
#                          aramis_cdt.y_arr_0[mask][0, :, :],
#                          plot3d_var[mask][0, :, :], 25, linewidths=.5, colors='k')
        # plotting filled contour
        CS = ax.contourf(self.aramis_data.x_arr_0,
                         self.aramis_data.y_arr_0,
                         plot3d_var, 2, cmap=plt.get_cmap('binary'))
        ax.plot(self.aramis_data.x_arr_0, self.aramis_data.y_arr_0, 'ko')

        ax.plot(self.aramis_data.x_arr_0[aramis_cdt.crack_filter],
                self.aramis_data.y_arr_0[
                    aramis_cdt.crack_filter], linestyle='None',
                marker='.', color='white')
#         CS = ax.contourf(aramis_cdt.x_arr_0,
#                          aramis_cdt.y_arr_0,
#                          plot3d_var, 256, cmap=plt.get_cmap('jet'))
#
#         ax.plot(aramis_cdt.x_arr_0[aramis_cdt.crack_filter],
#                  aramis_cdt.y_arr_0[aramis_cdt.crack_filter],
#                  'k.')

        ax.vlines(self.aramis_data.x_arr_0[0, :][aramis_cdt.crack_filter_avg],
                  [0], np.nanmax(self.aramis_data.y_arr_0[mask]),
                  color='magenta', zorder=100, linewidth=2)

        ax.set_xlabel('x [mm]')
        ax.set_ylabel('y [mm]')

        # plt.colorbar()

        # plt.axis('equal')

        if self.save_plot:
            fig.savefig(
                os.path.join(self.save_dir, 'crack_filter_crack_avg.png'))

        if self.show_plot:
            fig.canvas.draw()

    test_figure = Instance(plt.Figure)

    plot_test = Button

    def _plot_test_fired(self):
        aramis_cdt = self.aramis_cdt
        if self.test_figure == None:
            self.test_figure = plt.figure(figsize=(12, 6), dpi=100)
            self.test_figure.canvas.mpl_connect(
                'close_event', self.handle_close)
        fig = self.test_figure
        fig.clf()

        fig.suptitle(aramis_cdt.aramis_info.specimen_name + ' - %d' %
                     self.aramis_data.current_step, y=1)

        ax_diag = plt.subplot2grid((3, 3), (0, 0))  # no colorbar (2, 3)
        ax_diag.locator_params(nbins=4)
        ax_hist = plt.subplot2grid((3, 3), (1, 0))  # no colorbar (2, 3)
        ax_hist.locator_params(nbins=4)
        ax_area = plt.subplot2grid((3, 3), (0, 1), rowspan=2, colspan=2,
                                   adjustable='box', aspect='equal')  # no colorbar (2, 3)

        x = self.aramis_data.step_times  # self.aramis_cdt.control_strain_t
        stress = self.aramis_data.ad_channels_arr[:, 1]
        ax_diag.plot(x, stress)
        ax_diag.plot(x[self.aramis_data.current_step],
                     stress[self.aramis_data.current_step], 'ro')
        ax_diag.plot(x[aramis_cdt.init_step_avg_lst], stress[
                     aramis_cdt.init_step_avg_lst], 'go', ms=4)

        ax_diag.set_xlabel('step number [-]')
        ax_diag.set_ylabel('nominal stress [MPa]')
        ax_diag.set_xlim(0, ax_diag.get_xlim()[1])

        if aramis_cdt.crack_arr.size != 0:
            ax_hist.hist(aramis_cdt.crack_arr.flatten(), bins=40, normed=True)

        ax_hist.set_xlabel('crack_width [mm]')
        ax_hist.set_ylabel('frequency [-]')

        ax_hist_2 = ax_hist.twinx()

        if aramis_cdt.crack_arr.size != 0:
            ax_hist_2.hist(aramis_cdt.crack_arr.flatten(), normed=True,
                           histtype='step', color='black',
                           cumulative=True, bins=40, linewidth=2)
        ax_hist_2.set_ylabel('probability [-]')
        ax_hist_2.set_ylim(0, 1)
        # ax_hist.set_xlim(0, 0.15)
        # ax_hist.set_ylim(0, 50)

        plot3d_var = getattr(self.aramis_data, 'd_ux')

        CS = ax_area.contourf(self.aramis_data.x_arr_0,
                              self.aramis_data.y_arr_0,
                              plot3d_var, 2, cmap=plt.get_cmap('binary'))
        ax_area.plot(self.aramis_data.x_arr_0, self.aramis_data.y_arr_0, 'ko')

        # ax_area.plot(self.aramis_data.x_arr_0[aramis_cdt.crack_filter],
        #         self.aramis_data.y_arr_0[aramis_cdt.crack_filter], linestyle='None',
        #         marker='.', color='white')

        # ax_area.scatter(self.aramis_data.x_arr_0[aramis_cdt.crack_filter],
        # self.aramis_data.y_arr_0[aramis_cdt.crack_filter], color='white',
        # zorder=10, s=aramis_cdt.crack_arr * 50)
        sc = ax_area.scatter(self.aramis_data.x_arr_0[aramis_cdt.crack_filter],
                             self.aramis_data.y_arr_0[aramis_cdt.crack_filter], cmap=plt.cm.get_cmap(
                                 'jet'),  # color='white',
                             zorder=100, s=aramis_cdt.crack_arr * 300, c=aramis_cdt.crack_arr, edgecolors='none')

        ax_col = plt.subplot2grid((3, 3), (2, 1), rowspan=1, colspan=2,
                                  adjustable='box')
        fig.colorbar(sc, cax=ax_col, orientation='horizontal')

#         ax_area.vlines(self.aramis_data.x_arr_0[0, :][aramis_cdt.crack_filter_avg],
#                        [0], np.nanmax(self.aramis_data.y_arr_0[None]),
#                        color='magenta', zorder=100, linewidth=2)
#         ax_area.vlines(aramis_cdt.x_arr_0[10, :-1][aramis_cdt.crack_filter_avg],
#                    [0], np.nanmax(aramis_cdt.y_arr_0),
#                    color='red', zorder=100, linewidth=1)

        ax_area.set_xlabel('x [mm]')
        ax_area.set_ylabel('y [mm]')

        # ax_area.set_colorbar(CS, orientation='horizontal')
        fig.tight_layout()

#         cbar_ax = fig.add_axes([0.45, 0.15, 0.5, 0.03])
#         fig.colorbar(CS, cax=cbar_ax, orientation='horizontal')

        fig.canvas.draw()

        if self.save_plot:
            fig.savefig(os.path.join(self.save_dir, '%s%04d.png'
                                     % (aramis_cdt.aramis_info.specimen_name, self.aramis_data.current_step)))

        if self.show_plot:
            fig.show()

    def handle_close(self, evt):
        print 'Closed Figure!'
        import gc
        print gc.collect()
        self.test_figure = None

    create_animation = Button

    def _create_animation_fired(self):
        aramis_cdt = self.aramis_cdt
        save_plot, show_plot = self.save_plot, self.show_plot
        self.save_plot = False
        self.show_plot = False
        start_step_idx = self.aramis_data.current_step
        fname_pattern = '%s%04d'
        for step_idx in self.aramis_info.step_list:
            self.aramis_data.current_step = step_idx
            self.plot_test = True
            self.test_figure.savefig(os.path.join(self.temp_dir, fname_pattern
                                                  % (aramis_cdt.aramis_info.specimen_name, self.aramis_data.current_step)))

        try:
            os.system('ffmpeg -framerate 3 -i %s.png -vcodec ffv1 -sameq %s.avi' %
                      (os.path.join(self.temp_dir, fname_pattern.replace('%s', aramis_cdt.aramis_info.specimen_name)),
                       os.path.join(self.save_dir, aramis_cdt.aramis_info.specimen_name)))
        except:
            print 'Cannot create video in avi format. Check if you have "ffmpeg" in in your system path.'

        try:
            os.system('convert -verbose -delay 25 %s* %s.gif' %
                      (os.path.join(self.temp_dir, aramis_cdt.aramis_info.specimen_name),
                       os.path.join(self.save_dir, aramis_cdt.aramis_info.specimen_name)))
        except:
            print 'Cannot create animated gif. Check if you have "convert" in in your system path.'

        self.save_plot = save_plot
        self.show_plot = show_plot
        self.aramis_data.current_step = start_step_idx

    view = View(
        Group(
            UItem('plot2d'),
            UItem('plot_crack_hist'),
            UItem('plot_number_of_cracks_t'),
            UItem('plot_stress_strain_init'),
            UItem('plot_stress_strain'),
            UItem('plot_w_strain'),
            UItem('plot_subw_strain'),
            UItem('plot_strain_crack_avg'),
            UItem('plot_crack_filter_crack_avg'),
            UItem('plot_crack_init'),
            UItem('plot_test'),
            '_',
            '_',
            UItem('create_animation'),
            label='Plot results',
        ),
        Group(
            UItem('plot_force_time'),
            UItem('plot_force_step'),
            UItem('plot_number_of_missing_facets'),
            label='Check data',
        ),
        id='aramisCDT.view2d',
    )
