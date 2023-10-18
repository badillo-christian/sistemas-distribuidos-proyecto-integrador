import socket
import sys
import threading
import errno

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import QPropertyAnimation, QTimer
from PyQt5.QtGui import QIcon, QImage
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QFileDialog, QMenu

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), '../'))

from Client.Bubble.LabelBubble import MessageDelegate, MessageModel, USER_ME, USER_THEM, USER_ADMIN
from Client.Username.Choose_Draggable import Draggable
from Client.Client_UI import Ui_MainWindow

import random
import colorsys
from time import time

import ast

from DropButton.dropbutton import DropButton

HOST = '127.0.0.1'
PORT = 1234
s_messages = ('Conectado al servidor!', 'desconectado del servidor!')
HEADER_LENGTH = 8192


def rand_color():
    h, s, l = random.uniform(0, 360) / 360, random.uniform(0.2, 1), random.uniform(0.5, 1)
    r, g, b = [int(256 * i) for i in colorsys.hls_to_rgb(h, l, s)]
    return '#%02X%02X%02X' % (r, g, b)


def find_nth_overlapping(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start + 1)
        n -= 1
    return start


clientColor = dict()
clientUser = list()
clientList = list()
fragments = list()


def set_message_color(username):
    clientList.append(username)
    for names in clientList:
        if names not in clientColor:
            clientColor[names] = rand_color()


