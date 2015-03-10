import wx
from wx.lib.pubsub import pub

"""
a simple statictext used to display the messages to the user instructing them
during the initialisation.  Messages can be either timed or timed AND include
a countdown.
"""

class TextDisplay(wx.Frame):

    def __init__(self, start_up_msg="", time=0):
        (screen_width, screen_height) = wx.DisplaySize()
        wx.Frame.__init__(self, None, 1, "title",
                          pos=(50,(screen_height*2)/3),
                          size=(screen_width-100, screen_height/5),
                          style=wx.NO_BORDER|
                          wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP)
        self.panel = wx.Panel(self, size=self.GetSize())
        self.text = wx.StaticText(self.panel, -1, "",
                                  style=wx.ALIGN_CENTRE)
        font = wx.Font(30, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                       wx.FONTWEIGHT_NORMAL)
        self.text.SetFont(font)
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.TimingOver, self.timer)
        self.DisplayMessage(start_up_msg, time)

    def TimingOver(self, event):
        self.timer.Stop()
        pub.sendMessage("InitMsg", msg="text display done")

    def DisplayMessage(self, msg, time=0):
        self.text.SetLabel(msg)
        self.text.Wrap(self.GetSize()[0])
        if time > 0:
            self.timer.Start(time*1000)
           

    def CloseWindow(self):
        self.Close()
        self.Show(False)


if __name__ == "__main__":
    class MyApp(wx.App):
        def OnInit(self):
            introduction_text = ("This Procedure will initialise the system."
            "During it images of your closed and open eyes will be captured."
            "This will allow the system to detect when you are blinking."
            "Please try to stay still, the process will start in ")
            self.frame = TextDisplay()
            self.frame.Show(True)
            self.frame.DisplayMessage(introduction_text)
            self.Bind(wx.EVT_CHAR_HOOK, self.KeyPress)
            return True

        def KeyPress(self, event):
            if event.GetKeyCode() == wx.WXK_ESCAPE:
                self.frame.CloseWindow()
                print 'closing'
                self.ExitMainLoop()

    app = MyApp(0)
    app.SetCallFilterEvent(True)
    app.MainLoop()
