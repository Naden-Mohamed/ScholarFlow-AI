from enum import Enum

class ProcessingEnum(Enum):
    PDF = ".pdf"
    WORD = ['.doc', '.docx']
    TEXT = ".txt"
    IMAGR = ['.jpeg', '.png']
    PPTX = ".pptx"