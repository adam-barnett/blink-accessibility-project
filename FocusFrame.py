import wx

class FocusFrame(wx.Frame):


    def __init__(self):

        (width,height) = wx.DisplaySize()
        size = 100

        wx.Frame.__init__(self, None, 1, "title",
                  pos=(width/2-size/2,height-size),
                  size=(100,100), style=
                  wx.NO_BORDER| wx.FRAME_NO_TASKBAR |wx.STAY_ON_TOP)
          
        self.panel = wx.Panel(self, size=self.GetSize())
        self.SetBackgroundColour((200,0,0))
        self.panel.SetFocus()

        (panelw, panelh) = self.panel.GetPosition()
        

        wx.StaticText(self.panel, -1, "Click Here for Focus ",
                      (panelw, panelh + size/3), self.GetSize(),
                      wx.ALIGN_CENTER)

    def CloseWindow(self):
        self.Close()  
        self.Show(False)


if __name__ == "__main__": 
    class MyApp(wx.App):
        def OnInit(self):
            self.frame = FocusFrame()  
            self.frame.Show(True)
            self.Bind(wx.EVT_CHAR_HOOK, self.KeyPressTest)
            return True

        def KeyPressTest(self, event):
            if event.GetKeyCode() == wx.WXK_ESCAPE:
                self.frame.CloseWindow(event)
                self.ExitMainLoop() 
            
  
    app = MyApp(0)
    app.SetCallFilterEvent(True)
    app.MainLoop()

