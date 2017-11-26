import wx 
import threading
import wx.aui
import os
import wx.lib.scrolledpanel as scrolled
import wx.richtext as rt
import datetime
import time
import PIL
from PIL import Image, ImageDraw
import numpy as np
import random
import colorsys
from wx.lib.pubsub import pub
import demo_preprocessed as dp
STATIC_PATH = "static/"


def getImg(path):
    return wx.Image(path)

IMG_QUALITY = wx.IMAGE_QUALITY_HIGH
MAX_MSG_PAUSE = 5.0 # in secs

class UserMessageDisplay(rt.RichTextCtrl):
    def __init__(self, parent, style, size, users=None):
        super(UserMessageDisplay, self).__init__(parent, style=style, size=size) 
        self.current_user = ""
        self.last_msg_time = 0.0
        self.users = users
        self.users_textcolour = {}
        if self.users is not None:
            self._assign_colors2users()
        
    def _assign_colors2users(self):
        for u in self.users:
            self.users_textcolour[u] = self._random_sensible_color()

    def _random_sensible_color(self):
        h,s,l = random.random(), 0.5 + random.random()/2.0, 0.4 + random.random()/5.0
        r,g,b = [int(256*i) for i in colorsys.hls_to_rgb(h,l,s)]
        return (r, g, b)


    def write_text(self, user, text): 
        self.BeginTextColour(self.users_textcolour[user])
        delta_t = abs(time.time() - self.last_msg_time)
        self.last_msg_time = time.time()
        if self.current_user != user or delta_t > MAX_MSG_PAUSE:
            self.SetInsertionPoint(-1)
            timestamp = datetime.datetime.fromtimestamp(self.last_msg_time).strftime('%Y-%m-%d %H:%M:%S')
            self.LineBreak()
            self.LineBreak()
            self.BeginBold()
            self.WriteText("%s(%s): " % (user, timestamp))
            self.EndBold()
            self.LineBreak()
            self.current_user = user
            self.WriteText(text)
            p = self.GetInsertionPoint()
            self.LineBreak()
            self.SetInsertionPoint(p)
        else:
            self.WriteText(text)
        self.EndTextColour()

SPEECH_RUNNING = 0
SPEECH_STOPPED = 1

DATA = [{"user": "Jonas", "dt": 5, "text": "Hola me llamo Jonas"}, {"user": "Eduardo", "dt": 3, "text": "Hola me llamo Eduardo"},
        {"user": "Jacek", "dt": 6, "text": "Hola me llamo Jacek"}]
USERS = ["Jonas", "Jacek", "Eduardo"]
SECS2MILLIS = 1000
import pyglet
class WavPlayer: 
    def __init__(self):
        self.thread = None 
        self.audio = None

    def play_file(self, pathname):
        self.audio = pyglet.media.load(pathname)
        self.thread = threading.Thread(target=self._play)
        self.thread.start()

    def _play(self):
        self.audio.play()



class RecordWindow(wx.Frame):
    def __init__(self, parent, users=None, record_data=None, title="Conversation"):
        super(RecordWindow, self).__init__(parent, title = title, size = (1000,600)) 
        self.panel = wx.Panel(self) 
        self.cancel_btn = wx.Button(self.panel, wx.ID_CANCEL, "Cancel")
        self.start_btn_img = wx.Image(os.path.join(STATIC_PATH, "play.png"))
        self.start_btn = wx.BitmapButton(self.panel, -1, self.start_btn_img.ConvertToBitmap())
        self.s = wx.Image(os.path.join(STATIC_PATH, "reset.png"))
        self.s = wx.BitmapButton(self.panel, -1, self.s.ConvertToBitmap())
        self.message_display = UserMessageDisplay(self.panel, wx.SIMPLE_BORDER|wx.VSCROLL, (900, 500), USERS)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.top_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.top_sizer.Add(self.start_btn, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        self.top_sizer.Add(self.s, 0, wx.ALIGN_RIGHT|wx.ALL, 5)
        self.main_sizer.Add(self.top_sizer, 0, wx.ALL, 5)
        self.main_sizer.Add(self.message_display, 1, wx.EXPAND|wx.ALL, 5)
        self.main_sizer.Add(self.cancel_btn, 0, wx.EXPAND|wx.ALL, 5)
        self.panel.SetSizer(self.main_sizer)
        self.start_btn.Bind(wx.EVT_BUTTON, self.on_start)
        self.s.Bind(wx.EVT_BUTTON, self.on_start1)
        self.start_btn_state = SPEECH_STOPPED
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_update, self.timer)
        self.Bind(wx.EVT_BUTTON, self.on_cancel)
        self.current_time_interval = 0
        self.record_data = record_data
        self.player = WavPlayer()

    def on_cancel(self, e):
        self.timer.Stop()
        pub.sendMessage("close.recording")

    def on_start(self, e):
        self.player.play_file("EmoFile.wav")
        if self.start_btn_state == SPEECH_RUNNING:
            self.start_btn_img = wx.Image(os.path.join(STATIC_PATH, "play.png"))
            self.start_btn.SetBitmap(self.start_btn_img.ConvertToBitmap())
            self.start_btn_state = SPEECH_STOPPED
        else:
            self.start_btn_img = wx.Image(os.path.join(STATIC_PATH, "pause.png"))
            self.start_btn.SetBitmap(self.start_btn_img.ConvertToBitmap())
            self.start_btn_state = SPEECH_RUNNING
            current_data = self.record_data[self.current_time_interval]
            self.message_display.write_text(current_data["user"], current_data["text"])
            self.timer.Start(current_data["dt"]*SECS2MILLIS)
            pub.sendMessage("user.activate", message=current_data["user"])

    def on_update(self, e):
        if self.current_time_interval < len(self.record_data)-1:
            self.current_time_interval += 1
            current_data = self.record_data[self.current_time_interval]
            self.message_display.write_text(current_data["user"], current_data["text"])
            self.timer.Start(current_data["dt"]*SECS2MILLIS)
            pub.sendMessage("user.activate", message=current_data["user"])
        else:
            self.timer.Stop()

    def on_start1(self, e):
        self.message_display.write_text("Jacek", "Hola me llamo Jacek y ")

