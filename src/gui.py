import sys

import PyQt5.QtWidgets as pqtw
import PyQt5.QtCore as pqtc
import PyQt5.QtGui as pqtg
# import PyQt5.QtGui as pqg
# from PyQt5.QtGui import QSurfaceFormat
# import numpy as np

import core
import data_reader
import large_strings


class GUIWindow(pqtw.QMainWindow):
    # all custom signals are handled by GUIWindow
    # fps_signal = pqtc.pyqtSignal(int)
    # reset_signal = pqtc.pyqtSignal(bool)
    # add_tab_signal = pqtc.pyqtSignal(str, bool, str)
    # insert_visual_signal = pqtc.pyqtSignal(int, int, object, object, object)
    # swap_visual_signal = pqtc.pyqtSignal(int, int, int)

    def __init__(self, visualizer: core.Visualizer, _app):
        super().__init__(None, pqtc.Qt.WindowStaysOnTopHint)
        self._app = _app
        self.visualizer = visualizer
        self.mf = MainFrame(self)
        self.setCentralWidget(self.mf)
        # self.mf.setMinimumSize(self.mf.qtab.size())
        # self.move(200, 0)
        self.setWindowTitle("VR Data visualizer 0.5a")
        self.init_menubar()
        self.setGeometry(self._app.primaryScreen().availableGeometry())
        # self.adjustSize()
        self.show()
        # self.fps_signal.connect(self.mf.timer.setInterval)
        # self.reset_signal.connect(self.mf.reset)
        # self.add_tab_signal.connect(self.mf.add_tab)
        # self.insert_visual_signal.connect(self.insert_visual)
        # self.swap_visual_signal.connect(self.swap_visual)

    # def swap_visual(self, tab, w_index, v_index):
        # self.mf.tabs[tab].frames[w_index].swap_visual(v_index)

    # def insert_visual(self, tab, index, class_, *args, **kwargs):
        # self.mf.tabs[tab].frames[index].insert_visual(class_, *args, **kwargs)
        # self.mf.frames[index].insert_visual(class_, *args, **kwargs)

    def init_menubar(self):
        mb = self.menuBar()
        mb.mfile = mb.addMenu("File")
        mb.mhelp = mb.addMenu("Help")
        open_action = mb.mfile.addAction("Subject directory...")
        open_action.triggered.connect(self.open_browser)
        open_obj_action = mb.mfile.addAction("Object directory...")
        open_obj_action.triggered.connect(lambda: self.open_browser(True))

        # Creating a separator action
        separator = pqtw.QAction(self)
        separator.setSeparator(True)
        # Adding the separator to the menu
        mb.mfile.addAction(separator)

        mb.mfile.addAction("Quit").triggered.connect(self.close)

    def open_browser(self, obj=False):
        dialog = pqtw.QFileDialog()
        dialog.setFileMode(pqtw.QFileDialog.Directory)
        dialog.setOption(pqtw.QFileDialog.ShowDirsOnly)
        fname = dialog.getExistingDirectory(self, "Select subject directory")
        if fname:
            print("Selected", fname)
            if not obj:
                self.visualizer.change_base_path(fname + "/")
            else:
                self.visualizer.object_base_path = fname + "/"


