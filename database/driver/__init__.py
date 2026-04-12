import sqlite3 as sq
from . import __exceptions__ as exceptions

from data.config import PATHS


class DataBase:
    def __init__(self, path: str, tables: list[str]):
        """
        :param path: имя файла базы данных (в директории PATHS.DB)
        :param tables: список имён таблиц в базе (можно выбрать один из списков в классе Tables)
        """

        self.tables = tables

        self.path = path.strip().lower().replace('\\', '/')
        if self.path[0] == '/':
            self.path = self.path[1:]
        self.path = PATHS.DATA + self.path

        with open(self.path) as _:
            pass

    def search(self, table: str, column: str, mean: str | int, quantity: bool = False) -> dict[str, ...] | list[dict[str, ...]]:
        """
        Функция поиска.

        Возможные ошибки: TableNotFound, sqlite3.OperationalError: no such column
        :param table: имя таблицы
        :param column: название колонки для поиска
        :param mean: цель поиска
        :param quantity: множественный поиск (по умолчанию выключен)
        :return: если множественный поиск включён, вернёт список словарей, иначе -- один словарь.
        Если записи не найдены, возвращает пустой список, если множественный поиск включён, иначе -- null
        """

        with sq.connect(self.path) as con:
            con.row_factory = sq.Row
            cur = con.cursor()

            cur.execute(f"select * from {table} where {column} = :x", {'x': mean})
            if quantity:
                res = cur.fetchall()
                if len(res) == 0:
                    raise exceptions.EntryNotFound
                return list(map(dict, res))
            else:
                res = cur.fetchone()
                if res is None:
                    raise exceptions.EntryNotFound
                return dict(res)


    def insert(self, table: str, values: list[...]):
        """
        Функция вставки данных в таблицу. Важно, чтобы количество данных совпадало с количеством колонок в таблице.

        Возможные ошибки: TableNotFound, встроенная ошибка sqlite3
        :param table: имя таблицы
        :param values: список данных, перечисленных в порядке колонок таблицы
        """

        with sq.connect(self.path) as con:
            cur = con.cursor()
            cur.execute(f"insert into {table} values (%s)" % ','.join('?' * len(values)), values)


    def searchall(self, table: str, column: str) -> list[...]:
        """
        Функция поиска всех значений определенной колонки определенной таблицы.

        Возможные ошибки: TableNotFound, sqlite3.OperationalError: no such column
        :param table: имя таблицы
        :param column: название колонки
        :return: список
        """

        with sq.connect(self.path) as con:
            con.row_factory = sq.Row
            cur = con.cursor()

            cur.execute(f"select {column} from {table}")
            res = cur.fetchall()
            return list(map(lambda d: d[column], res))


    def manual(self, comm: str):
        """
        Ручное управление
        :param comm: SQL-запрос
        :return: ответ на запрос списком или None, если ничего не найдено
        """

        with sq.connect(self.path) as con:
            cur = con.cursor()
            cur.execute(comm)
            return cur.fetchall()


    def update(self, table: str, check_column: str, check_mean: str | int, update_column: str, update_mean: str | int | None):
        """
        Обновляет указанное значение, выполняя поиск по check_column и check_mean.
        Например: update("users", "userID", 123, "tag", "aboba")

        Возможные ошибки: TableNotFound, EntryNotFound
        :param table: имя таблицы
        :param check_column: название колонки для поиска записи
        :param check_mean: значение колонки для поиска записи
        :param update_column: название колонки для обновления
        :param update_mean: значение для обновления
        """

        with sq.connect(self.path) as con:
            cur = con.cursor()

            cur.execute(f"select * from {table} where {check_column} = :x", {'x': check_mean})
            res = cur.fetchone()
            if res is not None:
                cur.execute(f"update {table} set {update_column} = :x where {check_column} = :y", {'x': update_mean, 'y': check_mean})
            else:
                raise exceptions.EntryNotFound
