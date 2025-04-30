import win32api
import win32con
import xlwings as xw
import numpy as np
import math
import fluids


def run_pressure_drop():

    wb = xw.Book.caller()
    sheet_name = "PressureDrop"
    wb.app.calculation = "manual"
    sheet = wb.sheets[sheet_name]

    sheet.range("REYNOLDS_NO").value = ""
    sheet.range("FRICTION_FACTOR").value = ""
    sheet.range("VELOCITY").value = ""
    sheet.range("PRESSURE_DROP").value = ""

    length = sheet.range("STRAIGHT_LENGTH").value
    rho = sheet.range("RHO").value
    ID = sheet.range("ID").value / 1000
    visc = sheet.range("VISC_CP").value / 1000
    roughness = (sheet.range("ROUGNESS").value) / 1000
    Q = sheet.range("VOL_FLOW").value / 3600

    entrance_no = sheet.range("ENTRANCE_NO").value
    bend_90_no = sheet.range("BEND_90_NO").value
    bend_90_rd = sheet.range("BEND_90_RD").value

    bend_45_no = sheet.range("BEND_45_NO").value
    bend_45_rd = sheet.range("BEND_45_RD").value
    exit_no = sheet.range("EXIT_NO").value

    gate_no = sheet.range("GATE_NO").value
    gate_throat = sheet.range("GATE_D1").value

    ball_no = sheet.range("BALL_NO").value
    ball_throat = sheet.range("BALL_D1").value

    check_no = sheet.range("CHECK_NO").value
    # check_throat = sheet.range("CHECK_D1").value

    globe_no = sheet.range("GLOBE_NO").value
    globe_throat = sheet.range("GLOBE_D1").value

    butterfly_no = sheet.range("BUTTERFLY_NO").value
    # butterfly_thorat = sheet.range("BUTTERFLY_D1").value

    tee_straight_no = sheet.range("TEE_STRAIGHT_NO").value
    tee_side_no = sheet.range("TEE_SIDE_NO").value

    V = Q / ((ID / 2) ** 2 * math.pi)
    Re = fluids.Reynolds(V=V, D=ID, rho=rho, mu=visc)
    fd = fluids.friction_factor(Re, eD=roughness / ID)
    K = fluids.K_from_f(fd=fd, L=length, D=ID)

    if entrance_no:
        K += entrance_no * fluids.entrance_sharp(method="Crane")
    if bend_90_no:
        if not bend_90_rd:
            bend_90_rd = 1.5

        K += bend_90_no * fluids.bend_rounded(
            ID,
            roughness=roughness,
            Re=Re,
            angle=90,
            bend_diameters=bend_90_rd,
            method="Rennels",
        )
    if bend_45_no:
        if not bend_45_rd:
            bend_45_rd = 1.5

        K += bend_45_no * fluids.bend_rounded(
            ID,
            roughness=roughness,
            Re=Re,
            angle=45,
            bend_diameters=bend_45_rd,
            method="Rennels",
        )
    if exit_no:
        K += exit_no * fluids.exit_normal()

    if gate_no:
        if not gate_throat:
            gate_throat = ID
        else:
            gate_throat /= 1000
        K += fluids.K_gate_valve_Crane(gate_throat, ID, angle=45, fd=fd)

    if ball_no:
        if not ball_throat:
            ball_throat = ID
        else:
            ball_throat /= 1000
        K += fluids.K_ball_valve_Crane(ball_throat, ID, angle=45, fd=fd)

    if globe_no:
        if not globe_throat:
            globe_throat = ID
        else:
            globe_throat /= 1000
        K += fluids.K_globe_valve_Crane(globe_throat, ID, fd=fd)

    if butterfly_no:
        K += fluids.K_butterfly_valve_Crane(ID, fd=fd, style=0)

    if check_no:
        K += fluids.K_swing_check_valve_Crane(ID, fd=fd)

    dP = fluids.dP_from_K(K, rho=rho, V=V) / 1e5

    sheet.range("REYNOLDS_NO").value = Re
    sheet.range("FRICTION_FACTOR").value = fd
    sheet.range("VELOCITY").value = V
    sheet.range("PRESSURE_DROP").value = dP
    wb.app.calculation = "automatic"
