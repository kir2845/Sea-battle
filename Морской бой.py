from random import randint

class BoardExcept(Exception):
    pass

class BoardOutExcept(BoardExcept):
    def __str__(self):
        print()
        return "Упс, Вы не попали в игровое поле :(\nКоординаты должны быть меньше 7-ми.\nПожалуйста, переходите."


class BoardUsedExcept(BoardExcept):
    def __str__(self):
        return "Вы сюда уже стреляли.\nПереходите еще раз."

class BoardWrongShipExcept(BoardExcept):
    pass


class Dot:
    def __init__(self, coordx, coordy):
        self.coordx = coordx
        self.coordy = coordy

    def __eq__(self, other):     # метод, сравнивающий содерживое клеток между собой
        return self.coordx == other.coordx and self.coordy == other.coordy

    def __repr__(self):           # метод, выдающий список клеток в консоль
        return f"Dot({self.coordx}, {self.coordy})"


class Ship:
    def __init__(self, len, nose, orient, alive):
        self.len= len           # длина корабля в клетках
        self.nose = nose        # положение "носа" корабля
        self.orient = orient    # ориентация корабля (горизонтальная при "0", вертикальная при "1"
        self.alive = alive      # количество еще живых клеток корабля

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.len):
            cur_x = self.nose.coordx  # координата "x" клетки
            cur_y = self.nose.coordy  # координата "y" клетки

            if self.orient == 1:
                cur_x += i

            elif self.orient == 0:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots


class Board:
    def __init__(self, hid = False, size = 6):
        self.hid = hid
        self.size = size
        self.count = 0

        self.field = [[" "] * size for _ in range(size)]

        self.busy = []
        self.ships = []

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        print('___________________________')
        for i, row in enumerate(self.field):
            res += f"\n---------------------------\n{i + 1} | " +  " | ".join(row) + " | "

        if self.hid:
            res = res.replace("П", " ")
        return res

    def out(self, d):
        return  not((0 <= d.coordx < self.size) and (0 <= d.coordy < self.size))

    def contour(self, ship, verb = False):
        near = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]

        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.coordx + dx, d.coordy + dy)
                #self.field[cur.coordx][cur.coordy] = "!"
                if not(self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.coordx][cur.coordy] = "-"
                    self.busy.append(cur)

    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipExcept()
        for d in ship.dots:
            self.field[d.coordx][d.coordy] = "П"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):
        if self.out(d):
             raise BoardOutExcept()

        if d in self.busy:
             raise BoardUsedExcept()

        self.busy.append(d)

        for ship in self.ships:
            if ship.shooten(d):
                ship.alive -= 1
                self.field[d.coordx][d.coordy] = "!"
                if ship.alive == 0:
                    self.count += 1
                    self.contour(ship, verb = True)
                    print("Ого! Корабль уничтожен!")
                    return  False
                else:
                    print("Ой, корабль ранен!")
                    return True

        self.field[d.coordx][d.coordy] = "-"
        print("Мимо")
        return False

    def begin(self):
        self.busy = []


class Game:
    def __init__(self, size = 6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size = self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(l, Dot(randint(0, self.size), randint(0, self.size)), randint(0, 1), l)
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipExcept:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return  board


    def loop(self):
        num = 0
        while True:
            print()
            print("   - Поле ПОЛЬЗОВАТЕЛЯ -")
            print(self.us.board)
            print("_" * 27)
            print()
            print("      - Поле КОМПА -")
            print(self.ai.board)
            print("_" * 27)
            if num % 2 == 0:
                #print("Ходит чел")
                repeat = self.us.move()
            else:
                print("Ходит комп")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print()
                print("_" * 36)
                print("Пользователь выиграл! ПОЗДРАВЛЯЕМ!!!")
                break

            if self.us.board.count == 7:
                print()
                print("_" * 40)
                print("КОМП выиграл! А тебе надо потренироваться:(")
                break
            num += 1


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
            except BoardExcept as e:
                print(e)


class User(Player):
    def ask(self):
        while True:
            print()
            cords = input("   Ходит ПОЛЬЗОВАТЕЛЬ\nВведите координаты X и Y\nчерез пробел и нажмите Enter:  ").split()

            if len(cords) != 2:
                print("Введите 2 координаты через пробел")
                continue

            x, y = cords

            if not(x.isdigit()) or not (y.isdigit()):
                print()
                print("Пожалуйста,Вводите только числа от 1 до 6!\nПопробуйте еще раз")
                continue

            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)


class AI(Player):
    def ask(self):
        d = Dot(randint(0,5), randint(0,5))
        print(f"Минуточку, ход ПК: {d.coordx+1} {d.coordy+1}")
        return d

print("_____________________________________")
print("Добро пожаловать в игру 'МОРСКОЙ БОЙ'\n\n     Формат ввода: x  y, где\n х - координата Х, а y - координата Y")
print("_____________________________________")

g = Game()
g.loop()