class ClientCode(Ui_MainWindow, QMainWindow):
    def __init__(self, host, port):
        super(ClientCode, self).__init__()
        self.setupUi(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.sock.setblocking(True)
        self.windowAvailable = None
        self.getUsername()
        self.gui_done = True
        self.running = True
        self.create_emojis()
        self.uiFunctions()
        self.threading()
        self.bubbleChat()
        self.send_server_messages()

    def threading(self):
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

    def create_emojis(self):
        buttons = {}
        for i in range(27):  
            for j in range(6):  
                buttons[(i, j)] = QPushButton(self.Emo_Smiles)
                buttons[(i, j)].setObjectName(f'emoji_{j}_smiles')
                buttons[(i, j)].setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                buttons[(i, j)].setFlat(True)
                self.gridLayout_2.addWidget(buttons[(i, j)], i, j)
        icons = []
        curr_moji_length = len(self.Emo_Smiles.children()[1:162]) + 1
        for items in range(0, curr_moji_length):
            icon = QIcon()
            icon.addPixmap(QtGui.QPixmap(f":/EmojisOpened/emoji_{items}.png"), QtGui.QIcon.Normal,
                           QtGui.QIcon.Off)
            icons.append(icon)
        for index, item in enumerate(self.Emo_Smiles.children()[1:163]):
            item.setIcon(icons[index])
            item.setIconSize(QtCore.QSize(32, 32))
        self.create_emojis_dropdown()

    def create_emojis_dropdown(self):
        buttons = {}
        for i in range(27, 34):  
            for j in range(6):  
                buttons[(i, j)] = DropButton(self.Emo_Smiles)
                buttons[(i, j)].setObjectName(f'emoji_{j}_smiles')
                buttons[(i, j)].setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))
                buttons[(i, j)].setFlat(True)
                self.gridLayout_2.addWidget(buttons[(i, j)], i, j)
        icons = []
        curr_moji_length = len(self.Emo_Smiles.children()[163:205])

        initial_counter = 163
        for items in range(0, curr_moji_length):
            icon = QIcon()
            icon.addPixmap(QtGui.QPixmap(f":/Yellow/emoji_{initial_counter}.png"), QtGui.QIcon.Normal,
                           QtGui.QIcon.Off)
            initial_counter += 6
            icons.append(icon)

        for index, item in enumerate(self.Emo_Smiles.children()[163:205]):
            item.setIcon(icons[index])
            item.setIconSize(QtCore.QSize(32, 32))
        for index, item in enumerate(self.Emo_Smiles.children()[163:205]):  
            item.clicked.connect(lambda checked, text=index: self.textEdit.insertPlainText(self.dynamic_emojis[text]))

        self.dynamic_emojis_menu()

    def dynamic_emojis_menu(self):
        button_index = 164
        emoji_index = 0
        jump = [i for i in range(163, 424, 6)]
        display_icons = []

        for items in range(164, 424):
            icon = QIcon()
            icon.addPixmap(QtGui.QPixmap(f":/EmojisOpened/emoji_{items}.png"))
            display_icons.append(icon)
        for button in self.Emo_Smiles.children()[163:424]:
            self.menu_emoji = QMenu()
            if button_index in jump:
                button_index += 1
                emoji_index += 1
            self.menu_emoji.addAction(display_icons[emoji_index], "",
                                      lambda index=button_index: self.textEdit.insertPlainText(self.emojis[index]))
            button_index += 1
            emoji_index += 1
            self.menu_emoji.addAction(display_icons[emoji_index], "",
                                      lambda index=button_index: self.textEdit.insertPlainText(self.emojis[index]))
            button_index += 1
            emoji_index += 1
            self.menu_emoji.addAction(display_icons[emoji_index], "",
                                      lambda index=button_index: self.textEdit.insertPlainText(self.emojis[index]))
            button_index += 1
            emoji_index += 1
            self.menu_emoji.addAction(display_icons[emoji_index], "",
                                      lambda index=button_index: self.textEdit.insertPlainText(self.emojis[index]))
            button_index += 1
            emoji_index += 1
            self.menu_emoji.addAction(display_icons[emoji_index], "",
                                      lambda index=button_index: self.textEdit.insertPlainText(self.emojis[index]))
            button_index += 1
            emoji_index += 1
            button.setMenu(self.menu_emoji)

    def uiFunctions(self):
        self.Hamburger.clicked.connect(self.slide_left_menu)
        self.Send_Button.clicked.connect(self.write)
        self.emojiButton.clicked.connect(self.emoji_pane)
        self.attachButton.clicked.connect(self.send_image)
        self.emojis = []

        self.textEdit.document()
        with open('EmojiList.txt', 'r', encoding="utf8") as file:
            self.emojis = file.read().splitlines()
        for index, item in enumerate(self.Emo_Smiles.children()[1:163]):
            item.clicked.connect(lambda checked, text=index: self.textEdit.insertPlainText(self.emojis[text]))
        self.dynamic_emojis = self.emojis[163::6]
        self.timer = QTimer()
        self.timer.timeout.connect(lambda: self.model.layoutChanged.emit())
        self.timer.start(150)

    def getUsername(self):
        if self.windowAvailable is None:
            self.windowAvailable = Draggable()
        if self.windowAvailable.exec_():
            self.username = self.windowAvailable.lineEdit.text().encode('utf-8')
            self.username_header = f'{len(self.username):<{HEADER_LENGTH}}'.encode('utf-8')
            self.sock.send(self.username_header + self.username)
            self.UserNickname.setText(self.username.decode('utf-8'))
        self.windowAvailable = None

    def send_server_messages(self, s_msg_type="Conectado"):
        if s_msg_type == "Connected":
            message = f"{self.username} > conectado al servidor! \n".encode('utf-8')
            message_header = f'{len(message):< {HEADER_LENGTH}}'.encode('utf-8')
            self.sock.send(message_header + message)
            self.model.add_message(USER_ADMIN, "Te has conectado al servidor", time(), self.username.decode('utf-8'),
                                   "#cccccc")
        elif s_msg_type == "Disconnected":
            message = f"{self.username} > desconectado del servidor! \n".encode('utf-8')
            message_header = f'{len(message):< {HEADER_LENGTH}}'.encode('utf-8')
            self.sock.send(message_header + message)

    def write(self):
        message = f"{self.username} > {self.textEdit.toPlainText()} \n".encode('utf-8')
        message_header = f'{len(message):< {HEADER_LENGTH}}'.encode('utf-8')
        self.sock.send(message_header + message)
        self.model.add_message(USER_ME, self.textEdit.toPlainText(), time(), self.username.decode('utf-8'), "#85EEB6")
        self.textEdit.clear()
        self.textEdit.setHtml(self.getTextStyles)

    def send_image(self, open_file=None):
        if not open_file:
            open_file = QFileDialog.getOpenFileName(None, 'Open File:', '', 'Images (*.png *.jpg)')
        if open_file[0]:
            with open(open_file[0], 'rb') as file:
                openFile_ok = file.read()
                image = QImage()
                image.loadFromData(openFile_ok)
                message = f"{self.username} > {openFile_ok} \n".encode('utf-8')
                message_header = f'{len((message)):< {HEADER_LENGTH}}'.encode('utf-8')
                self.sock.send(message_header + message)
                self.model.add_message(USER_ME, "Imagen Enviada", time(), self.username.decode('utf-8'), "#90caf9", image)
                self.textEdit.clear()
                self.textEdit.setHtml(self.getTextStyles)
        else:
            pass

    def receive(self):
        try:
            while True:
                username_header = self.sock.recv(HEADER_LENGTH)
                if not len(username_header):
                    print("Connection closed by the server")
                    sys.exit()
                username_length = int(username_header.decode('utf-8').strip())
                username = self.sock.recv(username_length).decode('utf-8')
                set_message_color(username)
                message_header = self.sock.recv(HEADER_LENGTH)
                message_length = int(message_header.decode('utf-8').strip())
                message = self.sock.recv(message_length).decode('utf-8')
                message = message[message.find(">") + 1:].replace(" ", "", 1)
                if any(check in message.strip("\n") for check in s_messages):
                    self.model.add_message(USER_ADMIN, f'{username} {message}', time(), "", "#FFFFFF")
                else:
                    if message.startswith("b'"):
                        image = QImage()
                        image.loadFromData(ast.literal_eval(message))
                        self.model.add_message(USER_THEM, "Imagen Recibida!", time(), username, clientColor[username],
                                               image)
                    else:
                        self.model.add_message(USER_THEM, message, time(), username, clientColor[username])
                print("Username:", username)
                print("Message:", message)

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print("reading error:", str(e))
                sys.exit()

        except Exception as e:
            print('General Error:', str(e))
            sys.exit()

    def closeEvent(self, event):
        self.send_server_messages("Disconnected")
        self.running = False
        self.sock.close()
        QMainWindow.closeEvent(self, event)
        exit(0)

    def slide_left_menu(self):
        width = self.SlidingMenu.width()
        if width == 50:
            new_width = 180
            self.UserLayout.setContentsMargins(-53, 0, -51, 9)
        else:
            new_width = 50
            self.UserLayout.setContentsMargins(51, 0, 51, 9)
        self.animation = QPropertyAnimation(self.SlidingMenu, b"minimumWidth")
        self.animation.setDuration(250)
        self.animation.setStartValue(width)
        self.animation.setEndValue(new_width)
        self.animation.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.animation.start()

    def emoji_pane(self):
        width = self.EmojiPane.width()
        if width == 0:
            new_width = 400  # 296
        else:
            new_width = 0
        self.emoji_panel = QPropertyAnimation(self.EmojiPane, b"minimumWidth")
        self.emoji_panel.setDuration(250)
        self.emoji_panel.setStartValue(width)
        self.emoji_panel.setEndValue(new_width)
        self.emoji_panel.setEasingCurve(QtCore.QEasingCurve.InOutQuart)
        self.emoji_panel.start()

    def bubbleChat(self):
        self.messagesView.setItemDelegate(MessageDelegate())
        self.model = MessageModel()
        self.messagesView.setModel(self.model)

    def resizeEvent(self, e):
        self.model.layoutChanged.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    clientCode = ClientCode(HOST, PORT)
    clientCode.show()
    sys.exit(app.exec_())
