from random import randint

class BoardException(Exception):
    pass

class BoardOutException(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за пределы игровой доски!"

class BoardUsedException(BoardException):
    def __str__(self):
        return "Зачем стрелять в одну и ту же клетку?"

class BoardWrongShipException(BoardException):
    pass

class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other): # метод, сравнивающий точки в нашей игре
        # OTHER - это другой объект, в игре будут сравниваться координаты
        return self.x == other.x and self.y == other.y

    def __repr__(self): # метод, отвечающий за вывод точек в консоль
        return f"Dot({self.x}, {self.y})"

class Ship:
    def __init__(self, bow, l, o):
        self.bow = bow # координаты носа корабля
        self.l = l # длинна корабля
        self.o = o # направление(вертикально 0 /горизонтально 1)
        self.lives = l

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.l):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot): # метод выстрел, при помощи метода EQ
        # сравнивает точки при выстреле в корабль по координатам
        return shot in self.dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid

        self.count = 0 # количество пораженных кораблей

        self.field = [["O"] * size for _ in range(size)] # игровая сетка

        self.busy = [] # атрибут, в котором хранятся занятые точки
        self.ships = [] # атрибут, в котором хранятся корабли

    def __str__(self):
        res = "" # записывается вся игровая доска
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d): # проверка, находится ли точка за пределами игровой доски
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))


    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ] # есть точка, near - формирует точки вокруг нашей существующей точки
        for d in ship.dots: # проходим по циклу все точки, которые соседствуют с кораблем
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship) # добавляем список собственных кораблей
        self.contour(ship) #  обводим по контуру корабли

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход противника: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:

    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def greet(self):
        print("-------------------")
        print("      Игра      ")
        print("    Морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Ваша доска:")
            print(self.us.board)
            print("-" * 20)
            print("Доска противника:")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("Ваш ход!")
                repeat = self.us.move()
            else:
                print("Ходит противник!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == len(self.ai.board.ships):
                print("-" * 20)
                print("Поздравляем, Вы одержали победу!")
                break

            if self.us.board.count == len(self.us.board.ships):
                print("-" * 20)
                print("Враг одержал победу!")
                break
            num += 1
    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()