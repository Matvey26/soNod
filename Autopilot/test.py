def test3(mu, r1, r2):
    # принимает стандартный гравитационный параметр mu
    # радиус круговой орбиты r1, радиус круговой орбиты r2
    # r1 < r2
    a = (r1 + r2) / 2
    dv1 = math.sqrt(mu / r1) * (math.sqrt(r2 / a) - 1)
    dv2 = math.sqrt(mu / r2) * (1 - math.sqrt(r1 / a))
    # dv1 - На такое значение нужно увеличить скорость, будучи на круговой орбите r1
    # dv2 - на Такое значение нужно увеличить скорость, будучи на переходной траектории гомана (высота апоцентра это r2)
    return dv1, dv2


# Planning circularization burn (using vis-viva equation)
print('Planning circularization burn')
mu = vessel.orbit.body.gravitational_parameter
delta_v = test3(mu, vessel.orbit.periapsis, vessel.orbit.apoapsis)[1]
node = control.add_node(ut() + vessel.orbit.time_to_apoapsis, prograde=delta_v)


# Calculating burn time (using rocket equation)
F = vessel.available_thrust
Isp = vessel.specific_impulse * 9.82
m0 = vessel.mass
m1 = m0 / math.exp(delta_v / Isp)
flow_rate = F / Isp
burn_time = (m0 - m1) / flow_rate
 
# Orientating the ship
ap.disengage()
print('Auto Pilot disengaged')
control.sas = True
print('SAS engaged')
time.sleep(1)
control.sas_mode = conn.space_center.SASMode.prograde
print('SAS set to prograde')

# Waiting until burn
print('Waiting until circularization burn')
burn_ut = ut() + vessel.orbit.time_to_apoapsis - (burn_time/2)
lead_time = 5
conn.space_center.warp_to(burn_ut - lead_time)

# Executing burn
print('Ready to execute burn')
time_to_apoapsis = conn.add_stream(getattr, vessel.orbit, 'time_to_apoapsis')
while time_to_apoapsis() - (burn_time/2) > 0:
	pass
print('Executing burn')
control.throttle = 1.0
time.sleep(burn_time)
print('The vessel is successfully parked at ', target_altitude // 1000,' km orbit')
control.throttle = 0
control.remove_nodes()