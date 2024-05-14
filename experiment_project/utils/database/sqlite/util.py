import os
from typing import Any, Optional, List, Dict, Tuple
import sqlite3
from sqlite3 import Error
import json

from experiment_project.utils.files.util import create_file_dir


class Database:
    def __init__(self, db_file:str='/mnt/d/project/zzbc/experiment_project/experiment_project/experiment/autogen_project/example/output/func_tool_example.db'):
        """初始化数据库连接"""
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_file)
            print("SQLite数据库已成功连接")
        except Error as e:
            print(e)

    def execute_sql(self, sql, params=None):
        """执行SQL语句"""
        try:
            cur = self.conn.cursor()
            if params:
                cur.execute(sql, params)
            else:
                cur.execute(sql)
            self.conn.commit()
            return cur
        except Error as e:
            print(e)
            return None

    def create_table(self, create_table_sql):
        """创建表"""
        self.execute_sql(create_table_sql)

    def insert(self, table, **kwargs):
        """插入记录"""
        columns = ', '.join(kwargs.keys())
        placeholders = ', '.join(['?'] * len(kwargs))
        sql = f'INSERT INTO {table} ({columns}) VALUES ({placeholders})'
        self.execute_sql(sql, tuple(kwargs.values()))

    def select(self, table, where=None, *args):
        """查询记录"""
        columns = ', '.join(args) if args else '*'
        sql = f'SELECT {columns} FROM {table}'
        if where:
            sql += ' WHERE ' + ' AND '.join([f"{k} = ?" for k in where])
            cur = self.execute_sql(sql, tuple(where.values()))
        else:
            cur = self.execute_sql(sql)
        return cur.fetchall() if cur else []

    def update(self, table, where, **kwargs):
        """更新记录"""
        set_clause = ', '.join([f"{k} = ?" for k in kwargs])
        where_clause = ' AND '.join([f"{k} = ?" for k in where])
        sql = f'UPDATE {table} SET {set_clause} WHERE {where_clause}'
        self.execute_sql(sql, tuple(kwargs.values()) + tuple(where.values()))

    def delete(self, table, **where):
        """删除记录"""
        where_clause = ' AND '.join([f"{k} = ?" for k in where])
        sql = f'DELETE FROM {table} WHERE {where_clause}'
        self.execute_sql(sql, tuple(where.values()))

    def insert_json_data(self, table_name, json_data):
        """将JSON数据插入到指定表中"""
        for item in json_data:
            keys = item.keys()
            columns = ', '.join(keys)
            placeholders = ', '.join(['?'] * len(item))
            values = tuple(item[key] for key in keys)
            sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            self.execute_sql(sql, values)



# db_file = '/mnt/d/project/zzbc/experiment_project/experiment_project/experiment/output/func_tool.db'




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
            return str(e)
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

def select(sql: str, db_file: str) -> List[Tuple]:
    """查询记录"""
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
# params = {"sql": "SELECT * FROM user_calendar WHERE date >= '2024-05-15' AND date <= '2024-05-17'", "db_file": "/mnt/d/project/zzbc/experiment_project/experiment_project/experiment/output/func_tool.db"}
# print(select(**params))



