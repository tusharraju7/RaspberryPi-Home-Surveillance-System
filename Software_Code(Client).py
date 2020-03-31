from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
import time
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager,Screen
from kivy.clock import Clock
from datetime import datetime
from datetime import timedelta
from kivy.uix.image import Image
import socket




client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.settimeout(2)
client_socket.setblocking(True)

doorcondition = False

class FirstPage(BoxLayout):
    orientation = 'vertical'
    global IP,PORT,PASSWORD
    PASSWORD = 'tushar'
    PORT = 8000
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        self.add_widget(Label(text='RaspberryPi Home Surveillance System',font_size=30,bold=True,color=(1,1,0,1)))

        self.layout1 = BoxLayout(orientation = 'horizontal')
        self.add_widget(self.layout1)

        self.startbutton = Button(text='Start',font_size=20,background_color=(0,1,0,1),bold=True)
        self.startbutton.bind(on_press=self.startfunction)
        self.layout1.add_widget(self.startbutton)

        self.exitbutton = Button(text='Exit', font_size=20, background_color=(1, 0, 0, 1),bold=True)
        self.exitbutton.bind(on_press=self.exitfunction)
        self.layout1.add_widget(self.exitbutton)

    def startfunction(self,instance):
        application.screen_manager.current = 'connect'
        application.screen_manager.transition.direction = 'left'

    def exitfunction(self,instance):
        application.get_running_app().stop()

