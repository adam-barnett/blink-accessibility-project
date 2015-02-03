import wx
from wx.lib.pubsub import pub

"""
a simple statictext used to display the messages to the user instructing them
during the initialisation.  Messages can be either timed or timed AND include
a countdown.
"""

class TextDisplay(wx.Frame):

    def __init__(self, start_up_msg=""):
        (screen_width, screen_height) = wx.DisplaySize()
        wx.Frame.__init__(self, None, 1, "title",
                          pos=(50,(screen_height*2)/3),
                          size=(screen_width-100, screen_height/5),
                          style=wx.NO_BORDER|
                          wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP)
        self.panel = wx.Panel(self, size=self.GetSize())
        self.text = wx.StaticText(self.panel, -1, start_up_msg,
                                  style=wx.ALIGN_CENTRE)
        font = wx.Font(30, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                       wx.FONTWEIGHT_NORMAL)
        self.text.SetFont(font)
        self.countdown = -1
        self.text_timer = wx.Timer(self)
        current_text = ""
        self.Bind(wx.EVT_TIMER, self.ChangeText, self.text_timer)

    def DisplayMessage(self, msg, countdown=-1, timer=-1):
        self.text_timer.Stop()
        self.current_text = msg
        if countdown == -1:
            self.text.SetLabel(self.current_text)
            self.text.Wrap(self.GetSize()[0])
            self.countdown = -1
            if not timer == -1:
                self.text_timer.Start(timer)
        else:
            self.countdown = countdown
            self.text_timer.Start(1000)
        
    def ChangeText(self, event):
        if self.countdown == -1:
            self.text_timer.Stop()
            pub.sendMessage("InitMsg", msg="text_display_finished")
        else:
            self.text.SetLabel(self.current_text + str(self.countdown))
            self.text.Wrap(self.GetSize()[0])
            self.countdown -= 1      

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
            self.frame.DisplayMessage(introduction_text, 20)
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
