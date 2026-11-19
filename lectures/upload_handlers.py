"""Upload handler that stops reading a file at UPLOAD_MAX_BYTES + 1 (AD-20 step 1)."""

from django.conf import settings
from django.core.files.uploadhandler import SkipFile, TemporaryFileUploadHandler


class LimitedTemporaryFileUploadHandler(TemporaryFileUploadHandler):
    """Writes the upload to a temporary file, but never more than the limit plus one byte.

    On an oversized file the temporary file is closed (and so deleted), the rest of that file is
    skipped, and `request.upload_too_big` is set so the view can show the 10 MB message.
    """

    def __init__(self, request=None):
        super().__init__(request)
        self.received = 0
        self.request = request

    def receive_data_chunk(self, raw_data, start):
        limit = settings.UPLOAD_MAX_BYTES
        room = limit + 1 - self.received
        if len(raw_data) >= room:
            self.file.write(raw_data[:room])  # the one extra byte proves the file is too big
            self.received += room
            self.file.close()  # deletes Django's temporary copy
            if self.request is not None:
                self.request.upload_too_big = True
            raise SkipFile()
        self.received += len(raw_data)
        return super().receive_data_chunk(raw_data, start)
