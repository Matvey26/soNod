import json
import math
import matplotlib.pyplot as plt

velocity = []
altitude = []

# Считываем данные с логов
with open('Logs/example.json', 'r') as file:
    for line in file:
        data = json.loads(line)
        velocity.append(math.sqrt((data["Velocity"][0]) ** 2 + (data["Velocity"][1]) ** 2 + (data["Velocity"][2]) ** 2))
        altitude.append(data["Altitude"])

# Построение графика
plt.figure(figsize=(8, 6))
plt.plot(velocity, altitude, 'b')
plt.title('Длина вектора скорости и высота')
plt.xlabel('Длина вектора скорости')
plt.ylabel('Высота')
plt.show()