# json_data = [{"event_name": "Morning Commute", "start_time": "07:40", "end_time": "08:30", "location": "Subway", "description": "Taking the subway to the company.", "people": [], "date": "2024-05-14"}, {"event_name": "Work Morning Session", "start_time": "08:30", "end_time": "11:40", "location": "Company", "description": "Morning work session.", "people": ["Alice", "Bob"], "date": "2024-05-14"}, {"event_name": "Lunch Break", "start_time": "11:40", "end_time": "13:30", "location": "Nearby Restaurant", "description": "Lunch and rest.", "people": ["Charlie"], "date": "2024-05-14"}, {"event_name": "Work Afternoon Session", "start_time": "13:30", "end_time": "17:30", "location": "Company", "description": "Afternoon work session.", "people": ["Dana", "Evan"], "date": "2024-05-14"}, {"event_name": "Evening Commute", "start_time": "17:40", "end_time": "18:20", "location": "Subway", "description": "Taking the subway back home.", "people": [], "date": "2024-05-14"}, {"event_name": "Morning Commute", "start_time": "07:40", "end_time": "08:30", "location": "Subway", "description": "Taking the subway to the company.", "people": [], "date": "2024-05-15"}, {"event_name": "Work Morning Session", "start_time": "08:30", "end_time": "11:40", "location": "Company", "description": "Morning work session.", "people": ["Alice", "Bob"], "date": "2024-05-15"}, {"event_name": "Lunch Break", "start_time": "11:40", "end_time": "13:30", "location": "Nearby Restaurant", "description": "Lunch and rest.", "people": ["Charlie"], "date": "2024-05-15"}, {"event_name": "Work Afternoon Session", "start_time": "13:30", "end_time": "17:30", "location": "Company", "description": "Afternoon work session.", "people": ["Dana", "Evan"], "date": "2024-05-15"}, {"event_name": "Evening Commute", "start_time": "17:40", "end_time": "18:20", "location": "Subway", "description": "Taking the subway back home.", "people": [], "date": "2024-05-15"}, {"event_name": "Morning Commute", "start_time": "07:40", "end_time": "08:30", "location": "Subway", "description": "Taking the subway to the company.", "people": [], "date": "2024-05-16"}, {"event_name": "Work Morning Session", "start_time": "08:30", "end_time": "11:40", "location": "Company", "description": "Morning work session.", "people": ["Alice", "Bob"], "date": "2024-05-16"}, {"event_name": "Lunch Break", "start_time": "11:40", "end_time": "13:30", "location": "Nearby Restaurant", "description": "Lunch and rest.", "people": ["Charlie"], "date": "2024-05-16"}, {"event_name": "Work Afternoon Session", "start_time": "13:30", "end_time": "17:30", "location": "Company", "description": "Afternoon work session.", "people": ["Dana", "Evan"], "date": "2024-05-16"}, {"event_name": "Evening Commute", "start_time": "17:40", "end_time": "18:20", "location": "Subway", "description": "Taking the subway back home.", "people": [], "date": "2024-05-16"}, {"event_name": "Morning Commute", "start_time": "07:40", "end_time": "08:30", "location": "Subway", "description": "Taking the subway to the company.", "people": [], "date": "2024-05-17"}, {"event_name": "Work Morning Session", "start_time": "08:30", "end_time": "11:40", "location": "Company", "description": "Morning work session.", "people": ["Alice", "Bob"], "date": "2024-05-17"}, {"event_name": "Lunch Break", "start_time": "11:40", "end_time": "13:30", "location": "Nearby Restaurant", "description": "Lunch and rest.", "people": ["Charlie"], "date": "2024-05-17"}, {"event_name": "Work Afternoon Session", "start_time": "13:30", "end_time": "17:30", "location": "Company", "description": "Afternoon work session.", "people": ["Dana", "Evan"], "date": "2024-05-17"}, {"event_name": "Evening Commute", "start_time": "17:40", "end_time": "18:20", "location": "Subway", "description": "Taking the subway back home.", "people": [], "date": "2024-05-17"}, {"event_name": "Morning Commute", "start_time": "07:40", "end_time": "08:30", "location": "Subway", "description": "Taking the subway to the company.", "people": [], "date": "2024-05-20"}, {"event_name": "Work Morning Session", "start_time": "08:30", "end_time": "11:40", "location": "Company", "description": "Morning work session.", "people": ["Alice", "Bob"], "date": "2024-05-20"}, {"event_name": "Lunch Break", "start_time": "11:40", "end_time": "13:30", "location": "Nearby Restaurant", "description": "Lunch and rest.", "people": ["Charlie"], "date": "2024-05-20"}, {"event_name": "Work Afternoon Session", "start_time": "13:30", "end_time": "17:30", "location": "Company", "description": "Afternoon work session.", "people": ["Dana", "Evan"], "date": "2024-05-20"}, {"event_name": "Evening Commute", "start_time": "17:40", "end_time": "18:20", "location": "Subway", "description": "Taking the subway back home.", "people": [], "date": "2024-05-20"}, {"event_name": "Volunteering", "date": "2024-07-07", "start_time": "11:00", "end_time": "14:00", "location": "Art Museum", "description": "Giving back to the community through volunteering.", "people": ["George"]}, {"event_name": "Gym Session", "date": "2024-07-13", "start_time": "14:00", "end_time": "16:00", "location": "Art Museum", "description": "Attending a workout session at the gym.", "people": ["Alice", "Fiona"]}, {"event_name": "Yoga Retreat", "date": "2024-06-14", "start_time": "15:00", "end_time": "21:00", "location": "Home", "description": "A day of yoga and meditation.", "people": ["Alice"]}, {"event_name": "City Exploration", "date": "2024-06-05", "start_time": "08:00", "end_time": "13:00", "location": "Art Museum", "description": "Exploring new places in the city.", "people": ["Evan", "Dana"]}, {"event_name": "Cooking Class", "date": "2024-07-03", "start_time": "11:00", "end_time": "13:00", "location": "New York Office", "description": "Learning new cooking techniques.", "people": ["Charlie", "Bob", "Alice"]}, {"event_name": "Photography Walk", "date": "2024-06-13", "start_time": "14:00", "end_time": "17:00", "location": "New York Office", "description": "Capturing the beauty of the city through the lens.", "people": ["Bob", "Fiona"]}, {"event_name": "Concert Night", "date": "2024-06-11", "start_time": "08:00", "end_time": "14:00", "location": "Local Gym", "description": "Enjoying live music at a concert.", "people": ["Fiona", "Evan"]}, {"event_name": "Cooking Class", "date": "2024-06-18", "start_time": "15:00", "end_time": "18:00", "location": "City Park", "description": "Learning new cooking techniques.", "people": ["Alice"]}, {"event_name": "Art Exhibition", "date": "2024-06-24", "start_time": "14:00", "end_time": "16:00", "location": "Local Gym", "description": "Visiting an art exhibition.", "people": ["Bob"]}, {"event_name": "Dinner with Friends", "date": "2024-06-16", "start_time": "12:00", "end_time": "13:00", "location": "New York Office", "description": "Catching up with friends over dinner.", "people": ["Fiona", "Evan"]}, {"event_name": "Concert Night", "date": "2024-07-09", "start_time": "16:00", "end_time": "19:00", "location": "Downtown Cafe", "description": "Enjoying live music at a concert.", "people": ["Bob", "Dana"]}, {"event_name": "Movie Marathon", "date": "2024-06-25", "start_time": "13:00", "end_time": "15:00", "location": "Downtown Cafe", "description": "A cozy night in with back-to-back movies.", "people": ["Fiona", "George", "Alice"]}, {"event_name": "Annual Leave", "date": "2024-06-03", "start_time": "11:00", "end_time": "12:00", "location": "New York Office", "description": "Taking a day off for relaxation.", "people": ["Bob"]}, {"event_name": "City Exploration", "date": "2024-06-28", "start_time": "09:00", "end_time": "13:00", "location": "Local Gym", "description": "Exploring new places in the city.", "people": ["Fiona"]}, {"event_name": "Concert Night", "date": "2024-07-08", "start_time": "08:00", "end_time": "11:00", "location": "Art Museum", "description": "Enjoying live music at a concert.", "people": ["Fiona", "George"]}, {"event_name": "Gym Session", "date": "2024-06-09", "start_time": "17:00", "end_time": "21:00", "location": "Home", "description": "Attending a workout session at the gym.", "people": ["Bob", "Evan"]}, {"event_name": "Weekend Getaway", "date": "2024-06-04", "start_time": "17:00", "end_time": "23:00", "location": "New York Office", "description": "A short trip to recharge.", "people": ["Evan", "Fiona"]}, {"event_name": "Dinner with Friends", "date": "2024-05-18", "start_time": "16:00", "end_time": "22:00", "location": "Company Conference Room", "description": "Catching up with friends over dinner.", "people": ["Evan", "George", "Alice"]}, {"event_name": "Visit Parents", "date": "2024-06-16", "start_time": "08:00", "end_time": "13:00", "location": "Art Museum", "description": "Spending quality time with parents.", "people": ["Alice", "Bob", "Charlie"]}, {"event_name": "Book Club Meeting", "date": "2024-06-17", "start_time": "13:00", "end_time": "18:00", "location": "City Park", "description": "Discussing the latest book with the club.", "people": ["Fiona"]}, {"event_name": "Annual Leave", "date": "2024-06-16", "start_time": "15:00", "end_time": "18:00", "location": "Home", "description": "Taking a day off for relaxation.", "people": ["Charlie", "Bob"]}, {"event_name": "Volunteering", "date": "2024-05-30", "start_time": "11:00", "end_time": "17:00", "location": "Company Conference Room", "description": "Giving back to the community through volunteering.", "people": ["George", "Alice"]}, {"event_name": "Movie Marathon", "date": "2024-06-29", "start_time": "13:00", "end_time": "15:00", "location": "Home", "description": "A cozy night in with back-to-back movies.", "people": ["Bob", "George", "Fiona"]}, {"event_name": "Movie Marathon", "date": "2024-06-12", "start_time": "12:00", "end_time": "17:00", "location": "Company Conference Room", "description": "A cozy night in with back-to-back movies.", "people": ["Alice"]}, {"event_name": "Weekend Getaway", "date": "2024-07-02", "start_time": "14:00", "end_time": "18:00", "location": "City Park", "description": "A short trip to recharge.", "people": ["George", "Bob"]}]
# table_name = 'calendar_events'
# insert_json_data(table=table_name,json_data=json_data)