class MainFrame(pqtw.QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.frames = []
        self.cf = None
        self.init_ui()
        self.new_control_frame()

    def init_ui(self):
        self.v_layout = pqtw.QVBoxLayout()
        self.g_layout = pqtw.QGridLayout()

        self.v_layout.addLayout(self.g_layout)
        # if self.buttons:
            # self.button_layout = self.init_buttons()
            # self.v_layout.addLayout(self.button_layout)

        self.setLayout(self.v_layout)

    def new_control_frame(self):
        pos = (0, 0, 1, 1)
        self.cf = ControlFrame(self, self.parent().visualizer)
        self.g_layout.addWidget(self.cf, *pos)

    def new_visual_frame(self, visual, *args, **kwargs):
        # pos = kwargs.pop("pos", (0, 0, 1, 1))
        pos = (0, 1, 1, 1)
        new_visual_frame = VisualFrame(self, visual, *args, **kwargs)
        self.cf.vf = new_visual_frame
        self.frames.append(new_visual_frame)
        self.g_layout.addWidget(new_visual_frame, *pos)
        return new_visual_frame

        # self.setStyleSheet(
            # """             QFrame{background-color: black; color: white}
                            # \\\\VispyFrame{background-color: #110626}
                            # VispyFrame{background-color: #24000E}
                            # QDialog{background-color: black}
                            # QTabWidget{
                                # background-color: black; 
                                # color: yellow; 
                                # background: yellow
                            # }
                            # QTabBar{
                                # background: yellow;
                                # border: 2px solid black;
                                # border-bottom-color: yellow;
                                # border-left-color: yellow;
                                # border-right-color: yellow;
                                # border-top-left-radius: 4px;
                                # border-top-right-radius: 4px;
                                # min-width: 8ex;
                                # padding: 2px;
                            # }
                            # V
                            # QComboBox{background-color: black; color: white}
                            # QLineEdit{background-color: black; color: white}
                            # QDial{background-color:yellow}
                            # QTextEdit{background-color: white; color: black;}
                            # QPushButton {background-color: yellow; color: black}
                        # """
        # )

        # self.qtab = pqtw.QTabWidget(self)
        # self.qtab.currentChanged.connect(self.tab_changed)

        # self.timer = pqtc.QTimer(self)
        # self.timer.setInterval(fps)

        # self.tabs = []
        # self.timer.timeout.connect(self.update)
        # self.timer.start()


class ControlFrame(pqtw.QFrame):
    def __init__(self, parent, visualizer: core.Visualizer):
        super(ControlFrame, self).__init__(parent)
        self.visualizer = visualizer 
        self.init_ui()

    def init_ui(self):
        g_width = 1
        g_height = 2
        g_hlen = 2
        g_wlen = 1
        self.g_layout = pqtw.QGridLayout()
        self.setLayout(self.g_layout)

        self.buttons = {}
        self.buttons["add"] = pqtw.QPushButton("Add patch", self)
        self.g_layout.addWidget(
            self.buttons["add"], 0, 0, g_height//g_hlen, g_width//g_wlen)
        self.buttons["add"].clicked.connect(self.add_patch)

        self.patch_list = pqtw.QListWidget()
        # self.patch_list.setFocusPolicy(pqtc.Qt.FocusPolicy.NoFocus)
        self.patch_list.setSizePolicy(pqtw.QSizePolicy(
            pqtw.QSizePolicy.Policy.Minimum, pqtw.QSizePolicy.Policy.Expanding))
        self.patch_list.itemDoubleClicked.connect(self.clicked_item)
        self.g_layout.addWidget(self.patch_list, 1, 0, g_height//g_hlen, g_width//g_wlen)

    def add_patch(self, *args, pp=None, item=None):
        popup = pqtw.QDialog(self)
        popup.show()
        popup.setLayout(pqtw.QGridLayout())
        pl = popup.layout()
        frame = pqtw.QFrame(popup)
        frame.setLayout(pqtw.QStackedLayout())
        frame.layout().addWidget(InsertTrajectoryFrame(popup, pp, item))
        # frame.layout().addWidget(InsertPresetFrame(popup))

        dropdown = pqtw.QComboBox()
        # dropdown.lineEdit().setReadOnly(True)
        dropdown.addItem("Trajectory")
        # dropdown.addItem("Multiple Trajectory Preset")
        if pp is None:
            frame.layout().addWidget(InsertTargetFrame(popup))
            dropdown.addItem("Object")
        dropdown.activated.connect(
            lambda: frame.layout().setCurrentIndex(dropdown.currentIndex()))
        pl.addWidget(dropdown, 0, 0, 1, 1)
        pl.addWidget(frame, 1, 0, 3, 1)

    def edit_trajectory(self, pp, item):
        plot_id = item.data(1)["patch_id"]
        if pp is None:
            item.setData(1, {"type": "plot", "patch_id": plot_id, "deleted": 1})
        else:
            new_id = self.visualizer.edit_plot(pp, plot_id)
            item.setData(1, {"type": item.data(1)["type"], "patch_id": new_id})
        # NOTE this got updated in the above line (possibly) It's a messy control flow
        if "deleted" in item.data(1).keys():
            self.remove_trajectory(item)
        else:
            color = self.visualizer.pp_set[new_id].color
            if type(color) is not str:
                item.setBackground(pqtg.QColor(int(color[0]*255),
                                               int(color[1]*255),
                                               int(color[2]*255)))
            item.setData(1, {"type": item.data(1)["type"], 
                             "patch_id": item.data(1)["patch_id"], 
                             "color": color})

    def edit_qa(self, pp, item_id):
        pass

    def add_trajectory(self, pp, quintile_analysis=False):
        # try:
        if not quintile_analysis:
            plot_id = self.visualizer.add_plot(pp)
            if plot_id is None:
                return
            item = pqtw.QListWidgetItem("Trajectory")
        else:
            plot_id = self.visualizer.perform_analysis(pp)
            if plot_id is None:
                return
            item = pqtw.QListWidgetItem("QA-TEST")
        # except:
            # TODO -- proper exception and warning
            # pass
        # bgc = pqtg.QColor(*color)
        # bgc.setRgbF(*color)
        item.setBackground(pqtg.QColor(int(pp.color[0]*255),
                                       int(pp.color[1]*255),
                                       int(pp.color[2]*255)))
        item.setData(1, {"type": "plot", "patch_id": plot_id, "color": pp.color})
        # item.setFocusPolicy(pqtc.Qt.FocusPolicy.NoFocus)
        self.patch_list.addItem(item)

    def clicked_object(self, item):
        def color_edit():
            color_d = pqtw.QColorDialog(self)
            self.change_color = color_d.getColor(parent=self).getRgbF()[:-1]
            hex = '#%02x%02x%02x' % (int(self.change_color[0]*255),
                                     int(self.change_color[1]*255),
                                     int(self.change_color[2]*255))
            col_button.setStyleSheet(f"background-color:{hex};")

        def del_f():
            self.remove_trajectory(item)
            popup.close()

        def change():
            if type(self.change_color) is tuple:
                color = (*self.change_color, alpha)
            else:
                color = self.change_color
            patch_id = item.data(1)["patch_id"]
            self.visualizer.change_object_color(patch_id, color)
            if type(color) is not str:
                item.setBackground(pqtg.QColor(int(color[0]*255),
                                               int(color[1]*255),
                                               int(color[2]*255)))
            item.setData(1, {"type": item.data(1)["type"], 
                             "patch_id": patch_id, "color": color})

            popup.close()

        # TODO variable
        alpha = 0.9
        popup = pqtw.QDialog(self)
        self.change_color = item.data(1)["color"]
        popup.show()
        popup.setLayout(pqtw.QHBoxLayout())
        del_button = pqtw.QPushButton("Delete", self)
        col_button = pqtw.QPushButton("Color", self)
        change_button = pqtw.QPushButton("Commit Changes", self)
        if type(self.change_color) is str:
            color = self.change_color
        else:
            color = '#%02x%02x%02x' % (int(self.change_color[0]*255),
                                       int(self.change_color[1]*255),
                                       int(self.change_color[2]*255))
        col_button.setStyleSheet(f"background-color:{color};")
        col_button.clicked.connect(color_edit)
        del_button.clicked.connect(del_f)
        change_button.clicked.connect(change)
        popup.layout().addWidget(col_button)
        popup.layout().addWidget(change_button)
        popup.layout().addWidget(del_button)

    def clicked_item(self, item):

        if item.data(1)["type"] == "plot":
            plot_id = item.data(1)["patch_id"]
            pp = self.visualizer.pp_set[plot_id]
            self.add_patch(pp=pp, item=item)
        elif item.data(1)["type"] == "obj":
            self.clicked_object(item)
            # self.visualizer.change_object_color(patch_id, color)

    def remove_trajectory(self, item):
        patch_id = item.data(1)["patch_id"]
        if item.data(1)["type"] == "plot":
            self.visualizer.remove_plot(patch_id)
        elif item.data(1)["type"] == "obj":
            self.visualizer.remove_object(patch_id)
        self.patch_list.takeItem(self.patch_list.row(item))

    def add_target(self, label, x, y, z, size, shape, color):
        # try:
        target_id = self.visualizer.add_target(x, y, z, size, shape, color)
        # except:
            # print("exception
            # TODO -- proper exception and warning
            # pass
        item = pqtw.QListWidgetItem(label)
        # bgc = pqtg.QColor(*color)
        # bgc.setRgbF(*color)
        # item.setBackground(pqtg.QColor(int(color[0]*255),
                                       # int(color[1]*255),
                                       # int(color[2]*255)))
        item.setBackground(pqtg.QColor(color))
        item.setData(1, {"type": "obj", "patch_id": target_id, "color": color})
        # item.setFocusPolicy(pqtc.Qt.FocusPolicy.NoFocus)
        self.patch_list.addItem(item)


# class InsertPresetFrame(pqtw.QFrame):
    # def __init__(self, parent):
        # super(InsertPresetFrame, self).__init__(parent)
        # self.popup = parent
        # # self.hidden_trajectory_frame = InsertTargetFrame(parent)
        # self.fname = self.popup.parent().visualizer.base_path
        # self.fname_label = pqtw.QLabel(self.fname)
        # self.color1 = (0.9, 0., 0.)
        # self.color2 = (0.0, 0.8, 0.)
        # self.avg_color = (1., 1., 1.)
        # self.alpha = 0.3
        # self.avg_alpha = 1.

        # self.h_layout = pqtw.QHBoxLayout()
        # # self.setLayout(self.g_layout)
        # self.setLayout(self.h_layout)

        # self.frame1 = pqtw.QFrame(self)
        # self.frame1.setLayout(pqtw.QVBoxLayout())
        # self.h_layout.addWidget(self.frame1)
        # self.frame2 = pqtw.QFrame(self)
        # self.frame2.setLayout(pqtw.QVBoxLayout())
        # self.h_layout.addWidget(self.frame2)
        # self.frame3 = pqtw.QFrame(self)
        # self.frame3.setLayout(pqtw.QVBoxLayout())
        # self.h_layout.addWidget(self.frame3)

        # self.buttons = {}
        # # self.buttons["get"] = pqtw.QPushButton("Get path...", self)
        # self.buttons["add"] = pqtw.QPushButton("Add trajectory", self)
        # # self.buttons["add"].setEnabled(False)
        # self.buttons["cancel"] = pqtw.QPushButton("Cancel", self)
        # self.buttons["color1"] = pqtw.QPushButton("Color 1", self)
        # hex = '#%02x%02x%02x' % (int(self.color1[0]*255),
                                 # int(self.color1[1]*255),
                                 # int(self.color1[2]*255))
        # self.buttons["color1"].setStyleSheet(f"background-color:{hex};")
        # self.buttons["color1"].clicked.connect(lambda: self.get_color(1))

        # self.buttons["color2"] = pqtw.QPushButton("Color 2", self)
        # hex = '#%02x%02x%02x' % (int(self.color2[0]*255),
                                 # int(self.color2[1]*255),
                                 # int(self.color2[2]*255))
        # self.buttons["color2"].setStyleSheet(f"background-color:{hex};")
        # self.buttons["color2"].clicked.connect(lambda: self.get_color(2))
        # # self.buttons["get"].clicked.connect(self.open_browser)
        # self.buttons["add"].clicked.connect(self.send_preset)
        # self.buttons["cancel"].clicked.connect(self.popup.close)
        # # self.g_layout.addWidget(self.fname_label, 0, 0, 1, 2)
        # # self.g_layout.addWidget(self.buttons["get"], 1, 0, 1, 2)
        # # self.g_layout.addWidget(self.buttons["color"], 2, 0, 1, 2)
        # # self.g_layout.addWidget(self.buttons["add"], 15, 0, 1, 1)
        # # self.g_layout.addWidget(self.buttons["cancel"], 3, 1, 1, 1)

        # selection_groupBox = pqtw.QGroupBox("Select subjects")
        # s_radio1 = pqtw.QRadioButton("All")
        # s_radio2 = pqtw.QRadioButton("Select")
        # s_radio3 = pqtw.QRadioButton("Custom group")
        # sgl = pqtw.QGridLayout(selection_groupBox)
        # subject_drop = pqtw.QComboBox(selection_groupBox)
        # subject_group_selector_dialog = pqtw.QDialog(self)
        # subject_group_selector_dialog.setLayout(pqtw.QGridLayout())
        # # TODO make the size of this dialog right
        # # subject_group_selector_dialog.setSizePolicy(pqtw.QSizePolicy(
            # # pqtw.QSizePolicy.Policy.Expanding, pqtw.QSizePolicy.Policy.Expanding))
        # loading_list = pqtw.QListWidget(self)
        # loading_list.setDragDropMode(pqtw.QAbstractItemView.DragDrop)
        # loading_list.setSelectionMode(pqtw.QAbstractItemView.ExtendedSelection)
        # loading_list.setDefaultDropAction(pqtc.Qt.MoveAction)
        # loading_list.setSortingEnabled(True)
        # # loading_list.setSizePolicy(pqtw.QSizePolicy(
            # # pqtw.QSizePolicy.Policy.Expanding, pqtw.QSizePolicy.Policy.Expanding))
        # self.using_list = pqtw.QListWidget(self)
        # self.using_list.setDragDropMode(pqtw.QAbstractItemView.DragDrop)
        # self.using_list.setSelectionMode(pqtw.QAbstractItemView.ExtendedSelection)
        # self.using_list.setDefaultDropAction(pqtc.Qt.MoveAction)
        # # self.using_list.setSizePolicy(pqtw.QSizePolicy(
            # # pqtw.QSizePolicy.Policy.Expanding, pqtw.QSizePolicy.Policy.Expanding))
        # ll_label = pqtw.QLabel("Unused subjects", subject_group_selector_dialog)
        # ul_label = pqtw.QLabel("Used subjects", subject_group_selector_dialog)
        # subject_group_selector_dialog.layout().addWidget(ul_label, 0, 0, 1, 1)
        # subject_group_selector_dialog.layout().addWidget(ll_label, 0, 1, 1, 1)
        # subject_group_selector_dialog.layout().addWidget(self.using_list, 1, 0, 10, 1)
        # subject_group_selector_dialog.layout().addWidget(loading_list, 1, 1, 10, 1)
        # sgsd_ok_button = pqtw.QPushButton("Ok", subject_group_selector_dialog)
        # sgsd_cancel_button = pqtw.QPushButton("Reset", subject_group_selector_dialog)
        # subject_group_selector_dialog.layout().addWidget(sgsd_ok_button, 11, 0, 1, 1)
        # subject_group_selector_dialog.layout().addWidget(sgsd_cancel_button, 11, 1, 1, 1)
        # sgsd_ok_button.clicked.connect(subject_group_selector_dialog.hide)
        # subject_group_select_button = pqtw.QPushButton("Create group", self)
        # subject_group_select_button.clicked.connect(subject_group_selector_dialog.show)

        # def reset_lists():
            # for i in range(self.using_list.count()):
                # loading_list.addItem(self.using_list.item(i).data(0))
            # self.using_list.clear()
        # sgsd_cancel_button.clicked.connect(reset_lists)

        # for subject in sorted(self.popup.parent().visualizer.subjects.keys()):
            # subject_drop.addItem(subject)
            # loading_list.addItem(subject)
        # # subject_text = pqtw.QLineEdit("eg. 1, 2, 8, 10-13")
        # # self.subject_text = subject_text
        # self.subject_drop = subject_drop
        # self.selection = [s_radio1, s_radio2, s_radio3]

        # subject_drop.setEnabled(False)
        # subject_group_select_button.setEnabled(False)

        # def disable_fields(r):
            # if r == 1:
                # subject_drop.setEnabled(False)
                # subject_group_select_button.setEnabled(False)
            # if r == 2:
                # subject_drop.setEnabled(True)
                # subject_group_select_button.setEnabled(False)
            # if r == 3:
                # subject_drop.setEnabled(False)
                # subject_group_select_button.setEnabled(True)

        # s_radio1.clicked.connect(lambda: disable_fields(1))
        # s_radio2.clicked.connect(lambda: disable_fields(2))
        # s_radio3.clicked.connect(lambda: disable_fields(3))
        # s_radio1.setChecked(True)
        # sgl.addWidget(s_radio1, 0, 0, 1, 4)
        # sgl.addWidget(s_radio2, 1, 0, 1, 1)
        # sgl.addWidget(subject_drop, 1, 1, 1, 3)
        # sgl.addWidget(s_radio3, 2, 0, 1, 1)
        # sgl.addWidget(subject_group_select_button, 2, 1, 1, 3)
        # selection_groupBox.setLayout(sgl)

        # self.buttons["avg_color"] = pqtw.QPushButton("Color for Average", self)
        # hex = '#%02x%02x%02x' % (int(self.avg_color[0]*255),
                                 # int(self.avg_color[1]*255),
                                 # int(self.avg_color[2]*255))
        # self.buttons["avg_color"].setStyleSheet(f"background-color:{hex};")
        # self.buttons["avg_color"].clicked.connect(lambda: self.get_color(0, True))

        # self.preset_list = pqtw.QListWidget(self)
        # self.preset_list.addItem(pqtw.QListWidgetItem("preset1"))
        # self.preset_list.setCurrentRow(0)
        # self.preset_list.setSelectionMode(pqtw.QAbstractItemView.SingleSelection)

        # self.frame1.layout().addWidget(self.fname_label)
        # self.frame1.layout().addWidget(self.buttons["add"])

        # self.frame2.layout().addWidget(self.fname_label)
        # self.frame2.layout().addWidget(selection_groupBox)
        # self.frame2.layout().addWidget(self.buttons["cancel"])

        # self.frame3.layout().addWidget(self.buttons["color1"])
        # self.frame3.layout().addWidget(self.buttons["color2"])
        # self.frame3.layout().addWidget(self.buttons["avg_color"])

    # def get_color(self, id, average=False):
        # color_d = pqtw.QColorDialog(self)
        # c = color_d.getColor(parent=self).getRgbF()[:-1]
        # hex = '#%02x%02x%02x' % (int(c[0]*255),
                                 # int(c[1]*255),
                                 # int(c[2]*255))
        # if not average:
            # if id == 1:
                # self.color1 = c 
                # self.buttons["color1"].setStyleSheet(f"background-color:{hex};")
            # else:
                # self.color2 = c 
                # self.buttons["color2"].setStyleSheet(f"background-color:{hex};")
        # else:
            # self.avg_color = c
            # self.buttons["avg_color"].setStyleSheet(f"background-color:{hex};")

    # def send_preset(self):
        # preset_id = self.preset_list.currentItem().data(0)

        # def parse_custom_int():
            # subjects = []
            # for i in range(self.using_list.count()):
                # subjects.append(self.using_list.item(i).text())
            # return subjects

        # subjects = []
        # if self.selection[2].isChecked():
            # subjects = parse_custom_int()
        # elif self.selection[1].isChecked():
            # subjects = [self.subject_drop.currentText()]
        # else:
            # subjects = self.popup.parent().visualizer.subjects
        # if not subjects:
            # warning = pqtw.QMessageBox(pqtw.QMessageBox.Icon.Warning,
                                       # "Empty subject list",
                                       # "The subject list is empty!",
                                       # parent=self)
            # warning.setInformativeText(large_strings.no_subject_warning)
            # warning.show()
            # return

        # if preset_id == "preset1":
            # filter_set = {"congruency": "1"}
            # self.send_patch(self.color1, self.alpha, self.avg_color, self.avg_alpha,
                            # 1,
                            # filter_set, subjects,
                            # 1, 0,
                            # )
            # filter_set = {"congruency": "0"}
            # self.send_patch(self.color2, self.alpha, self.avg_color, self.avg_alpha,
                            # 1,
                            # filter_set, subjects,
                            # 2, 0,
                            # )

        # self.popup.close()

    # def send_patch(self, color, alpha, avg_color, avg_alpha, 
                   # avg_bool,
                   # custom_filter_set, subjects,
                   # transform, normalisation):
        # color = (*color, alpha)
        # avg_color = (*avg_color, avg_alpha)
        # # avg_bool = self.avg_checkbox.checkState()

        # filter_types = []

        # pp = core.PlotParameters(subjects, color, 
                                 # filter_types, 
                                 # avg_color, avg_bool,
                                 # transform,
                                 # 0.95,
                                 # normalisation,
                                 # custom_filter_set
                                 # )
        # self.popup.parent().add_trajectory(pp)


class InsertTrajectoryFrame(pqtw.QFrame):
    def __init__(self, parent, pp: core.PlotParameters = None, item=None):
        super(InsertTrajectoryFrame, self).__init__(parent)
        self.popup = parent

        self.pp = pp
        self.item = item
        self.fname = self.popup.parent().visualizer.base_path
        self.fname_label = pqtw.QLabel(self.fname)
        # TODO cycle this
        self.color = pp.color[:3] if pp else (0.9, 0., 0.)
        self.avg_color = pp.avg_color[:3] if pp else (1., 1., 1.)
        # TODO variabel
        self.alpha = 0.3
        self.avg_alpha = 1.

        # self.g_layout = pqtw.QGridLayout()
        self.h_layout = pqtw.QHBoxLayout()
        # self.setLayout(self.g_layout)
        self.setLayout(self.h_layout)

        self.frame1 = pqtw.QFrame(self)
        self.frame1.setLayout(pqtw.QVBoxLayout())
        self.h_layout.addWidget(self.frame1)
        self.frame2 = pqtw.QFrame(self)
        self.frame2.setLayout(pqtw.QVBoxLayout())
        self.h_layout.addWidget(self.frame2)
        self.frame3 = pqtw.QFrame(self)
        self.frame3.setLayout(pqtw.QVBoxLayout())
        self.h_layout.addWidget(self.frame3)

        self.buttons = {}
        # self.buttons["get"] = pqtw.QPushButton("Get path...", self)
        self.buttons["add"] = pqtw.QPushButton("Add trajectory", self)
        if pp is not None:
            self.buttons["delete"] = pqtw.QPushButton("Delete trajectory", self)
            self.buttons["delete"].clicked.connect(self.delete)
        if pp:
            self.buttons["add"].setText("Edit trajectory")
        # self.buttons["add"].setEnabled(False)
        self.buttons["cancel"] = pqtw.QPushButton("Cancel", self)
        self.buttons["color"] = pqtw.QPushButton("Color", self)
        hex = '#%02x%02x%02x' % (int(self.color[0]*255),
                                 int(self.color[1]*255),
                                 int(self.color[2]*255))
        print("COLOR", hex)
        self.buttons["color"].setStyleSheet(f"background-color:{hex};")
        # self.buttons["get"].clicked.connect(self.open_browser)
        self.buttons["add"].clicked.connect(self.send_patch)
        self.buttons["cancel"].clicked.connect(self.popup.close)
        self.buttons["color"].clicked.connect(self.get_color)
        # self.g_layout.addWidget(self.fname_label, 0, 0, 1, 2)
        # self.g_layout.addWidget(self.buttons["get"], 1, 0, 1, 2)
        # self.g_layout.addWidget(self.buttons["color"], 2, 0, 1, 2)
        # self.g_layout.addWidget(self.buttons["add"], 15, 0, 1, 1)
        # self.g_layout.addWidget(self.buttons["cancel"], 3, 1, 1, 1)

        selection_groupBox = pqtw.QGroupBox("Select subjects")
        s_radio1 = pqtw.QRadioButton("All")
        s_radio2 = pqtw.QRadioButton("Select")
        s_radio3 = pqtw.QRadioButton("Custom group")
        sgl = pqtw.QGridLayout(selection_groupBox)
        subject_drop = pqtw.QComboBox(selection_groupBox)
        subject_group_selector_dialog = pqtw.QDialog(self)
        subject_group_selector_dialog.setLayout(pqtw.QGridLayout())
        # TODO make the size of this dialog right
        # subject_group_selector_dialog.setSizePolicy(pqtw.QSizePolicy(
            # pqtw.QSizePolicy.Policy.Expanding, pqtw.QSizePolicy.Policy.Expanding))
        loading_list = pqtw.QListWidget(self)
        loading_list.setDragDropMode(pqtw.QAbstractItemView.DragDrop)
        loading_list.setSelectionMode(pqtw.QAbstractItemView.ExtendedSelection)
        loading_list.setDefaultDropAction(pqtc.Qt.MoveAction)
        loading_list.setSortingEnabled(True)
        # loading_list.setSizePolicy(pqtw.QSizePolicy(
            # pqtw.QSizePolicy.Policy.Expanding, pqtw.QSizePolicy.Policy.Expanding))
        self.using_list = pqtw.QListWidget(self)
        self.using_list.setDragDropMode(pqtw.QAbstractItemView.DragDrop)
        self.using_list.setSelectionMode(pqtw.QAbstractItemView.ExtendedSelection)
        self.using_list.setDefaultDropAction(pqtc.Qt.MoveAction)
        # self.using_list.setSizePolicy(pqtw.QSizePolicy(
            # pqtw.QSizePolicy.Policy.Expanding, pqtw.QSizePolicy.Policy.Expanding))
        ll_label = pqtw.QLabel("Unused subjects", subject_group_selector_dialog)
        ul_label = pqtw.QLabel("Used subjects", subject_group_selector_dialog)
        subject_group_selector_dialog.layout().addWidget(ul_label, 0, 0, 1, 1)
        subject_group_selector_dialog.layout().addWidget(ll_label, 0, 1, 1, 1)
        subject_group_selector_dialog.layout().addWidget(self.using_list, 1, 0, 10, 1)
        subject_group_selector_dialog.layout().addWidget(loading_list, 1, 1, 10, 1)
        sgsd_ok_button = pqtw.QPushButton("Ok", subject_group_selector_dialog)
        sgsd_cancel_button = pqtw.QPushButton("Reset", subject_group_selector_dialog)
        subject_group_selector_dialog.layout().addWidget(sgsd_ok_button, 11, 0, 1, 1)
        subject_group_selector_dialog.layout().addWidget(sgsd_cancel_button, 11, 1, 1, 1)
        sgsd_ok_button.clicked.connect(subject_group_selector_dialog.hide)
        subject_group_select_button = pqtw.QPushButton("Create group", self)
        subject_group_select_button.clicked.connect(subject_group_selector_dialog.show)

        def reset_lists():
            for i in range(self.using_list.count()):
                loading_list.addItem(self.using_list.item(i).data(0))
            self.using_list.clear()
        sgsd_cancel_button.clicked.connect(reset_lists)

        for subject in sorted(self.popup.parent().visualizer.subjects.keys()):
            subject_drop.addItem(subject)
            loading_list.addItem(subject)
        # subject_text = pqtw.QLineEdit("eg. 1, 2, 8, 10-13")
        # self.subject_text = subject_text
        self.subject_drop = subject_drop
        self.selection = [s_radio1, s_radio2, s_radio3]

        if pp is None or len(pp.subjects) != 1:
            subject_drop.setEnabled(False)
            subject_group_select_button.setEnabled(False)

        def disable_fields(r):
            if r == 1:
                subject_drop.setEnabled(False)
                subject_group_select_button.setEnabled(False)
            if r == 2:
                subject_drop.setEnabled(True)
                subject_group_select_button.setEnabled(False)
            if r == 3:
                subject_drop.setEnabled(False)
                subject_group_select_button.setEnabled(True)

        s_radio1.clicked.connect(lambda: disable_fields(1))
        s_radio2.clicked.connect(lambda: disable_fields(2))
        s_radio3.clicked.connect(lambda: disable_fields(3))
        if pp is None or len(pp.subjects) == len(self.popup.parent().visualizer.subjects.keys()):
            s_radio1.setChecked(True)
        elif len(pp.subjects) == 1:
            s_radio2.setChecked(True)
            subject_drop.setCurrentText(pp.subjects[0])
        else:
            # TODO redo how that one works
            s_radio3.setChecked(True)

        sgl.addWidget(s_radio1, 0, 0, 1, 4)
        sgl.addWidget(s_radio2, 1, 0, 1, 1)
        sgl.addWidget(subject_drop, 1, 1, 1, 3)
        sgl.addWidget(s_radio3, 2, 0, 1, 1)
        sgl.addWidget(subject_group_select_button, 2, 1, 1, 3)
        selection_groupBox.setLayout(sgl)
        # self.g_layout.addWidget(selection_groupBox, 12, 0, 2, 2)
        n_groupBox = pqtw.QGroupBox("Normalisation")
        n_radio1 = pqtw.QRadioButton("No normalisation")
        n_radio2 = pqtw.QRadioButton("Per Subject")
        n_radio3 = pqtw.QRadioButton("Total")
        ngl = pqtw.QHBoxLayout(n_groupBox)
        if pp is None or pp.normalisation == 0:
            n_radio1.setChecked(True)
        elif pp.normalisation == 1:
            n_radio2.setChecked(True)
        else:
            n_radio3.setChecked(True)
        ngl.addWidget(n_radio1)
        ngl.addWidget(n_radio2)
        ngl.addWidget(n_radio3)
        n_groupBox.setLayout(ngl)
        self.n_filters = [n_radio1, n_radio2, n_radio3]

        c_groupBox = pqtw.QGroupBox("Congruency criteria")
        c_radio1 = pqtw.QRadioButton("All")
        c_radio2 = pqtw.QRadioButton("Congruent")
        c_radio3 = pqtw.QRadioButton("Incongruent")
        cgl = pqtw.QHBoxLayout(c_groupBox)
        if pp is None or not (core.FilterType.CONGRUENT in pp.filter_types
                              or core.FilterType.INCONGRUENT in pp.filter_types):
            c_radio1.setChecked(True)
        elif core.FilterType.CONGRUENT in pp.filter_types:
            c_radio2.setChecked(True)
        elif core.FilterType.INCONGRUENT in pp.filter_types:
            c_radio3.setChecked(True)
        cgl.addWidget(c_radio1)
        cgl.addWidget(c_radio2)
        cgl.addWidget(c_radio3)
        c_groupBox.setLayout(cgl)
        # self.g_layout.addWidget(c_groupBox, 4, 0, 2, 2)
        self.c_filters = [c_radio1, c_radio2, c_radio3]

        c2_groupBox = pqtw.QGroupBox("2nd order congruency criteria")
        c2_radio1 = pqtw.QRadioButton("All")
        c2_radio2 = pqtw.QRadioButton("Congruent")
        c2_radio3 = pqtw.QRadioButton("Incongruent")
        cgl2 = pqtw.QHBoxLayout(c2_groupBox)
        if pp is None or not (core.FilterType.CONGRUENT2 in pp.filter_types
                              or core.FilterType.INCONGRUENT2 in pp.filter_types):
            c2_radio1.setChecked(True)
        elif core.FilterType.CONGRUENT2 in pp.filter_types:
            c2_radio2.setChecked(True)
        elif core.FilterType.INCONGRUENT2 in pp.filter_types:
            c2_radio3.setChecked(True)
        cgl2.addWidget(c2_radio1)
        cgl2.addWidget(c2_radio2)
        cgl2.addWidget(c2_radio3)
        c2_groupBox.setLayout(cgl2)
        # self.g_layout.addWidget(c2_groupBox, 6, 0, 2, 2)
        self.c2_filters = [c2_radio1, c2_radio2, c2_radio3]

        l_groupBox = pqtw.QGroupBox("Stimulus location")
        l_radio1 = pqtw.QRadioButton("All")
        l_radio2 = pqtw.QRadioButton("Left")
        l_radio3 = pqtw.QRadioButton("Right")
        lgl = pqtw.QHBoxLayout(l_groupBox)
        if pp is None or not (core.FilterType.LEFT in pp.filter_types
                              or core.FilterType.RIGHT in pp.filter_types):
            l_radio1.setChecked(True)
        elif core.FilterType.CONGRUENT in pp.filter_types:
            l_radio2.setChecked(True)
        elif core.FilterType.INCONGRUENT in pp.filter_types:
            l_radio3.setChecked(True)
        lgl.addWidget(l_radio1)
        lgl.addWidget(l_radio2)
        lgl.addWidget(l_radio3)
        l_groupBox.setLayout(lgl)
        self.l_filters = [l_radio1, l_radio2, l_radio3]
        # self.g_layout.addWidget(l_groupBox, 8, 0, 2, 2)

        filter_dialog = pqtw.QDialog(self)
        self.custom_filter_frame = CustomFilterFrame(
            filter_dialog, self.popup.parent().visualizer.get_custom_filter_list())
        filter_dialog.setLayout(pqtw.QHBoxLayout())
        filter_dialog.layout().addWidget(self.custom_filter_frame)

        fd_button = pqtw.QPushButton("Set custom criteria", self)
        fd_button.clicked.connect(filter_dialog.show)

        self.buttons["avg_color"] = pqtw.QPushButton("Color for Average", self)
        hex = '#%02x%02x%02x' % (int(self.avg_color[0]*255),
                                 int(self.avg_color[1]*255),
                                 int(self.avg_color[2]*255))
        self.buttons["avg_color"].setStyleSheet(f"background-color:{hex};")
        self.buttons["avg_color"].clicked.connect(lambda: self.get_color(True))
        self.avg_checkbox = pqtw.QCheckBox("Plot mean trajectory?", self)

        if pp and pp.average:
            self.avg_checkbox.setChecked(True)
        self.ci_frame = pqtw.QFrame(self)
        self.ci_label = pqtw.QLabel("Confidence interval:", self.ci_frame)
        self.conf_spinbox = pqtw.QDoubleSpinBox(self.ci_frame)
        self.ci_frame.setLayout(pqtw.QHBoxLayout())
        self.ci_frame.layout().addWidget(self.ci_label)
        self.ci_frame.layout().addWidget(self.conf_spinbox)
        self.conf_spinbox.setRange(0, 1)
        self.conf_spinbox.setSingleStep(0.01)
        if pp is None:
            self.conf_spinbox.setValue(0.95)
        else:
            self.conf_spinbox.setValue(pp.conf_int)

        t_groupBox = pqtw.QGroupBox("Transformation")
        t_radio1 = pqtw.QRadioButton("No transform")
        t_radio2 = pqtw.QRadioButton("To right")
        t_radio3 = pqtw.QRadioButton("To left")
        tgl = pqtw.QHBoxLayout(t_groupBox)
        if pp is None or core.Transform.NONE == pp.transform:
            t_radio1.setChecked(True)
        elif core.Transform.LR == pp.transform:
            t_radio2.setChecked(True)
        elif core.Transform.RL == pp.transform:
            t_radio3.setChecked(True)
        tgl.addWidget(t_radio1)
        tgl.addWidget(t_radio3)
        tgl.addWidget(t_radio2)
        t_groupBox.setLayout(tgl)
        self.t_filters = [t_radio1, t_radio2, t_radio3]

        qa_groupBox = pqtw.QGroupBox("Quintile Analysis")
        self.qa_check = pqtw.QCheckBox(self)

        def toggle_qa():
            on = self.qa_check.isChecked()
            if on:
                self.qa_sorting_drop.setEnabled(True)
                self.buttons["add"].setText("Add QA plot")
                self.n_bins_spinbox.setEnabled(True)
                new_text = f"Colour sequence:\n{self.popup.parent().visualizer.color_seq}"
                self.buttons["color"].setText(new_text)
                # self.buttons["color"].clicked.connect(self.select_cseq)
            else:
                self.qa_sorting_drop.setEnabled(False)
                self.buttons["add"].setText("Add trajectory")
                self.buttons["color"].setText("Colour")
                self.buttons["color"].clicked.connect(self.get_color)
                if pp:
                    self.buttons["add"].setText("Edit trajectory")
                self.n_bins_spinbox.setEnabled(False)
        self.qa_check.clicked.connect(toggle_qa)

        self.qa_sorting_drop = pqtw.QComboBox(qa_groupBox)
        for field in (self.popup.parent().visualizer.get_custom_filter_list(True)):
            self.qa_sorting_drop.addItem(field)
        self.width_label = pqtw.QLabel("n bins:", self)
        self.n_bins_spinbox = pqtw.QSpinBox(self)
        self.n_bins_spinbox.setEnabled(False)
        self.n_bins_spinbox.setRange(2, 10)
        self.n_bins_spinbox.setValue(5)

        self.qa_sorting_drop.setEnabled(False)
        qagl = pqtw.QHBoxLayout(qa_groupBox)
        qagl.addWidget(self.qa_check)
        qagl.addWidget(self.qa_sorting_drop)
        qagl.addWidget(self.width_label)
        qagl.addWidget(self.n_bins_spinbox)
        qa_groupBox.setLayout(qagl)

        if pp is not None:
            if pp.qap:
                self.qa_check.setChecked(True)
                self.n_bins_spinbox.setValue(pp.n_bins)
                self.qa_sorting_drop.setCurrentText(pp.sort_field)
            self.qa_check.setEnabled(False)

        self.frame1.layout().addWidget(self.fname_label)
        self.frame1.layout().addWidget(selection_groupBox)
        self.frame1.layout().addWidget(self.buttons["color"])
        self.frame1.layout().addWidget(self.buttons["add"])
        if pp is not None:
            self.frame1.layout().addWidget(self.buttons["delete"])

        self.frame2.layout().addWidget(c_groupBox)
        self.frame2.layout().addWidget(c2_groupBox)
        self.frame2.layout().addWidget(l_groupBox)
        self.frame2.layout().addWidget(fd_button)
        self.frame2.layout().addWidget(self.buttons["cancel"])

        self.frame3.layout().addWidget(self.avg_checkbox)
        self.frame3.layout().addWidget(self.buttons["avg_color"])
        self.frame3.layout().addWidget(self.ci_frame)
        self.frame3.layout().addWidget(t_groupBox)
        self.frame3.layout().addWidget(n_groupBox)
        self.frame3.layout().addWidget(qa_groupBox)

    # TODO
    def select_cseq(self):
        pass
    
    def get_color(self, average=False):
        color_d = pqtw.QColorDialog(self)
        c = color_d.getColor(parent=self).getRgbF()[:-1]
        hex = '#%02x%02x%02x' % (int(c[0]*255),
                                 int(c[1]*255),
                                 int(c[2]*255))
        if not average:
            self.color = c 
            self.buttons["color"].setStyleSheet(f"background-color:{hex};")
        else:
            self.avg_color = c
            self.buttons["avg_color"].setStyleSheet(f"background-color:{hex};")

    # def open_browser(self):
        # self.fname = pqtw.QFileDialog().getOpenFileName(
            # self, ("Results path"), "../data", ("trial_results (trial_results.csv)"))[0]
        # self.buttons["add"].setEnabled(True)
        # self.fname_label.setText(self.fname)
    def delete(self):
        self.popup.parent().edit_trajectory(None, self.item)
        self.popup.close()

    def send_patch(self):
        self.color = (*self.color, self.alpha)
        self.avg_color = (*self.avg_color, self.avg_alpha)
        avg_bool = self.avg_checkbox.checkState()

        filter_types = []
        i = 0
        for fs in [self.c_filters, self.c2_filters, self.l_filters]:
            for f in fs:
                if f.isChecked():
                    if i % 3:
                        filter_types.append(i)
                i += 1

        def parse_custom_int():
            subjects = []
            for i in range(self.using_list.count()):
                subjects.append(self.using_list.item(i).text())
            return subjects

        subjects = []
        if self.selection[2].isChecked():
            try:
                subjects = parse_custom_int()
            except ValueError:
                # TODO make a dialogue, maybe handle differently
                print("parse_custom_int failed, using ALL subjects instead")
                subjects = self.popup.parent().visualizer.subjects
        elif self.selection[1].isChecked():
            subjects = [self.subject_drop.currentText()]
        else:
            subjects = self.popup.parent().visualizer.subjects

        if not subjects:
            warning = pqtw.QMessageBox(pqtw.QMessageBox.Icon.Warning,
                                       "Empty subject list",
                                       "The subject list is empty!",
                                       parent=self)
            warning.setInformativeText(large_strings.no_subject_warning)
            warning.show()
            return

        # NOTE -- this is a bit of a hack for transform and normalisation. 
        # Changes may be needed
        for i, t in enumerate(self.t_filters):
            if t.isChecked():
                transform = i 
        for i, n in enumerate(self.n_filters):
            if n.isChecked():
                normalisation = i 

        if not self.qa_check.isChecked():
            new_pp = core.PlotParameters(subjects, self.color, 
                                         filter_types, 
                                         self.avg_color, avg_bool,
                                         transform,
                                         self.conf_spinbox.value(),
                                         normalisation,
                                         self.custom_filter_frame.get_filters()
                                         )
            if self.pp is None:
                self.popup.parent().add_trajectory(new_pp)
            else:
                if (self.pp.subjects != new_pp.subjects
                        or self.pp.filter_types != new_pp.filter_types
                        or self.pp.custom_filter_set != new_pp.custom_filter_set
                        or self.pp.transform != new_pp.transform
                        or self.pp.normalisation != new_pp.normalisation):
                    new_pp.plot_changed.append("plots")
                if self.pp.color != new_pp.color:
                    new_pp.plot_changed.append("col")
                if self.pp.avg_color != new_pp.avg_color:
                    new_pp.plot_changed.append("avg col")
                if not self.pp.average and new_pp.average:
                    new_pp.plot_changed.append("average added")
                elif self.pp.average and not new_pp.average:
                    new_pp.plot_changed.append("average removed")
                elif self.pp.average and self.pp.conf_int != new_pp.conf_int:
                    new_pp.plot_changed.append("average removed")
                    new_pp.plot_changed.append("average added")
                self.popup.parent().edit_trajectory(new_pp, self.item)

        else:
            qap = core.PlotParameters(subjects, self.color, 
                                      filter_types, 
                                      self.avg_color, avg_bool,
                                      transform,
                                      self.conf_spinbox.value(),
                                      normalisation,
                                      self.custom_filter_frame.get_filters(),
                                      qap=True, n_bins=self.n_bins_spinbox.value(),
                                      sort_field=self.qa_sorting_drop.currentText(),
                                      )
            self.popup.parent().add_trajectory(qap, True)
        self.popup.close()


class CustomFilterFrame(pqtw.QFrame):
    def __init__(self, parent, possible_filters):
        super(CustomFilterFrame, self).__init__(parent)
        self.field_value_dict = possible_filters
        self.label_dropdowns = {}
        self.setLayout(pqtw.QVBoxLayout())
        for field_name, valid_values in self.field_value_dict.items():
            frame = pqtw.QFrame(self)
            frame.setLayout(pqtw.QHBoxLayout())
            label = pqtw.QLabel(field_name, self)
            dropdown = pqtw.QComboBox(self)
            dropdown.addItem("Any")
            for vv in valid_values:
                dropdown.addItem(str(vv))
            frame.layout().addWidget(label)
            frame.layout().addWidget(dropdown)
            self.label_dropdowns[field_name] = dropdown
            self.layout().addWidget(frame)
        reset = pqtw.QPushButton("Reset", self)
        ok = pqtw.QPushButton("Ok", self)
        ok.clicked.connect(self.parent().hide)
        bframe = pqtw.QFrame(self)
        bframe.setLayout(pqtw.QHBoxLayout())
        bframe.layout().addWidget(ok)
        bframe.layout().addWidget(reset)
        self.layout().addWidget(bframe)

        def reset_f():
            for dropdown in self.label_dropdowns.values():
                dropdown.setCurrentText("Any")
        reset.clicked.connect(reset_f)

    def get_filters(self):
        return {k: v.currentText() for k, v in self.label_dropdowns.items()}


class InsertTargetFrame(pqtw.QFrame):
    def __init__(self, parent):
        super(InsertTargetFrame, self).__init__(parent)
        self.popup = parent
        self.color = (0., 0.7, 0.)
        self.alpha = 0.4
        self.object_fname = None

        self.g_layout = pqtw.QGridLayout()
        self.v_layout = pqtw.QVBoxLayout()
        self.setLayout(self.v_layout)
        # self.inputx = pqtw.QLineEdit("-.1")
        # self.inputy = pqtw.QLineEdit(".9")
        # self.inputz = pqtw.QLineEdit(".6")
        self.label = pqtw.QLineEdit("Object")
        self.buttons = {}
        self.buttons["select"] = pqtw.QPushButton("Select input file", self)
        self.buttons["add"] = pqtw.QPushButton("Add Object", self)
        self.buttons["cancel"] = pqtw.QPushButton("Cancel", self)
        # self.buttons["color"] = pqtw.QPushButton("Color", self)
        # hex = '#%02x%02x%02x' % (int(self.color[0]*255),
                                 # int(self.color[1]*255),
                                 # int(self.color[2]*255))
        # self.buttons["color"].setStyleSheet(f"background-color:{hex};")
        self.buttons["add"].clicked.connect(self.read_file)
        self.buttons["cancel"].clicked.connect(self.popup.close)
        self.buttons["add"].setEnabled(False)
        # self.buttons["color"].clicked.connect(self.get_color)
        self.buttons["select"].clicked.connect(self.get_input)
        self.v_layout.addWidget(self.buttons["select"])
        self.v_layout.addWidget(self.buttons["add"])
        self.v_layout.addWidget(self.buttons["cancel"])
        # self.g_layout.addWidget(self.label, 0, 0, 1, 4)
        # self.g_layout.addWidget(self.inputx, 1, 0, 1, 1)
        # self.g_layout.addWidget(self.inputy, 1, 1, 1, 1)
        # self.g_layout.addWidget(self.inputz, 1, 2, 1, 1)
        # self.g_layout.addWidget(self.buttons["add"], 1, 3, 1, 1)
        # self.g_layout.addWidget(self.buttons["color"], 2, 0, 1, 4)
        # self.g_layout.addWidget(self.buttons["cancel"], 3, 0, 1, 4)

    def get_input(self):
        dialog = pqtw.QFileDialog()
        dialog.setDirectory(self.parent().parent().parent().visualizer.object_base_path)
        self.object_fname = dialog.getOpenFileName(self, "Selfect input file")[0]
        if self.object_fname:
            self.buttons["add"].setEnabled(True)
        else:
            self.buttons["add"].setEnabled(False)

    # TODO set this up to be safe with no file (disable add)
    def read_file(self):
        objects = data_reader.get_object_data(self.object_fname)
        for obj in objects.values():
            self.send_patch(obj)
        self.popup.close()

    def get_color(self):
        def set(color):
            self.color = color
        color_d = pqtw.QColorDialog(self)
        self.color = color_d.getColor(parent=self).getRgbF()[:-1]
        hex = '#%02x%02x%02x' % (int(self.color[0]*255),
                                 int(self.color[1]*255),
                                 int(self.color[2]*255))
        self.buttons["color"].setStyleSheet(f"background-color:{hex};")

    def send_patch(self, obj):
        # self.color = (*self.color, self.alpha)
        # # TODO check value safety
        # x = float(self.inputx.text())
        # y = float(self.inputy.text())
        # z = float(self.inputz.text())
        self.popup.parent().add_target(self.label.text(), 
                                       obj.x, obj.y, obj.z, obj.size, obj.shape, obj.c)


class VisualFrame(pqtw.QFrame):
    def __init__(self, parent, visual, *args, **kwargs):
        super(VisualFrame, self).__init__(parent)
        self.box = pqtw.QHBoxLayout(self)
        self.index = 0
        # self.setSizePolicy(pqtw.QSizePolicy.Policy)
        self.setSizePolicy(pqtw.QSizePolicy(
            pqtw.QSizePolicy.Policy.Expanding, pqtw.QSizePolicy.Policy.Expanding))
        # size = kwargs.pop("size", (800, 800))
        # self.setMaximumSize(*size)
        # self.setMinimumWidth(self.parent.size.)
        self.visuals = []
        if visual is not None:
            self.visuals.append(visual)
            visual.canvas.parent = self
        # TODO is this stuff needed?
        # self.add_widget()
        self.show()

    def set_visual(self, viz):
        self.box.addWidget(viz.canvas.native)

    def insert_visual(self, class_, *args, **kwargs):
        self.visuals.append(class_(self, *args, **kwargs))
        if len(self.visuals) > 1:
            self.box.itemAt(self.index).widget().hide()
        self.index = len(self.visuals) - 1
        self.add_widget()
        self.adjustSize()

    def swap_visual(self, index):
        self.box.itemAt(self.index).widget().hide()
        self.index = index
        self.box.itemAt(self.index).widget().show()

    def update(self):
        if self.visuals:
            self.visuals[self.index].iterate()

    def reset(self):
        if self.visuals:
            self.visuals[self.index].reset()

    def add_widget(self):
        if self.visuals[self.index].frontend == "vispy":
            self.box.addWidget(self.visuals[self.index].canvas.native)
        elif self.visuals[self.index].frontend == "matplotlib":
            self.box.addWidget(self.visuals[self.index].canvas)
        else:
            raise NameError("Only vispy and matplotlib currently supported")


class GUI:
    def __init__(self, visualizer):
        if pqtw.QApplication.instance() is None:
            self._app = pqtw.QApplication(sys.argv)
        self._window = GUIWindow(visualizer, self._app)

    def fps(self, fps):
        self._window.fps_signal.emit(1000 // fps)

    def quit(self):
        self._window.close()

    def reset(self, reseed=False):
        self._window.reset_signal.emit(reseed)

    def show_windows(self):
        self._window.show()

    def _begin(self):
        self._app.exec_()
