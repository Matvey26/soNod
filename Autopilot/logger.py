import json
import time
import datetime
import krpc

# Флаг для остановки логгера
continue_logging = True

# Создаем файл с уникальным именем
def create_log_file():
    current_time = datetime.datetime.now().strftime("%H-%M")  # Генерируем уникальное имя файла на основе текущего времени
    file_name = f"Logs/{current_time}.json"
    file = open(file_name, 'a')
    return file

# Записываем данные в файл
def append_to_log(file, data):
    json.dump(data, file)
    file.write('\n')

# Остановка логгера
def stop_logging():
    global continue_logging
    continue_logging = False 

# Сбор информации о ракете (каждые 0.5 секунд)
def collect_data_and_log(vessel, log_file):
    while vessel.situation.name != "splashed" and vessel.situation.name != "landed" and continue_logging:

        # Считываиние данных
        velocity = vessel.flight(vessel.orbit.body.reference_frame).velocity
        altitude = vessel.flight().mean_altitude
        acceleration = vessel.flight().g_force

        data = {
            "Velocity": velocity,
            "Acceleration": acceleration,
            "Altitude": altitude
        }
        
        # Вносим данные
        append_to_log(log_file, data)
        time.sleep(0.5)

    # Закрываем файл, когда полёт окончен
    log_file.close()