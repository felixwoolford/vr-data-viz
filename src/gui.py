import sys

import PyQt5.QtWidgets as pqtw
import PyQt5.QtCore as pqtc
import PyQt5.QtGui as pqtg
# import PyQt5.QtGui as pqg
# from PyQt5.QtGui import QSurfaceFormat
# import numpy as np

# import core

class GUIWindow(pqtw.QMainWindow):
    # all custom signals are handled by GUIWindow
    # fps_signal = pqtc.pyqtSignal(int)
    # reset_signal = pqtc.pyqtSignal(bool)
    # add_tab_signal = pqtc.pyqtSignal(str, bool, str)
    # insert_visual_signal = pqtc.pyqtSignal(int, int, object, object, object)
    # swap_visual_signal = pqtc.pyqtSignal(int, int, int)

    def __init__(self, visualizer, _app):
        super().__init__(None, pqtc.Qt.WindowStaysOnTopHint)
        self._app = _app
        self.visualizer = visualizer
        self.mf = MainFrame(self)
        self.setCentralWidget(self.mf)
        # self.mf.setMinimumSize(self.mf.qtab.size())
        # self.move(200, 0)
        self.setWindowTitle("TODO")
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
        open_action = mb.mfile.addAction("Open")
        open_action.triggered.connect(self.open_browser)

        # Creating a separator action
        separator = pqtw.QAction(self)
        separator.setSeparator(True)
        # Adding the separator to the menu
        mb.mfile.addAction(separator)

        mb.mfile.addAction("Quit").triggered.connect(self.close)

    def open_browser(self):
        fname = pqtw.QFileDialog().getOpenFileName(self, "./", "")[0]
        lines = self.visualizer.open_data(fname)

        print("opened", fname)

        self.visualizer.set_plots(lines)


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
    def __init__(self, parent, visualizer):
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

    def add_patch(self):
        popup = pqtw.QDialog(self)
        popup.show()
        popup.setLayout(pqtw.QGridLayout())
        pl = popup.layout()
        frame = pqtw.QFrame(popup)
        frame.setLayout(pqtw.QStackedLayout())
        frame.layout().addWidget(InsertTrajectoryFrame(popup))
        frame.layout().addWidget(InsertTargetFrame(popup))

        dropdown = pqtw.QComboBox()
        # dropdown.lineEdit().setReadOnly(True)
        dropdown.addItem("Trajectory")
        dropdown.addItem("Target")
        dropdown.activated.connect(
            lambda: frame.layout().setCurrentIndex(dropdown.currentIndex()))
        pl.addWidget(dropdown, 0, 0, 1, 1)
        pl.addWidget(frame, 1, 0, 3, 1)

    def add_trajectory(self, subjects, color, filter_types):
        # try:
        print("filtes", filter_types)
        plot_id = self.visualizer.add_plot(subjects, color, filter_types)
        # except:
            # TODO -- proper exception and warning
            # pass
        item = pqtw.QListWidgetItem("Trajectory")
        # bgc = pqtg.QColor(*color)
        # bgc.setRgbF(*color)
        item.setBackground(pqtg.QColor(int(color[0]*255),
                                       int(color[1]*255),
                                       int(color[2]*255)))
        item.setData(1, {"plot_id": plot_id, "color": color})
        # item.setFocusPolicy(pqtc.Qt.FocusPolicy.NoFocus)
        self.patch_list.addItem(item)

    # TODO this is busted for now
    def clicked_item(self, item):
        def color_edit():
            color_d = pqtw.QColorDialog(self)
            self.change_color = color_d.getColor().getRgbF()[:-1]
            hex = '#%02x%02x%02x' % (int(self.change_color[0]*255),
                                     int(self.change_color[1]*255),
                                     int(self.change_color[2]*255))
            col_button.setStyleSheet(f"background-color:{hex};")

        def del_f():
            self.remove_trajectory(item)
            popup.close()

        def change():
            self.edit_trajectory(item, (*self.change_color, alpha))
            popup.close()

        # TODO variable
        alpha = 0.4
        popup = pqtw.QDialog(self)
        self.change_color = item.data(1)["color"]
        popup.show()
        popup.setLayout(pqtw.QHBoxLayout())
        del_button = pqtw.QPushButton("Delete", self)
        col_button = pqtw.QPushButton("Color", self)
        change_button = pqtw.QPushButton("Commit Changes", self)
        hex = '#%02x%02x%02x' % (int(self.change_color[0]*255),
                                 int(self.change_color[1]*255),
                                 int(self.change_color[2]*255))
        col_button.setStyleSheet(f"background-color:{hex};")
        col_button.clicked.connect(color_edit)
        del_button.clicked.connect(del_f)
        change_button.clicked.connect(change)
        popup.layout().addWidget(col_button)
        popup.layout().addWidget(change_button)
        popup.layout().addWidget(del_button)

    def edit_trajectory(self, item, color):
        plot_id = item.data(1)["plot_id"]
        self.visualizer.change_plot_color(plot_id, color)
        item.setBackground(pqtg.QColor(int(color[0]*255),
                                       int(color[1]*255),
                                       int(color[2]*255)))
        item.setData(1, {"plot_id": plot_id, "color": color})

    # TODO make remove patch generic!!
    def remove_trajectory(self, item):
        plot_id = item.data(1)["plot_id"]
        self.visualizer.remove_plot(plot_id)
        self.patch_list.takeItem(self.patch_list.row(item))

    def add_target(self, label, x, y, z, color):
        # try:
        target_id = self.visualizer.add_target(x, y, z, color)
        # except:
            # print("exception
            # TODO -- proper exception and warning
            # pass
        item = pqtw.QListWidgetItem(label)
        # bgc = pqtg.QColor(*color)
        # bgc.setRgbF(*color)
        item.setBackground(pqtg.QColor(int(color[0]*255),
                                       int(color[1]*255),
                                       int(color[2]*255)))
        item.setData(1, {"type": "target", "target_id": target_id, "color": color})
        # item.setFocusPolicy(pqtc.Qt.FocusPolicy.NoFocus)
        self.patch_list.addItem(item)