class ConnectPage(GridLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.cols = 2

        self.add_widget(Label(text='RaspberryPi IP Address :',font_size = 20,color=(0,0,1,1),bold = True))
        self.ip = TextInput(multiline = False)
        self.add_widget(self.ip)

        self.add_widget(Label(text='Port Number :', font_size=20, color=(0, 0, 1, 1), bold=True))
        self.port = TextInput(multiline=False)
        self.add_widget(self.port)

        self.add_widget(Label(text='Password :', font_size=20, color=(0, 0, 1, 1), bold=True))
        self.password = TextInput(multiline=False)
        self.add_widget(self.password)

        self.infolabel = (Label(text='Welcome',font_size=20,color=(0,1,0,1)))
        self.add_widget(self.infolabel)

        self.connect_button = Button(text = "Connect",font_size=20,background_color=(0,1,0,1),bold=True)
        self.connect_button.bind(on_press=self.connectbutton)
        self.add_widget(self.connect_button)

    def connectbutton(self,instance):
        global PORT,IP,PASSWORD
        IP =self.ip.text
        if(PASSWORD == self.password.text and PORT == int(self.port.text)):
            client_socket.connect((IP, PORT))
            client_socket.close()
            application.screen_manager.current = 'no2'
            application.screen_manager.transition.direction = 'left'
        else:
            self.ip.text = ''
            self.port.text = ''
            self.password.text = ''
            self.infolabel.text = 'Try Again'
            self.infolabel.color = (1,0,0,1)


class SecondPage(BoxLayout):
    orientation = 'vertical'
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        self.livevideobutton = Button(text='Live Video Stream', font_size=20,background_color=(0,0,1,1),bold=True)
        self.livevideobutton.bind(on_press=self.videostreamfunction)
        self.add_widget(self.livevideobutton)

        self.databutton = Button(text='Data', font_size=20,background_color=(0,1,1,1),bold=True )
        self.databutton.bind(on_press=self.datafunction)
        self.add_widget(self.databutton)

        self.layout2 = BoxLayout(orientation ='horizontal')
        self.add_widget(self.layout2)

        self.doorconditionlabel = (Label(text="Current Status : Locked", font_size=20,color=(1,0,0,1),bold=True))
        self.layout2.add_widget(self.doorconditionlabel)

        self.doorbutton = Button(text='Unlock Door', font_size=20,background_color=(1,1,0,1),bold=True)
        self.doorbutton.bind(on_press=self.doorfunction)
        self.layout2.add_widget(self.doorbutton)

        self.settingsbutton = Button(text='Settings', font_size=20, background_color=(1, 0, 1, 1), bold=True)
        self.settingsbutton.bind(on_press=self.settingsfunction)
        self.add_widget(self.settingsbutton)

        self.returnbutton = Button(text='Return', font_size=20,background_color=(1,0,0,1),bold=True)
        self.returnbutton.bind(on_press=self.returnfunction)
        self.add_widget(self.returnbutton)

    def videostreamfunction(self,instance):
        application.screen_manager.current = 'video'
        application.screen_manager.transition.direction = 'left'

    def datafunction(self,instance):
        application.screen_manager.current='data'
        application.screen_manager.transition.direction = 'left'

    def doorfunction(self,instance):
        global doorcondition
        if(doorcondition == False):
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((IP,PORT))
            send_message('1',client_socket)
            self.doorbutton.text = "Lock Door"
            self.doorconditionlabel.text = "Current Status : Unlocked"
            self.doorconditionlabel.color = (0,1,0,1)
            client_socket.close()
        else:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((IP, PORT))
            send_message('2',client_socket)
            self.doorbutton.text = "Unlock Door"
            self.doorconditionlabel.text = "Current Status : Locked"
            self.doorconditionlabel.color = (1, 0, 0, 1)
            client_socket.close()
        doorcondition = not doorcondition

    def settingsfunction(self,instance):
        application.screen_manager.current='settings'
        application.screen_manager.transition.direction = 'left'

    def returnfunction(self,instance):
        application.screen_manager.current='no1'
        application.screen_manager.transition.direction ='right'


class DataPage(BoxLayout):
    orientation = 'vertical'

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.currenttemp = 30
        self.currenthumidity = 10
        self.now = datetime.now()

        Clock.schedule_interval(self.update_clock, 1)


        self.timelabel = Label(text=self.now.strftime('%b %d %Y %a %I:%M:%S %p'),font_size=20,bold=True)
        self.add_widget(self.timelabel)

        self.temp = (Label(text=f'Temperature : {self.currenttemp} Celsius',font_size = 20,bold=True))
        self.humi = (Label(text=f'Humidity : {self.currenthumidity} %',font_size = 20,bold=True))
        self.add_widget(self.temp)
        self.add_widget(self.humi)

        self.showdatabasebutton = Button(text='Show Database',font_size=20,bold=True)
        self.showdatabasebutton.bind(on_press = self.showdatabasefunction)
        self.add_widget(self.showdatabasebutton)

        self.refreshbutton = Button(text='Refresh Data',font_size=20,background_color =(0,0,1,1),bold=True)
        self.refreshbutton.bind(on_press = self.update_data)
        self.add_widget(self.refreshbutton)

        self.returnbutton = Button(text='Return',font_size = 20,background_color=(1,0,0,1),bold=True)
        self.returnbutton.bind(on_press = self.returnfunction)
        self.add_widget(self.returnbutton)

    def update_clock(self, *args):
        self.now = self.now + timedelta(seconds=1)
        self.timelabel.text = self.now.strftime('%b %d %Y %a %I:%M:%S %p')

    def returnfunction(self,instance):
        application.screen_manager.current='no2'
        application.screen_manager.transition.direction='right'

    def update_data(self,instance):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP, PORT))
        send_message('5',client_socket)
        client_socket.close()
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP, PORT))
        data = client_socket.recv(8)
        data = data.decode('utf-8')
        self.currenthumidity,self.currenttemp = data.split()
        self.temp.text = f'Temperature : {self.currenttemp} Celsius'
        self.humi.text = f'Humidity : {self.currenthumidity} %'

    def showdatabasefunction(self,instance):
        pass


class VideoPage(BoxLayout):
    orientation = 'vertical'

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.now = datetime.now()

        self.layout1 = BoxLayout(orientation='horizontal')
        self.add_widget(self.layout1)
        self.layout2 = BoxLayout(orientation='vertical')
        self.layout1.add_widget(self.layout2)

        self.layout2.add_widget(Label(text="Live Video Streaming",font_size=20,bold=True))

        Clock.schedule_interval(self.update_clock, 1)
        self.timelabel = Label(text=self.now.strftime('%b %d %Y %a %I:%M:%S %p'),font_size=20,bold=True)
        self.layout2.add_widget(self.timelabel)

        self.playbutton = Button(text="Play",font_size=20)
        self.playbutton.bind(on_press = self.playfunction)
        self.layout2.add_widget(self.playbutton)

        self.videostream = Image(source='foo.jpg')
        self.layout1.add_widget(self.videostream)

        self.returnbutton = Button(text='Return', font_size=20,background_color=(1,0.3,0.2,1),size_hint=(1,0.2),bold=True)
        self.returnbutton.bind(on_press=self.returnfunction)
        self.add_widget(self.returnbutton)

    def playfunction(self,instance):
        if(self.playbutton.text == "Play"):
            self.playbutton.text = 'Stop'
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((IP, PORT))
            send_message('4',client_socket)
            client_socket.close()
            Clock.schedule_interval(self.recv, 0.1)
        else:
            self.playbutton.text = 'Play'
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((IP, PORT))
            send_message('0', client_socket)
            client_socket.close()
            Clock.unschedule(self.recv)

    def recv(self,dt):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((IP,PORT))
        send_message('1',client_socket)
        with open('foo.jpg','wb') as file:
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                else:
                    file.write(data)
        self.videostream.reload()

    def returnfunction(self,instance):
        application.screen_manager.current='no2'
        application.screen_manager.transition.direction='right'

    def update_clock(self, *args):
        self.now = self.now + timedelta(seconds=1)
        self.timelabel.text = self.now.strftime('%b %d %Y %a\n %I:%M:%S %p')

