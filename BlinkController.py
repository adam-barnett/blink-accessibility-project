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

"""
to do:
- figure out if/when focusFrame needs to appear
- add keyboard commands along with an output to inform the user of them
- create a set up protocol based on the blink_detection_experiments folder
  saving_eyes_to_file
"""


class BlinkControllerFrame(wx.Frame):
    
  def __init__(self, moving_horizontally=True, speed=20):
    self.left_to_right = MovingFrame()
    self.top_to_bottom = MovingFrame(False)
    self.left_to_right.Show(True)
    self.top_to_bottom.Show(True)
    wx.Frame.__init__(self, None, 1, "title", pos=(0,0),
                  size=(0,0), style=
                  wx.NO_BORDER| wx.FRAME_NO_TASKBAR |wx.STAY_ON_TOP)
    self.mouse = PyMouse()
    self.watcher = BlinkDetector(True)
    pub.subscribe(self.SwitchInput, ("SwitchInput"))
    self.last_detection = time.time()
    self.watcher.RunDetect()
        
  def SwitchInput(self, msg):
    print 'msg is:', msg
    if msg == "0":
      #close command sent
      self.CloseWindow()
    if msg == '1':
      #blink detected 
      new_detection = time.time()
      if new_detection- self.last_detection < 0.600:
        return 0
      else:
        self.last_detection = new_detection
      if self.left_to_right.IsMoving():
        print '1'
        self.left_to_right.ToggleStopStart()
        self.top_to_bottom.ToggleStopStart()
      elif self.top_to_bottom.IsMoving():
        print '2'
        self.top_to_bottom.ToggleStopStart()
        xpos = self.left_to_right.GivePosition()
        ypos = self.top_to_bottom.GivePosition()
        self.left_to_right.ResetPosition()
        self.top_to_bottom.ResetPosition()
        self.Click(xpos, ypos)
      else:
        print '0'
        self.left_to_right.ToggleStopStart()
        self.left_to_right.panel.SetFocus()

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
