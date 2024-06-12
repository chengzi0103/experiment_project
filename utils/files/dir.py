import shutil
from pathlib import Path
from typing import Union


def check_dir(dir_path: Union[Path, str]):
    # Convert the input to a Path object if it's not already
    folder_path = Path(dir_path)
    # Return True if the folder exists, otherwise False
    return folder_path.exists() and folder_path.is_dir()


def make_dir(dir_path: Union[Path, str]):
    p: Path = Path(dir_path)
    p.mkdir(exist_ok=True, parents=True)


def remove_dir(dir_path: Union[str, Path]):
    if Path(dir_path).is_dir():
        shutil.rmtree(dir_path)
