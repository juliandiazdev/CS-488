from __future__ import annotations

from abc import abstractmethod
from contextlib import suppress
from dataclasses import dataclass, field
from enum import Enum
from itertools import accumulate, chain
from random import choice, randrange
from typing import ClassVar, Container, Final, Iterable, Optional, Protocol


class Color(Enum):
    RED = 'R'
    YELLOW = 'Y'
    GREEN = 'G'
    BLUE = 'B'
    WHITE = 'W'

    def __str__(self):
        return self.value


ROW_COLORS: Final[tuple[Color, Color, Color, Color]] = (Color.RED, Color.YELLOW, Color.GREEN, Color.BLUE)


@dataclass(frozen=True)
class Die:
    color: Color
    face: int = field(default_factory=lambda: randrange(1, 7))

    def __add__(self, other) -> int:
        return self.face + other

    def __radd__(self, other) -> int:
        return other + self.face

    def __str__(self):
        return f'{self.color}{self.face}'


class Dice(tuple[Die, ...]):
    NON_GRID_COLORS: Final[tuple[Color, Color]] = (Color.WHITE, Color.WHITE)
    COLORS: Final[tuple[Color, Color, Color, Color, Color, Color]] = NON_GRID_COLORS + ROW_COLORS

    @classmethod
    def roll(cls, locked: Container[int] = ()) -> Dice:
        return Dice([Die(c) for c in cls.COLORS if c not in locked])

    def table_takes(self) -> Iterable[Take]:
        total = sum(self[:(len(self.NON_GRID_COLORS))])
        return tuple((Take(i, total)) for i, _ in enumerate(ROW_COLORS))

    def roller_takes(self) -> Iterable[Take]:
        color_map = {c: i for i, c in enumerate(ROW_COLORS)}
        n = len(self.NON_GRID_COLORS)
        for w, c in zip(self[:n], self[n:]):
            yield Take(color_map[c.color], w + c)


@dataclass(frozen=True)
class Take:
    """Taking some combination of dice to mark a spot."""
    row_id: int
    spot: int

    @classmethod
    def from_string(cls, s: str) -> Take:
        try:
            color = Color(s[0].upper())
            row_id = ROW_COLORS.index(color)
            return cls(row_id, int(s[1:]))
        except (KeyError, IndexError, ValueError):
            raise ValueError

    def __str__(self):
        return f"{ROW_COLORS[self.row_id]}{self.spot}"


Move = Optional[Take]


@dataclass
class Row:
    spots: tuple[int, ...]
    marks: list[int] = field(default_factory=list)
    LOCK_REQUIRES: Final[int] = 5  # Spots you need to mark before you can mark the final row and lock it.

    def __str__(self) -> str:
        line = []
        for n in self.spots:
            if n in self.marks:
                line.append('  X')
            elif self.valid_spot(n):
                line.append(f"{n:3d}")
            else:
                line.append('   ')
        return f'{"".join(line)} {"X" if self.locked else "L"}'

    @property
    def locked(self) -> bool:
        return bool(self.marks) and self.marks[-1] == self.spots[-1]

    @property
    def open_spots(self) -> tuple[int, ...]:
        if not self.marks:
            return self.spots
        last_marked_i = self.spots.index(self.marks[-1])
        return self.spots[last_marked_i + 1:]

    @property
    def can_lock(self):
        return len(self.marks) >= self.LOCK_REQUIRES

    def valid_spot(self, spot):
        return spot in self.open_spots and not self.locked and (spot != self.spots[-1] or self.can_lock)

    @property
    def score(self) -> int:
        return Grid.SCORES[len(self.marks) + self.locked]


class Grid(tuple[Row, Row, Row, Row]):
    SPOTS: Final[tuple[range, ...]] = (
        (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12),
        (2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12),
        (12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2),
        (12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2),
    )
    SCORES: Final[tuple[int, ...]] = tuple(accumulate(range(13)))

    def __new__(cls) -> Grid:
        return super().__new__(cls, map(Row, cls.SPOTS))

    def __str__(self) -> str:
        return '\n'.join([f'{ROW_COLORS[i]}{row}' for i, row in enumerate(self)])

    def valid_takes(self, takes: Iterable[Take]) -> Iterable[Take]:
        return (take for take in takes if self[take.row_id].valid_spot(take.spot))

    @property
    def mark_count(self) -> int:
        return sum(len(row.marks) for row in self)


