import Rocket
import Models
import matplotlib.pyplot as plt
import math

# Для первой ступени
T0, T1 = 5_100_000, 4_545_651  # тяга в вакууме, тяга у земли (взято из KSP)
drag_coefs = [(0.18, 0.2), (3.4, 0.4), *[(9, 0.25) for i in range(3)], *[(0.3, 0.2) for i in range(4)], (3, 0.2), (0.16, 0.25), (0.2, 0.2), (36, 0.25), (4, 0.2), *[(0.04, 0.001) for i in range(4)], *[(70, 0.25) for i in range(3)], *[(0.2, 0.1) for i in range(3)]]  # [(масса детали в тоннах, коэффициент её сопротивления), ...]
M0, M1 = 287_593, 75_792  # начальная и конечная масса
FuelConsumption = 100.494 * 0.697542142  # потребление твёрдого топлива [ед_т/с]
FuelAmount = 8000  # количество твёрдого топлива [ед_т]
ALL_PARAMETERS_1 = (T0, T1, M0, M1, drag_coefs, FuelConsumption, FuelAmount)


def set_linear(pos0, pos1):
    k = (pos1[1] - pos0[1]) / (pos1[0] - pos0[0])
    b = pos0[1] - pos0[0] * k

    def func(x):
        return min(max(k * x + b, 0), math.pi / 2)
    
    return func


def set_parabolic(pos0, pos1):
    p, q = pos0
    s, r = pos1
    a = (q - r) / (2 * p * s - s ** 2 - p ** 2)
    b = -2 * a * p
    c = q - a * p ** 2 - b * p
    
    def func(x):
        if x < pos0[0] or x > pos1[0]:
            return pos0[1] if x < pos0[0] else pos1[1]
        return a * x**2 + b * x + c

    return func


def set_elliptic(pos0, pos1):
    p, q = pos0
    s, r = pos1
    a = s - p
    b = r - q
    
    def func(x):
        if x < pos0[0] or x > pos1[0]:
            return pos0[1] if x < pos0[0] else pos1[1]
        return math.sqrt(b ** 2 - (b / a) ** 2 * (x - s) ** 2) + q

    return func


def EXPERIMENTS(function_setter):
    OPTIMAL_ELLIPTIC = [(0, 0), ([], []), ([], []), 10**10, ()]
    index = 1
    # Эксперементируем с линейной функцией
    for low in range(8_000, 30_001, 1_500):
        for high in range(30_000, 60_001, 1_500):
            lin_func = function_setter((low, 0), (high, math.pi / 2))
            sonod_ship = Rocket.Rocket(lin_func)
            sonod_ship.CreateStage(stage=Rocket.Stage(*ALL_PARAMETERS_1))

            traectory, orbit, dv, some = Models.Model(sonod_ship, sonod_ship.stages[0], sonod_ship.stages[0].duration)

            if dv < OPTIMAL_ELLIPTIC[3]:
                OPTIMAL_ELLIPTIC[0] = (low, high)
                OPTIMAL_ELLIPTIC[1] = traectory
                OPTIMAL_ELLIPTIC[2] = orbit
                OPTIMAL_ELLIPTIC[3] = dv
                OPTIMAL_ELLIPTIC[4] = some
            
            index += 1

    print("Необходимый delta_v", OPTIMAL_ELLIPTIC[3])
    print(OPTIMAL_ELLIPTIC[0])

    # Рисуем орбиту Кербина
    KERBIN_ORBIT = Models.OrbitKerbin()
    plt.plot(*KERBIN_ORBIT)
    plt.plot(*OPTIMAL_ELLIPTIC[1])
    plt.plot(*OPTIMAL_ELLIPTIC[2])
    plt.gca().set_aspect('equal', adjustable='box')
    plt.show()

    plt.plot(*OPTIMAL_ELLIPTIC[4])
    plt.show()


print("Эллиптический закон")
EXPERIMENTS(set_elliptic)
# print("Линейный закон")
# EXPERIMENTS(set_linear)
# print("Параболический закон")
# EXPERIMENTS(set_parabolic)