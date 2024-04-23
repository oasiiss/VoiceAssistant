import sys, time, threading, requests, pygame, os, threading, time, sys
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtWidgets import QApplication, QLabel, QWidget
from PyQt5.QtGui import QMovie
import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO
from gtts import gTTS as gt
import speech_recognition as sr
from answer import MainAnswer, CreateImage
        
class Worker(QThread):
    started = pyqtSignal()
    stopped = pyqtSignal()
    animated_label = pyqtSignal(str, int)
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.running = False

    def AnimateWrite(self, value, status):
        text = ""
        for i in value:
            text += i
            self.animated_label.emit(text, status)
            time.sleep(0.1)

    def LoadImage(self, url, max_size=(800, 600)):
        response = requests.get(url)
        image_data = response.content
        
        image = Image.open(BytesIO(image_data))
        image.thumbnail(max_size, Image.ANTIALIAS)

        return ImageTk.PhotoImage(image)
    
    def DownloadImage(self, url, title):
        response = requests.get(url)
        image_data = response.content
        
        with open(f"{title}.jpg", "wb") as file:
            file.write(image_data)
        print("Resim başarıyla indirildi.")

    def ShowImage(self, image_url, desc):
        title = str(desc).replace(" ", "_")
        window = tk.Tk()
        window.title(desc)
        img = self.LoadImage(image_url)
        label = tk.Label(image=img)
        label.pack()
        download_button = tk.Button(window, text="Resmi İndir", command=lambda: self.DownloadImage(image_url, title))
        download_button.pack()
        window.after(20000, window.destroy)
        window.mainloop()

    def Speak(self, text):
        tts = gt(text=text, lang="tr", slow=False)
        file = "answer.mp3"
        tts.save(file)
        pygame.init()
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.quit()
        os.remove(file)
        self.record = False

    def Record(self, ask=False):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            threading.Thread(target=self.AnimateWrite, args=("Dinliyorum...", 1, )).start()
            self.started.emit()
            if ask:
                print(ask)
            audio = r.listen(source)
            try:
                voice = [True, r.recognize_google(audio, language="tr-TR")]
            except sr.WaitTimeoutError:
                voice = [False, "10 Saniye sonra tekrar konuşmayı dene"]
            except sr.UnknownValueError:
                voice = [False, "10 Saniye sonra tekrar konuşmayı dene"]
            except sr.RequestError:
                voice = [False, "10 Saniye sonra tekrar konuşmayı dene"]
        self.stopped.emit()
        return voice

    def RecordMain(self):
        while True:
            voice = self.Record()

            if not voice[0]:
                threading.Thread(target=self.AnimateWrite, args=(voice[1], 1, )).start()
                time.sleep(10)
                continue
            else:
                self.AnimateWrite(voice[1], 2, )
                self.AnimateWrite("Düşünüyorum...", 1, )
                result = MainAnswer(voice[1])
                if result[0]:
                    threading.Thread(target=self.Speak, args=(result[1], )).start()
                    self.AnimateWrite(result[1], 1, )

                    if result[2] == 4:
                        time.sleep(1)
                        self.finished.emit()

                    elif result[2] == 2:
                        image_voice = self.Record()

                        if image_voice[0]:
                            self.AnimateWrite(image_voice[1], 2, )
                            self.AnimateWrite("Çiziyorum...", 1, )
                            image = CreateImage(image_voice[1])

                            if image[0]:
                               self.ShowImage(image[1], image_voice[1])
                               continue

                            else:
                                self.AnimateWrite("10 Saniye sonra tekrar konuşmayı dene", 1, )
                                time.sleep(10)

                    elif result[2] == 3:
                        program_voice = self.Record()
                else:
                    threading.Thread(target=self.AnimateWrite, args=(result[1], 1, )).start()
                    time.sleep(10)
                    continue

    def run(self):
        self.running = True
        self.started.emit()
        self.stopped.emit()
        threading.Thread(target=self.AnimateWrite, args=("Merhaba, size nasıl yardımcı olabilirim ?", 1, )).start()
        self.Speak("Merhaba, size nasıl yardımcı olabilirim ?")
        self.RecordMain()

class AssistantUi(QWidget):
    def __init__(self):
        super().__init__()
        self.Ui()

    def Ui(self):
        self.setGeometry(100, 100, 500, 500)
        self.setWindowTitle('Sesli Asistan')
        self.setFixedSize(500, 420)
        self.movie = QMovie("media/circle.gif")
        self.movie_label = QLabel(self)
        self.movie_label.setAlignment(Qt.AlignCenter)
        self.movie_label.setMovie(self.movie)
        self.movie_label.setGeometry(0, -80, 500, 500)

        self.assistant_label = QLabel("", self)
        self.assistant_label.setAlignment(Qt.AlignCenter)
        self.assistant_label.setGeometry(0, 370, 500, 50)
        self.assistant_label.setWordWrap(True)

        self.user_label = QLabel("", self)
        self.user_label.setAlignment(Qt.AlignCenter)
        self.user_label.setGeometry(0, 325, 500, 50)
        self.user_label.setWordWrap(True)

        self.thread = Worker()
        self.thread.started.connect(self.StartMovie)
        self.thread.stopped.connect(self.StopMovie)
        self.thread.animated_label.connect(self.AnimatedLabel)
        self.thread.finished.connect(self.QuitApplication)

    def StartMovie(self):
        self.movie.start()

    def StopMovie(self):
        self.movie.stop()

    def AnimatedLabel(self, text, status, color="rgba(255, 255, 255, 0.7)", font="17"):
        if status == 1:
            label = self.assistant_label
        elif status == 2:
            label = self.user_label
            color="rgba(255, 255, 255, 1)"

        label.setText(text)
        label.setStyleSheet(f"color: {color}; font-size: {font}px;")

    def StartWork(self):
        if not self.thread.isRunning():
            self.thread.start()

    def QuitApplication(self):
        app.quit()

    def closeEvent(self, event):
        self.thread.Speak("Görüşmek üzere, kendine iyi bak.")
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    assistant = AssistantUi()
    assistant.show()
    assistant.StartWork()
    sys.exit(app.exec_())