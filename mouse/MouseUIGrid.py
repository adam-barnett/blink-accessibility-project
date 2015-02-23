import wx
import os


"""
A simple frame which displays the options for controlling the mouse,
highlighting them in order until the a click is entered, returning the
highlighted button when it is.
"""



class MouseUIGrid(wx.Frame):
    
    def __init__(self):
        self.button_dict = {0:"up", 1:"down", 2:"left", 3:"right",
                            4:"scrl_down", 5:"scrl_up", 6:"left_click",
                            7:"dbl_left_click", 8:"right_click", 9:"menu",
                            10:"hold_left", 11:"keyboard"}
        button_size = (100,100)
        self.grid = (3,4)
        self.timer_speed = 800
        (screen_w, screen_h) = wx.DisplaySize()
        this_size = (button_size[0]*self.grid[0], button_size[1]*self.grid[1])
        wx.Frame.__init__(self, None, 1, "title",
                          pos=(screen_w - this_size[0],
                               screen_h*3/4 - this_size[1]/2),
                          size=this_size,
                          style=wx.NO_BORDER|
                          wx.FRAME_NO_TASKBAR |wx.STAY_ON_TOP)
        self.panel = wx.Panel(self, size=self.GetSize())
        self.SetTransparent(230)
        if os.path.isfile("MouseUI.py"):
            add = ""
        else:
            add = "\\mouse\\"
        current_dir = os.getcwd() + add + "\\mouseUIbuttons\\"
        self.buttons = [[None]*self.grid[0] for i in range(self.grid[1])]
        self.bitmap_lists_dict = {"normal":[], "clicked":[],
                                  "highlight_row":[], "highlight_col":[]}
        self.highlight_column_images = []
        self.highlight_row_images = []
        self.normal_images = []
        self.click_images = []
        x = 0
        y = 0
        for i in xrange(12):
            button_f = current_dir + "button" + str(i) + ".bmp"
            high_row_f = current_dir + "highlightrow" + str(i) + ".bmp"
            high_col_f = current_dir + "highlight" + str(i) + ".bmp"
            clicked_f = current_dir + "clicked" + str(i) + ".bmp"
            butt_im = wx.Image(button_f, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            high_row_im = wx.Image(high_row_f, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            high_col_im = wx.Image(high_col_f, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            click_im = wx.Image(clicked_f, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
            button = wx.BitmapButton(self.panel, id=i, bitmap=butt_im,
                                     pos=(x*button_size[0], y*button_size[1]),
                                     size=button_size)
            #uncomment these lines to allow interaction with a mouse for tests
            #button.SetBitmapHover(high_im)
            #button.SetBitmapSelected(click_im)
            self.buttons[y][x] = button
            self.bitmap_lists_dict["normal"].append(butt_im)
            self.bitmap_lists_dict["clicked"].append(click_im)
            self.bitmap_lists_dict["highlight_row"].append(high_row_im)
            self.bitmap_lists_dict["highlight_col"].append(high_col_im)
            if(x == self.grid[0]-1):
                x = 0
                y += 1
            else:
                x += 1
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.IterateThroughButtons, self.timer)
        self.ResetAll()

    def IterateThroughButtons(self, event):
        if self.timer.GetInterval() != self.timer_speed:
            self.timer.Start(self.timer_speed)
        if self.cur_row == -1:
            self.ResetAll()
        elif self.cur_col == -1:
            for button in self.buttons[self.cur_row]:
                self.SetButtonBitmap(button, "normal")
            self.cur_row = (self.cur_row + 1) % self.grid[1]
            for button in self.buttons[self.cur_row]:
                self.SetButtonBitmap(button, "highlight_row")
        else:
            self.SetButtonBitmap(self.buttons[self.cur_row][self.cur_col],
                                 "highlight_row")                            
            self.cur_col = (self.cur_col + 1) % self.grid[0]
            self.SetButtonBitmap(self.buttons[self.cur_row][self.cur_col],
                                 "highlight_col") 
            
                             

    def ClickInput(self):
        button = self.buttons[self.cur_row][self.cur_col]
        if self.timer.IsRunning():
            if self.cur_col == -1:
                self.cur_col = 0
                self.SetButtonBitmap(self.buttons[self.cur_row][self.cur_col],
                                     "highlight_col")
                self.timer.Start(int(self.timer_speed * 1.3))
            else:
                self.SetButtonBitmap(button, "clicked")
                button_text = self.button_dict[button.GetId()]
                if (button.GetId() < 4 or button.GetId() == 10):
                        #then this is a continuous action
                        self.timer.Stop()
                else:
                    self.cur_row = -1
                return button_text
        else:
            button_text = self.button_dict[button.GetId()]
            self.cur_row = -1
            self.timer.Start(self.timer_speed)
            return button_text

    def SetButtonBitmap(self, button, bitmap):
        button.SetBitmap(self.bitmap_lists_dict[bitmap][button.GetId()])
        

    def ResetAll(self):
        for button_list in self.buttons:
            for button in button_list:
                self.SetButtonBitmap(button, "normal")                          
        self.cur_col = -1
        self.cur_row = 0
        for button in self.buttons[self.cur_row]:
            self.SetButtonBitmap(button, "highlight_row")
        self.timer.Start(int(self.timer_speed * 1.3))
            

    def CloseWindow(self):
        self.Close()
        self.Show(False)




if __name__ == "__main__":
    class MyApp(wx.App):
        def OnInit(self):
            self.frame = MouseUIGrid()  
            self.frame.Show(True)
            self.SetTopWindow(self.frame)
            self.Bind(wx.EVT_CHAR_HOOK, self.KeyPress)
            return True

        def KeyPress(self, event):
            if event.GetKeyCode() == wx.WXK_ESCAPE:
                self.frame.CloseWindow()
                self.ExitMainLoop()
            elif event.GetKeyCode() == wx.WXK_SPACE:
                print self.frame.ClickInput()

    app = MyApp(0)
    app.SetCallFilterEvent(True)
    app.MainLoop()