@dataclass
class Card:
    grid: Grid = field(default_factory=Grid)
    penalties: int = 0
    PENALTY_LIMIT: Final[ClassVar[int]] = 4
    PENALTY_POINTS: Final[ClassVar[int]] = 5

    def __str__(self):
        penalties = ' ' * 31 + 'X' * self.penalties + 'O' * (self.PENALTY_LIMIT - self.penalties)
        return f'{self.grid}\n{penalties}'

    def score(self) -> int:
        return sum(row.score for row in self.grid) - self.penalties * self.PENALTY_POINTS

    def locked_row_ids(self) -> Iterable[int]:
        return [i for i, row in enumerate(self.grid) if row.locked]

    def valid_moves(self, takes: Iterable[Take]) -> Iterable[Move]:
        yield None
        yield from self.grid.valid_takes(takes)

    def apply_take(self, take: Take) -> None:
        self.grid[take.row_id].marks.append(take.spot)


class Player(Protocol):
    @abstractmethod
    def take_turn(self, card: Card, dice: Dice, is_roller: bool, moves: Iterable[Move]) -> Move:
        pass


class RandomPlayer(Player):
    def take_turn(self, card: Card, dice: Dice, is_roller: bool, moves: Iterable[Move]) -> Move:
        return choice(list(moves))


class HumanPlayer(Player):
    def __init__(self, name):
        self.name = name

    def take_turn(self, card: Card, dice: Dice, is_roller: bool, moves: Iterable[Move]) -> Move:
        moves = set(moves)
        print('\n' * 10)
        print(self.name)
        print(card)
        print(' '.join(map(str, dice)))
        print('Roller' if is_roller else 'Watcher')
        move = object()
        while move not in moves:
            s = input('Move: ')
            if s.lower() == 'p':
                move = None
            else:
                with suppress(ValueError):
                    move = Take.from_string(s)
        return move


@dataclass
class Game:
    players: tuple[Player, ...]
    cards: tuple[Card, ...] = field(init=False)
    roller_id: int = 0
    dice: Dice = Dice.roll()

    def __post_init__(self) -> None:
        self.cards = tuple(Card() for _ in self.players)

    @property
    def roller(self):
        return self.players[self.roller_id]

    @property
    def roller_card(self):
        return self.cards[self.roller_id]

    def locked(self) -> set[int]:
        return set(chain(*[card.locked_row_ids() for card in self.cards]))

    def is_over(self) -> bool:
        return len(self.locked()) > 1 or max(c.penalties for c in self.cards) >= Card.PENALTY_LIMIT

    def scores(self):
        return [card.score() for card in self.cards]

    def turn(self, player: Player, card: Card, takes: Iterable[Take]) -> None:
        moves = card.valid_moves(takes)
        move = player.take_turn(card, self.dice, self.roller is player, moves)
        if move is not None:
            card.apply_take(move)

    def take_white(self):
        table_takes = self.dice.table_takes()
        for i, (player, card) in enumerate(zip(self.players, self.cards)):
            self.turn(player, card, table_takes)

    def take_colors(self):
        roller_takes = self.dice.roller_takes()
        self.turn(self.roller, self.roller_card, roller_takes)

    def do_round(self) -> bool:
        self.dice = Dice.roll(self.locked())
        roller_marks = self.roller_card.grid.mark_count
        self.take_white()
        if self.is_over():
            return True
        self.take_colors()
        if roller_marks == self.roller_card.grid.mark_count:
            self.roller_card.penalties += 1
        self.roller_id = (self.roller_id + 1) % len(self.players)
        return self.is_over()

    def play(self):
        is_over = False
        while not is_over:
            is_over = self.do_round()
        return self.scores()


print(Game((HumanPlayer('Bob'), HumanPlayer('Alice'))).play())
