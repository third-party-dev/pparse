#!/usr/bin/env python3

import http.server
import os


class RangeRequestHandler(http.server.SimpleHTTPRequestHandler):
    def send_head(self):
        """Intercept GET to handle Range requests."""
        range_header = self.headers.get("Range")
        if not range_header:
            return super().send_head()

        # Parse "bytes=start-end"
        try:
            range_spec = range_header.strip().removeprefix("bytes=")
            start_str, end_str = range_spec.split("-")
            path = self.translate_path(self.path)
            file_size = os.path.getsize(path)

            start = int(start_str) if start_str else 0
            end   = int(end_str)   if end_str   else file_size - 1
            end   = min(end, file_size - 1)

            if start > end or start >= file_size:
                self.send_error(416, "Requested Range Not Satisfiable")
                return None

            length = end - start + 1

            f = open(path, "rb")
            f.seek(start)

            self.send_response(206)
            self.send_header("Content-Type",  self.guess_type(path))
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
            self.send_header("Content-Length", str(length))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Last-Modified", self.date_time_string(os.path.getmtime(path)))
            self.end_headers()
            return f

        except (ValueError, OSError) as e:
            self.send_error(400, f"Bad Range request: {e}")
            return None

    def copyfile(self, source, outputfile):
        """Only copy as many bytes as the range specifies."""
        range_header = self.headers.get("Range")
        if not range_header:
            return super().copyfile(source, outputfile)

        try:
            range_spec = range_header.strip().removeprefix("bytes=")
            start_str, end_str = range_spec.split("-")
            file_size = os.path.getsize(self.translate_path(self.path))

            start = int(start_str) if start_str else 0
            end   = int(end_str)   if end_str   else file_size - 1
            end   = min(end, file_size - 1)
            length = end - start + 1

            remaining = length
            while remaining:
                chunk = source.read(min(65536, remaining))
                if not chunk:
                    break
                outputfile.write(chunk)
                remaining -= len(chunk)
        finally:
            source.close()


if __name__ == "__main__":
    http.server.test(HandlerClass=RangeRequestHandler)

'''
With file io.
real    0m0.714s
user    0m1.006s
sys     0m2.591s

With test-server.py.
real    0m15.338s
user    0m9.357s
sys     0m3.129s
'''