class SettingPage(BoxLayout):
    orientation = 'vertical'
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

        self.resetpasswordbutton = Button(text='Reset Password',font_size=20,background_color =(0,0,1,1),bold=True)
        self.resetpasswordbutton.bind(on_press = self.resetpasswordfunction)
        self.add_widget(self.resetpasswordbutton)

        self.addnewfacebutton = Button(text='Add New Face to Database',font_size=20,background_color =(0,1,0,1),bold=True)
        self.addnewfacebutton.bind(on_press = self.addnewfacefunction)
        self.add_widget(self.addnewfacebutton)

        self.deleteoldfacebutton = Button(text='Delete Face From Database',font_size=20,background_color =(1,0,1,1),bold=True)
        self.deleteoldfacebutton.bind(on_press = self.deleteoldfacefunction)
        self.add_widget(self.deleteoldfacebutton)

        self.returnbutton = Button(text='Return',font_size=20,bold=True,background_color=(1,0,0,1))
        self.returnbutton.bind(on_press = self.returnfunction)
        self.add_widget(self.returnbutton)

    def resetpasswordfunction(self,instance):
        application.screen_manager.current = 'resetpassword'
        application.screen_manager.transition.direction = 'left'

    def addnewfacefunction(self,instance):
        application.screen_manager.current = 'addnewface'
        application.screen_manager.transition.direction = 'left'

    def deleteoldfacefunction(self,instance):
        application.screen_manager.current = 'deleteoldface'
        application.screen_manager.transition.direction = 'left'

    def returnfunction(self,instance):
        application.screen_manager.current = 'no2'
        application.screen_manager.transition.direction = 'right'


class ResetPasswordPage(GridLayout):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.cols = 1

        self.add_widget(Label(text='Enter Current Password',font_size=20, bold=True))

        self.currentpassword = TextInput(text='')
        self.add_widget(self.currentpassword)

        self.add_widget(Label(text='Enter New Password',font_size=20, bold=True))

        self.newpassword = TextInput(text = '')
        self.add_widget(self.newpassword)

        self.add_widget(Label(text='Re-Enter New Password',font_size=20, bold=True))

        self.newpassword2 = TextInput(text = '')
        self.add_widget(self.newpassword2)

        self.infolabel = Label(text='Submit',font_size=20, bold=True)
        self.add_widget(self.infolabel)

        self.submitbutton = Button(text='Press Button...',background_color=(0,1,0,1),font_size=20, bold=True)
        self.submitbutton.bind(on_press = self.submitfunction)
        self.add_widget(self.submitbutton)

        self.returnbutton = Button(text='Return', font_size=20, bold=True,background_color=(1,0,0,1))
        self.returnbutton.bind(on_press = self.returnfunction)
        self.add_widget(self.returnbutton)

    def submitfunction(self,instance):
        global PASSWORD
        if(self.currentpassword.text == PASSWORD):
            if(self.newpassword.text == self.newpassword2.text):
                if(self.newpassword.text != self.currentpassword.text):
                    PASSWORD = self.newpassword2.text
                    self.infolabel.text = "Password changed success..."
                else:
                    self.infolabel.text = "Old password is the same as new... Try Again"
            else:
                self.infolabel.text = 'New passwords do not match... Try Again'
        else:
            self.infolabel.text = 'Current Password is wrong... Try Again'

    def returnfunction(self,instance):
        application.screen_manager.current = 'settings'
        application.screen_manager.transition.direction = 'right'

