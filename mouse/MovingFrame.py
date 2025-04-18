import wx
import time
from FocusFrame import FocusFrame

"""
A simple frame which moves across the screen until stopped either top to
bottom or left to right.
Used to specify a particular piece of the screen
"""

class MovingFrame(wx.Frame):
    
    def __init__(self, moving_horizontally=True, speed=4):

        self.speed = speed
        (width, height) = wx.DisplaySize()
        self.moving_horizontally = moving_horizontally
        xpos = 0
        ypos = 0
        self.move = (0,0)
        if(self.moving_horizontally):
            xpos = width/2
            width = 6
        else:
            ypos = height/2
            height = 6

        wx.Frame.__init__(self, None, 1, "title", pos=(xpos, ypos),
                  size=(width, height), style=
                  wx.NO_BORDER| wx.FRAME_NO_TASKBAR |wx.STAY_ON_TOP)
        self.panel = wx.Panel(self, pos=(xpos, ypos), size=self.GetSize())
        self.SetBackgroundColour((200,0,0))

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.Move, self.timer)

    def Move(self, event):  
        pos = self.GetPosition()
        (width, height) = wx.DisplaySize()
        (x, y) = self.GetSize()
        if pos.x + x < width or pos.y + y < height:
            pos.x += self.move[0]
            pos.y += self.move[1]
            self.SetPosition(pos)
        self.Refresh()


    def StartMoving(self, top_left_corner=True):
        direction = 1
        if top_left_corner:
            direction = -1
        if self.moving_horizontally:
            self.move = (direction * self.speed, 0)
        else:
            self.move = (0, direction * self.speed)
        self.timer.Start(20)

    def StopMoving(self):
        self.move = (0,0)
        self.timer.Stop()

    def CloseWindow(self):
        self.Close()  
        self.Show(False)

    def IsMoving(self):
        return self.timer.IsRunning()

    def ResetPosition(self, x_avoid, y_avoid):
        (x,y) = wx.DisplaySize()
        (self_w, self_h) = self.GetSize()
        if self.moving_horizontally:
            x = x/2
            self_w_ceil = self_w/2 + 1
            if(x - self_w_ceil < x_avoid
               and x + self_w_ceil > x_avoid):
                x = x - self_w
            y = 0
        else:
            y = y/2
            self_h_ceil = self_h/2 + 1
            if(y - self_h_ceil < y_avoid
               and y + self_h_ceil > y_avoid):
                y = y - self_h
            x = 0
        self.SetPosition((x,y))


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
                if self.frame1.IsMoving():
                    self.frame1.StopMoving()
                    self.frame2.StopMoving()
                else:
                    self.frame1.StartMoving()
                    self.frame2.StartMoving()
            elif event.GetKeyCode() == wx.WXK_SHIFT:
                if self.frame1.IsMoving():
                    self.frame1.StopMoving()
                    self.frame2.StopMoving()
                else:
                    self.frame1.StartMoving(top_left_corner=False)
                    self.frame2.StartMoving(top_left_corner=False)
            elif event.GetKeyCode() == wx.WXK_ESCAPE:
                self.frame1.CloseWindow()
                self.frame2.CloseWindow()
                self.frame3.CloseWindow()
                self.ExitMainLoop()
            elif event.GetKeyCode() == wx.WXK_RETURN:
                self.frame1.ResetPosition(0,0)
                self.frame2.ResetPosition(0,0)
            
    app = MyApp(0)
    app.SetCallFilterEvent(True)
    app.MainLoop()
