from functools import reduce
import json
from typing import Union, Optional
import hashlib


class Message:

    def __init__(self, message_id: int, message: str) -> None:
        """
        Creat a new Message
        :param message_id:
        Id of the message
        :param message:
        Content of the message
        """
        self.parity_check = lambda msg: reduce(lambda x, y: int(x) ^ int(y),
                                               "".join([bin(msg[i])[2:] for i in range(len(msg))]), 0)
        self.id = message_id
        self.len = len(message)
        self.parity = self.parity_check(bytes(message, "utf8"))
        self.message = message
        self.content = dict()

    def verif(self) -> bool:
        """
        Check if the message is corrupted
        :return:
        Bool (True if not corrupted, else False)
        """
        if self.parity_check(bytes(self.message, "utf8")) != self.parity:
            return False
        elif len(self.message) != self.len:
            return False
        else:
            return True

    @staticmethod
    def from_json(data_string: str):
        """
        Check if the received message can be transform in a Message object, if it is possible, return
        a Message containing the received data, if it failed it return None
        :return:
        A Message object
        """
        message = Message(0, "")
        try:

            json_dict = json.loads(data_string)
            message.import_json(json_dict)
            if message.verif():
                return message
            else:
                return None
        except:
            return None

    def import_json(self, json_in):
        """
        If it is possible, load the data of a Json string into the Message object
        :param json_in:
        The Json to read
        :return:
        None
        """
        if "id" in json_in and "parity" in json_in and "len" in json_in and "message" in json_in:
            self.id = json_in["id"]
            self.parity = json_in["parity"]
            self.len = json_in["len"]
            self.message = json_in["message"]
            self.content = json.loads(self.message)

    def __iter__(self) -> Union[int, str]:
        yield "id", self.id
        yield "parity", self.parity
        yield "len", self.len
        yield "message", self.message

    def __str__(self) -> str:
        """
        Convert the message to a Json object
        :return:
        str : the Json object
        """
        return json.dumps(dict(self))

    def to_json(self) -> str:
        """
        Convert the message to a Json object
        :return:
        str : the Json object
        """
        return str(self)

    @staticmethod
    def connection_message(password: str, verbose: Optional[int] = 1, hash_pass: Optional[bool] = False) -> str:
        if hash_pass:
            hash_password = hashlib.sha1(bytes(password, "utf8")).hexdigest()
        else:
            hash_password = password

        return '{"password": "' + str(hash_password) + '" , "verbose": ' + str(verbose) + '}'

    @staticmethod
    def is_message(data_string: str):
        """
        Check if the received message is a Message object.
        :return:
        True if it is a Message object else False
        """
        return not Message.from_json(data_string) is None

    @staticmethod
    def command_json(move_up: bool = False, move_down: bool = False, rotate_left: bool = False, rotate_right: bool = False) -> str:
        """
        Create the json string used to command a player
        :param player_no: The id of the player to command
        :param move_up: True if the player must go up
        :param move_down: True if the player must go down
        :param move_left: True if the player must go left
        :param move_right: True if the player must go right
        :param rotate_left: True if the player must rotate left
        :param rotate_right: True if the player must rotate right
        :return: A well formatted json string to send in a message object with information to command a player
        """

        return json.dumps({"move_forward": "1" if move_up else "0", "move_backwards": "1" if move_down else "0",
                           "rotate_left": "1" if rotate_left else "0", "rotate_right": "1" if rotate_right else "0"})

    @staticmethod
    def command_message(move_up: bool = False, move_down: bool = False, rotate_left: bool = False, rotate_right: bool = False) -> str:
        return Message(102, Message.command_json(move_up, move_down, rotate_left, rotate_right)).to_json()
