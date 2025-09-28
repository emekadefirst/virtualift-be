from enum import Enum


class FileType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    DOCUMENT = "document"
    AUDIO = "audio"


class ImageExtension(str, Enum):
    JPG = "jpg"
    PNG = "png"
    JPEG = "jpeg"
    GIF = "gif"
    WEBP = "webp"
    BMP = "bmp"
    TIFF = "tiff"


class VideoExtension(str, Enum):
    MP4 = "mp4"
    AVI = "avi"
    MKV = "mkv"
    MOV = "mov"
    WMV = "wmv"
    FLV = "flv"
    WEBM = "webm"


class DocumentExtension(str, Enum):
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    PPTX = "pptx"
    XLSX = "xlsx"
    TXT = "txt"
    ODT = "odt"
    RTF = "rtf"


class AudioExtension(str, Enum):
    MP3 = "mp3"
    WAV = "wav"
    AAC = "aac"
    FLAC = "flac"
    OGG = "ogg"
    WMA = "wma"
    M4A = "m4a"


class Action(str, Enum):
    READ = "read"
    WRITE = "write"
    UPDATE = "update"
    DELETE = "delete"



class Resource(str, Enum):
    FILE = "file"
    USER = "user"
    TRIAL = "trial"


class UsageType(str, Enum):
    TRIAL = "trial"
    SUBSCRIBER = "subscriber"


class SubscriptionType(str, Enum):
    ...

class SubscriptionDuration(str, Enum):
    MONTHLY = "monthly"
    YEARLY = "yearly"

class PaymentStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    CANCELLED = "cancelled"

    
