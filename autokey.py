#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import os
import sys
from datetime import datetime
import win32api, win32gui, win32con
import subprocess
import sqlite3
import importlib

# add timer message
# add command self add/delete function
## format: {Emacs} : {D:\Program Files\emacs-24\bin\runemacs.exe}

importlib.reload(sys)
sys.setdefaultencoding("utf-8")
_ = wx.GetTranslation

Default_timeout = 4
Autokey_state = False
app4_cmd = r'"D:\Program Files\emacs-24\bin\runemacs.exe"'
app3_cmd = r'"C:\Program Files\Mozilla Firefox\firefox.exe"'
app2_cmd = r'"C:\Program Files\SecureCRT\SecureCRT.EXE"'
app1_cmd = r'"C:\Program Files\Outlook Express\msimn.exe"'
text_filename = "autokey_text.txt"
quickmenu_filename = "quickmenu.txt"

log = False

class AppPanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)


        self.menudb = []
        self.quickmenufile = "quickmenu.txt"
        self.number_of_command = 0
        self.subs = []
        self.addApp()

    def addApp(self):
        for app in self.subs:
            if log:
                print(("destroy" + str(app)))
            app.Destroy()
        self.subs = []

        self.sizer = wx.GridSizer(cols=4, hgap=2, vgap=12)

        self.quickmenu_read()
        for li in self.menudb:
            self.number_of_command += 1
            name = li[0]
            if log:
                print(name)
            button_cmd = wx.Button(self, label=name, name=name)
            self.subs.append(button_cmd)
            button_cmd.name = name
            self.sizer.Add(button_cmd, 0, wx.ALIGN_CENTER)
            button_cmd.Bind(wx.EVT_BUTTON, self.OnCommand)

        self.Refresh()
        self.SetSizerAndFit(self.sizer)
        
    def OnCommand(self, event):
        print("OnCommand")
        name = event.GetEventObject().name
        for li in self.menudb:
            if name == li[0]:
                cmd = "".join(li[1:])
                #cmd = li[1]+li[2]
                #cmd = r'"C:\Program Files\SecureCRT\SecureCRT.EXE"'
                #cmd = "C:\Program Files (x86)\SecureCRT\SecureCRT.EXE"
                print((name, cmd))
                subprocess.Popen(cmd, shell=True)

    def quickmenu_read(self):
        if os.path.isfile(self.quickmenufile):
            fd = open(self.quickmenufile, 'r')
            del self.menudb[:]
            while True:
                line = fd.readline()
                if not line:
                    break
                line = line.strip()
                li = line.split("::")
                li = [str.strip() for str in li]
                if line[0] != '#':
                    self.menudb.append(li)
            fd.close()

