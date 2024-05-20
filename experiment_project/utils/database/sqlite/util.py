import os
from typing import Any, Optional, List, Dict, Tuple
import sqlite3
from sqlite3 import Error
import json

from langchain.tools import tool
from experiment_project.utils.files.util import create_file_dir

import sqlite3
from typing import Optional, Tuple, Any, List, Dict


class Database:

    @tool("创建数据库连接")
    def create_connection(db_file: str) -> Optional[sqlite3.Connection]:
        """
        创建数据库连接

        :param db_file: 数据库文件的路径
        :return: 数据库连接对象或None（如果连接失败）
        """
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except sqlite3.Error as e:
            print(e)
            raise RuntimeError(str(e))

    @tool("执行SQL语句")
    def execute_sql(self, sql: str, db_file: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[sqlite3.Cursor]:
        """
        执行SQL语句

        :param sql: 要执行的SQL语句
        :param db_file: 数据库文件的路径
        :param params: 可选的SQL参数
        :return: 游标对象或None（如果执行失败）
        """
        conn = self.create_connection(db_file)
        if conn is not None:
            try:
                cur = conn.cursor()
                if params:
                    cur.execute(sql, params)
                else:
                    cur.execute(sql)
                conn.commit()
                return cur
            except sqlite3.Error as e:
                print(e)
                return None
            finally:
                conn.close()

    @tool("检查并创建表")
    def check_and_create_table(self, table_name: str, create_table_sql: str, db_file: str) -> str:
        """
        检查指定的表是否存在，如果不存在，则创建表

        :param table_name: 要检查的表名
        :param create_table_sql: 创建表的SQL语句
        :param db_file: 数据库文件的路径
        :return: 操作结果的字符串描述
        """
        conn = self.create_connection(db_file)
        if conn is not None:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                if cursor.fetchone()[0] == 1:
                    print(f"表 {table_name} 已存在。")
                else:
                    cursor.execute(create_table_sql)
                    print(f"表 {table_name} 创建成功。")
                return 'Success Create Table'
            except sqlite3.Error as e:
                print(f"在检查或创建表时发生错误，错误信息：{e}")
                raise RuntimeError(str(e))
            finally:
                conn.close()
        else:
            print("数据库连接未成功创建，无法执行检查或创建表的操作。")
            return 'connection Error'

    @tool("插入记录，特殊处理列表数据")
    def insert(self, table: str, db_file: str, **kwargs: Any) -> None:
        """
        插入记录，特殊处理列表数据

        :param table: 表名
        :param db_file: 数据库文件的路径
        :param kwargs: 要插入的数据，键值对形式
        """
        processed_kwargs = {}
        for key, value in kwargs.items():
            if isinstance(value, list):
                processed_kwargs[key] = ','.join(value)
            else:
                processed_kwargs[key] = value

        columns = ', '.join(processed_kwargs.keys())
        placeholders = ', '.join(['?'] * len(processed_kwargs))
        sql = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
        self.execute_sql(sql, db_file, tuple(processed_kwargs.values()))
        print(f'在 {db_file} 中 {table} 表数据插入成功  : ', tuple(processed_kwargs.values()))

    @tool("使用create data的SQL语句将数据插入到数据库中")
    def insert_data_by_sql(self, create_sql: str, db_file: str) -> str:
        """
        使用create data的SQL语句将数据插入到数据库中

        :param create_sql: 插入数据的SQL语句
        :param db_file: 数据库文件的路径
        :return: 操作结果的字符串描述
        """
        try:
            self.execute_sql(sql=create_sql, db_file=db_file)
            return 'Insert Data Success'
        except Exception as e:
            print('Insert Data Error :', str(e))
            return str(e)

    @tool("根据SQL语句查询记录")
    def select(self, sql: str, db_file: str) -> List[Tuple]:
        """
        根据SQL语句查询记录

        :param sql: 要执行的查询SQL语句
        :param db_file: 数据库文件的路径
        :return: 查询结果列表
        """
        conn = self.create_connection(db_file)
        if conn is not None:
            try:
                cur = conn.cursor()
                cur.execute(sql)
                result = cur.fetchall()
                return result
            except sqlite3.Error as e:
                print(e)
                return []
            finally:
                cur.close()
                conn.close()
        else:
            return []

    @tool("将JSON数据插入到指定表中")
    def insert_json_data(self, table: str, data: List[Dict[str, Any]], db_file: str) -> str:
        """
        将JSON数据插入到指定表中

        :param table: 表名
        :param data: 要插入的数据列表，每个元素是一个字典
        :param db_file: 数据库文件的路径
        :return: 操作结果的字符串描述
        """
        try:
            for item in data:
                self.insert(table, db_file, **item)
            return 'Success'
        except Exception as e:
            return str(e)


def create_connection(db_file: str) -> Optional[sqlite3.Connection]:
    """创建数据库连接"""
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
        return None

def execute_sql(sql: str, db_file: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[sqlite3.Cursor]:
    """执行SQL语句"""
    conn = create_connection(db_file)
    if conn is not None:
        try:
            cur = conn.cursor()
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            conn.commit()
            return cur
        except Error as e:
            print(e)
            return None
        finally:
            conn.close()

def check_and_create_table(table_name:str,create_table_sql: str, db_file: str) -> str:
    """创建表"""
    """
        检查指定的表是否存在，如果不存在，则创建表。

        :param db_file: SQLite数据库文件的路径。
        :param table_name: 要检查的表名。
        :param create_table_sql: 创建表的SQL语句。
        """
    create_file_dir(file_path=db_file)
    conn = create_connection(db_file)
    if conn is not None:
        try:
            cursor = conn.cursor()
            # 检查表是否存在
            cursor.execute("SELECT count(name) FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
            if cursor.fetchone()[0] == 1:
                print(f"表 {table_name} 已存在。")
            else:
                # 表不存在，创建表
                cursor.execute(create_table_sql)
                print(f"表 {table_name} 创建成功。")
            return 'Success Create Table'
        except Error as e:
            print(f"在检查或创建表时发生错误，错误信息：{e}")
            raise RuntimeError(str(e))
        finally:
            # 关闭数据库连接
            conn.close()
    else:
        print("数据库连接未成功创建，无法执行检查或创建表的操作。")
        return 'connection Error'

def insert(table: str, db_file: str, **kwargs: Any) -> None:
    """插入记录，特殊处理列表数据"""
    processed_kwargs = {}
    for key, value in kwargs.items():
        if isinstance(value, list):  # 检查值是否为列表
            # 将列表转换为JSON字符串
            processed_kwargs[key] = ','.join(value)
        else:
            processed_kwargs[key] = value

    columns = ', '.join(processed_kwargs.keys())
    placeholders = ', '.join(['?'] * len(processed_kwargs))
    sql = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
    execute_sql(sql, db_file, tuple(processed_kwargs.values()))
    print(f'在 {db_file}  中 {table} 表数据插入成功  : ',tuple(processed_kwargs.values()))

def insert_sql(create_sql:str, db_file: str,) -> str:
    """使用create data的sql语句,将数据插入到数据库中"""
    try:
        execute_sql(sql=create_sql, db_file=db_file,)
        return 'Insert Data Success'
    except Exception as e :
        print('Insert Data Error :',str(e))
        return str(e)



def select(sql: str, db_file: str) -> List[Tuple]:
    """根据sql语句查询记录"""
    conn = create_connection(db_file)  # 创建数据库连接
    if conn is not None:
        try:
            cur = conn.cursor()  # 创建游标
            cur.execute(sql)  # 执行SQL语句
            result = cur.fetchall()  # 获取所有查询结果
            return result
        except sqlite3.Error as e:  # 捕获可能的异常
            print(e)
            return []  # 发生异常时返回空列表
        finally:
            cur.close()  # 关闭游标
            conn.close()  # 关闭数据库连接
    else:
        return []  # 如果连接失败，返回空列表

def update(table: str, where: Dict[str, Any], db_file: str, **kwargs: Any) -> None:
    """更新记录"""
    set_clause = ', '.join([f"{k} = ?" for k in kwargs])
    where_clause = ' AND '.join([f"{k} = ?" for k in where])
    sql = f'UPDATE {table} SET {set_clause} WHERE {where_clause}'
    execute_sql(sql, db_file, tuple(kwargs.values()) + tuple(where.values()))

def delete(table: str, db_file: str, **where: Any) -> None:
    """删除记录"""
    where_clause = ' AND '.join([f"{k} = ?" for k in where])
    sql = f'DELETE FROM {table} WHERE {where_clause}'
    execute_sql(sql, db_file, tuple(where.values()))

def insert_json_data(table: str, data: List[Dict[str, Any]], db_file: str) -> str:
    """将JSON数据插入到指定表中"""
    try:
        for item in data:
            insert(table, db_file, **item)
        return 'Success'
    except Exception as e :
        return str(e)
# params = {"create_sql": "INSERT INTO user_calendar (title, participants, location, start_time, end_time) VALUES ('讨论Agent对未来的影响', '我,吴博,门总', '线上会议,腾讯会议', '2024-05-18 15:00:00', '2024-05-18 18:00:00');", "db_file": "/mnt/d/project/zzbc/experiment_project/experiment_project/experiment/output/func_tool.db"}
# print(insert_sql(**params))



# json_data = [{"event_name": "Morning Commute", "start_time": "07:40", "end_time": "08:30", "location": "Subway", "description": "Taking the subway to the company.", "people": [], "date": "2024-05-14"}, {"event_name": "Work Morning Session", "start_time": "08:30", "end_time": "11:40", "location": "Company", "description": "Morning work session.", "people": ["Alice", "Bob"], "date": "2024-05-14"}, {"event_name": "Lunch Break", "start_time": "11:40", "end_time": "13:30", "location": "Nearby Restaurant", "description": "Lunch and rest.", "people": ["Charlie"], "date": "2024-05-14"}, {"event_name": "Work Afternoon Session", "start_time": "13:30", "end_time": "17:30", "location": "Company", "description": "Afternoon work session.", "people": ["Dana", "Evan"], "date": "2024-05-14"}, {"event_name": "Evening Commute", "start_time": "17:40", "end_time": "18:20", "location": "Subway", "description": "Taking the subway back home.", "people": [], "date": "2024-05-14"}, {"event_name": "Morning Commute", "start_time": "07:40", "end_time": "08:30", "location": "Subway", "description": "Taking the subway to the company.", "people": [], "date": "2024-05-15"}, {"event_name": "Work Morning Session", "start_time": "08:30", "end_time": "11:40", "location": "Company", "description": "Morning work session.", "people": ["Alice", "Bob"], "date": "2024-05-15"}, {"event_name": "Lunch Break", "start_time": "11:40", "end_time": "13:30", "location": "Nearby Restaurant", "description": "Lunch and rest.", "people": ["Charlie"], "date": "2024-05-15"}, {"event_name": "Work Afternoon Session", "start_time": "13:30", "end_time": "17:30", "location": "Company", "description": "Afternoon work session.", "people": ["Dana", "Evan"], "date": "2024-05-15"}, {"event_name": "Evening Commute", "start_time": "17:40", "end_time": "18:20", "location": "Subway", "description": "Taking the subway back home.", "people": [], "date": "2024-05-15"}, {"event_name": "Morning Commute", "start_time": "07:40", "end_time": "08:30", "location": "Subway", "description": "Taking the subway to the company.", "people": [], "date": "2024-05-16"}, {"event_name": "Work Morning Session", "start_time": "08:30", "end_time": "11:40", "location": "Company", "description": "Morning work session.", "people": ["Alice", "Bob"], "date": "2024-05-16"}, {"event_name": "Lunch Break", "start_time": "11:40", "end_time": "13:30", "location": "Nearby Restaurant", "description": "Lunch and rest.", "people": ["Charlie"], "date": "2024-05-16"}, {"event_name": "Work Afternoon Session", "start_time": "13:30", "end_time": "17:30", "location": "Company", "description": "Afternoon work session.", "people": ["Dana", "Evan"], "date": "2024-05-16"}, {"event_name": "Evening Commute", "start_time": "17:40", "end_time": "18:20", "location": "Subway", "description": "Taking the subway back home.", "people": [], "date": "2024-05-16"}, {"event_name": "Morning Commute", "start_time": "07:40", "end_time": "08:30", "location": "Subway", "description": "Taking the subway to the company.", "people": [], "date": "2024-05-17"}, {"event_name": "Work Morning Session", "start_time": "08:30", "end_time": "11:40", "location": "Company", "description": "Morning work session.", "people": ["Alice", "Bob"], "date": "2024-05-17"}, {"event_name": "Lunch Break", "start_time": "11:40", "end_time": "13:30", "location": "Nearby Restaurant", "description": "Lunch and rest.", "people": ["Charlie"], "date": "2024-05-17"}, {"event_name": "Work Afternoon Session", "start_time": "13:30", "end_time": "17:30", "location": "Company", "description": "Afternoon work session.", "people": ["Dana", "Evan"], "date": "2024-05-17"}, {"event_name": "Evening Commute", "start_time": "17:40", "end_time": "18:20", "location": "Subway", "description": "Taking the subway back home.", "people": [], "date": "2024-05-17"}, {"event_name": "Morning Commute", "start_time": "07:40", "end_time": "08:30", "location": "Subway", "description": "Taking the subway to the company.", "people": [], "date": "2024-05-20"}, {"event_name": "Work Morning Session", "start_time": "08:30", "end_time": "11:40", "location": "Company", "description": "Morning work session.", "people": ["Alice", "Bob"], "date": "2024-05-20"}, {"event_name": "Lunch Break", "start_time": "11:40", "end_time": "13:30", "location": "Nearby Restaurant", "description": "Lunch and rest.", "people": ["Charlie"], "date": "2024-05-20"}, {"event_name": "Work Afternoon Session", "start_time": "13:30", "end_time": "17:30", "location": "Company", "description": "Afternoon work session.", "people": ["Dana", "Evan"], "date": "2024-05-20"}, {"event_name": "Evening Commute", "start_time": "17:40", "end_time": "18:20", "location": "Subway", "description": "Taking the subway back home.", "people": [], "date": "2024-05-20"}, {"event_name": "Volunteering", "date": "2024-07-07", "start_time": "11:00", "end_time": "14:00", "location": "Art Museum", "description": "Giving back to the community through volunteering.", "people": ["George"]}, {"event_name": "Gym Session", "date": "2024-07-13", "start_time": "14:00", "end_time": "16:00", "location": "Art Museum", "description": "Attending a workout session at the gym.", "people": ["Alice", "Fiona"]}, {"event_name": "Yoga Retreat", "date": "2024-06-14", "start_time": "15:00", "end_time": "21:00", "location": "Home", "description": "A day of yoga and meditation.", "people": ["Alice"]}, {"event_name": "City Exploration", "date": "2024-06-05", "start_time": "08:00", "end_time": "13:00", "location": "Art Museum", "description": "Exploring new places in the city.", "people": ["Evan", "Dana"]}, {"event_name": "Cooking Class", "date": "2024-07-03", "start_time": "11:00", "end_time": "13:00", "location": "New York Office", "description": "Learning new cooking techniques.", "people": ["Charlie", "Bob", "Alice"]}, {"event_name": "Photography Walk", "date": "2024-06-13", "start_time": "14:00", "end_time": "17:00", "location": "New York Office", "description": "Capturing the beauty of the city through the lens.", "people": ["Bob", "Fiona"]}, {"event_name": "Concert Night", "date": "2024-06-11", "start_time": "08:00", "end_time": "14:00", "location": "Local Gym", "description": "Enjoying live music at a concert.", "people": ["Fiona", "Evan"]}, {"event_name": "Cooking Class", "date": "2024-06-18", "start_time": "15:00", "end_time": "18:00", "location": "City Park", "description": "Learning new cooking techniques.", "people": ["Alice"]}, {"event_name": "Art Exhibition", "date": "2024-06-24", "start_time": "14:00", "end_time": "16:00", "location": "Local Gym", "description": "Visiting an art exhibition.", "people": ["Bob"]}, {"event_name": "Dinner with Friends", "date": "2024-06-16", "start_time": "12:00", "end_time": "13:00", "location": "New York Office", "description": "Catching up with friends over dinner.", "people": ["Fiona", "Evan"]}, {"event_name": "Concert Night", "date": "2024-07-09", "start_time": "16:00", "end_time": "19:00", "location": "Downtown Cafe", "description": "Enjoying live music at a concert.", "people": ["Bob", "Dana"]}, {"event_name": "Movie Marathon", "date": "2024-06-25", "start_time": "13:00", "end_time": "15:00", "location": "Downtown Cafe", "description": "A cozy night in with back-to-back movies.", "people": ["Fiona", "George", "Alice"]}, {"event_name": "Annual Leave", "date": "2024-06-03", "start_time": "11:00", "end_time": "12:00", "location": "New York Office", "description": "Taking a day off for relaxation.", "people": ["Bob"]}, {"event_name": "City Exploration", "date": "2024-06-28", "start_time": "09:00", "end_time": "13:00", "location": "Local Gym", "description": "Exploring new places in the city.", "people": ["Fiona"]}, {"event_name": "Concert Night", "date": "2024-07-08", "start_time": "08:00", "end_time": "11:00", "location": "Art Museum", "description": "Enjoying live music at a concert.", "people": ["Fiona", "George"]}, {"event_name": "Gym Session", "date": "2024-06-09", "start_time": "17:00", "end_time": "21:00", "location": "Home", "description": "Attending a workout session at the gym.", "people": ["Bob", "Evan"]}, {"event_name": "Weekend Getaway", "date": "2024-06-04", "start_time": "17:00", "end_time": "23:00", "location": "New York Office", "description": "A short trip to recharge.", "people": ["Evan", "Fiona"]}, {"event_name": "Dinner with Friends", "date": "2024-05-18", "start_time": "16:00", "end_time": "22:00", "location": "Company Conference Room", "description": "Catching up with friends over dinner.", "people": ["Evan", "George", "Alice"]}, {"event_name": "Visit Parents", "date": "2024-06-16", "start_time": "08:00", "end_time": "13:00", "location": "Art Museum", "description": "Spending quality time with parents.", "people": ["Alice", "Bob", "Charlie"]}, {"event_name": "Book Club Meeting", "date": "2024-06-17", "start_time": "13:00", "end_time": "18:00", "location": "City Park", "description": "Discussing the latest book with the club.", "people": ["Fiona"]}, {"event_name": "Annual Leave", "date": "2024-06-16", "start_time": "15:00", "end_time": "18:00", "location": "Home", "description": "Taking a day off for relaxation.", "people": ["Charlie", "Bob"]}, {"event_name": "Volunteering", "date": "2024-05-30", "start_time": "11:00", "end_time": "17:00", "location": "Company Conference Room", "description": "Giving back to the community through volunteering.", "people": ["George", "Alice"]}, {"event_name": "Movie Marathon", "date": "2024-06-29", "start_time": "13:00", "end_time": "15:00", "location": "Home", "description": "A cozy night in with back-to-back movies.", "people": ["Bob", "George", "Fiona"]}, {"event_name": "Movie Marathon", "date": "2024-06-12", "start_time": "12:00", "end_time": "17:00", "location": "Company Conference Room", "description": "A cozy night in with back-to-back movies.", "people": ["Alice"]}, {"event_name": "Weekend Getaway", "date": "2024-07-02", "start_time": "14:00", "end_time": "18:00", "location": "City Park", "description": "A short trip to recharge.", "people": ["George", "Bob"]}]
# table_name = 'calendar_events'
# insert_json_data(table=table_name,json_data=json_data)

