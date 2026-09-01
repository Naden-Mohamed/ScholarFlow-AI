from enum import Enum


class ProcessingEnum(Enum):
    PDF = ".pdf"
    WORD = (".doc", ".docx")
    TEXT = ".txt"
    IMAGE = (".jpeg", ".png")
    PPTX = ".pptx"
