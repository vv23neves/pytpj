# Сделать: Поменять фон, ещё что-нибудь..., промотку на 10 сек.?
# Скорость воспроизведения
import sys
from PyQt5.QtGui import QIcon, QFont, QPalette
from PyQt5.QtCore import Qt, QUrl, QSize
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import (QApplication, QFileDialog, QHBoxLayout,
        QPushButton, QSlider, QStyle, QVBoxLayout, QWidget, QStatusBar, QLineEdit)
from pytube import YouTube
import sqlite3
class WatchVid(QWidget):
    def __init__(self, parent=None):
        super(WatchVid, self).__init__(parent)

        self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

        SizeBtn = QSize(16, 16) # Размер для кнопок
        videoWidget = QVideoWidget()

        openButton = QPushButton("Открыть видео")
        openButton.setFixedHeight(24)
        openButton.setIconSize(SizeBtn)
        openButton.setFont(QFont("Arial Unicode MS", 8)) # 'Ready' по ум., показывает что готово к исп.
        openButton.clicked.connect(self.ChooseFile)

        pallette = self.palette()
        pallette.setColor(QPalette.Window, Qt.white)
        self.setPalette(pallette)

        self.playButton = QPushButton()
        self.playButton.setEnabled(False)
        self.playButton.setFixedHeight(24)
        self.playButton.setIconSize(SizeBtn)
        self.playButton.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.playButton.clicked.connect(self.play)

        self.positionSlider = QSlider(Qt.Horizontal)
        self.positionSlider.setRange(0, 0)
        self.positionSlider.sliderMoved.connect(self.setPosition)

        self.volume = QSlider(Qt.Horizontal)
        self.volume.setRange(0, 100)
        self.volume.setTickPosition(QSlider.TicksAbove)
        self.volume.setTickInterval(10)
        self.volume.setValue(50)
        self.volume.valueChanged.connect(self.mediaPlayer.setVolume)

        self.statusBar = QStatusBar()
        self.statusBar.setFont(QFont("Arial Unicode MS", 10))
        self.statusBar.setFixedHeight(14)

        self.name = QLineEdit("Введите название")
        self.ssil_strok = QLineEdit("Введите ссылку")
        self.yt_btn = QPushButton()
        self.yt_btn.setText('Скачать видео с Youtube')
        self.yt_btn.clicked.connect(self.click)

        MainLT = QHBoxLayout()
        MainLT.setContentsMargins(0, 0, 0, 0)
        MainLT.addWidget(openButton)
        MainLT.addWidget(self.playButton)
        MainLT.addWidget(self.positionSlider)
        MainLT.addWidget(self.volume)

        V_layout = QVBoxLayout()
        V_layout.addWidget(videoWidget)
        V_layout.addLayout(MainLT)
        V_layout.addWidget(self.statusBar)
        V_layout.addWidget(self.name)
        V_layout.addWidget(self.ssil_strok)
        V_layout.addWidget(self.yt_btn)

        self.setLayout(V_layout)

        self.mediaPlayer.setVideoOutput(videoWidget)
        self.mediaPlayer.stateChanged.connect(self.IconImage)
        self.mediaPlayer.positionChanged.connect(self.positionChanged)
        self.mediaPlayer.durationChanged.connect(self.durationChanged)
        self.mediaPlayer.error.connect(self.handleError)
        self.statusBar.showMessage("Ready")

    # Выбираем файл
    def ChooseFile(self):
        fileName, _ = QFileDialog.getOpenFileName(self, "Выберите файл",
                ".", "Видео_Файлы (*.avi *.mp4)")

        if fileName != '':
            self.mediaPlayer.setMedia(
                    QMediaContent(QUrl.fromLocalFile(fileName)))
            self.playButton.setEnabled(True)
            self.statusBar.showMessage(fileName)
            self.play()

    def play(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.mediaPlayer.pause()
        else:
            self.mediaPlayer.play()

    def IconImage(self):
        if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPause))
        else:
            self.playButton.setIcon(
                    self.style().standardIcon(QStyle.SP_MediaPlay))

    def positionChanged(self, position):
        self.positionSlider.setValue(position)

    def durationChanged(self, duration):
        self.positionSlider.setRange(0, duration)

    def setPosition(self, position):
        self.mediaPlayer.setPosition(position)

    def handleError(self):
        self.playButton.setEnabled(False)
        self.statusBar.showMessage("Error: " + self.mediaPlayer.errorString())

