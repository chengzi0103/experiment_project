import os
def init_sys_env(is_proxy:bool=True,proxy_url:str='http://192.168.0.75:10809',):
    if is_proxy:
        os.environ['http_proxy'] = proxy_url
        os.environ['https_proxy'] = proxy_url


def init_env(env:dict):
    for env_name, env_value in env.items():
        os.environ[env_name] = env_value