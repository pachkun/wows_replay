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


class LoadReplayDialog(wx.Dialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.replay_path_directory = str(Path.home())

        self._border_size = 5
        self.Center()
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        fg_replay_path_sizer = wx.FlexGridSizer(2, 3, 0, 0)

        self.st_dir_path = wx.StaticText(self, wx.ID_ANY, "Путь к каталогу реплеев:", wx.DefaultPosition,
                                         wx.DefaultSize, self._border_size)
        fg_replay_path_sizer.Add(self.st_dir_path, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, self._border_size)

        self.edit_dir_path = wx.TextCtrl(self, wx.ID_ANY, self.replay_path_directory, wx.DefaultPosition,
                                         size=(300, -1), validator=DirValidator())
        fg_replay_path_sizer.Add(self.edit_dir_path, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, self._border_size)

        self.btn_dir_path = wx.Button(self, wx.ID_ANY, 'Выбрать ...', wx.DefaultPosition,
                                      wx.DefaultSize, self._border_size)
        fg_replay_path_sizer.Add(self.btn_dir_path, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, self._border_size)

        self.edit_dir_path.Bind(wx.EVT_TEXT, self.on_edit_dir_path_text)
        self.btn_dir_path.Bind(wx.EVT_BUTTON, self.choose_dir)

        static_line1 = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)
        static_line2 = wx.StaticLine(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, wx.LI_HORIZONTAL)

        # действия
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btn_apply = wx.Button(self, wx.ID_ANY, 'Пуск', wx.DefaultPosition, wx.DefaultSize, self._border_size)
        self.btn_cancel = wx.Button(self, wx.ID_CANCEL, 'Отмена', wx.DefaultPosition, wx.DefaultSize, self._border_size)

        self.btn_apply.Bind(wx.EVT_BUTTON, self.on_apply)

        btn_sizer.Add(self.btn_apply, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, self._border_size)
        btn_sizer.Add(self.btn_cancel, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, self._border_size)

        # Формирования формы
        main_sizer.Add(fg_replay_path_sizer, 0, wx.EXPAND, self._border_size)
        main_sizer.Add(static_line1, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, self._border_size)
        main_sizer.Add(static_line2, 0, wx.EXPAND | wx.TOP | wx.BOTTOM, self._border_size)
        main_sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT, self._border_size)

        self.SetSizer(main_sizer)
        main_sizer.Fit(self)

    def choose_dir(self, event):
        dlg_dir = wx.DirDialog(self, message='Выберите папку с реплеями World of Warships',
                               defaultPath=self.replay_path_directory)
        if dlg_dir.ShowModal() == wx.ID_OK:
            self.edit_dir_path.SetValue(dlg_dir.GetPath())
        dlg_dir.Destroy()

    def on_edit_dir_path_text(self, event):
        self.replay_path_directory = self.edit_dir_path.GetValue()

    def on_apply(self, event):
        if self.Validate():
            # TODO вызов парсилки
            self.Close(True)
        else:
            return
