# -*- coding: utf-8 -*-
from pathlib import Path
import wx

__author__ = 'pachkun'


class DirValidator(wx.Validator):

    def __init__(self):
        super().__init__()

    def Clone(self):
        return DirValidator()

    def Validate(self, parent):
        TextCtrl = self.GetWindow()  # type: TextCtrl
        val = TextCtrl.GetValue()
        if not Path(val).is_dir():
            wx.MessageBox(f"Указаной папки {val} не сущестует", "Error", style=wx.ICON_ERROR)
            TextCtrl.SetFocus()
            return False
        return True

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True