class MiddlePanel(wx.Panel):
    def __init__(self, *args, **kwargs):
        wx.Panel.__init__(self, *args, **kwargs)

        self.autokey_timeout = int(Default_timeout * 60)
        self.shutdown_timeout = 0
        self.shutdown_or_restart = True
        self.autokey_state = False
        self.shutdown_state = False

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        button_autokey = wx.Button(self, label="AutoKey", size=(-1, 30))
        self.label_key_state = wx.StaticText(self, -1, "Stop")
        self.text_key_time = wx.TextCtrl(self, -1, "4", size=(150, -1))
        label_second = wx.StaticText(self, -1, "m")


        button_shutdown = wx.Button(self, label="Shutdown", size=(-1, 30))
        button_restart = wx.Button(self, label="Restart", size=(-1, 30))
        self.text_shutdown_time = wx.TextCtrl(self, -1, "0", size=(150, 30))
        label_units = wx.StaticText(self, -1, "m/h")

        self.text_multi_text = wx.TextCtrl(self, -1, "", size=(700, 500), style=wx.TE_MULTILINE)
        font=wx.Font(14, wx.ROMAN, wx.NORMAL, wx.NORMAL)
        self.text_multi_text.SetFont(font)
        button_close = wx.Button(self, label="Close", size=(-1, 30))

        self.vbox_top = wx.BoxSizer(wx.VERTICAL)

        vbox_grid = wx.FlexGridSizer(cols=4, hgap=5, vgap=5)

        vbox_grid.Add(button_autokey, 0, flag=wx.ALIGN_CENTER)
        vbox_grid.Add(self.label_key_state, 0, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER)
        vbox_grid.Add(self.text_key_time, 0, flag=wx.EXPAND|wx.ALL)
        vbox_grid.Add(label_second, 0, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER)

        vbox_grid.Add(button_shutdown, 0, flag=wx.ALIGN_CENTER)
        vbox_grid.Add(button_restart, 0, flag=wx.ALIGN_CENTER)
        vbox_grid.Add(self.text_shutdown_time, 0, flag=wx.ALIGN_RIGHT)
        vbox_grid.Add(label_units, 0, flag=wx.ALIGN_LEFT|wx.ALIGN_CENTER)

        self.sizer.Add(vbox_grid, 0, wx.ALIGN_CENTER)

        self.sizer.Add(self.text_multi_text, 0, wx.ALIGN_CENTER)
        self.sizer.Add(button_close, 0, wx.ALIGN_CENTER)

        self.SetSizerAndFit(self.sizer)

        self.key_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnKeyTimer, self.key_timer)

        self.Bind(wx.EVT_BUTTON, self.OnAutoKey, button_autokey)
        self.Bind(wx.EVT_BUTTON, self.OnShutdown, button_shutdown)
        self.Bind(wx.EVT_BUTTON, self.OnRestart, button_restart)
        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)
        
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
        self.OnAddCommand()
        #self.parse_shutdown_string()
        #cmd_shutdown = "shutdown /s -t " + str(self.shutdown_timeout)
        #self.text_multi_text.AppendText(cmd_shutdown + "\n")
        #os.system(cmd_shutdown)
        #self.SysClose(event)

    def OnRestart(self, event):
        #self.parse_shutdown_string()
        cmd_restart = "shutdown /r -t " + str(self.shutdown_timeout)
        #self.text_multi_text.AppendText(cmd_restart + "\n")
        #os.system(cmd_restart)
        #self.SysClose(event)

    def OnClose(self, event):
        self.read_write_text(True)
        self.SysClose(event)

    def SysClose(self, event):
        self.GetParent().Close()
        self.Close()
        event.Skip()

    def OnExit(self, event):
        print("OnExit, main_frame")
        #self.Close()
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

class MainFrame(wx.Frame):
    def __init__(self):
#        wx.Frame.__init__(self, None)
        wx.Frame.__init__(self, None, -1, "Auto Key", size=(900, 700))

        self.Centre()

#        panel = wx.Panel(self)

        # popup menu start
        self.popupmenu = wx.Menu()

        menu_item1 = self.popupmenu.Append(2001, "&test1 menu\tCtrl-B")
        menu_item2 = self.popupmenu.Append(2002, "&test2 menu\tCtrl-X")
        menu_quickmenu_setup = self.popupmenu.Append(2003, "&QuickMenuSetup\tCtrl-Q")
        menu_timer_setup = self.popupmenu.Append(2004, "&TimerSetup\tCtrl-T")
        self.popupmenu.AppendSeparator()
        menu_exit = self.popupmenu.Append(-1, "E&xit")

        self.Bind(wx.EVT_MENU, self.OnExit, menu_exit)

        self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)

        acceltbl = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('B'), menu_item1.GetId()),
            (wx.ACCEL_CTRL, ord('X'), menu_item2.GetId()),
            (wx.ACCEL_CTRL, ord('Q'), menu_quickmenu_setup.GetId()),
            (wx.ACCEL_CTRL, ord('T'), menu_timer_setup.GetId())
            ])
        self.SetAcceleratorTable(acceltbl)

        self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, menu_item1)
        self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, menu_item2)
        self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, menu_quickmenu_setup)
        self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, menu_timer_setup)
        # popup menu end

        self.middlePanel = MiddlePanel(self)
        self.appPanel = AppPanel(self)
