import wx 
import wx.aui
import os
import wx.lib.scrolledpanel as scrolled

STATIC_PATH = "static/"


def getImg(path):
    return wx.Image(path)

IMG_QUALITY = wx.IMAGE_QUALITY_HIGH

class UserDockElement(wx.Panel):
    def __init__(self, parent, user_name):
        wx.Panel.__init__(self, parent)
        self.user_img_size = (200,250)
        self.user_name = user_name
        self.user_panel = wx.Panel(self, -1)
        self.user_img = wx.Image(os.path.join(STATIC_PATH, "%s.jpeg" % user_name))
        self.user_img = self.user_img.Scale(width=self.user_img_size[0], 
                                       height=self.user_img_size[1], quality=IMG_QUALITY)
        self.user_bitmap = wx.StaticBitmap(self.user_panel, wx.ID_ANY, self.user_img.ConvertToBitmap())
        self.hexagon_img_size = (300,300)
        self.hexagon_img = wx.Image(os.path.join(STATIC_PATH, "hexagon.jpeg"))
        self.hexagon_img = self.hexagon_img.Scale(width=self.hexagon_img_size[0], 
                                       height=self.hexagon_img_size[1], quality=IMG_QUALITY)
        self.hexagon_panel = wx.Panel(self, -1)
        self.hexagon_bitmap = wx.StaticBitmap(self.hexagon_panel, wx.ID_ANY, self.hexagon_img.ConvertToBitmap())
        self.user_label = wx.StaticText(self, -1, self.user_name, style=wx.ALIGN_CENTRE)
        self.user_sizer = wx.BoxSizer(wx.VERTICAL) 
        self.user_sizer.Add(self.user_label, 0, wx.ALL, 5) 
        self.user_sizer.Add(self.user_panel, 0, wx.ALL, 5) 
        self.top_sizer = wx.BoxSizer(wx.HORIZONTAL) 
        self.top_sizer.Add(self.user_sizer, 0, wx.ALL, 5)
        self.top_sizer.Add(self.hexagon_panel, 0, wx.ALL, 5) 
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.top_sizer, 0, wx.ALL, 5) 
        self.main_sizer.Add(wx.StaticLine(self, -1, size=(600, -1)), 0, wx.ALL)
        self.SetSizer(self.main_sizer)


#class UserDock(scrolled.ScrolledPanel):
class UserDockWindow(wx.Frame):
    def __init__(self, parent, users=None, title="Users"):
        # scrolled.ScrolledPanel.__init__(self, parent)
        super(UserDockWindow, self).__init__(parent, title = title, size = (600,1000)) 
        self.panel = scrolled.ScrolledPanel(self)
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.elements = {}
        self.no_users = 0
        self.panel.SetSizer(self.main_sizer)
        self.panel.SetupScrolling()
    #    self.main_sizer.Fit(self)
        self.panel.SetAutoLayout(True)

    def add_element(self, user_name):
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

    def on_record_click(self, e):
        self.user_dock_window = UserDockWindow(None)
        self.user_dock_window.add_element("eduardo")
        self.user_dock_window.add_element("jacek")
        self.user_dock_window.add_element("jonas")
        self.user_dock_window.add_element("jonas")


        self.user_dock_window.Show()
	
    def on_file_click(self, e):
        with wx.FileDialog(self, "Open an audio file...", wildcard="*",
                       style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as fileDialog:

            if fileDialog.ShowModal() == wx.ID_CANCEL:
                return     # the user changed their mind

            # Proceed loading the file chosen by the user
            pathname = fileDialog.GetPath()
            print (pathname)
            # try:
            #     with open(pathname, 'r') as file:
            #         self.doLoadDataOrWhatever(file)
            # except IOError:
            #     wx.LogError("Cannot open file '%s'." % newfile)
     
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


class App(wx.Frame):
    def __init__(self, parent, title): 
        super(Mywin, self).__init__(parent, title = title, size = (1000,1000)) 
        self.panel = wx.Panel(parent)
        main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.panel.SetSizer(main_sizer)
        self.show()

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
