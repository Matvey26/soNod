import krpc
import time
import math

conn = krpc.connect()  # подключаемся к серверу 
vessel = conn.space_center.active_vessel  # активный корабль
control = vessel.control  # контролировать корабль
ap = vessel.auto_pilot  # работать с автопилотом

# готовимся к запуску
ap.target_pitch_and_heading(90, 90)
ap.engage()

stage_5_resources = vessel.resources_in_decouple_stage(stage=5, cumulative=False)
ut = conn.add_stream(getattr, conn.space_center, 'ut')
srb_fuel = conn.add_stream(stage_5_resources.amount, 'SolidFuel')  
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')
periapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')
pitch = conn.add_stream(getattr, vessel.flight(), 'pitch')


# запускаем ракету
print("3...")
time.sleep(0.5)
print("2...")
time.sleep(0.5)
print("1...")
time.sleep(0.5)

print("Start!")
control.activate_next_stage()

pos1, pos2 = (50_000, 90), (100_000, 0)
k = (pos2[1] - pos1[1]) / (pos2[0] - pos1[0])
b = pos1[1] - pos1[0] * k


def angle(ap):
  return k * ap + b


print(angle(50_000), angle(100_000))

while apoapsis() < pos1[0]:
   time.sleep(0.5)  

while srb_fuel() >= 0.01:
    print(apoapsis(), angle(apoapsis()))
    ap.target_pitch = angle(apoapsis())
    time.sleep(0.2)

control.activate_next_stage()

# Мы вылетели из атмосферы кербина (NEXT STEP)

# Получение конкертной антенны и солнечной панели
#antennas = vessel.parts.with_tag('com1')
#solar_pannels = vessel.parts.with_tag('Pan1')

# Включение
antennas = vessel.parts.antennas
solar_pannels = vessel.parts.solar_panels

for s in solar_pannels:
    s.deployed = True

print("автопилот установлен на pitch = 0...")
ap.target_pitch = 0


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
print("Добавляем ноду манёвра")
mu = vessel.orbit.body.gravitational_parameter
delta_v = test3(mu, vessel.orbit.periapsis, vessel.orbit.apoapsis)[1]
node = control.add_node(ut() + vessel.orbit.time_to_apoapsis, prograde=delta_v)

time.sleep(1)

# Calculating burn time (using rocket equation)
print("Считаем время работы двигателя")
F = vessel.available_thrust
Isp = vessel.specific_impulse * 9.82
m0 = vessel.mass
m1 = m0 / math.exp(delta_v / Isp)
flow_rate = F / Isp
burn_time = (m0 - m1) / flow_rate
 
# Orientating the ship
ap.disengage()
print("Выключаем автопилот")
control.sas = True
print("Включаем САС")
time.sleep(1)
control.sas_mode = conn.space_center.SASMode.prograde
print("Ставим САС на прогрейд")

# Waiting until burn
print("Ускоряем время до момента, когда мы ускоряться будем")
burn_ut = ut() + vessel.orbit.time_to_apoapsis - (burn_time/2)
lead_time = 5
# conn.space_center.warp_to(burn_ut - lead_time)

# Executing burn
print("Ща запустим двигатели")
time_to_apoapsis = conn.add_stream(getattr, vessel.orbit, "time_to_apoapsis")
while time_to_apoapsis() - (burn_time / 2) > 0:
	time.sleep(0.05)
    
print("Запускаем двигатели")
control.throttle = 1.0
time_when_end = ut() + vessel.orbit.time_to_apoapsis + burn_time / 2
print(time_when_end - ut())
while time_when_end - ut() > 0:
    time.sleep(0.05)
print("The vessel is successfully parked at 100km orbit")
control.throttle = 0
control.remove_nodes()