#        button = wx.Button(self, label="Close")

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.appPanel, 0, wx.EXPAND)
        self.sizer.Add(wx.StaticLine(self), flag=wx.EXPAND)
        self.sizer.Add(self.middlePanel, 0, wx.EXPAND)
#        self.sizer.Add(button, 0, wx.ALIGN_CENTER)
#        button.Bind(wx.EVT_BUTTON, self.OnClose)

        self.SetSizerAndFit(self.sizer)

    def addApp(self):
        print("on add app ")
        self.appPanel.addApp()
        self.SetSizerAndFit(self.sizer)
        self.sizer.Layout()

    def OnCommand(self, event):
        print("mainframe add app")
        self.appPanel.addApp()
        self.SetSizerAndFit(self.sizer)
        self.sizer.Layout()
  

    def OnClose(self, event):
#        self.read_write_text(True)
        self.SysClose(event)

    def SysClose(self, event):
#        self.Destroy()
        self.Close()
        event.Skip()

    def OnShowPopup(self, event):
        pos = event.GetPosition()
        pos = self.ScreenToClient(pos)
        self.PopupMenu(self.popupmenu, pos)

    def OnPopupItemSelected(self, event):
        print("OnPopupItemSelected")
        #item = self.popupmenu.FindItemById(event.GetId())
        #print("select: %s" % item.GetText())
        print(event.GetId())
        id = event.GetId()
        if id == 2001:
            print("menu 1")
            pass
        elif id == 2002:
            print("menu 2")
            pass
        elif id == 2003:
            print("try to call quick menu setup")
            quickmenu_setup_frame = QuickMenuSetupFrame(self)
            quickmenu_setup_frame.Show(True)
        elif id == 2004:
            print("try to call timer setup")
            timer_setup_frame = TimerSetupFrame(self)
            timer_setup_frame.Show(True)

    def OnExit(self, event):
        print("OnExit, main_frame")
        #self.Close()
        self.Destroy()
        event.Skip()

class Frame(wx.Frame):
    """Frame class, main window."""
    def __init__(self):
        """Create a Frame instance"""
        wx.Frame.__init__(self, None, -1, "Auto Key", size=(900, 700))
        self.Centre()
#        self.panel = wx.Panel(self)
        self.autokey_timeout = int(Default_timeout * 60)
        self.shutdown_timeout = 0
        self.shutdown_or_restart = True
        self.autokey_state = False
        self.shutdown_state = False

        self.menudb = []
        self.quickmenufile = "quickmenu.txt"

        # popup menu start
        self.popupmenu = wx.Menu()

        menu_item1 = self.popupmenu.Append(2001, "&test1 menu\tCtrl-B")
        menu_item2 = self.popupmenu.Append(2002, "&test2 menu\tCtrl-X")
        menu_quickmenu_setup = self.popupmenu.Append(2003, "&QuickMenuSetup\tCtrl-Q")
        menu_timer_setup = self.popupmenu.Append(2004, "&TimerSetup\tCtrl-T")
        self.popupmenu.AppendSeparator()
        menu_exit = self.popupmenu.Append(-1, "E&xit")

        self.Bind(wx.EVT_MENU, self.OnExit, menu_exit)

        self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)

        acceltbl = wx.AcceleratorTable([
            (wx.ACCEL_CTRL, ord('B'), menu_item1.GetId()),
            (wx.ACCEL_CTRL, ord('X'), menu_item2.GetId()),
            (wx.ACCEL_CTRL, ord('Q'), menu_quickmenu_setup.GetId()),
            (wx.ACCEL_CTRL, ord('T'), menu_timer_setup.GetId())
            ])
        self.SetAcceleratorTable(acceltbl)

        self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, menu_item1)
        self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, menu_item2)
        self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, menu_quickmenu_setup)
        self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, menu_timer_setup)
        # popup menu end

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

        self.vbox_top = wx.BoxSizer(wx.VERTICAL)

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

        self.vbox_top.Add(vbox_grid, 0, wx.ALIGN_CENTER)

        self.number_of_command = 0
        self.vbox_command = wx.BoxSizer(wx.VERTICAL)
        self.vbox_top.Add(self.vbox_command, 0, wx.ALIGN_CENTER)

        self.vbox_top.Add(self.text_multi_text, 0, wx.ALIGN_CENTER)
        self.vbox_top.Add(button_close, 0, wx.ALIGN_CENTER)