class DBConnect:
    def __init__(self, path: str) -> None:
        if not isinstance(path, str):
            raise TypeError(f"bad operand type{self.__class__.__name__}: '{type(path)}'; expected: 'str'")
        self.connect: sqlite3.Connection = sqlite3.connect(path)
        cursor: sqlite3.Cursor = self.connect.cursor()
        print(f'Установлено соединение{path}')
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS video_name
            (title TEXT, Url TEXT)
        """)

    def vnesti_v_bd(self, title: str, Url: str):
        if not isinstance(title, str):
            raise TypeError(f"bad operand type{self.__class__.__name__}: '{type(title)}'; expected: 'str'")
        if not isinstance(Url, str):
            raise TypeError(f"bad operand type{self.__class__.__name__}: '{type(Url)}'; expected: 'str'")
        cursor: sqlite3.Cursor = self.connect.cursor()
        data: tuple = (
            title,
            Url,
        )
        cursor.execute("""
                    INSERT INTO video_name (title, Url)
                    VALUES (?, ?)
                """, data)
        self.connect.commit()
        yt = YouTube(Url)
        stream = yt.streams.get_by_itag(22)
        stream.download()
        print('Занесены в базу:\n{}={}\n{}={}\n'.format(
            'title',
            title,
            'Url',
            Url
        ))

    def watch_in_bd(self, title: str, Url: str):
        if not isinstance(title, str):
            raise TypeError(f"bad operand type{self.__class__.__name__}: '{type(title)}'; expected: 'str'")
        if not isinstance(Url, str):
            raise TypeError(f"bad operand type{self.__class__.__name__}: '{type(Url)}'; expected: 'str'")
        flag = False
        cursor: sqlite3.Cursor = self.connect.cursor()
        data: tuple = (
            title,
            Url
        )
        exec = cursor.execute("""
                    SELECT title, Url FROM video_name
                    WHERE title = ? AND Url = ?""", data).fetchone()
        if exec:
            flag = True
        if flag:
            print('Полученные записи из БД:\n{}={}\n{}={}\n'.format(
                'title',
                title,
                'Url',
                Url
            ))
        if exec:
            output: dict = {
                'title': exec[0],
                'Url': exec[1]
            }
        else:
            output: dict = {}
        return output

    def __del__(self):
        self.connect.close()
        print('Подключение разорвано')

class MainApp(WatchVid):
    def __init__(self, connector: DBConnect):
        super().__init__()
        if not isinstance(connector, DBConnect):
            raise TypeError(f"bad operand type'{type(connector)}'; expected: 'DataBaseConnector'")
        self.connector: DBConnect = connector
        self.sp = []
        print('Построено окно приложения')

    def click(self):

        print('Производится запрос к базе данных')
        try:
            print(self.name.text(), self.ssil_strok.text())
            NM = self.name.text()
            url = self.ssil_strok.text()
            data = self.connector.watch_in_bd(NM, url)
            if data:
                print('Такая ссылка уже существует: ', url)
                print('Пожалуйста, введите другое URL')
            else:
                print('Такого нет, сейчас исправим')
                self.connector.vnesti_v_bd(NM, url)
        except Exception as error:
            error = error

if __name__ == '__main__':
    connector: DBConnect = DBConnect('video_name.db')
    app = QApplication(sys.argv)
    player = MainApp(connector)
    player.setWindowTitle("VidPlay")
    player.resize(600, 600)
    player.show()
    sys.exit(app.exec_())
