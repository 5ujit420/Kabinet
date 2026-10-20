from enum import Enum


class ReadingStatus(str, Enum):
    READ = "READ"
    READING = "READING"
    WANT_TO_READ = "WANT_TO_READ"
    DID_NOT_FINISH = "DID_NOT_FINISH"
