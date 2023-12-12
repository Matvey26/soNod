import math


class Rocket:
    def __init__(self, angle_height):
        self.stages = []  # ступени расположены в привычном порядке. 0 индекс это 1-я ступень
        self.position, self.velocity = (0, 0), (0, 0)  # последние сохранённые позиция и вектор скорости
        self.current_mass = 0  # последняя сохранённая масса ракеты, используйте GetLastMass для получения этого параметра
        self.beta = math.pi / (2 * angle_height)

    
    def CreateStage(self, stage):
        '''Добавляет новую ступень. Новая ступень становится первой'''
        self.stages = [stage] + self.stages

    
    def StageSeparation(self):
        if len(self.stages) > 1:
            self.stages = self.stages[1:]
            print("Ступень отброшена успешно")
        else:
            print("Ступень не отброшена: нечего отсоединять")

    
    def GetLastMass(self):
        if len(self.stages) > 0:
            self.current_mass = self.stages[0].GetLastMass()
            return self.current_mass

    
    def GetDragCoef(self):
        a, b = 0, 0
        for stage in self.stages:
            for i in stage.drag_coefs:
                a += i[0] * i[1]
                b += i[0]
        
        return a / b
    

    def GetAngle(self, height):
        '''зависимость угла наклона [рад] от высоты полёта'''
        return max(min(height * self.beta, math.pi / 2), 0)


class Stage:
    def __init__(self, thrust_start, thrust_end, mass_start, mass_end, drag_coefs, fuel_consumption, fuel_amount):
        self.T0, self.T1 = thrust_start, thrust_end  # тяга в вакууме, тяга у земли
        self.dT = self.T1 - self.T0

        self.M0, self.M1 = mass_start, mass_end   # начальная и конечная масса (нужно брать массу всей ракеты, кроме ступеней, которые ниже)
        self.current_mass = self.M0  # последняя сохранённая масса
        self.duration = fuel_amount / fuel_consumption
        self.kM = (self.M1 - self.M0) / self.duration

        self.drag_coefs = drag_coefs  # массив вида [(масса детали в тоннах, её коэффициент сопротивления), ...]
    

    def GetThrust(self, press):
        '''Тяга [Н] в KSP зависит от давления и рассчитывается по формуле T(p) = T0 + deltaT * p(h),
        где T(p) - искомая тяга [Н],
            T0 - тяга в вакууме [Н],
            delta T - разность между тягой у земли и тягой в вакууме [Н/атм],
            p(h) - давление на данной высоте [атм]'''
        return max(min(self.T0 + self.dT * press, self.T0), self.T1)
    

    def GetMass(self, t):
        '''зависимость массы [кг] корабля от времени. k - расход массы в секунду [кг/с]'''
        self.current_mass = max(min(self.M0 + self.kM * t, self.M0), self.M1)  # фиксируем последнее значение массы
        return self.current_mass
    

    def GetLastMass(self):
        return self.current_mass