#        self.vbox_top.Hide(self.vbox_command)

        self.panel.SetSizer(self.vbox_top)

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

    def OnAddCommand(self):
        self.quickmenu_read()
        for li in self.menudb:
            self.number_of_command += 1
            name = li[0]
            print(name)
            new_button = wx.Button(self, label=name, name=name)
            new_button.name = name
            self.vbox_command.Add(new_button, 0, wx.ALL, 5)
            new_button.Bind(wx.EVT_BUTTON, self.OnCommand)

#        self.SetSizerAndFit(self.vbox_command)
#        self.vbox_top.Show(self.vbox_command)
#        self.Layout()
#        self.Fit()
            #        self.frame.fSizer.Layout()

    def OnCommand(self, event):
        name = event.GetEventObject().name
        print(name)
        for li in self.menudb:
            if name == li[0]:
                print(name)
            else:
                print(("not " + name))

    def quickmenu_read(self):
        if os.path.isfile(self.quickmenufile):
            fd = open(self.quickmenufile, 'r')
            while True:
                line = fd.readline()
                if not line:
                    break
                line = line.strip()
                li = line.split("::")
                li = [str.strip() for str in li]
                if line[0] != '#':
                    self.menudb.append(li)
            fd.close()

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
        self.OnAddCommand()
        #self.parse_shutdown_string()
        #cmd_shutdown = "shutdown /s -t " + str(self.shutdown_timeout)
        #self.text_multi_text.AppendText(cmd_shutdown + "\n")
        #os.system(cmd_shutdown)
        #self.SysClose(event)

    def OnRestart(self, event):
        #self.parse_shutdown_string()
        cmd_restart = "shutdown /r -t " + str(self.shutdown_timeout)
        #self.text_multi_text.AppendText(cmd_restart + "\n")
        #os.system(cmd_restart)
        #self.SysClose(event)

    def OnClose(self, event):
        self.read_write_text(True)
        self.SysClose(event)

    def SysClose(self, event):
        self.Destroy()
        event.Skip()

    def OnShowPopup(self, event):
        pos = event.GetPosition()
        pos = self.panel.ScreenToClient(pos)
        self.panel.PopupMenu(self.popupmenu, pos)

    def OnPopupItemSelected(self, event):
        print("OnPopupItemSelected")
        #item = self.popupmenu.FindItemById(event.GetId())
        #print("select: %s" % item.GetText())
        print(event.GetId())
        id = event.GetId()
        if id == 2001:
            print("menu 1")
            pass
        elif id == 2002:
            print("menu 2")
            pass
        elif id == 2003:
            print("try to call quick menu setup")
            quickmenu_setup_frame = QuickMenuSetupFrame()
            quickmenu_setup_frame.Show(True)
        elif id == 2004:
            print("try to call timer setup")
            timer_setup_frame = TimerSetupFrame()
            timer_setup_frame.Show(True)

    def OnExit(self, event):
        print("OnExit, main_frame")
        #self.Close()
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


class QuickMenuSetupFrame(wx.Frame):
    """System Setup Frame class, sub window."""
    def __init__(self, frame):
        """Create a Frame instance"""
        wx.Frame.__init__(self, None, title="System Setup", size=(850, 650))
        self.Centre()
        print(self.GetSize())

        self.main_frame= frame
        panel = wx.Panel(self)

        self.menudb = []
        self.quickmenufile = "quickmenu.txt"
        self.listboxChanged = False

        label_title = wx.StaticText(panel, -1, "Quick Menu Setup")

