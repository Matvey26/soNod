import krpc
import time
import math

conn = krpc.connect()  # подключаемся к серверу 
vessel = conn.space_center.active_vessel  # активный корабль
control = vessel.control  # контролировать корабль
ap = vessel.auto_pilot  # работать с автопилотом

# переменные потоки, при вызове которых мы получаем данные из KSP
ut = conn.add_stream(getattr, conn.space_center, 'ut')  # текущее время в KSP

def length_of_vector(v):
    return math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)


def angle_between_2_vectors(v1, v2):
    r1 = length_of_vector(v1)
    r2 = length_of_vector(v2)
    scalar = sum([v1[i] * v2[i] for i in range(3)])
    return math.acos(scalar / (r1 * r2))


def vector_minus_vector(v1, v2):
    return v1[0] - v2[0], v1[1] - v2[1], v1[2] - v2[2]


Sun = vessel.orbit.body.orbit.body
Sun_rf = Sun.reference_frame
Kerbin = Sun.satellites[2]
Duna = Sun.satellites[3]

def kerbin_pos():
    return Kerbin.position(Sun_rf)

def duna_pos():
    return Duna.position(Sun_rf)

# Считаем фазовый угол между Дюной и Кербином в радианах
phase_angle = angle_between_2_vectors(kerbin_pos(), duna_pos())
TT = 0.5 * Kerbin.orbit.semi_major_axis / Duna.orbit.semi_major_axis + 0.5
need_phase_angle = math.pi * (1 - TT ** (3 / 2))

print(f'Текущий угол: {phase_angle}, требуемый угол: {need_phase_angle}')


w_kerbin = 2 * math.pi / Kerbin.orbit.period  # Угловая скорость Кербина на Солнечной орбите 
w_duna = 2 * math.pi / Duna.orbit.period  # Угловая скорость Дюны на Солнечной орбите

# Пытаемся понять, в какой конфигурации сейчас Кербин и Дюна:
pha0 = angle_between_2_vectors(kerbin_pos(), duna_pos())
time.sleep(0.1)
pha1 = angle_between_2_vectors(kerbin_pos(), duna_pos())
if pha0 > pha1:
    print("Кербин догоняет Дюну")
    delta_angle = phase_angle - need_phase_angle
    if delta_angle < 0:
        print("Мы профукали момент, ждём полного оборота")
        delta_angle += 2 * math.pi
    else:
        print("Нужный момент скоро настанет, ждём")
else:
    print("Кербин обогнал Дюну, ждём полный круг")
    delta_angle = 2 * math.pi - phase_angle - need_phase_angle

t_sec = delta_angle / (w_kerbin - w_duna)  # количество секунд, через которые будет окно старта
t_days = t_sec / (3600 * 6)
t_years = t_days // 426.08
t_days -= t_years * 426.08
print(f"Через {t_years} лет и {t_days} дней нужно запускать ракету")
