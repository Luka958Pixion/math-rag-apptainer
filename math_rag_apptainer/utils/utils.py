from io import BytesIO
from tarfile import open as tar_open
from typing import Generator


def stream_sif_file(
    stream: Generator[bytes, None, None],
) -> Generator[bytes, None, None]:
    buffer = BytesIO()

    for chunk in stream:
        buffer.write(chunk)
        buffer.seek(0)

        with tar_open(fileobj=buffer, mode='r') as tar:
            member = tar.next()

            if member:
                file_obj = tar.extractfile(member)

                if file_obj:
                    yield from file_obj

        buffer.seek(0)
        buffer.truncate()
