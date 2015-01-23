import wx
import time
from wx.lib.pubsub import pub
from BlinkDetector import BlinkDetector
from MouseFrame import MouseFrame
from MouseController import MouseController


"""
A simple frame which will coordinate between the blink detection and display
elements to allow the user control
"""

class BlinkControllerFrame(wx.Frame):
    
  def __init__(self, moving_horizontally=True, speed=20):

    def to_be_done():
        print 'currently there is no menu available'
    
    self.mouse_frame = MouseFrame()
    self.mouse_frame.Show(True)
    self.mouse_cont = MouseController()
    self.mouse_actions = {"up":self.mouse_cont.Up, "down":self.mouse_cont.Down,
                          "left":self.mouse_cont.Left,
                          "right":self.mouse_cont.Right,
                          "scrl_down":self.mouse_cont.ScrlDown,
                          "scrl_up":self.mouse_cont.ScrlUp,
                          "left_click":self.mouse_cont.LeftClick,
                          "dbl_left_click":self.mouse_cont.DoubleLeftClick,
                          "right_click":self.mouse_cont.RightClick,
                          "menu":to_be_done}

    wx.Frame.__init__(self, None, 1, "title", pos=(0,0),
                  size=(0,0), style=
                  wx.NO_BORDER| wx.FRAME_NO_TASKBAR |wx.STAY_ON_TOP)
    self.watcher = BlinkDetector(wx.DisplaySize(), True)
    pub.subscribe(self.SwitchInput, ("SwitchInput"))
    self.blink_started = None
    
    self.watcher.RunDetect()
        
  def SwitchInput(self, msg):
    if msg == "closing":
      #close command sent
      self.CloseWindow()
    elif msg == "shut":
      current_blink = time.time()
      if self.blink_started is None:
        self.blink_started = current_blink
      elif current_blink - self.blink_started > 0.100:
        #blink detected
        self.blink_started = None
        command = self.mouse_frame.ClickInput()
        print command
        self.mouse_actions[command]()
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
    self.mouse_frame.Close()
    self.mouse_cont.Close()
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
