from typing import Union

import pendulum
def now_time(format:Union[str,None]='YYYY-MM-DD HH:mm:ss'):
    """
    获取当前时间并根据指定格式返回。
    参数:
    format (Union[str, None]): 可选参数，指定时间的格式。默认值为 'YYYY-MM-DD HH:mm:ss'。
    返回:
    str: 按指定格式返回当前时间的字符串表示。
    """
    return pendulum.now().format(format)


