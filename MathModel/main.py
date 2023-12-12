import Rocket
import Models
import matplotlib.pyplot as plt

# Для первой ступени
T0, T1 = 10_800_000, 9_806_900  # тяга в вакууме, тяга у земли (взято из KSP)
drag_coefs = [*[[0.2, 0.1] * 4], *[[0.05, 0.2] * 4], *[[70, 0.2] * 4], (15, 0.2), *[[40.5, 2.5]] * 7, [0.2, 0.1], [0.05, 0.2], [0.48, 0.2]]  # коэффициент лобового сопротивления
M0, M1 = 543_380, 303_380  # начальная и конечная масса
FuelConsumption = 100.494  # потребление твёрдого топлива взято из KSP, [ед_т/с]
FuelAmount = 8000  # количество твёрдого топлива, взято из KSP [ед_т]
ALL_PARAMETERS_1 = (T0, T1, M0, M1, drag_coefs, FuelConsumption, FuelAmount)

# Для первой ступени
T0, T1 = 650_000, 586_750  # тяга в вакууме, тяга у земли (взято из KSP)
drag_coefs = [(0.18, 0.2), (18, 0.25), (18, 0.25), (3, 0.2)]  # коэффициент лобового сопротивления (посчитано самостоятельно)
M0, M1 = 43067, 11067  # начальная и конечная масса
FuelConsumption = 18.642  # потребление жидкого топлива взято из KSP, [ед_т/с]
FuelAmount = 1440 * 2.5  # количество жидкого топлива, взято из KSP. На два умножается, т.к. всего два топливных бака, [ед_т]
ALL_PARAMETERS_1 = (T0, T1, M0, M1, drag_coefs, FuelConsumption, FuelAmount)

# # Для второй ступени
# T0, T1 = 4_000_000, 3_746_032  # тяга в вакууме, тяга у земли (взято из KSP)
# drag_coefs = [(15, 0.2), *[[40.5, 2.5]] * 7, [0.2, 0.1], [0.05, 0.2], [0.48, 0.2]]  # коэффициент лобового сопротивления
# M0, M1 = 261_980, 81_980  # начальная и конечная масса
# FuelConsumption = 116.539  # потребление жидкого топлива взято из KSP, [ед_т/с]
# FuelAmount = 3240 * 5  # количество жидкого топлива, взято из KSP [ед_т]
# ALL_PARAMETERS_2 = (T0, T1, M0, M1, drag_coefs, FuelConsumption, FuelAmount)

# Создаём тестовую ракету и одну ступень для неё
sonod_ship = Rocket.Rocket(50_000)
sonod_ship.CreateStage(stage=Rocket.Stage(*ALL_PARAMETERS_1))
# sonod_ship.CreateStage(stage=Rocket.Stage(*ALL_PARAMETERS_1))

 # Рисуем орбиту Кербина
KERBIN_ORBIT = Models.OrbitKerbin()
plt.plot(KERBIN_ORBIT[0], KERBIN_ORBIT[1])

X, Y = Models.Model(sonod_ship, sonod_ship.stages[0], sonod_ship.stages[0].duration)

plt.plot(X, Y)
plt.gca().set_aspect('equal', adjustable='box')
plt.show()