from MovingFrame import MovingFrame
from pymouse import PyMouse
import time
import wx

"""
A class which takes input from BlinkController and uses it to control everything
to do with the mouse
"""

class MouseController():

    def __init__(self):
        self.mouse = PyMouse()
        self.left_to_right = MovingFrame()
        self.top_to_bottom = MovingFrame(False)
        self.left_to_right.Show(True)
        self.top_to_bottom.Show(True)

    def Up(self):
        print 'mouse_cont_up'
        if self.top_to_bottom.IsMoving():
            self.top_to_bottom.StopMoving()
        else:
            self.top_to_bottom.StartMoving()

    def Down(self):
        print 'mouse_cont_down'
        if self.top_to_bottom.IsMoving():
            self.top_to_bottom.StopMoving()
        else:
            self.top_to_bottom.StartMoving(top_left_corner=False)

    def Left(self):
        print 'mouse_cont_left'
        if self.left_to_right.IsMoving():
            self.left_to_right.StopMoving()
        else:
            self.left_to_right.StartMoving()

    def Right(self):
        print 'mouse_cont_right'
        if self.left_to_right.IsMoving():
            self.left_to_right.StopMoving()
        else:
            self.left_to_right.StartMoving(top_left_corner=False)

    def ScrlDown(self):
        self.mouse.scroll(0,-20)

    def ScrlUp(self):
        self.mouse.scroll(0,20)

    def LeftClick(self):
        pos = self.GetMousePos()
        self.left_to_right.Hide()
        self.top_to_bottom.Hide()
        self.mouse.click(pos[0],pos[1])
        self.left_to_right.Show()
        self.top_to_bottom.Show()
        self.left_to_right.ResetPosition()
        self.top_to_bottom.ResetPosition()

    def DoubleLeftClick(self):
        pos = self.GetMousePos()
        self.left_to_right.Hide()
        self.top_to_bottom.Hide()
        self.mouse.click(pos[0],pos[1])
        time.sleep(0.05)
        self.mouse.click(pos[0],pos[1])
        self.left_to_right.Show()
        self.top_to_bottom.Show()
        self.left_to_right.ResetPosition()
        self.top_to_bottom.ResetPosition()

    def RightClick(self):
        pos = self.GetMousePos()
        self.left_to_right.Hide()
        self.top_to_bottom.Hide()
        self.mouse.rightClick(pos[0],pos[1])
        self.left_to_right.Show()
        self.top_to_bottom.Show()
        self.left_to_right.ResetPosition()
        self.top_to_bottom.ResetPosition()

    def GetMousePos(self):
        xpos = self.left_to_right.GivePosition()
        ypos = self.top_to_bottom.GivePosition()
        return (xpos,ypos)

    def Close(self):
        self.top_to_bottom.CloseWindow()
        self.left_to_right.CloseWindow()

if __name__ == "__main__":
    class MyApp(wx.App):
        def OnInit(self):
            self.mouse = MouseController()
            self.Bind(wx.EVT_CHAR_HOOK, self.KeyPress)
            return True

        def KeyPress(self, event):
            if event.GetKeyCode() == wx.WXK_SPACE:
                self.mouse.LeftClick()
                self.mouse.ScrlDown()
            elif event.GetKeyCode() == wx.WXK_SHIFT:
                pass
            elif event.GetKeyCode() == wx.WXK_ESCAPE:
                self.mouse.Close()
                self.ExitMainLoop()
            elif event.GetKeyCode() == wx.WXK_RETURN:
                pass
      
    app = MyApp(0)
    app.SetCallFilterEvent(True)
    app.MainLoop()



