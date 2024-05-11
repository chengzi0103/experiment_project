from aiverse.data_classes.matrix import RoomMessageTextPydantic
import pytest

def test_class_creation(self):
    room_message_text = RoomMessageTextPydantic()
    assert isinstance(room_message_text, RoomMessageTextPydantic)



def test_invalid_arguments(self):
    with pytest.raises(Exception):
        room_message_text = RoomMessageTextPydantic(invalid_argument="invalid")