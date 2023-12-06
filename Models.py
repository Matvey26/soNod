import Settings
import math
import Physics
import Rocket

import matplotlib.pyplot as plt

def OrbitFunction(rocket: Rocket.Rocket, duration: float) -> tuple:
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
    dt = duration / 1000
    while t <= duration:
        r = math.sqrt((pos[0] - xc) ** 2 + (pos[1] - yc) ** 2)  # расстояние относительно новых координат
        height = r - Settings.KERBIN_RADIUS
        press = Physics.Pressure(height)
        VEL = math.sqrt(vel[0] ** 2 + vel[1] ** 2)
        drag = Physics.Drag(Physics.Density(press), VEL, drag_coef, mass)
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

    return (X, Y), Ap, Pr, state_Ap, state_Pr


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


def Model(rocket: Rocket.Rocket):
    # Рисуем кусочек орбиты Кербина
    KERBIN_ORBIT = OrbitKerbin()
    ya_ustal = len(KERBIN_ORBIT[0]) # Придумай нормальные названия этим перменным...
    pomogite = ya_ustal // 4
    gospodi = pomogite + round(ya_ustal * 0.1)
    plt.plot(KERBIN_ORBIT[0][pomogite:gospodi], KERBIN_ORBIT[1][pomogite:gospodi])

    xc, yc = Settings.KERBIN_POS
    mu = Settings.mu
    g = Settings.g
    
    t, dt = 0, 0.05  # time and delta time
    X, Y = [], []
    is_apoasis_reached = False

    # Берём каждую стадию и последовательно её запускаем
    for stage in rocket.stages:
        stage_live_duration = stage.duration

        t = 0
        while t <= stage_live_duration:
            # Считаем ускорение тела в момент времени t
            r = math.sqrt((rocket.position[0] - xc) ** 2 + (rocket.position[1] - yc) ** 2)

            height = r - Settings.KERBIN_RADIUS
            angle = stage.GetAngle(height)
            press = Physics.Pressure(height)
            thrust = stage.GetThrust(press)
            velocity = math.sqrt(rocket.velocity[0] ** 2 + rocket.velocity[1] ** 2)
            mass = stage.GetMass(t)
            drag = Physics.Drag(Physics.Density(press), velocity, rocket.GetDragCoef(), mass)

            g_x, g_y = g * (xc - rocket.position[0]) / r, g * (yc - rocket.position[1]) / r
            a = [math.sin(angle) * (thrust - drag) / mass + g_x, 
                 math.cos(angle) * (thrust - drag) / mass + g_y]  # обновляем ускорение
            
            # Считаем скорость в момент времени t + 1
            rocket.velocity = [rocket.velocity[0] + a[0] * dt, rocket.velocity[1] + a[1] * dt]

            # Считаем координаты ракеты в момент времени t + 1
            rocket.position = [rocket.position[0] + rocket.velocity[0] * dt, rocket.position[1] +rocket.velocity[1] * dt]

            # Смотрим на высоту апоцентра
            if not is_apoasis_reached and height > 10_000:
                graph, Ap, Pr, ap_state, _ = OrbitFunction(rocket, 700)
                if Ap >= Settings.target_apoasis and ap_state[0][0] > 0:
                    print(f't: {t}, Ap: {Ap:.3f}, Pr: {Pr:.3f}', f'pos: {ap_state[0]}, vel: {ap_state[1]}')
                    print(f'Delta v_2 is {math.sqrt(mu / Ap) * (1 - math.sqrt(Pr / ((Ap + Pr) / 2)))}')
                    print(f'Двигатель нужно отключить на высоте {r - Settings.KERBIN_RADIUS}')
                    is_apoasis_reached = True

                    prcnt = round(len(graph[0]) * 30 / 100)
                    plt.plot(graph[0][:prcnt], graph[1][:prcnt])

                    plt.scatter(x=[ap_state[0][0]], y=[ap_state[0][1]])
                    plt.scatter(x=[rocket.position[0]], y=[rocket.position[1]])

            X.append(rocket.position[0])
            Y.append(rocket.position[1])

            t += dt
        
        rocket.StageSeparation()
    
    return X, Y

