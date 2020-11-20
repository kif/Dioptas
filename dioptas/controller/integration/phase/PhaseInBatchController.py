from ....model.util.HelperModule import get_partial_index

# imports for type hinting in PyCharm -- DO NOT DELETE
from ....model.DioptasModel import DioptasModel
from ....widgets.integration import IntegrationWidget
from ....widgets.plot_widgets.ImgWidget import IntegrationImgWidget


class PhaseInBatchController(object):
    """
    PhaseInBatchController handles all the interaction between the phase controls and the plotted lines in the cake view.
    """

    def __init__(self, batch_widget, dioptas_model):
        """
        :param batch_widget: Reference to an IntegrationWidget
        :param dioptas_model: reference to DioptasModel object

        :type batch_widget: IntegrationWidget
        :type dioptas_model: DioptasModel
        """
        self.model = dioptas_model
        self.phase_model = self.model.phase_model
        self.batch_widget = batch_widget
        self.batch_view_widget = batch_widget.img_view  # type: IntegrationImgWidget

        self.connect()

    def connect(self):
        self.phase_model.phase_added.connect(self.add_phase_plot)
        self.model.phase_model.phase_removed.connect(self.batch_view_widget.del_cake_phase)

        self.phase_model.phase_changed.connect(self.update_phase_lines)
        self.phase_model.phase_changed.connect(self.update_phase_color)
        self.phase_model.phase_changed.connect(self.update_phase_visible)

        self.phase_model.reflection_added.connect(self.reflection_added)
        self.phase_model.reflection_deleted.connect(self.reflection_deleted)

    def get_phase_position_and_intensities(self, ind, clip=True):
        """
        Obtains the positions and intensities for lines of a phase with an index ind within the batch view.

        No clipping is used for the first call to add the CakePhasePlot to the ImgWidget. Subsequent calls are used with
        clipping. Thus, only lines within the cake_tth are returned. The visibility of each line is then estimated in
        the ImgWidget based on the length of the clipped and not clipped lists.

        :param ind: the index of the phase
        :param clip: whether or not the lists should be clipped. Clipped means that lines which have positions larger
                     than the
        :return: line_positions, line_intensities
        """
        cake_tth = self.model.batch_model.binning
        if cake_tth is None:
            return
        reflections_tth = self.phase_model.get_phase_line_positions(ind, 'tth',
                                                                    self.model.calibration_model.wavelength * 1e10)
        reflections_intensities = [reflex[1] for reflex in self.phase_model.reflections[ind]]

        cake_line_positions = []
        cake_line_intensities = []

        for ind, tth in enumerate(reflections_tth):
            pos_ind = get_partial_index(cake_tth, tth)
            if pos_ind is not None:
                cake_line_positions.append(pos_ind + 0.5)
                cake_line_intensities.append(reflections_intensities[ind])
            elif clip is False:
                cake_line_positions.append(0)
                cake_line_intensities.append(reflections_intensities[ind])

        return cake_line_positions, cake_line_intensities

    def add_phase_plot(self):
        cake_line_positions, cake_line_intensities = self.get_phase_position_and_intensities(-1, False)

        self.batch_view_widget.add_cake_phase(cake_line_positions, cake_line_intensities,
                                              self.phase_model.phase_colors[-1])

    def update_phase_lines(self, ind):
        cake_line_positions, cake_line_intensities = self.get_phase_position_and_intensities(ind)
        self.batch_view_widget.update_phase_intensities(ind, cake_line_positions, cake_line_intensities)

    def update_phase_color(self, ind):
        self.batch_view_widget.set_cake_phase_color(ind, self.model.phase_model.phase_colors[ind])

    def update_phase_visible(self, ind):
        if self.phase_model.phase_visible[ind] and self.batch_widget.phases_btn.isChecked():
            self.batch_view_widget.show_cake_phase(ind)
        else:
            self.batch_view_widget.hide_cake_phase(ind)

    def reflection_added(self, ind):
        self.batch_view_widget.phases[ind].add_line()

    def reflection_deleted(self, phase_ind, reflection_ind):
        self.batch_view_widget.phases[phase_ind].delete_line(reflection_ind)