#!/usr/bin/env python
# -*- coding: utf-8 -*-
import wx
import os
import sys
import shutil
import subprocess 

class Frame(wx.Frame):
    """Frame class, main window."""
    def __init__(self):
        """Create a Frame instance"""
        wx.Frame.__init__(self, None, -1, "Update Online", size=(800, 600))
        self.Centre()
        self.panel = wx.Panel(self)

        self.update_info = "update.info"
        self.update_path = "update"

        label_title = wx.StaticText(self.panel, -1, "Update Online")
        self.text_multi_text = wx.TextCtrl(self.panel, -1, "", size=(700, 400), style=wx.TE_MULTILINE)
        button_close = wx.Button(self.panel, -1, label="Close")

        vbox_top = wx.BoxSizer(wx.VERTICAL)
        vbox_top.Add((15,15))
        vbox_top.Add(label_title, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(wx.StaticLine(self.panel), flag=wx.EXPAND)
        vbox_top.Add((15,15))
        vbox_top.Add(self.text_multi_text, 0, wx.ALIGN_CENTER)
        vbox_top.Add((15,15))
        vbox_top.Add(wx.StaticLine(self.panel), flag=wx.EXPAND)
        vbox_top.Add((15,15))
        vbox_top.Add((15,15))
        vbox_top.Add(button_close, 0, wx.ALIGN_CENTER)

        self.panel.SetSizer(vbox_top)
        vbox_top.Fit(self.panel)

        self.Bind(wx.EVT_BUTTON, self.OnClose, button_close)

        self.do_update()

    def OnClose(self, event):
        self.Destroy()
        if sys.platform == "win32":
            subprocess.Popen("newmenus.exe")
        elif sys.platform == "darwin":
            subprocess.Popen("newmenus.dmg")
        else:
            subprocess.Popen("newmenus.py")

    def do_update(self):
        # print "current directory: " + os.getcwd()
        os.chdir(self.update_path)
        try:
            fd = open(self.update_info, 'r')
        except IOError:
            print(("file: " + self.update_info + " no exist!"))
            return False

        # os.getcwd()
        package_enable = False
        for line in fd:
            line = line.strip()
            if line.startswith("update package"):
                package_enable = True
            elif (package_enable == True) and line.startswith("+"):
                #+ file:; to:  #- file:
                li = (line[1:].strip()).split(":")
                if (len(li) > 1):
                    file = li[1].strip()
                    d_file = ".." + os.sep + file
                    if os.path.exists(file):
                        shutil.copy2(file, d_file)
                        # print "copy " + file + " to " + d_file
                        string = "copy " + file + " to " + d_file
                        self.text_multi_text.AppendText(string+"\n")
            elif (package_enable == True) and line.startswith("-"):
                li = (line[1:].strip()).split(":")
                if (len(li) > 1):
                    file = li[1]
                    if os.path.isdir(file):
                        shutil.rmtree(file)
                        # print "rmtree " + file
                        string = "rmtree " + file
                        self.text_multi_text.AppendText(string+"\n")

                    elif os.path.isfile(file):
                        os.remove(file)
                        # print "remove " + file
                        string = "remove " + file
                        self.text_multi_text.AppendText(string+"\n")

            else:
                package_enable = False
        fd.close()
        shutil.rmtree(self.update_path)
        self.text_multi_text.AppendText("\nUpdate finished. We will start newmenus.\n")

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
    if (len(sys.argv) > 1):
        if sys.argv[1] == "newmenus":
            main()
