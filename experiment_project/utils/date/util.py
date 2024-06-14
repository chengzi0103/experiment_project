from typing import Union

import pendulum
def now_time(format:Union[str,None]='YYYY-MM-DD HH:mm:ss'):
    return pendulum.now().format(format)
