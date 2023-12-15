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

# переменные потоки, при вызове которых мы получаем данные из KSP
ut = conn.add_stream(getattr, conn.space_center, 'ut')  # текущее время в KSP
altitude = conn.add_stream(getattr, vessel.flight(), 'mean_altitude')  # высота над уровнем моря в метрах
apoapsis = conn.add_stream(getattr, vessel.orbit, 'apoapsis_altitude')  # высота апоцентра в метрах, если считать от уровня моря
periapsis = conn.add_stream(getattr, vessel.orbit, 'periapsis_altitude')  # высота перицентра в метрах, если счтиать от уровня моря
pitch = conn.add_stream(getattr, vessel.flight(), 'pitch')  # рысканье ракеты


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
while True:
    vessel_pos = vessel.position(Sun_rf)
    kerbin_pos = Kerbin.position(Sun_rf)
    kebin_vel = Kerbin.velocity(Sun_rf)
    duna_pos = Duna.position(Sun_rf)
    # Считаем фазовый угол между Дюной и Кербином
    phase_angle = angle_between_2_vectors(kerbin_pos, duna_pos)
    # Считаем угол для вылета из SOI
    theta = math.pi - angle_between_2_vectors(kebin_vel, vector_minus_vector(vessel_pos, kerbin_pos))

    w_kerbin = 2 * math.pi / 9_203_545  # Угловая скорость Кербина
    w_duna = 2 * math.pi / 17_315_400  # Угловая скорость
    t_days = ((phase_angle - math.radians(44.36)) / (w_kerbin - w_duna)) / (60 * 60 * 6)

    # Так как угол тета берётся по модулю, нужно учесть, что ракета должна находиться от Солцна дальше, чем Кербин
    if length_of_vector(kerbin_pos) < length_of_vector(vessel_pos):
        if phase_angle == 44.36 and theta == 150.36:
            print("LETS GO")
    print(phase_angle, theta)

    time.sleep(0.5)