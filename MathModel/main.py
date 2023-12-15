import Rocket
import Models
import matplotlib.pyplot as plt
import math

# Для первой ступени
T0, T1 = 5_100_000, 4_545_651  # тяга в вакууме, тяга у земли (взято из KSP)
drag_coefs = [(0.18, 0.2), (3.4, 0.4), *[(9, 0.25) for i in range(3)], *[(0.3, 0.2) for i in range(4)], (3, 0.2), (0.16, 0.25), (0.2, 0.2), (36, 0.25), (4, 0.2), *[(0.04, 0.001) for i in range(4)], *[(70, 0.25) for i in range(3)], *[(0.2, 0.1) for i in range(3)]]  # [(масса детали в тоннах, коэффициент её сопротивления), ...]
M0, M1 = 290_254, 110_254  # начальная и конечная масса
FuelConsumption = 100.494 * 0.497542142  # потребление твёрдого топлива [ед_т/с]
FuelAmount = 8000  # количество твёрдого топлива [ед_т]
ALL_PARAMETERS_1 = (T0, T1, M0, M1, drag_coefs, FuelConsumption, FuelAmount)

# Создаём тестовую ракету и одну ступень для неё
sonod_ship = Rocket.Rocket((17_000, 0), (45_000, math.pi / 2))
sonod_ship.CreateStage(stage=Rocket.Stage(*ALL_PARAMETERS_1))

 # Рисуем орбиту Кербина
KERBIN_ORBIT = Models.OrbitKerbin()
plt.plot(KERBIN_ORBIT[0], KERBIN_ORBIT[1])

print(f'Масса ракеты перед началом полёта {sonod_ship.GetLastMass()}')
X, Y = Models.Model(sonod_ship, sonod_ship.stages[0], sonod_ship.stages[0].duration)
print(f'Масса ракеты под конец работы двигателей {sonod_ship.GetLastMass()}')

plt.plot(X, Y)
plt.gca().set_aspect('equal', adjustable='box')
plt.show()