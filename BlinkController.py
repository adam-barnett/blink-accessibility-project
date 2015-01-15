import wx
import time
from wx.lib.pubsub import pub
from BlinkDetector import BlinkDetector
from MovingFrame import MovingFrame
from pymouse import PyMouse


"""
A simple frame which will coordinate between the blink detection and display
elements to allow the user control
"""

class BlinkControllerFrame(wx.Frame):
    
  def __init__(self, moving_horizontally=True, speed=20):
    self.left_to_right = MovingFrame(speed=3)
    self.top_to_bottom = MovingFrame(False, speed=3)
    self.left_to_right.Show(True)
    self.top_to_bottom.Show(True)
    wx.Frame.__init__(self, None, 1, "title", pos=(0,0),
                  size=(0,0), style=
                  wx.NO_BORDER| wx.FRAME_NO_TASKBAR |wx.STAY_ON_TOP)
    self.mouse = PyMouse()
    self.watcher = BlinkDetector(wx.DisplaySize(), True)
    pub.subscribe(self.SwitchInput, ("SwitchInput"))
    self.blink_started = None
    self.watcher.RunDetect()
        
  def SwitchInput(self, msg):
    if msg == "closing":
      #close command sent
      self.CloseWindow()
    elif msg == "shut" and self.blink_started != -1:
      #blink detected 
      current_blink = time.time()
      if self.blink_started is None:
        self.blink_started = current_blink
      elif current_blink - self.blink_started > 0.120:
        self.blink_started = -1
        if self.left_to_right.IsMoving():
          self.left_to_right.ToggleStopStart()
          self.top_to_bottom.ToggleStopStart()
        elif self.top_to_bottom.IsMoving():
          self.top_to_bottom.ToggleStopStart()
          xpos = self.left_to_right.GivePosition()
          ypos = self.top_to_bottom.GivePosition()
          self.left_to_right.ResetPosition()
          self.top_to_bottom.ResetPosition()
          self.Click(xpos, ypos)
        else:
          self.left_to_right.ToggleStopStart()
    elif msg == "open":
      #eyes are open
      self.blink_started = None

  def Click(self, x, y):
    print 'clicking at', x, ' by ', y
    self.left_to_right.Hide()
    self.top_to_bottom.Hide()
    self.mouse.click(x,y)
    self.left_to_right.Show()
    self.top_to_bottom.Show()

  def CloseWindow(self):
    self.left_to_right.CloseWindow()
    self.top_to_bottom.CloseWindow()
    self.Destroy()


if __name__ == "__main__":
  class MyApp(wx.App):
    def OnInit(self):
      self.frame = BlinkControllerFrame()
      self.Bind(wx.EVT_CHAR_HOOK, self.KeyPress)
      return True

    def KeyPress(self, event):
      if event.GetKeyCode() == wx.WXK_ESCAPE:
        self.frame.CloseWindow()
        self.ExitMainLoop() 
      
  app = MyApp(0)
  app.SetCallFilterEvent(True)
  app.MainLoop()
