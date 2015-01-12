import wx
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
    pub.subscribe(self.SwitchInput, ("SwitchInput"))
    self.watcher = BlinkDetector(True)
    self.watcher.RunDetect()
    self.left_to_right = MovingFrame()
    self.top_to_bottom = MovingFrame(False)
    self.mouse = PyMouse()
        
  def SwitchInput(self, msg):
    if msg == '1':
      #blink detected by controller
      if self.left_to_right.IsMoving():
        self.left_to_right.ToggleStopStart()
        self.top_to_bottom.ToggleStopStart()
      elif self.top_to_bottom.IsMoving():
        self.top_to_bottom.ToggleStopStart()
        xpos = self.left_to_right.GivePosition()
        ypos = self.top_to_bottom.GivePosition()
        self.mouse.click(xpos, ypos)
        self.left_to_right.ResetPosition()
        self.top_to_bottom.ResetPosition()
      else:
        self.left_to_right.ToggleStopStart()

  def CloseWindow(self, event):
    self.Close()  
    self.Show(False)
    event.Skip()


if __name__ == "__main__":
  class MyApp(wx.App):
    def OnInit(self):
      self.frame = BlinkControllerFrame()
      self.Bind(wx.EVT_CHAR_HOOK, self.KeyPress)
      return True

    def KeyPress(self, event):
      if event.GetKeyCode() == wx.WXK_ESCAPE:
        self.frame.CloseWindow(event)
        self.ExitMainLoop() 
      
  app = MyApp(0)
  app.SetCallFilterEvent(True)
  app.MainLoop()
