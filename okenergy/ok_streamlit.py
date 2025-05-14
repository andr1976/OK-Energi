import streamlit as st
import numpy as np
import math
import fluids

length = float(st.text_input("Length (m)", 0))


length = float(st.text_input("Length (m)", 0))
rho = float(st.text_input("Density (kg/h)", 1000))
ID = float(st.text_input("Inner diameter (mm)", 0)) / 1000
visc = float(st.text_input("Viscosity (cP)", 1)) / 1000
roughness = float(st.text_input("Roughness", 0.045)) / 1000
Q = float(st.text_input("Volume flow (m3/h)", 0)) / 3600

entrance_no = 1  # sheet.range("ENTRANCE_NO").value

bend_90_no = float(st.text_input("90 degree bends", 0))
bend_90_rd = float(st.text_input("90 degree nemd r/D", 1.5))
bend_45_no = float(st.text_input("45 degree bends", 0))
bend_45_rd = float(st.text_input("45 degree nemd r/D", 1.5))

exit_no = 1

gate_no = float(st.text_input("Number of gate valves", 0))
gate_throat = float(st.text_input("Gate valve throat area (mm)", ID * 1000)) / 1000

ball_no = float(st.text_input("Number of ball valves", 0))
ball_throat = float(st.text_input("Ball valve throat area (mm)", ID * 1000)) / 1000

globe_no = float(st.text_input("Number of globe valves", 0))
globe_throat = float(st.text_input("Globe valve throat area (mm)", ID * 1000)) / 1000


check_no = float(st.text_input("Number of check valves"), 0)

butterfly_no = float(st.text_input("Number of butterfly valves"), 0)

tee_straight_no = float(st.text_input("Number of tee's (straight through)"), 0)
tee_side_no = float(st.text_input("Number of tee's (side through)"), 0)

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
    K += gate_no * fluids.K_gate_valve_Crane(gate_throat, ID, angle=45, fd=fd)

if ball_no:
    if not ball_throat:
        ball_throat = ID
    else:
        ball_throat /= 1000
    K += ball_no * fluids.K_ball_valve_Crane(ball_throat, ID, angle=45, fd=fd)

if globe_no:
    if not globe_throat:
        globe_throat = ID
    else:
        globe_throat /= 1000
    K += globe_no * fluids.K_globe_valve_Crane(globe_throat, ID, fd=fd)

if butterfly_no:
    K += butterfly_no * fluids.K_butterfly_valve_Crane(ID, fd=fd, style=0)

if check_no:
    K += check_no * fluids.K_swing_check_valve_Crane(ID, fd=fd)

if tee_straight_no:
    K += tee_straight_no * fluids.Darby3K(
        Di=ID, Re=Re, name="Tee, Run-through, threaded, (r/D = 1)"
    )

if tee_side_no:
    K += tee_side_no * fluids.Darby3K(
        Di=ID, Re=Re, name="Tee, Through-branch, (as elbow), flanged, (r/D = 1)"
    )

dP = fluids.dP_from_K(K, rho=rho, V=V) / 1e5

st.text("REYNOLDS_NO", str(Re))

# sheet.range("FRICTION_FACTOR").value = fd
# sheet.range("VELOCITY").value = V
# sheet.range("PRESSURE_DROP").value = dP
