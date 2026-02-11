from enum import Enum

class ResponseEnum(Enum):
    FILE_TYPE_NOT_SUPPORTED = "File type is not supported."
    FILE_SIZE_EXCEEDED = "File size exceeds the maximum allowed size."
    FILE_UPLOADED_SUCCESSFULLY = "File uploaded successfully."
    FILE_UPLOAD_FAILED = "File upload failed."
    FILE_VALIDATED_SUCCESSFULLY = "File validated successfully."