class AddNewFacePage(BoxLayout):
    orientation = 'vertical'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout2 = BoxLayout(orientation='horizontal')
        self.add_widget(self.layout2)

        self.layout3 = BoxLayout(orientation='vertical')
        self.layout2.add_widget(self.layout3)

        self.infolabel = Label(text="Enter Person's Name",font_size=20, bold=True)
        self.layout3.add_widget(self.infolabel)

        self.addfaceinput = TextInput(text='')
        self.layout3.add_widget(self.addfaceinput)

        self.addbutton = Button(text='Add New Face',font_size=20,background_color=(0,1,0,1), bold=True)
        self.addbutton.bind(on_press = self.addfunction)
        self.layout3.add_widget(self.addbutton)

        self.faceimage = Image(source='foo.jpg')
        self.layout2.add_widget(self.faceimage)

        self.returnbutton = Button(text='Return',background_color=(1,0,0,1),size_hint=(1,0.2), font_size=20, bold=True)
        self.returnbutton.bind(on_press = self.returnfunction)
        self.add_widget(self.returnbutton)

    def addfunction(self,instace):
        pass

    def returnfunction(self, instance):
        application.screen_manager.current = 'settings'
        application.screen_manager.transition.direction = 'right'

class DeleteOldFacePage(BoxLayout):
    orientation = 'vertical'
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.layout2 = BoxLayout(orientation='horizontal')
        self.add_widget(self.layout2)

        self.layout3 = BoxLayout(orientation='vertical')
        self.layout2.add_widget(self.layout3)

        self.infolabel = Label(text="Enter Person's Name", font_size=20, bold=True)
        self.layout3.add_widget(self.infolabel)

        self.deletefaceinput = TextInput(text='')
        self.layout3.add_widget(self.deletefaceinput)

        self.deletebutton = Button(text='Delete Old Face',background_color=(0,1,0,1), font_size=20, bold=True)
        self.deletebutton.bind(on_press = self.deletefunction)
        self.layout3.add_widget(self.deletebutton)

        self.faceimage = Image(source='foo.jpg')
        self.layout2.add_widget(self.faceimage)

        self.returnbutton = Button(text='Return',size_hint=(1,0.2), font_size=20,background_color=(1,0,0,1), bold=True)
        self.returnbutton.bind(on_press = self.returnfunction)
        self.add_widget(self.returnbutton)

    def deletefunction(self,instance):
        pass

    def returnfunction(self, instance):
        application.screen_manager.current = 'settings'
        application.screen_manager.transition.direction = 'right'

class MainApp(App):
    currenttime = time.asctime()

    def build(self):

        self.screen_manager = ScreenManager()

        self.page1 = FirstPage()
        screen = Screen(name='no1')
        screen.add_widget(self.page1)
        self.screen_manager.add_widget(screen)

        self.connection = ConnectPage()
        screen = Screen(name='connect')
        screen.add_widget(self.connection)
        self.screen_manager.add_widget(screen)

        self.page2 = SecondPage()
        screen = Screen(name='no2')
        screen.add_widget(self.page2)
        self.screen_manager.add_widget(screen)

        self.datapage = DataPage()
        screen = Screen(name='data')
        screen.add_widget(self.datapage)
        self.screen_manager.add_widget(screen)

        self.videopage = VideoPage()
        screen = Screen(name='video')
        screen.add_widget(self.videopage)
        self.screen_manager.add_widget(screen)

        self.settingspage = SettingPage()
        screen = Screen(name='settings')
        screen.add_widget(self.settingspage)
        self.screen_manager.add_widget(screen)

        self.resetpassword = ResetPasswordPage()
        screen = Screen(name='resetpassword')
        screen.add_widget(self.resetpassword)
        self.screen_manager.add_widget(screen)

        self.addnewface = AddNewFacePage()
        screen = Screen(name='addnewface')
        screen.add_widget(self.addnewface)
        self.screen_manager.add_widget(screen)

        self.deleteoldface = DeleteOldFacePage()
        screen = Screen(name='deleteoldface')
        screen.add_widget(self.deleteoldface)
        self.screen_manager.add_widget(screen)


        return self.screen_manager

def send_message(message,socket):
    message = message.encode("utf-8")
    socket.send(message)


if __name__ == "__main__":
    application = MainApp()
    application.run()