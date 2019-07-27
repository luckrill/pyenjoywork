#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import os
import sys
import win32api, win32gui, win32con
import subprocess
import importlib

importlib.reload(sys)
sys.setdefaultencoding("utf-8")
_ = wx.GetTranslation

Default_timeout = 4
Autokey_state = True
app4_cmd = r'"D:\Program Files\emacs-24\bin\runemacs.exe"'
app3_cmd = r'"C:\Program Files\Mozilla Firefox\firefox.exe"'
app2_cmd = r'"C:\Program Files\SecureCRT\SecureCRT.EXE"'
app1_cmd = r'"C:\Program Files\Outlook Express\msimn.exe"'
text_filename = "autokey_text.txt"

class Frame(wx.Frame):
    """Frame class, main window."""
    def __init__(self):
        """Create a Frame instance"""
        wx.Frame.__init__(self, None, -1, "Auto Key", size=(900, 700))
        self.Centre()
        self.panel = wx.Panel(self)
        self.autokey_timeout = int(Default_timeout * 60)
        self.shutdown_timeout = 0
        self.shutdown_or_restart = True
        self.autokey_state = False
        self.shutdown_state = False

        self.key_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnKeyTimer, self.key_timer)

        button_autokey = wx.Button(self.panel, label="AutoKey", size=(-1, 30))
        self.label_key_state = wx.StaticText(self.panel, -1, "Stop")
        self.text_key_time = wx.TextCtrl(self.panel, -1, "4", size=(150, -1))
        label_second = wx.StaticText(self.panel, -1, "m")

        button_app1 = wx.Button(self.panel, label="Outlook", size=(-1, 30))
        button_app2 = wx.Button(self.panel, label="SecureCRT", size=(-1, 30))
        button_app3 = wx.Button(self.panel, label="Firefox", size=(-1, 30))
        button_app4 = wx.Button(self.panel, label="Emacs", size=(-1, 30))

        button_shutdown = wx.Button(self.panel, label="Shutdown", size=(-1, 30))
        button_restart = wx.Button(self.panel, label="Restart", size=(-1, 30))
        self.text_shutdown_time = wx.TextCtrl(self.panel, -1, "0", size=(150, 30))
        label_units = wx.StaticText(self.panel, -1, "m/h")

        self.text_multi_text = wx.TextCtrl(self.panel, -1, "", size=(700, 500), style=wx.TE_MULTILINE)
        font=wx.Font(14, wx.ROMAN, wx.NORMAL, wx.NORMAL)
        self.text_multi_text.SetFont(font)
        button_close = wx.Button(self.panel, label="Close", size=(-1, 30))

        vbox_top = wx.BoxSizer(wx.VERTICAL)

        vbox_grid = wx.FlexGridSizer(cols=4, hgap=5, vgap=5)
        vbox_grid.Add(button_autokey, 0, flag=wx.ALIGN_CENTER)
        vbox_grid.Add(self.label_key_state, 0, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER)
        vbox_grid.Add(self.text_key_time, 0, flag=wx.EXPAND|wx.ALL)
        vbox_grid.Add(label_second, 0, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER)

        vbox_grid.Add(button_app1, 0, flag=wx.ALIGN_CENTER)
        vbox_grid.Add(button_app2, 0, flag=wx.ALIGN_CENTER)
        vbox_grid.Add((15,15))
        vbox_grid.Add((15,15))
        vbox_grid.Add(button_app3, 0, flag=wx.ALIGN_CENTER)
        vbox_grid.Add(button_app4, 0, flag=wx.ALIGN_CENTER)
        vbox_grid.Add((15,15))
        vbox_grid.Add((15,15))

        vbox_grid.Add(button_shutdown, 0, flag=wx.ALIGN_CENTER)
        vbox_grid.Add(button_restart, 0, flag=wx.ALIGN_CENTER)
        vbox_grid.Add(self.text_shutdown_time, 0, flag=wx.ALIGN_RIGHT)
        vbox_grid.Add(label_units, 0, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER)

        vbox_top.Add(vbox_grid, 0, wx.ALIGN_CENTER)
        vbox_top.Add(self.text_multi_text, 0, wx.ALIGN_CENTER)
        vbox_top.Add(button_close, 0, wx.ALIGN_CENTER)

        self.panel.SetSizer(vbox_top)

        self.Bind(wx.EVT_BUTTON, self.OnAutoKey, button_autokey)
        self.Bind(wx.EVT_BUTTON, self.OnShutdown, button_shutdown)
        self.Bind(wx.EVT_BUTTON, self.OnRestart, button_restart)
        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)
        self.Bind(wx.EVT_BUTTON, self.OnApp1, button_app1)
        self.Bind(wx.EVT_BUTTON, self.OnApp2, button_app2)
        self.Bind(wx.EVT_BUTTON, self.OnApp3, button_app3)
        self.Bind(wx.EVT_BUTTON, self.OnApp4, button_app4)
        
        self.execute_autokey_task()
        self.read_write_text(False)

    def read_write_text(self, Write = False):
        if (Write == False) and os.path.isfile(text_filename):
            fd = open(text_filename, 'r')
            while True:
                line = fd.readline()
                if not line:
                    break
                self.text_multi_text.AppendText(line)
            fd.close()
        if Write == True:
            self.text_multi_text.SaveFile(text_filename)

    def OnApp1(self, event):
        subprocess.Popen(app1_cmd, shell=True)

    def OnApp2(self, event):
        subprocess.Popen(app2_cmd, shell=True)

    def OnApp3(self, event):
        subprocess.Popen(app3_cmd, shell=True)

    def OnApp4(self, event):
        subprocess.Popen(app4_cmd, shell=True)

    def OnAutoKey(self, event):
        self.execute_autokey_task()

    def execute_autokey_task(self):
        # "start a task or stop a task"
        if (self.autokey_state == False):
            input_string = self.text_key_time.GetValue().strip()
            num = 0
            if input_string.isdigit():
                num = int(input_string)
                self.autokey_timeout = int(num * 5 * 1000)
                self.press_key()
                self.key_timer.Start(self.autokey_timeout)
                self.autokey_state = True
                self.label_key_state.SetLabel("Start")
                #self.text_multi_text.AppendText("auto key start\n")
        else:
            self.key_timer.Stop()
            self.autokey_state = False
            self.label_key_state.SetLabel("Stop")
            #self.text_multi_text.AppendText("auto key stop\n")

    def parse_shutdown_string(self):
        input_string = self.text_shutdown_time.GetValue().strip()
        if input_string.find('.') > -1:
            try:
                num = float(input_string)
            except:
                num = 0.0
            self.shutdown_timeout = int(num * 60 * 60)
        else:
            if input_string.isdigit():
                num = int(input_string)
                self.shutdown_timeout = int(num * 60)

    def OnShutdown(self, event):
        self.parse_shutdown_string()
        cmd_shutdown = "shutdown /s -t " + str(self.shutdown_timeout)
        #self.text_multi_text.AppendText(cmd_shutdown + "\n")
        os.system(cmd_shutdown)
        self.SysClose()

    def OnRestart(self, event):
        self.parse_shutdown_string()
        cmd_restart = "shutdown /r -t " + str(self.shutdown_timeout)
        #self.text_multi_text.AppendText(cmd_restart + "\n")
        os.system(cmd_restart)
        self.SysClose()

    def OnClose(self, event):
        self.read_write_text(True)
        self.SysClose()

    def SysClose(self):
        self.Destroy()
        event.Skip()

    def OnKeyTimer(self, event):
        self.press_key()

    def press_key(self):
        # 17, 144, Num Lock key
        win32api.keybd_event(144,0,0,0) 
        win32api.keybd_event(144,0,win32con.KEYEVENTF_KEYUP,0) 
        # press 17, 144 again
        win32api.keybd_event(144,0,0,0) 
        win32api.keybd_event(144,0,win32con.KEYEVENTF_KEYUP,0) 

class App(wx.App):
    """Application class."""
    def OnInit(self):
        self.frame = Frame()
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return True

def main():
    app = App()
    app.MainLoop()

if __name__ == '__main__':
    main()