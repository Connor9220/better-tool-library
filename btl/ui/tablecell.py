import re
import FreeCAD
from PySide import QtGui, QtSvg, QtCore
from ..i18n import translate
from .util import get_pixmap_from_shape

def isub(text, old, repl_pattern):
    pattern = '|'.join(re.escape(o) for o in old)
    return re.sub('('+pattern+')', repl_pattern, text, flags=re.I)

def interpolate_colors(start_color, end_color, ratio):
    r = 1.0 - ratio
    red = start_color.red() * r + end_color.red() * ratio
    green = start_color.green() * r + end_color.green() * ratio
    blue = start_color.blue() * r + end_color.blue() * ratio
    return QtGui.QColor(int(red), int(green), int(blue))


class TwoLineTableCell(QtGui.QWidget):
    def __init__ (self, parent=None):
        super(TwoLineTableCell, self).__init__(parent)
        self.tool_no = ''
        self.pocket = ''
        self.upper_text = ''
        self.lower_text = ''
        self.search_highlight = ''

        palette = self.palette()
        bg_role = self.backgroundRole()
        bg_color = palette.color(bg_role)
        fg_role = self.foregroundRole()
        fg_color = palette.color(fg_role)

        self.vbox = QtGui.QVBoxLayout()
        self.label_upper = QtGui.QLabel()
        self.label_upper.setStyleSheet("margin-top: 8px")

        color = interpolate_colors(bg_color, fg_color, .8)
        style = "margin-bottom: 8px; color: {};".format(color.name())
        self.label_lower = QtGui.QLabel()
        self.label_lower.setStyleSheet(style)
        self.vbox.addWidget(self.label_upper)
        self.vbox.addWidget(self.label_lower)

        self.label_left = QtGui.QLabel()
        self.label_left.setMinimumWidth(40)
        self.label_left.setTextFormat(QtCore.Qt.RichText)
        self.label_left.setAlignment(QtCore.Qt.AlignCenter|QtCore.Qt.AlignVCenter)

        self.icon_size = QtCore.QSize(75, 90) #Upped the icoon from 50x60 to 75x90
        self.icon_widget = QtGui.QLabel()

        self.label_right = QtGui.QLabel()
        self.label_right.setMinimumWidth(40)
        self.label_right.setTextFormat(QtCore.Qt.RichText)
        self.label_right.setAlignment(QtCore.Qt.AlignCenter)

        self.hbox = QtGui.QHBoxLayout()
        self.hbox.addWidget(self.label_left, 0)
        self.hbox.addWidget(self.icon_widget, 0)
        self.hbox.addLayout(self.vbox, 1)
        self.hbox.addWidget(self.label_right, 0)

        self.setLayout(self.hbox)

    def _highlight(self, text):
        if not self.search_highlight:
            return text
        highlight_fmt = r'<font style="background: yellow; color: black">\1</font>'
        return isub(text, self.search_highlight.split(' '), highlight_fmt)

    def _update(self):
        text = self._highlight(self.tool_no)
        text = f"<b><h4>{text}</h4></b>" if text else ''
        self.label_left.setText(text)

        text = self._highlight(self.pocket)
        lbl = translate('btl', 'Pocket')
        text = f"{lbl}\n<h3>{text}</h3>" if text else ''
        self.label_right.setText(text)

        text = self._highlight(self.upper_text)
        self.label_upper.setText(f'<big><b>{text}</b></big>')

        text = self._highlight(self.lower_text)
        self.label_lower.setText(text)
        self.label_lower.setText(f'<h4>{text}</h4>')

    def set_tool_no(self, no):
        self.tool_no = str(no)
        self._update()

    def set_pocket(self, pocket):
        self.pocket = str(pocket) if pocket else ''
        self._update()

    def set_upper_text(self, text):
        self.upper_text = text
        self._update()

    def set_lower_text(self, text):
        self.lower_text = text
        self._update()

    def set_icon(self, pixmap):
        self.hbox.removeWidget(self.icon_widget)
        self.icon_widget = QtGui.QLabel()
        self.icon_widget.setPixmap(pixmap)
        self.hbox.insertWidget(1, self.icon_widget, 0)

    def set_icon_from_shape(self, shape):
        ratio = self.devicePixelRatioF()
        pixmap = get_pixmap_from_shape(shape, self.icon_size, ratio)
        if pixmap:
            self.set_icon(pixmap)

    def contains_text(self, text):
        for term in text.lower().split(' '):
            if term not in self.tool_no.lower() \
                and term not in self.upper_text.lower() \
                and term not in self.lower_text.lower():
                return False
        return True

    def highlight(self, text):
        self.search_highlight = text
        self._update()
