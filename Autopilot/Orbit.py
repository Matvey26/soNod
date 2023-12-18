import krpc
import time
import math
import threading

import logger as log

conn = krpc.connect()  # подключаемся к серверу 
vessel = conn.space_center.active_vessel  # активный корабль
control = vessel.control  # контролировать корабль
ap = vessel.auto_pilot  # работать с автопилотом

# готовимся к запуску
ap.target_pitch_and_heading(90, 90)
ap.engage()

# переменные потоки, при вызове которых мы получаем данные из KSP
ut = conn.add_stream(getattr, conn.space_center, 'ut')  # текущее время в KSP
stage_4_resources = vessel.resources_in_decouple_stage(stage=4, cumulative=False)  # пятая ступень (та, где отделяются ускорители)
srb_fuel = conn.add_stream(stage_4_resources.amount, 'SolidFuel')  # количество топлива во всех ускорителях в сумме
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')  # высота над уровнем моря в метрах
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')  # высота апоцентра в метрах, если считать от уровня моря
periapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')  # высота перицентра в метрах, если счтиать от уровня моря
pitch = conn.add_stream(getattr, vessel.flight(), 'pitch')  # рысканье ракеты

# создаем отдельный поток для логирования
log_file = log.create_log_file()
log_thread = threading.Thread(target=log.collect_data_and_log, args=(vessel, log_file,))
log_thread.start()

# запускаем ракету
print("3...")
time.sleep(0.5)
print("2...")
time.sleep(0.5)
print("1...")
time.sleep(0.5)

print("Start!")
control.activate_next_stage()


# параметры, с которыми ракета будет наклоняться в виде (высота апоцентра, угол рысканья)
# первая точка, это какой угол должен быть в начале его изменения и на какой высоте апоцентра начать его менять
# вторая точка, это значение угла в конце его изменения и высота апоцентра, на котором угол должен быть достигнут
pos1, pos2 = (50_000, 90), (100_000, 0)
k = (pos2[1] - pos1[1]) / (pos2[0] - pos1[0])
b = pos1[1] - pos1[0] * k


# сама функция угла
def angle(ap):
  return k * ap + b


"""
ВЗЛЁТ РАКЕТЫ (доорбитальный этап)
Задачи:
    1. запустить ракету
    2. плавно лечь в горизонт
    3. отбросить ускорители
"""
# ждём, пока апоцентр достигнет нужной высоты
while apoapsis() < pos1[0]:
   time.sleep(0.5)  

# наклоняем ракету до тех пор, пока топливо в тту не закончится
while srb_fuel() >= 0.1:
    # print(apoapsis(), angle(apoapsis()))
    ap.target_pitch = angle(apoapsis())
    time.sleep(0.2)
ap.target_pitch = 0

# отсоединаяем их
control.activate_next_stage()
print("Ускорители отброшены")




"""
ВЫХОД НА КРУГОВУЮ ОРБИТУ (орбитальный этап)
Задачи:
    1. Открыть солнечные панели
    2. Набрать необходимую дельта скорость
"""
# Получение конкретной антенны и солнечной панели
antennas = vessel.parts.antennas
solar_pannels = vessel.parts.solar_panels

# Раскрываем антенны 
for a in antennas:
    if a.deployable:
        a.deployed = True

# Раскрываем панели
for s in solar_pannels:
    if s.deployable:
        s.deployed = True


# Функция, которая считает гомановский переход
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

time.sleep(3)

print("Добавляем ноду манёвра")
mu = vessel.orbit.body.gravitational_parameter
delta_v = test3(mu, vessel.orbit.periapsis, vessel.orbit.apoapsis)[1]
node = control.add_node(ut() + vessel.orbit.time_to_apoapsis, prograde=delta_v)
time.sleep(1)

print("Считаем время работы двигателя")
F = vessel.available_thrust
Isp = vessel.specific_impulse * 9.82
m0 = vessel.mass
m1 = m0 / math.exp(delta_v / Isp)
flow_rate = F / Isp
burn_time = (m0 - m1) / flow_rate

print("Выключаем автопилот")
ap.disengage()
print("Включаем САС")
control.sas = True
time.sleep(1)
print("Ставим САС на манёвр")
control.sas_mode = conn.space_center.SASMode.maneuver

print("Ждём момента до ускорения")
burn_ut = ut() + vessel.orbit.time_to_apoapsis - (burn_time/2)
lead_time = 5
time_to_apoapsis = conn.add_stream(getattr, vessel.orbit, "time_to_apoapsis")
while time_to_apoapsis() - (burn_time / 2) > 0:
	time.sleep(0.05)
    
print("Запускаем двигатели")
control.throttle = 1.0
time_when_end = ut() + vessel.orbit.time_to_apoapsis + burn_time / 2
print(time_when_end - ut())
while time_when_end - ut() > 0:
    time.sleep(0.05)

print("Ракета успешно выведена на орбиту 100 км")
control.throttle = 0
control.remove_nodes()