class AnalyzeProgressDialog(wx.ProgressDialog):

    def __init__(self, parent):
        wx.ProgressDialog.__init__(self, "Analyzer", "Analyzing conversation...", maximum=100, parent=parent,
                               style=wx.PD_APP_MODAL|wx.PD_AUTO_HIDE)
        pub.subscribe(self._onUpdate, 'analyze.update')

    def _onUpdate(self, message):
        self.Update(message)



class UserDockElement(wx.Panel):
    def __init__(self, parent, user_name):
        wx.Panel.__init__(self, parent)
        self.user_img_size = (200,250)
        self.user_name = user_name
        self.user_panel = wx.Panel(self, -1)
        self.user_img = wx.Image(os.path.join(STATIC_PATH, "%s.jpeg" % user_name))
        self.user_img = self.user_img.Scale(width=self.user_img_size[0], 
                                       height=self.user_img_size[1], quality=IMG_QUALITY)
        self.user_bitmap = wx.StaticBitmap(self.user_panel,wx.SUNKEN_BORDER| wx.ID_ANY, self.user_img.ConvertToBitmap())
        self.hexagon_img_size = (300,300)
        self.hexagon_img_base = Image.open(os.path.join(STATIC_PATH, "hexagon.png"))
        self.hexagon_img = self.PIL2wxImage(self.hexagon_img_base)
        self.hexagon_panel = wx.Panel(self, -1)
        self.hexagon_bitmap = wx.StaticBitmap(self.hexagon_panel, wx.ID_ANY, self.hexagon_img.ConvertToBitmap())
        self.user_label = wx.StaticText(self, -1, self.user_name, style=wx.ALIGN_CENTRE)
        font = wx.Font(14, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        self.user_label.SetFont(font)
        self.user_sizer = wx.BoxSizer(wx.VERTICAL) 
        self.user_sizer.Add(self.user_label, 0, wx.ALL, 5) 
        self.user_sizer.Add(self.user_panel, 0,wx.ALL, 5) 
        self.top_sizer = wx.BoxSizer(wx.HORIZONTAL) 
        self.top_sizer.Add(self.user_sizer, 0, wx.ALL, 5)
        self.top_sizer.Add(self.hexagon_panel, 0, wx.ALL, 5) 
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.top_sizer, 0, wx.ALL, 5) 
        self.main_sizer.Add(wx.StaticLine(self, -1, size=(600, -1)), 0, wx.ALL)
        self.SetSizer(self.main_sizer)


    def update_hexagon(self, emotions_factors):
        # 0: happyness, 1: neutra, 2: surprise, 3: sad, 4: anger, 5: fear
        scaling_factors = np.array(emotions_factors)
        static_hex_pnts = np.array([[167,72], [434, 72], [568, 305], [434, 536], [167, 536], [32, 305]])/2.0
        hex_center = np.array([150, 150])
        vectors = static_hex_pnts - hex_center
        for i, s in enumerate(scaling_factors):
            vectors[i,:] = vectors[i,:] * s
        new_hexagon_pnts = hex_center + vectors
        context = ImageDraw.Draw(self.hexagon_img_base)
        context.polygon(list(new_hexagon_pnts.flatten()), fill=(197, 198, 204), outline=(60, 95, 209))
        del context
        wximage = self.PIL2wxImage(self.hexagon_img_base)
        self.hexagon_bitmap.SetBitmap(wximage.ConvertToBitmap())
        #TODO: Change this to avoid reloading
        self.hexagon_img_base = Image.open(os.path.join(STATIC_PATH, "hexagon.png"))

    def PIL2wxImage(self, pilImage):
        wximage = wx.Image(*pilImage.size)
        wximage.SetData(pilImage.convert( 'RGB').tobytes())
        wximage.SetAlpha(pilImage.convert( 'RGBA' ).tobytes()[3::4])
        return wximage

