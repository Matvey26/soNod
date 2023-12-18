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


# считаем скорости, с которыми ракеты вылетит/влетит из/в сферы влияния Кербина/Дюны
v_sk, v_sd = test3(Sun.gravitational_parameter, Kerbin.orbit.semi_major_axis, Duna.orbit.semi_major_axis)
# считаем, с какой скоростью 
v_ej = math.sqrt(v_sk ** 2 + 2 * Kerbin.gravitational_parameter * (1 / vessel.orbit.semi_major_axis - 1 / Kerbin.sphere_of_influence))
v_rocket = math.sqrt(Kerbin.gravitational_parameter / vessel.orbit.semi_major_axis)
burn = v_ej - v_rocket
print(f'Delta v посчитан {burn}')

# Calculating burn time (using rocket equation)
F = vessel.available_thrust
Isp = vessel.specific_impulse * 9.82
m0 = vessel.mass
m1 = m0 / math.exp(burn/Isp)
flow_rate = F / Isp
burn_time = (m0 - m1) / flow_rate
print(f'Время работы двигателя {burn_time}')


def kerbin_pos():
    return Kerbin.position(Sun_rf)


def kebin_vel():
    return Kerbin.velocity(Sun_rf)


def vessel_pos():
    return vessel.position(Sun_rf)


# Считаем нужный угол для вылета из SOI, в радианах
some_e = 1 + vessel.orbit.semi_major_axis * v_sk ** 2 / Kerbin.gravitational_parameter
need_theta = math.acos(-1 / some_e)
print(f'Требуется угол {math.degrees(need_theta)}')

# угловая скорость ракеты
mu_kerbin = Kerbin.gravitational_parameter
w_rocket = math.sqrt(mu_kerbin / (vessel.orbit.semi_major_axis**3))

# Смотрим на углы в разные моменты времени
theta0 = math.pi - angle_between_2_vectors(kebin_vel(), vector_minus_vector(vessel_pos(), kerbin_pos()))
time.sleep(0.1)
theta1 = math.pi - angle_between_2_vectors(kebin_vel(), vector_minus_vector(vessel_pos(), kerbin_pos()))

print(f"Текущий угол {math.degrees(theta1)}")
if theta0 > theta1:
    if math.pi >= theta1 >= need_theta:
        # print('Подходящий момент для запуска, но нужно проверить, успеем ли мы включить двигатели')
        delta_angle = theta1 - need_theta
        time_to_angle = delta_angle / w_rocket
        if time_to_angle - burn_time / 2 <= 0:
            # print('Момент упущен, ждём полный оборот')
            delta_angle = 2 * math.pi + theta1 - need_theta
    else:
        # print('Момент упущен, ждём полный оборот')
        delta_angle = 2 * math.pi + theta1 - need_theta
else:
    print('Момент упущен, ждём полный оборот')
    delta_angle = 2 * math.pi - (theta1 + need_theta)

print(f'Приёдтся пройти градусов {math.degrees(delta_angle)}')
time_to_angle = delta_angle / w_rocket
min_to_angle = time_to_angle // 60
sec_to_angle = time_to_angle - min_to_angle * 60
print(f'следует стартовать через {min_to_angle} минут и {sec_to_angle} секунд')

print("Устанавливаем манёвр")
node = control.add_node(ut() + time_to_angle, prograde=burn)

print("Устанавливаем цель на Дюну")
conn.space_center.target_body = Duna

# while True:
#     print(node.orbit.distance_at_closest_approach(Duna.orbit))
#     time.sleep(0.1)

print(node.orbit.body.name)

print("Выключаем автопилот")
ap.disengage()
print("Включаем САС")
control.sas = True
time.sleep(1)
print("Ставим САС на манёвр")
control.sas_mode = conn.space_center.SASMode.maneuver


print("Ждём момента до ускорения")
time_when_start = ut() + time_to_angle - burn_time / 2
while time_when_start - ut() > 0:
	time.sleep(0.05)
    
print("Запускаем двигатели")
control.throttle = 1.0
time_when_end = ut() + time_to_angle + burn_time / 2
print(time_when_end - ut())
while time_when_end - ut() > 0:
    time.sleep(0.05)

print("Ракета отправлена в трансфер")
control.throttle = 0
control.remove_nodes()