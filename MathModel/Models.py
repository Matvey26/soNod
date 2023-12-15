import Settings
import math
import Physics
import Rocket

import matplotlib.pyplot as plt


def OrbitFunction(rocket: Rocket.Rocket) -> tuple:
    '''Функция моделирует полёт ракеты, если бы её двигатели были отключены на время дрейфа по орбите.
    Возвращает X, Y - график полёта, высоту апо-, перицентра, состояние ракеты в апо- и перицентре (координаты и вектор скорости)'''
    pos, vel = rocket.position, rocket.velocity
    mass = rocket.GetLastMass()
    drag_coef = rocket.GetDragCoef()

    xc, yc = Settings.KERBIN_POS
    mu = Settings.mu

    Pr, Ap = 0, 0
    state_Pr, state_Ap = (0, 0), (0, 0)
    MAX_VEL, MIN_VEL = 0, 10**9

    X, Y = [pos[0]], [pos[1]]

    t = 0
    semi_major = 1 / (2 / math.sqrt((pos[0] - xc) ** 2 + (pos[1] - yc) ** 2) - (vel[0] ** 2 + vel[1] ** 2) / mu)
    duration = 2 * math.pi * math.sqrt(semi_major ** 3 / mu)  # период вращения по орбите
    dt = duration / 1000
    while t <= duration:
        r = math.sqrt((pos[0] - xc) ** 2 + (pos[1] - yc) ** 2)  # расстояние относительно новых координат
        a = [mu * (xc - pos[0]) / (r ** 3), mu * (yc - pos[1]) / (r ** 3)]  # обновляем ускорение
        
        vel = [vel[0] + a[0] * dt, vel[1] + a[1] * dt]  # обновляем скорость относительно старого ускорения
        pos = [pos[0] + vel[0] * dt, pos[1] + vel[1] * dt]  # обновляем координаты
        
        VEL = math.sqrt(vel[0] ** 2 + vel[1] ** 2)
        if VEL > MAX_VEL:
            MAX_VEL = VEL
            Pr = r
            state_Pr = (pos, vel)
        if VEL < MIN_VEL:
            MIN_VEL = VEL
            Ap = r
            state_Ap = (pos, vel)

        X.append(pos[0])
        Y.append(pos[1])

        t += dt

    return (X, Y), (Ap, state_Ap), (Pr, state_Pr)


# формула была выведена для координат Кербина (0, -600_000)
def OrbitKerbin():
    X_KERBIN, Y_KERBIN = [], []
    RADIUS = Settings.KERBIN_RADIUS

    for x in range(-RADIUS, RADIUS, 10):
        D = math.sqrt(RADIUS ** 2 - x ** 2)

        y = -RADIUS + D
        X_KERBIN.append(x)
        Y_KERBIN.append(y)

    for x in range(RADIUS, -RADIUS, -10):
        D = math.sqrt(RADIUS ** 2 - x ** 2)

        y = -RADIUS - D
        X_KERBIN.append(x)
        Y_KERBIN.append(y)


    return X_KERBIN, Y_KERBIN


def Model(rocket: Rocket.Rocket, stage: Rocket.Stage, stage_live_duration: float):
    xc, yc = Settings.KERBIN_POS
    mu = Settings.mu
    g = Settings.g
    
    t, dt = 0, stage_live_duration / 1000  # time and delta time
    X, Y = [], []
    is_apoasis_reached = False

    t = 0
    while t <= stage_live_duration:
        # Считаем ускорение тела в момент времени t
        radius_vector = rocket.position[0] - xc, rocket.position[1] - yc  # радиус вектор до ракеты
        r = math.sqrt(radius_vector[0] ** 2 + radius_vector[1] ** 2)
        velocity_vector = rocket.velocity  # вектор скорости ракеты 
        velocity = math.sqrt(velocity_vector[0] ** 2 + velocity_vector[1] ** 2)

        height = r - Settings.KERBIN_RADIUS
        angle = rocket.GetAngle(height)
        press = Physics.Pressure(height)
        thrust = stage.GetThrust(press)
        mass = stage.GetMass(t)
        drag = Physics.Drag(Physics.Density(press), velocity, rocket.GetDragCoef(), mass)

        g_x, g_y = g * (xc - rocket.position[0]) / r, g * (yc - rocket.position[1]) / r
        a = [math.sin(angle) * (thrust - drag) / mass + g_x, 
                math.cos(angle) * (thrust - drag) / mass + g_y]  # обновляем ускорение

        # Считаем скорость в момент времени t + 1
        rocket.velocity = [rocket.velocity[0] + a[0] * dt, rocket.velocity[1] + a[1] * dt]

        # Считаем координаты ракеты в момент времени t + 1
        rocket.position = [rocket.position[0] + rocket.velocity[0] * dt, rocket.position[1] +rocket.velocity[1] * dt]

        # Считаем необходимые величины для поиска апоцентра
        h_squared = (radius_vector[0] * velocity_vector[1] - radius_vector[1] * velocity_vector[0]) ** 2  # specific relative angular momentum в квадрате
        epsilon = (velocity ** 2) / 2 - mu / r  # specific orbital energy
        eccentricity = math.sqrt(1 + 2 * epsilon * h_squared / (mu ** 2))  # эксцентриситет
        semi_major = 1 / (2 / math.sqrt(radius_vector[0] ** 2 + radius_vector[1] ** 2) - (velocity_vector[0] ** 2 + velocity_vector[1] ** 2) / mu)

        apoapsis = (1 + eccentricity) * semi_major
        periapsis = (1 - eccentricity) * semi_major

        if apoapsis >= Settings.target_apoapsis:
            print(f'Двигатели нужно выключить на высоте {height} м')
            delta_v = math.sqrt(mu / apoapsis) * (1 - math.sqrt(periapsis / semi_major))
            print(f'При этом в апоцентре нужно будет ускориться на дельту {delta_v} м/с')
            graph, APOAPSIS, _ = OrbitFunction(rocket)

            plt.plot(graph[0], graph[1])

            break
            

        X.append(rocket.position[0])
        Y.append(rocket.position[1])

        t += dt
    else:
        print('мы так и не достигли апоцентра')

    return X, Y