class UserDockWindow(wx.Frame):
    def __init__(self, parent, users=None, title="Users"):
        # scrolled.ScrolledPanel.__init__(self, parent)
        super(UserDockWindow, self).__init__(parent, title = title, size = (600,1000)) 
        self.users = users
        self.panel = scrolled.ScrolledPanel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.elements = {}
        self.no_users = 0
        self.panel.SetSizer(self.main_sizer)
        self.panel.SetupScrolling()
        self.panel.SetAutoLayout(True)
        pub.subscribe(self.activate_user, "user.activate")
        self.active_user = None
        self._add_users()

    def _add_users(self):
        for u in self.users:
            self.add_user(u)
            self.elements[u][1].Enable(False)

    def text2sentiment(self, text):
        if self.active_user.user_name == "Jonas":
            return [0.5, 0.3, 1.0, 0.25, 0.5, 0.70]
        elif self.active_user.user_name == "Eduardo":
            return [0.1, 0.2, 0.9, 0.7, 0.5, 0.60]
        else:
            return [0.0, 0.2, 0.9, 0.5, 0.5, 0.40]

    def activate_user(self, message):
        if self.active_user is not None:
            self.active_user.Enable(False)
        self.active_user = self.elements[message][1]
        self.active_user.update_hexagon(self.text2sentiment("text from data"))
        self.active_user.Enable(True)

    def add_user(self, user_name):
        # Add to self.elements()
        e = UserDockElement(self.panel, user_name)
        self.elements[user_name] = (self.no_users, e)
        self.no_users += 1
        self.main_sizer.Add(e, 0, wx.ALL, 5)

class MainTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.record_btn_img = wx.Image(os.path.join(STATIC_PATH, "record_btn.png"))
        self.record_btn = wx.BitmapButton(self, -1, self.record_btn_img.ConvertToBitmap())
        self.file_btn_img = wx.Image(os.path.join(STATIC_PATH, "file_btn.png"))
        self.file_btn = wx.BitmapButton(self, -1, self.file_btn_img.ConvertToBitmap())
        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.main_sizer.Add(self.file_btn, 0, wx.ALL, 5)
        self.main_sizer.Add(self.record_btn, 0, wx.ALL, 5)
        self.SetSizer(self.main_sizer)
        self.record_btn.Bind(wx.EVT_BUTTON, self.on_record_click)
        self.file_btn.Bind(wx.EVT_BUTTON, self.on_file_click)
        self.user_dock_window = None
        self.record_window = None
        pub.subscribe(self.on_save_analysis, "save.analysis")
        pub.subscribe(self.close_recording, "close.recording")

    def close_recording(self):
        self.user_dock_window.Close()
        self.record_window.Close()


    def on_save_analysis(self, message):
        with wx.FileDialog(self, "Save an analysis file...", wildcard="*.speemo",
                           style=wx.FD_SAVE) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
            pathname = fileDialog.GetPath()
        message.save(pathname)


    def on_record_click(self, e):
        pathname = ""
        with wx.FileDialog(self, "Open an analysis file...", wildcard="*",
                           style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind
            pathname = fileDialog.GetPath()

        self.record_data = dp.DemoPreprocessor.read(pathname) 
        self.user_dock_window = UserDockWindow(None, USERS)
        self.record_window = RecordWindow(None, USERS, DATA)
        self.user_dock_window.Show()
        self.record_window.Show()
	
    def on_file_click(self, e):
        pathname = ""
        with wx.FileDialog(self, "Open an audio file...", wildcard="*",
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
        pathname = fileDialog.GetPath()
        self.setup_analize_dialog = AnalyzeProgressDialog(self) 
        def analyze_conversation(pathname):
            processor = dp.DemoPreprocessor(pathname, dp.dict_id2name, 4000)
            processor.run()
            wx.CallAfter(pub.sendMessage, 'analyze.update', message=100)
            wx.CallAfter(pub.sendMessage, 'save.analysis', message=processor)

        thread = threading.Thread(target=analyze_conversation, args=(pathname,))
        thread.start()
        
     
class UsersTab(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        t = wx.StaticText(self, -1, "This is the second tab", (20,20))
 
class MainWindow(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="wxPython tabs example @pythonspot.com")
 
        # Create a panel and notebook (tabs holder)
        self.panel = wx.Panel(self)
        self.tabs = wx.Notebook(self.panel)
 
        # Create the tab windows
        main_tab = MainTab(self.tabs)
        users_tab = UsersTab(self.tabs)
 
        # Add the windows to tabs and name them.
        self.tabs.AddPage(main_tab, "Main")
        self.tabs.AddPage(users_tab, "Users")
 
        # Set noteboook in a sizer to create the layout
        self.main_sizer = wx.BoxSizer()
        self.main_sizer.Add(self.tabs, 1, wx.EXPAND)
        self.panel.SetSizer(self.main_sizer)
    
if __name__ == "__main__":
    app = wx.App()
    window = MainWindow()
    # user_dock = UserDockWindow(None)
    # user_dock.add_element("eduardo")
    # user_dock.add_element("jacek")
    # user_dock.add_element("jonas")
    # user_dock.add_element("jonas")
    # user_dock.Show()
    window.Show()
    app.MainLoop()