class InsertTrajectoryFrame(pqtw.QFrame):
    def __init__(self, parent):
        super(InsertTrajectoryFrame, self).__init__(parent)
        self.popup = parent

        self.fname = self.popup.parent().visualizer.base_path
        self.fname_label = pqtw.QLabel(self.fname)
        # TODO cycle this
        self.color = (0.7, 0., 0.)
        # TODO variabel
        self.alpha = 0.2

        self.g_layout = pqtw.QGridLayout()
        self.setLayout(self.g_layout)

        self.buttons = {}
        # self.buttons["get"] = pqtw.QPushButton("Get path...", self)
        self.buttons["add"] = pqtw.QPushButton("Add trajectory", self)
        # self.buttons["add"].setEnabled(False)
        self.buttons["cancel"] = pqtw.QPushButton("Cancel", self)
        self.buttons["color"] = pqtw.QPushButton("Color", self)
        hex = '#%02x%02x%02x' % (int(self.color[0]*255),
                                 int(self.color[1]*255),
                                 int(self.color[2]*255))
        self.buttons["color"].setStyleSheet(f"background-color:{hex};")
        # self.buttons["get"].clicked.connect(self.open_browser)
        self.buttons["add"].clicked.connect(self.send_patch)
        self.buttons["cancel"].clicked.connect(self.popup.close)
        self.buttons["color"].clicked.connect(self.get_color)
        self.g_layout.addWidget(self.fname_label, 0, 0, 1, 2)
        # self.g_layout.addWidget(self.buttons["get"], 1, 0, 1, 2)
        self.g_layout.addWidget(self.buttons["color"], 2, 0, 1, 2)
        self.g_layout.addWidget(self.buttons["add"], 3, 0, 1, 1)
        self.g_layout.addWidget(self.buttons["cancel"], 3, 1, 1, 1)

        selection_groupBox = pqtw.QGroupBox("Select subjects")
        s_radio1 = pqtw.QRadioButton("All")
        s_radio2 = pqtw.QRadioButton("Select")
        s_radio3 = pqtw.QRadioButton("Custom indices")
        sgl = pqtw.QGridLayout(selection_groupBox)
        subject_drop = pqtw.QComboBox(selection_groupBox)
        for subject in self.popup.parent().visualizer.subjects:
            subject_drop.addItem(subject)
        subject_text = pqtw.QLineEdit("eg. 1, 2, 8, 10-13")
        self.subject_text = subject_text
        self.subject_drop = subject_drop
        self.selection = [s_radio1, s_radio2, s_radio3]

        subject_drop.setEnabled(False)
        subject_text.setEnabled(False)

        def disable_fields(r):
            if r == 1:
                subject_drop.setEnabled(False)
                subject_text.setEnabled(False)
            if r == 2:
                subject_drop.setEnabled(True)
                subject_text.setEnabled(False)
            if r == 3:
                subject_drop.setEnabled(False)
                subject_text.setEnabled(True)

        s_radio1.clicked.connect(lambda: disable_fields(1))
        s_radio2.clicked.connect(lambda: disable_fields(2))
        s_radio3.clicked.connect(lambda: disable_fields(3))
        s_radio1.setChecked(True)
        sgl.addWidget(s_radio1, 0, 0, 1, 4)
        sgl.addWidget(s_radio2, 1, 0, 1, 1)
        sgl.addWidget(subject_drop, 1, 1, 1, 3)
        sgl.addWidget(s_radio3, 2, 0, 1, 1)
        sgl.addWidget(subject_text, 2, 1, 1, 3)
        selection_groupBox.setLayout(sgl)
        self.g_layout.addWidget(selection_groupBox, 12, 0, 2, 2)

        c_groupBox = pqtw.QGroupBox("Filter congruency")
        c_radio1 = pqtw.QRadioButton("No filter")
        c_radio2 = pqtw.QRadioButton("Congruent")
        c_radio3 = pqtw.QRadioButton("Incongruent")
        cgl = pqtw.QHBoxLayout(c_groupBox)
        c_radio1.setChecked(True)
        cgl.addWidget(c_radio1)
        cgl.addWidget(c_radio2)
        cgl.addWidget(c_radio3)
        c_groupBox.setLayout(cgl)
        self.g_layout.addWidget(c_groupBox, 4, 0, 2, 2)
        self.c_filters = [c_radio1, c_radio2, c_radio3]

        c2_groupBox = pqtw.QGroupBox("Filter 2nd order congruency")
        c2_radio1 = pqtw.QRadioButton("No filter")
        c2_radio2 = pqtw.QRadioButton("Congruent")
        c2_radio3 = pqtw.QRadioButton("Incongruent")
        cgl2 = pqtw.QHBoxLayout(c2_groupBox)
        c2_radio1.setChecked(True)
        cgl2.addWidget(c2_radio1)
        cgl2.addWidget(c2_radio2)
        cgl2.addWidget(c2_radio3)
        c2_groupBox.setLayout(cgl2)
        self.g_layout.addWidget(c2_groupBox, 6, 0, 2, 2)
        self.c2_filters = [c2_radio1, c2_radio2, c2_radio3]

        l_groupBox = pqtw.QGroupBox("Filter stimulus location")
        l_radio1 = pqtw.QRadioButton("No filter")
        l_radio2 = pqtw.QRadioButton("Left")
        l_radio3 = pqtw.QRadioButton("Right")
        lgl = pqtw.QHBoxLayout(l_groupBox)
        l_radio1.setChecked(True)
        lgl.addWidget(l_radio1)
        lgl.addWidget(l_radio2)
        lgl.addWidget(l_radio3)
        l_groupBox.setLayout(lgl)
        self.g_layout.addWidget(l_groupBox, 8, 0, 2, 2)
        self.l_filters = [l_radio1, l_radio2, l_radio3]

    def get_color(self):
        def set(color):
            self.color = color
        color_d = pqtw.QColorDialog(self)
        self.color = color_d.getColor().getRgbF()[:-1]
        hex = '#%02x%02x%02x' % (int(self.color[0]*255),
                                 int(self.color[1]*255),
                                 int(self.color[2]*255))
        self.buttons["color"].setStyleSheet(f"background-color:{hex};")

    # def open_browser(self):
        # self.fname = pqtw.QFileDialog().getOpenFileName(
            # self, ("Results path"), "../data", ("trial_results (trial_results.csv)"))[0]
        # self.buttons["add"].setEnabled(True)
        # self.fname_label.setText(self.fname)

    def send_patch(self):
        self.color = (*self.color, self.alpha)

        filter_types = []
        i = 0
        for fs in [self.c_filters, self.c2_filters, self.l_filters]:
            for f in fs:
                if f.isChecked():
                    if i % 3:
                        filter_types.append(i)
                i += 1

        def parse_custom_int(text):
            sub_list = self.popup.parent().visualizer.subjects
            items = text.split(",")
            for i in len(range(items)):
                items[i] = ''.join(e for e in items[i] if e in "012345689-")
            subjects = []
            for item in items:
                if "-" in item:
                    rng = item.split("-")
                    mn = int(rng[0]) - 1
                    mx = int(rng[-1])
                    subjects += sub_list[mn:mx]
                else:
                    subjects.append(sub_list[int(item) - 1])
            return subjects

        subjects = []
        if self.selection[2].isChecked():
            try:
                subjects = parse_custom_int(self.subject_text.text())
            except ValueError:
                # TODO make a dialogue, maybe handle differently
                print("parse_custom_int failed, using ALL subjects instead")
                subjects = self.popup.parent().visualizer.subjects
        elif self.selection[1].isChecked():
            subjects = [self.subject_drop.currentText()]
        else:
            subjects = self.popup.parent().visualizer.subjects

        print(subjects)
        self.popup.parent().add_trajectory(subjects, self.color, filter_types)
        self.popup.close()


