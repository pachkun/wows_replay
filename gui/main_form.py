# -*- coding: utf-8 -*-
import wx
from logging import getLogger
from pathlib import Path

from validator import DirValidator

__author__ = 'pachkun'

logger = getLogger('gui.main')


class MainForm(wx.Frame):

    def __init__(self, *args, **kwargs):
        super().__init__(parent=None,
                         style=wx.SYSTEM_MENU | wx.CAPTION | wx.CLOSE_BOX,
                         *args, **kwargs)
        self.Center()
        self.main_pnl = wx.Panel(self)

        main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.SetSizer(main_sizer)
        self.make_menu_bar()
        self.Show(True)

    def make_menu_bar(self):
        file_menu = wx.Menu()
        parse_replay = file_menu.Append(wx.NewId(), '&Загрузка реплеев из директории')
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT)

        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT)

        menu_bar = wx.MenuBar()
        menu_bar.Append(file_menu, '&Файл')
        menu_bar.Append(help_menu, '&Помощь')
        self.SetMenuBar(menuBar=menu_bar)

        self.Bind(wx.EVT_MENU, self.on_exit, exit_item)
        self.Bind(wx.EVT_MENU, self.on_about, about_item)
        self.Bind(wx.EVT_MENU, self.on_load_replays, parse_replay)

    def on_load_replays(self, event):
        load_replay_dlg = LoadReplayDialog(parent=self, title='Загрузка реплеев')
        load_replay_dlg.ShowModal()

    def on_exit(self, event):
        self.Close(True)

    def on_about(self, event):
        wx.MessageBox('ups', 'test', wx.ICON_INFORMATION)

