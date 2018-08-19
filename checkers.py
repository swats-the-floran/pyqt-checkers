# roadmap
# ограничение движения шашки за пределы поля мышкой
# превращение в дамку, движение дамок
# множественный захват шашек
# отмена ходов
# анимация
# звуки

import sys

from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QPoint

from PyQt5 import QtGui, QtCore
import math

movedChecker = None
white_rows = 'upper'
this_turn_of = 'white'
turns_log = []
FIELD_SIZE = 800
CHECKER_SIZE = FIELD_SIZE / 8


def log_turn(*args):
    global turns_log
    turns_log += [*args]
    print(turns_log)


class Square:
    def __init__(self, row=None, col=None, point=None):
        if point is not None:
            self.row = math.ceil(point.y() / CHECKER_SIZE)
            self.col = math.ceil(point.x() / CHECKER_SIZE)
            self.x = point.x()
            self.y = point.y()
        else:
            self.x = row * CHECKER_SIZE
            self.y = col * CHECKER_SIZE
        self.row = row
        self.col = col
        self.checker = None

    def getPos(self):
        return self.x, self.y

    def isPlayable(self):
        return (self.row + self.col) % 2 != 0


class Checker(QLabel):
    def __init__(self, color, row, col, field, isQueen=False):
        super(Checker, self).__init__(field)
        self.color = color
        if row >= 5:
            self.direction = 'up'
        elif row <= 2:
            self.direction = 'down'
        self.setPixmap(QPixmap(f'./assets/{color}_checkers.png'))
        self.field = field
        self.isQueen = isQueen
        self.captured = False
        self.row = row
        self.col = col
        self.square = field.squares[row][col]
        self.posx = col * CHECKER_SIZE
        self.posy = row * CHECKER_SIZE
        self.resize(CHECKER_SIZE, CHECKER_SIZE)
        self.move(self.posx, self.posy, square=field.squares[row][col])

    # def mouseDoubleClickEvent(self, event: QtGui.QMouseEvent):
    #     if event.button() & QtCore.Qt.LeftButton:
    #         self.setCaptured()

    def mousePressEvent(self, event: QtGui.QMouseEvent):
        if event.button() == QtCore.Qt.LeftButton:
            self.drag_start_position = event.pos()
            global movedChecker
            movedChecker = self

    def move(self, x=None, y=None, point=None, square=None):
        if point is not None:
            x = int(point.x())
            y = int(point.y())
        super().move(x, y)
        self.square.checker = None
        self.square = square
        self.square.checker = self
        self.row = square.row
        self.col = square.col
        # adding log record
        if hasattr(self, 'drag_start_position'):
            log_turn('move', self, self.drag_start_position.x(), self.drag_start_position.y(), x, y)
        print(self.x(), self.y())
        # if bottom_rows == 'white':
        # if self.color == 'white' and square.row == 7

    def setCaptured(self):
        self.captured = True
        self.hide()
        self.square.checker = None
        if self.color == 'white':
            self.field.white_checkers.remove(self)
        elif self.color == 'black':
            self.field.black_checkers.remove(self)

    def mouseMoveEvent(self, event: QtGui.QMouseEvent):
        if not (event.buttons() & QtCore.Qt.LeftButton):
            return
        if (event.pos() - self.drag_start_position).manhattanLength() < QApplication.startDragDistance():
            return
        drag = QtGui.QDrag(self)
        mimedata = QtCore.QMimeData()
        mimedata.setData('Checker', bytearray('Checker', 'utf8'))
        mimedata.setProperty('offset', QPoint(event.x(), event.y()))
        drag.setMimeData(mimedata)
        drag.setDragCursor(QPixmap('./assets/emptyCursor.png'), QtCore.Qt.MoveAction)
        drag.setPixmap(self.pixmap())
        drag.setHotSpot(event.pos())
        self.hide()
        drag.exec_(Qt.CopyAction | Qt.MoveAction)


class Field(QWidget):
    def __init__(self):
        QWidget.__init__(self)
        self.setAcceptDrops(True)
        self.setGui()
        self.setSquares()
        self.setCheckers()

    def setGui(self):
        self.fieldLabel = QLabel(self)
        self.fieldLabel.setScaledContents(True)
        self.fieldLabel.setPixmap(QPixmap('./assets/field_wooden_2.png'))
        self.fieldLabel.setGeometry(0, 0, FIELD_SIZE, FIELD_SIZE)

    def setSquares(self):
        self.squares = [[Square(row, col) for col in range(8)] for row in range(8)]

    def setCheckers(self):
        self.white_checkers = []
        self.black_checkers = []
        for row in range(0, 3):
            for col in range(8):
                if self.squares[row][col].isPlayable():
                    self.white_checkers += [Checker('white', row, col, field=self)]

        for row in range(5, 8):
            for col in range(8):
                if self.squares[row][col].isPlayable():
                    self.black_checkers += [Checker('black', row, col, field=self)]

    def getSquare(self, row=None, col=None, point=None):
        if point is not None:
            row = math.ceil(point.y() / CHECKER_SIZE) - 1
            col = math.ceil(point.x() / CHECKER_SIZE) - 1
        return self.squares[row][col]

    def removeChecker(self, checker):
        pass

    def squareIsAvailable(self, square):
        # square is not playable
        if (square.row + square.col) % 2 == 0:
            return False
        # there is already another checker in the square
        if square.checker is not None:
            return False
        if movedChecker.isQueen:
            True  # finish later
        else:
            available_squares = [movedChecker.square]
            row, col = movedChecker.square.row, movedChecker.square.col
            available_squares += [self.squares[row+y][col+x] for x in (2, -2) for y in (2, -2) if row + y in range(8) and col + x in range(8)]
            if movedChecker.direction == 'up' and row - 1 in range(8):
                available_squares += [self.squares[row-1][col+x] for x in (1, -1) if col + x in range(8)]
            elif movedChecker.direction == 'down' and row + 1 in range(8):
                available_squares += [self.squares[row+1][col+x] for x in (1, -1) if col + x in range(8)]
            if square in available_squares:
                return True

        return False

    def dragEnterEvent(self, event):
        if event.mimeData().hasFormat('Checker'):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasFormat('Checker'):
            global this_turn_of
            mime = event.mimeData()
            checkerCenterPos = event.pos() - mime.property('offset') + QPoint(50, 50)
            square = self.getSquare(point=checkerCenterPos)
            if this_turn_of == movedChecker.color and self.squareIsAvailable(square):
                row, col = movedChecker.square.row, movedChecker.square.col
                movedChecker.move(point=event.pos() - mime.property('offset'), square=square)
                distanceY, distanceX = movedChecker.square.row - row, movedChecker.square.col - col
                # such move means that checker has been captured
                if abs(distanceX) == 2 and abs(distanceY) == 2:
                    self.squares[row + distanceY // 2][col + distanceX // 2].checker.setCaptured()
                this_turn_of = 'black' if this_turn_of == 'white' else 'white'
            movedChecker.show()
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()


app = QApplication(sys.argv)
app.setApplicationName('PyQt Checkers')
app.setWindowIcon(QtGui.QIcon(QPixmap('./assets/icon.png')))
widget = Field()

widget.show()
sys.exit(app.exec_())