#        self.listbox = wx.ListBox(panel, -1, (20, 20), (220, 360), "", wx.LB_EXTENDED)
        self.listbox = wx.ListBox(panel, -1, (20, 20), (220, 360), "", wx.LB_SINGLE)
        list_up = wx.Button(panel, -1, label=_("Up"))
        list_down = wx.Button(panel, -1, label=_("Down"))
        list_delete = wx.Button(panel, -1, label=_("Delete"))

        self.cmd_name = wx.TextCtrl(panel, 0, "", size=(100, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);
        self.cmd_command = wx.TextCtrl(panel, 0, "", size=(230, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);
        self.cmd_parameter = wx.TextCtrl(panel, 0, "", size=(100, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);
        cmd_add = wx.Button(panel, -1, label=_("Add"))
        cmd_clear = wx.Button(panel, -1, label=_("Clear"))
        cmd_close = wx.Button(panel, -1, label=_("Close"))

        # start layout
        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_list = wx.BoxSizer(wx.HORIZONTAL)
        vbox_list_cmd = wx.BoxSizer(wx.VERTICAL)
        vbox_list_cmd.Add(list_up, 0, flag=wx.ALIGN_CENTER)
        vbox_list_cmd.Add((15,15))
        vbox_list_cmd.Add(list_down, 0, flag=wx.ALIGN_CENTER)
        vbox_list_cmd.Add((15,15))
        vbox_list_cmd.Add(list_delete, 0, flag=wx.ALIGN_CENTER)
        vbox_list.Add(self.listbox, 0, flag=wx.ALIGN_CENTER)
        vbox_list.Add((15,15))
        vbox_list.Add(vbox_list_cmd, 0, flag=wx.ALIGN_CENTER)
        vbox_add_content = wx.BoxSizer(wx.HORIZONTAL)
        vbox_add_content.Add(self.cmd_name, 0, flag=wx.ALIGN_CENTER)
        vbox_add_content.Add((15,15))
        vbox_add_content.Add(self.cmd_command, 0, flag=wx.ALIGN_CENTER)
        vbox_add_content.Add((15,15))
        vbox_add_content.Add(self.cmd_parameter, 0, flag=wx.ALIGN_CENTER)
        vbox_add_cmd = wx.BoxSizer(wx.HORIZONTAL)
        vbox_add_cmd.Add(cmd_add, 0, flag=wx.ALIGN_CENTER)
        vbox_add_cmd.Add((15,15))
        vbox_add_cmd.Add(cmd_clear, 0, flag=wx.ALIGN_CENTER)
        vbox_add_cmd.Add((15,15))
        vbox_add_cmd.Add(cmd_close, 0, flag=wx.ALIGN_CENTER)

        vbox_top.Add((15,15))
        vbox_top.Add(label_title, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(wx.StaticLine(panel), flag=wx.EXPAND)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_list, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_add_content, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_add_cmd, 0, wx.ALIGN_CENTER)

        #Start Fit
        panel.SetSizer(vbox_top)

        #        self.Bind(wx.EVT_LISTBOX, self.OnListBox, self.listbox)
        #       self.Bind(wx.EVT_LISTBOX_DCLICK, self.OnDclickListBox, self.listbox)
        self.Bind(wx.EVT_LISTBOX, self.OnListBox, self.listbox)
        self.Bind(wx.EVT_BUTTON, self.OnListUp, list_up)
        self.Bind(wx.EVT_BUTTON, self.OnListDown, list_down)
        self.Bind(wx.EVT_BUTTON, self.OnListDelete, list_delete)
        self.Bind(wx.EVT_BUTTON, self.OnCmdAdd, cmd_add)
        self.Bind(wx.EVT_BUTTON, self.OnCmdClear, cmd_clear)
        self.Bind(wx.EVT_BUTTON, self.OnCmdClose, cmd_close)
        self.quickmenu_read_write()

    def quickmenu_read_write(self, Write = False):
        if (Write == False) and os.path.isfile(self.quickmenufile):
            fd = open(self.quickmenufile, 'r')
            self.listbox.Clear()
            del self.menudb[:]
            while True:
                line = fd.readline()
                if not line:
                    break
                line = line.strip()
                li = line.split("::")
                li = [str.strip() for str in li]
                if line[0] != '#':
                    self.menudb.append(li)
                    self.listbox.Append(li[0])
                    # self.text_multi_text.AppendText(line)
            self.listbox.SetSelection(0)
            fd.close()
        if Write == True:
            fd = open(self.quickmenufile, 'w')
            currtime = "#quickmenu write at " + datetime.now().strftime("%Y-%m-%d %H:%M") + "\n"
            fd.write(currtime)
            for li in self.menudb:
                line = "::".join(ele for ele in li) + "\n"
                fd.write(line)
            fd.close()
            #self.text_multi_text.SaveFile(quickmenu_filename)

    def OnListBox(self, event):
        pass

    def OnListUp(self, event):
        total = self.listbox.GetCount()
        select = self.listbox.GetSelection()
        if log:
            print("-----------------------")
        if (total > 0) and (select > 0):
            name1 = self.listbox.GetString(select -1)
            name2 = self.listbox.GetString(select)
            self.listbox.SetString(select-1, name2)
            self.listbox.SetString(select, name1)
            self.menudb[select-1], self.menudb[select] = self.menudb[select], self.menudb[select-1]
            self.listbox.SetSelection(select-1)
            self.listboxChanged = True
        if log:
            for li in self.menudb:
                print(li)

    def OnListDown(self, event):
        total = self.listbox.GetCount()
        select = self.listbox.GetSelection()
        if log:
            print("==================")
        if (total > 0)  and (select < total - 1):
            name1 = self.listbox.GetString(select )
            name2 = self.listbox.GetString(select+1)
            self.listbox.SetString(select, name2)
            self.listbox.SetString(select+1, name1)
            self.menudb[select], self.menudb[select+1] = self.menudb[select+1], self.menudb[select]
            self.listbox.SetSelection(select+1)
            self.listboxChanged = True
        if log:
            for li in self.menudb:
                print(li)

    def OnListDelete(self, event):
        total = self.listbox.GetCount()
        select = self.listbox.GetSelection()
        if (total > 0)  and (select < total):
            self.listbox.Delete(select)
            del self.menudb[select]
            self.listboxChanged = True

        if log:
            for li in self.menudb:
                print(li)

    def OnCmdAdd(self, event):
        name = self.cmd_name.GetValue()
        command = self.cmd_command.GetValue()
        parameter = self.cmd_parameter.GetValue()
        if [name, command, parameter] not in self.menudb:
            self.menudb.append([name, command, parameter])
            self.listbox.Append(name)
            self.cmd_name.SetValue("")
            self.cmd_command.SetValue("")
            self.cmd_parameter.SetValue("")
            self.listboxChanged = True
        else:
            print("command duplication errors")

        pass

    def OnCmdClear(self, event):
        self.cmd_name.SetValue("")
        self.cmd_command.SetValue("")
        self.cmd_parameter.SetValue("")

#      self.quickmenu_read_write()
#      self.text_multi_text.SetValue(dbfamous.famous_list_get_text_by_index(self.current_item).decode("utf-8"))
#      self.text_multi_text.SetValue("")


    def OnCmdClose(self, event):
        if self.listboxChanged:
            print("changed and save")
            self.quickmenu_read_write(True)
            self.main_frame.addApp()

        self.Destroy()
        event.Skip()

class DBase():
    def __init__(self):
        self.conn = sqlite3.connect("database.db3")
        self.cur = self.conn.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS  timer(o_id INTEGER PRIMARY KEY, name VARCHAR(20), message VARCHAR(50), timeout INTEGER, loop_times INTEGER, enable BOOLEAN)")

    def db_commit(self):
        print("db commit")
        self.conn.commit()

    def db_timer_insert(self):
        pass

    def db_timer_remove(self):
        pass

# timer name, sentence, timeout: XXX; run mode: once, times, loop; enable
# write to text file


class TimerSetupFrame(wx.Frame):
    """System Setup Frame class, sub window."""
    def __init__(self, frame):
        """Create a Frame instance"""
        wx.Frame.__init__(self, None, title="System Setup", size=(850, 650))
        #self.ShowFullScreen(True, style=wx.FULLSCREEN_ALL)
        self.Centre()
        print(self.GetSize())

        self.main_frame= frame
        panel = wx.Panel(self)

        self.timerdb = []
        self.quickmenufile = "quickmenu.txt"
        self.listboxChanged = False

        label_title = wx.StaticText(panel, -1, "Timer Setup")

#        self.listbox = wx.ListBox(panel, -1, (20, 20), (220, 360), "", wx.LB_SINGLE)
        self.listbox = wx.ListBox(panel, -1, (20, 20), (220, 360), "", wx.LB_SINGLE)
        list_up = wx.Button(panel, -1, label=_("Up"))
        list_down = wx.Button(panel, -1, label=_("Down"))
        list_delete = wx.Button(panel, -1, label=_("Delete"))

#        self.cmd_name = wx.TextCtrl(panel, 0, "", size=(100, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);
#        self.cmd_command = wx.TextCtrl(panel, 0, "", size=(230, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);
#        self.cmd_parameter = wx.TextCtrl(panel, 0, "", size=(100, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);

        self.timer_name = wx.TextCtrl(panel, 0, "", size=(100, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);
        self.timer_message = wx.TextCtrl(panel, 0, "", size=(230, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);
        self.timer_timeout = wx.TextCtrl(panel, 0, "", size=(100, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);
        self.timer_loop_times = wx.TextCtrl(panel, 0, "", size=(100, -1), style=wx.TE_PROCESS_ENTER|wx.TE_LEFT);
        self.timer_enable = wx.CheckBox(panel, 0, "Enable");

        cmd_add = wx.Button(panel, -1, label=_("Add"))
        cmd_clear = wx.Button(panel, -1, label=_("Clear"))
        cmd_update = wx.Button(panel, -1, label=_("Update"))
        cmd_close = wx.Button(panel, -1, label=_("Close"))

        # start layout
        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_list = wx.BoxSizer(wx.HORIZONTAL)
        vbox_list_cmd = wx.BoxSizer(wx.VERTICAL)
        vbox_list_cmd.Add(list_up, 0, flag=wx.ALIGN_CENTER)
        vbox_list_cmd.Add((15,15))
        vbox_list_cmd.Add(list_down, 0, flag=wx.ALIGN_CENTER)
        vbox_list_cmd.Add((15,15))
        vbox_list_cmd.Add(list_delete, 0, flag=wx.ALIGN_CENTER)
        vbox_list.Add(self.listbox, 0, flag=wx.ALIGN_CENTER)
        vbox_list.Add((15,15))
        vbox_list.Add(vbox_list_cmd, 0, flag=wx.ALIGN_CENTER)

        vbox_add_content1 = wx.BoxSizer(wx.HORIZONTAL)
        vbox_add_content1.Add(self.timer_name, 0, flag=wx.ALIGN_CENTER)
        vbox_add_content1.Add((15,15))
        vbox_add_content1.Add(self.timer_message, 0, flag=wx.ALIGN_CENTER)

        vbox_add_content2 = wx.BoxSizer(wx.HORIZONTAL)
        vbox_add_content2.Add(self.timer_timeout, 0, flag=wx.ALIGN_CENTER)
        vbox_add_content2.Add((15,15))
        vbox_add_content2.Add(self.timer_loop_times, 0, flag=wx.ALIGN_CENTER)
        vbox_add_content2.Add((15,15))
        vbox_add_content2.Add(self.timer_enable, 0, flag=wx.ALIGN_CENTER)

        vbox_add_cmd = wx.BoxSizer(wx.HORIZONTAL)
        vbox_add_cmd.Add(cmd_add, 0, flag=wx.ALIGN_CENTER)
        vbox_add_cmd.Add((15,15))
        vbox_add_cmd.Add(cmd_clear, 0, flag=wx.ALIGN_CENTER)
        vbox_add_cmd.Add((15,15))
        vbox_add_cmd.Add(cmd_update, 0, flag=wx.ALIGN_CENTER)
        vbox_add_cmd.Add((15,15))
        vbox_add_cmd.Add(cmd_close, 0, flag=wx.ALIGN_CENTER)

        vbox_top.Add((15,15))
        vbox_top.Add(label_title, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(wx.StaticLine(panel), flag=wx.EXPAND)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_list, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_add_content1, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_add_content2, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(vbox_add_cmd, 0, wx.ALIGN_CENTER)

        #Start Fit
        panel.SetSizer(vbox_top)

        self.Bind(wx.EVT_LISTBOX, self.OnListBox, self.listbox)
        self.Bind(wx.EVT_BUTTON, self.OnListUp, list_up)
        self.Bind(wx.EVT_BUTTON, self.OnListDown, list_down)
        self.Bind(wx.EVT_BUTTON, self.OnListDelete, list_delete)
        self.Bind(wx.EVT_BUTTON, self.OnCmdAdd, cmd_add)
        self.Bind(wx.EVT_BUTTON, self.OnCmdClear, cmd_clear)
        self.Bind(wx.EVT_BUTTON, self.OnCmdClose, cmd_close)

        timer_data = database.cur.execute("SELECT * FROM timer")
        print(timer_data)
        #        database.create_db()
        #        database.db_commit()

    def OnListBox(self, event):
        pass

    def OnListUp(self, event):
        total = self.listbox.GetCount()
        select = self.listbox.GetSelection()
        if log:
            print("-----------------------")
        if (total > 0) and (select > 0):
            name1 = self.listbox.GetString(select -1)
            name2 = self.listbox.GetString(select)
            self.listbox.SetString(select-1, name2)
            self.listbox.SetString(select, name1)
            self.menudb[select-1], self.menudb[select] = self.menudb[select], self.menudb[select-1]
            self.listbox.SetSelection(select-1)
            self.listboxChanged = True
        if log:
            for li in self.menudb:
                print(li)

    def OnListDown(self, event):
        total = self.listbox.GetCount()
        select = self.listbox.GetSelection()
        if log:
            print("==================")
        if (total > 0)  and (select < total - 1):
            name1 = self.listbox.GetString(select )
            name2 = self.listbox.GetString(select+1)
            self.listbox.SetString(select, name2)
            self.listbox.SetString(select+1, name1)
            self.menudb[select], self.menudb[select+1] = self.menudb[select+1], self.menudb[select]
            self.listbox.SetSelection(select+1)
            self.listboxChanged = True
        if log:
            for li in self.menudb:
                print(li)

    def OnListDelete(self, event):
        total = self.listbox.GetCount()
        select = self.listbox.GetSelection()
        if (total > 0)  and (select < total):
            self.listbox.Delete(select)
            del self.menudb[select]
            self.listboxChanged = True

        if log:
            for li in self.menudb:
                print(li)

    def OnCmdAdd(self, event):
        name = self.timer_name.GetValue()
        message = self.timer_message.GetValue()
        timeout = self.timer_timeout.GetValue()
        loop_times = self.timer_loop_times.GetValue()
        enable = self.timer_enable.GetValue()
        
        if True:
#        if [name, command, parameter] not in self.menudb:
#            self.menudb.append([name, command, parameter])
            database.cur.execute("INSERT INTO timer VALUES(?,?,?,?)", name, message,timeout, loop_times, enable)
            self.listbox.Append(name)

            self.timer_name.SetValue("")
            self.timer_message.SetValue("")
            self.timer_timeout.SetValue("")
            self.timer_loop_times.SetValue("")
            self.timer_enable.SetValue(False)
            self.listboxChanged = True
        else:
            print("command duplication errors")

    def OnCmdClear(self, event):
        self.cmd_name.SetValue("")
        self.cmd_command.SetValue("")
        self.cmd_parameter.SetValue("")

    def OnCmdClose(self, event):
        if self.listboxChanged:
            print("changed and save")
            #self.quickmenu_read_write(True)
            #self.main_frame.addApp()

        self.Destroy()
        event.Skip()



class App(wx.App):
    """Application class."""
    def OnInit(self):
        self.frame = MainFrame()
        self.frame.Show(True)
        self.SetTopWindow(self.frame)
        return True


database = DBase()

def main():
    app = App()
    app.MainLoop()

if __name__ == '__main__':
    main()
