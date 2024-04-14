import enum

class CarStatus(enum.Enum):
    ON_ROAD = 1
    PARKING = 2
class IncreaseSpeed():
    '''
    Iterator for increasing the speed with the default step of 10 km/h
    You can implement this one after Iterators FP topic

    Constructor params:
      current_speed: a value to start with, km/h
      max_speed: a maximum possible value, km/h

    Make sure your iterator is not exceeding the maximum allowed value
    '''

    def __init__(self, current_speed: int, max_speed: int):
        self.current_speed = current_speed
        self.max_speed = max_speed

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_speed <= self.max_speed - 10:
            self.current_speed += 10
            return self.current_speed
        else:
            self.current_speed = self.max_speed
            return self.current_speed


class DecreaseSpeed():
    '''
    Iterator for decreasing the speed with the default step of 10 km/h
    You can implement this one after Iterators FP topic

    Constructor params:
      current_speed: a value to start with, km/h

    Make sure your iterator is not going below zero
    '''

    def __init__(self, current_speed: int):
        self.current_speed = current_speed

    def __iter__(self):
        return self

    def __next__(self):
        if self.current_speed >= 10:
            self.current_speed -= 10
            return self.current_speed
        else:
            self.current_speed = 0
            return self.current_speed

class Car():
    '''
    Car class.
    Has a class variable for counting total amount of cars on the road (increased by 1 upon instance initialization).

    Constructor params:
      max_speed: a maximum possible speed, km/h
      current_speed: current speed, km/h (0 by default)
      state: reflects if the Car is in the parking or on the road

    Methods:
      accelerate: increases the speed using IncreaseSpeed() iterator either once or gradually to the upper_border
      brake: decreases the speed using DecreaseSpeed() iterator either once or gradually to the lower_border
      parking: if the Car is not already in the parking, removes the Car from the road
      total_cars: show the total amount of cars on the road
      show_weather: shows the current weather conditions
    '''
    car_ctr = 0
    def __init__(self, max_speed: int, current_speed = 0):
        self.max_speed = max_speed
        if current_speed <= 0:
            self.current_speed = 0
            self.state = CarStatus.PARKING
        else:
            self.current_speed = current_speed
            self.state = CarStatus.ON_ROAD
            Car.car_ctr += 1
        self.decr_iter = iter(DecreaseSpeed(current_speed))
        self.incr_iter = iter(IncreaseSpeed(current_speed, max_speed))



    def accelerate(self, upper_border=None):
        # check for state
        # create an instance of IncreaseSpeed iterator
        # check if smth passed to upper_border and if it is valid speed value
        # if True, increase the speed gradually iterating over your increaser until upper_border is met
        # print a message at each speed increase
        # else increase the speed once
        # return the message with current speed
        if upper_border > self.max_speed:
            upper_border = self.max_speed
        while upper_border > self.current_speed:
            self.current_speed = next(self.incr_iter)

    def brake(self, lower_border=None):
        # create an instance of DecreaseSpeed iterator
        # check if smth passed to lower_border and if it is valid speed value
        # if True, decrease the speed gradually iterating over your decreaser until lower_border is met
        # print a message at each speed decrease
        # else increase the speed once
        # return the message with current speed
        if lower_border < 0:
            lower_border = 0
        while lower_border < self.current_speed:
            self.current_speed = next(self.decr_iter)


    # the next three functions you have to define yourself
    # one of the is class method, one - static and one - regular method (not necessarily in this order, it's for you to think)

    def parking(self):
        # gets car off the road (use state and class variable)
        # check: should not be able to move the car off the road if it's not there
        self.brake(0)
        self.state = CarStatus.PARKING

    def total_cars(self):
        # displays total amount of cars on the road
        print(Car.car_ctr)
        return Car.car_ctr

    def show_weather(self):
        # displays weather conditions
        pass

if __name__ == "__main__":
    porche = Car(400, 0)
    kopeika = Car(60, 40)
    porche.accelerate(600)
    print(porche.current_speed)
