import sqlite3
from typing import Optional, Tuple, Any, List, Dict

from langchain_core.tools import tool

@tool('创建sqlite数据库连接')
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
def execute_sql( sql: str, db_file: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[sqlite3.Cursor]:
    """
    执行SQL语句

    :param sql: 要执行的SQL语句
    :param db_file: 数据库文件的路径
    :param params: 可选的SQL参数
    :return: 游标对象或None（如果执行失败）
    """
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
        except sqlite3.Error as e:
            print(e)
            return None
        finally:
            conn.close()

@tool("检查并创建表")
def check_and_create_table( table_name: str, create_table_sql: str, db_file: str) -> str:
    """
    检查指定的表是否存在，如果不存在，则创建表

    :param table_name: 要检查的表名
    :param create_table_sql: 创建表的SQL语句
    :param db_file: 数据库文件的路径
    :return: 操作结果的字符串描述
    """
    conn = create_connection(db_file)
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
def insert( table: str, db_file: str, **kwargs: Any) -> None:
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
    execute_sql(sql, db_file, tuple(processed_kwargs.values()))
    print(f'在 {db_file} 中 {table} 表数据插入成功  : ', tuple(processed_kwargs.values()))

@tool("使用create data的SQL语句将数据插入到数据库中")
def insert_data_by_sql( create_sql: str, db_file: str) -> str:
    """
    使用create data的SQL语句将数据插入到数据库中

    :param create_sql: 插入数据的SQL语句
    :param db_file: 数据库文件的路径
    :return: 操作结果的字符串描述
    """
    try:
        execute_sql(sql=create_sql, db_file=db_file)
        return 'Insert Data Success'
    except Exception as e:
        print('Insert Data Error :', str(e))
        return str(e)

@tool("根据SQL语句查询记录")
def select( sql: str, db_file: str) -> List[Tuple]:
    """
    根据SQL语句查询记录

    :param sql: 要执行的查询SQL语句
    :param db_file: 数据库文件的路径
    :return: 查询结果列表
    """
    conn = create_connection(db_file)
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
def insert_json_data( table: str, data: List[Dict[str, Any]], db_file: str) -> str:
    """
    将JSON数据插入到指定表中

    :param table: 表名
    :param data: 要插入的数据列表，每个元素是一个字典
    :param db_file: 数据库文件的路径
    :return: 操作结果的字符串描述
    """
    try:
        for item in data:
            insert(table, db_file, **item)
        return 'Success'
    except Exception as e:
        return str(e)