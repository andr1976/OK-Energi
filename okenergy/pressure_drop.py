import win32api
import win32con
import xlwings as xw
import numpy as np
import math
import fluids


def run_pressure_drop():

    wb = xw.Book.caller()
    wb.app.calculation = "manual"
    sheet = wb.sheets[sheet_name]

    length = sheet.range("STRAIGHT_LENGTH").value
    mesg = "Length = " + str(length)
    win32api.MessageBox(wb.app.hwnd, str(mesg), "Warning", win32con.MB_ICONINFORMATION)

    wb.app.calculation = "automatic"
