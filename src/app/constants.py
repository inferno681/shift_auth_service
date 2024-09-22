"""Base settings."""

ENCODING_FORMAT = 'utf-8'
LOGIN_LENGTH = 20
BALANCE_DEFAULT_VALUE = 0
HASHED_PASSWORD_LENGTH = 60
TOKEN_LENGTH = 300

"""Error messages."""
INVALID_TOKEN_MESSAGE = 'Invalid token'
TOKEN_EXPIRED_MESSAGE = 'Token has expired'
USER_EXISTS_MESSAGE = 'User {login} already exists'
USER_NOT_FOUND = 'User with the provided details not found'
TOKEN_NOT_FOUND = 'Token not found'
UPLOAD_ERROR = 'Error during file upload'
WRONG_IMAGE_FORMAT = 'Invalid image format {extension}'
FILENAME_ERROR = 'File name is too short or the file has no extension'


"""Default values."""
DEFAULT_BALANCE = 500


"""Text for responses."""
KAFKA_RESPONSE = 'Message received for processing'
