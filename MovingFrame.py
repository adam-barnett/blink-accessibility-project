import wx
import time
from FocusFrame import FocusFrame

"""
A simple frame which moves across the screen until stopped either top to
bottom or left to right.
Used to specify a particular piece of the screen
"""

class MovingFrame(wx.Frame):
    
    def __init__(self, moving_horizontally=True, speed=20):

        print 'moving frame started'
        self.speed = speed
        (width, height) = wx.DisplaySize()
        self.moving_horizontally = moving_horizontally
        if(self.moving_horizontally):
            width = 6
            self.move = (2,0)
        else:
            height = 6
            self.move = (0,2)
        wx.Frame.__init__(self, None, 1, "title", pos=(0,0),
                  size=(width, height), style=
                  wx.NO_BORDER| wx.FRAME_NO_TASKBAR |wx.STAY_ON_TOP)
          
        self.panel = wx.Panel(self, size=self.GetSize())
        self.SetBackgroundColour((200,0,0))
        self.panel.SetFocus()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.Move, self.timer)

    def Move(self, event):
        print 'moving'
        pos = self.GetPosition()
        (width, height) = wx.DisplaySize()
        (x, y) = self.GetSize()
        if pos.x + x < width or pos.y + y < height:
            pos.x += self.move[0]
            pos.y += self.move[1]
            self.SetPosition(pos)
        self.Refresh()

    def ToggleStopStart(self):
        if self.timer.IsRunning():
            self.timer.Stop()
        else:
            print 'starting to move'
            self.timer.Start(self.speed)

    def CloseWindow(self):
        self.Close()  
        self.Show(False)

    def IsMoving(self):
        return self.timer.IsRunning()

    def ResetPosition(self):
        self.SetPosition((0,0))

    def GivePosition(self):
        pos = self.GetPosition()
        if self.moving_horizontally:
            return pos.x
        else:
            return pos.y


if __name__ == "__main__":
    class MyApp(wx.App):
        def OnInit(self):
            self.frame1 = MovingFrame()  
            self.frame1.Show(True)
            self.frame2 = MovingFrame(moving_horizontally=False)
            self.frame2.Show(True)
            self.frame3 = FocusFrame()
            self.frame3.Show(True)
            self.SetTopWindow(self.frame1)
            self.Bind(wx.EVT_CHAR_HOOK, self.KeyPress)
            return True

        def KeyPress(self, event):
            if event.GetKeyCode() == wx.WXK_SPACE:
                self.frame1.ToggleStopStart()
                self.frame2.ToggleStopStart()
            elif event.GetKeyCode() == wx.WXK_ESCAPE:
                self.frame1.CloseWindow()
                self.frame2.CloseWindow()
                self.frame3.CloseWindow()
                self.ExitMainLoop()
            elif event.GetKeyCode() == wx.WXK_RETURN:
                self.frame1.ResetPosition()
                self.frame2.ResetPosition()
            
    app = MyApp(0)
    app.SetCallFilterEvent(True)
    app.MainLoop()