class InsertTargetFrame(pqtw.QFrame):
    def __init__(self, parent):
        super(InsertTargetFrame, self).__init__(parent)
        self.popup = parent
        self.color = (0., 0.7, 0.)
        self.alpha = 0.4

        self.g_layout = pqtw.QGridLayout()
        self.setLayout(self.g_layout)
        self.inputx = pqtw.QLineEdit("-.1")
        self.inputy = pqtw.QLineEdit(".9")
        self.inputz = pqtw.QLineEdit(".6")
        self.label = pqtw.QLineEdit("Target")
        self.buttons = {}
        self.buttons["add"] = pqtw.QPushButton("Add Target", self)
        self.buttons["cancel"] = pqtw.QPushButton("Cancel", self)
        self.buttons["color"] = pqtw.QPushButton("Color", self)
        hex = '#%02x%02x%02x' % (int(self.color[0]*255),
                                 int(self.color[1]*255),
                                 int(self.color[2]*255))
        self.buttons["color"].setStyleSheet(f"background-color:{hex};")
        self.buttons["add"].clicked.connect(self.send_patch)
        self.buttons["cancel"].clicked.connect(self.popup.close)
        self.buttons["color"].clicked.connect(self.get_color)
        self.g_layout.addWidget(self.label, 0, 0, 1, 4)
        self.g_layout.addWidget(self.inputx, 1, 0, 1, 1)
        self.g_layout.addWidget(self.inputy, 1, 1, 1, 1)
        self.g_layout.addWidget(self.inputz, 1, 2, 1, 1)
        self.g_layout.addWidget(self.buttons["add"], 1, 3, 1, 1)
        self.g_layout.addWidget(self.buttons["color"], 2, 0, 1, 4)
        self.g_layout.addWidget(self.buttons["cancel"], 3, 0, 1, 4)

    def get_color(self):
        def set(color):
            self.color = color
        color_d = pqtw.QColorDialog(self)
        self.color = color_d.getColor().getRgbF()[:-1]
        hex = '#%02x%02x%02x' % (int(self.color[0]*255),
                                 int(self.color[1]*255),
                                 int(self.color[2]*255))
        self.buttons["color"].setStyleSheet(f"background-color:{hex};")

    def send_patch(self):
        self.color = (*self.color, self.alpha)
        # TODO check value safety
        x = float(self.inputx.text())
        y = float(self.inputy.text())
        z = float(self.inputz.text())
        self.popup.parent().add_target(self.label.text(), x, y, z, self.color)
        self.popup.close()

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
        # core = core
        # fps = fps
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
        # for w in self._window.mf.slave_windows:
            # w.show()

    # def add_visual_frame(self, tab, class_, *args, **kwargs):
        # if threading.current_thread().name == "cli":
            # print("Adding frames from CLI unsupported, add a new tab instead")
        # else:
            # self._window.mf.tabs[tab].new_visual_frame(class_, *args, **kwargs)

    # def add_tab(self, name = "tab", buttons = True, layout = None):
        # if threading.current_thread().name == "cli":
            # if layout is None:
                # print("Must assign a standard layout from CLI")
            # else:
                # self._window.add_tab_signal.emit(name, buttons, layout)
        # else:        
            # self._window.mf.add_tab(name, buttons, layout)

    # def add_slave(self, name = "Slave Window"):
        # if threading.current_thread().name == "cli":
            # self._window.add_slave_signal.emit(name)
        # else:
            # self._window.mf.add_slave(name)

    # def insert_visual(self, tab, index, class_, *args, window = 0, **kwargs):
        # if threading.current_thread().name == "cli":
            # self._window.insert_visual_signal.emit(window, tab, index, class_, args, kwargs)
        # else:
            # if window == 0:
                # self._window.mf.tabs[tab].frames[index].insert_visual(class_, *args, **kwargs)
            # else:
                # w = self._window.mf.slave_windows[window - 1].frame 
                # if tab != -1:
                    # w.tabs[tab].frames[index].insert_visual(class_, *args, **kwargs)
                # else:
                    # w.new_visual_frame(class_, *args, **kwargs)

    # def swap_visual(self, tab, w_index, v_index, window = 0):
        # if threading.current_thread().name == "cli":
            # self._window.swap_visual_signal.emit(tab, w_index, v_index, window)
        # else:    
            # if window == 0:
                # self._window.mf.tabs[tab].frames[w_index].swap_visual(v_index)
            # else:
                # w = self._window.mf.slave_windows[window - 1].frame 
                # if tab != -1:
                    # w.tabs[tab].frames[w_index].swap_visual(v_index)
                # else:
                    # w.swap_visual(v_index)

    # def get_timer(self):
        # return self._window.mf.timer

    # def pause(self):
        # self._window.pause_signal.emit()

    # def trigger_update(self):
        # mf = self._window.mf
        # mf.tab_changed(mf.qtab.currentIndex())

    def _begin(self):
        self._app.exec_()
