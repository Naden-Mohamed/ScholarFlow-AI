from enum import Enum

class ResponseStatus(Enum):
    FILE_TYPE_NOT_SUPPORTED = "File type is not supported."
    FILE_SIZE_EXCEEDED = "File size exceeds the maximum allowed size."
    FILE_UPLOADED_SUCCESSFULLY = "File uploaded successfully."
    FILE_UPLOAD_FAILED = "File upload failed."
    FILE_VALIDATED_SUCCESSFULLY = "File validated successfully."
    FILE_PROCESSED_SUCCESSFULLY = "File processed successfully."
    FILE_PROCESSING_FAILED = "File processing failed."
    FILE_ID_ERROR = "File ID does not exist in the project."
    NO_FILES_FOUNDED_TO_PROCESS = "No files found to process in the project."