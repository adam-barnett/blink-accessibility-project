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
        if self.top_to_bottom.IsMoving():
            self.top_to_bottom.StopMoving()
        else:
            self.top_to_bottom.StartMoving()

    def Down(self):
        if self.top_to_bottom.IsMoving():
            self.top_to_bottom.StopMoving()
        else:
            self.top_to_bottom.StartMoving(top_left_corner=False)

    def Left(self):
        if self.left_to_right.IsMoving():
            self.left_to_right.StopMoving()
        else:
            self.left_to_right.StartMoving()

    def Right(self):
        if self.left_to_right.IsMoving():
            self.left_to_right.StopMoving()
        else:
            self.left_to_right.StartMoving(top_left_corner=False)

    def ScrlDown(self):
        self.mouse.scroll(-5,0)

    def ScrlUp(self):
        self.mouse.scroll(5,0)

    def LeftClick(self):
        pos = self.GetMousePos()
        self.left_to_right.ResetPosition(pos[0], pos[1])
        self.top_to_bottom.ResetPosition(pos[0], pos[1])
        self.mouse.click(pos[0],pos[1])


    def DoubleLeftClick(self):
        pos = self.GetMousePos()
        self.left_to_right.ResetPosition(pos[0], pos[1])
        self.top_to_bottom.ResetPosition(pos[0], pos[1])
        self.mouse.click(pos[0],pos[1], n=2)

    def RightClick(self):
        pos = self.GetMousePos()
        self.left_to_right.ResetPosition(pos[0], pos[1])
        self.top_to_bottom.ResetPosition(pos[0], pos[1])
        self.mouse.click(pos[0],pos[1], button=2)
        

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



