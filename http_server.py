import mimetypes
import os
import socket
import sys
import traceback

def response_ok(body=b"This is a minimal response", mimetype=b"text/plain"):
    """
    returns a basic HTTP response
    Ex:
        response_ok(
            b"<html><h1>Welcome:</h1></html>",
            b"text/html"
        ) ->

        b'''
        HTTP/1.1 200 OK\r\n
        Content-Type: text/html\r\n
        \r\n
        <html><h1>Welcome:</h1></html>\r\n
        '''
    """

    return b"\r\n".join([
        b'HTTP/1.1 200 OK',
        b'Content-Type: ' + mimetype,
        b'',
        body
        ])


def response_method_not_allowed():
    """Returns a 405 Method Not Allowed response"""

    return b"\r\n".join([
        b'HTTP/1.1 405 Method Not Allowed',
        b'Content-Type: text/html'
        b'',
        b'<thml><h1 color=red>405 Method Not Allowed</h1></html>'
        ])


def response_not_found():
    """Returns a 404 Not Found response"""

    return b"\r\n".join([
        b'HTTP/1.1 404 Not Found',
        b'Content-Type: text/html'
        b'',
        b'<html><h1 color=red>404 Not Found</h1></html>'
        ])


def parse_request(request):
    """
    Given the content of an HTTP request, returns the path of that request.

    This server only handles GET requests, so this method shall raise a
    NotImplementedError if the method of the request is not GET.
    """
    method, uri, _ = request.split('\r\n')[0].split(' ')

    if method != 'GET':
        print("{} received".format(method))
        raise NotImplementedError
    else:
        print('GET received')

    return uri


def response_path(_path):
    """
    This method should return appropriate content and a mime type.

    If the requested path is a directory, then the content should be a
    plain-text listing of the contents with mimetype `text/plain`.

    If the path is a file, it should return the contents of that file
    and its correct mimetype.

    If the path does not map to a real location, it should raise an
    exception that the server can catch to return a 404 response.

    Ex:
        response_path('/a_web_page.html') -> (b"<html><h1>North Carolina...",
                                            b"text/html")

        response_path('/images/sample_1.png')
                        -> (b"A12BCF...",  # contents of sample_1.png
                            b"image/png")

        response_path('/') -> (b"images/, a_web_page.html, make_type.py,...",
                             b"text/plain")

        response_path('/a_page_that_doesnt_exist.html') -> Raises a NameError

    """
    web_path = os.path.join(os.getcwd(), 'webroot', _path.lstrip('/'))

    if(os.path.exists(web_path)):
        if(os.path.isdir(web_path)):
            mime_type = b'text/plain'
            contents = str(os.listdir(web_path)).encode('utf-8')
        else:
            mime_type = mimetypes.MimeTypes().guess_type(web_path)[0].encode('utf-8')
            if(mime_type == b'text/plain'):
                with open(web_path, 'r') as file:
                    contents = file.read().encode('utf-8')
            else:
                with open(web_path, 'rb') as file:
                    contents = file.read()
    else:
        print('path not found {}'.format(web_path))
        raise NameError

    # If the path is "make_time.py", then you may OPTIONALLY return the
    # result of executing `make_time.py`. But you need only return the
    # CONTENTS of `make_time.py`.

    return contents, mime_type


def server(log_buffer=sys.stderr):
    """ Run the server """
    address = ('127.0.0.1', 10000)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print("making a server on {0}:{1}".format(*address), file=log_buffer)
    sock.bind(address)
    sock.listen(1)

    try:
        while True:
            print('waiting for a connection', file=log_buffer)
            conn, addr = sock.accept()  # blocking
            try:
                print('connection - {0}:{1}'.format(*addr), file=log_buffer)

                request = ''
                while True:
                    data = conn.recv(1024)
                    request += data.decode('utf8')

                    if '\r\n\r\n' in request:
                        break


                print("Request received:\n{}\n\n".format(request))

                contents = b''
                mime_type = b'text/plain'

                try:
                    path = parse_request(request)
                    contents, mime_type = response_path(path)
                    response = response_ok(
                        body = contents,
                        mimetype = mime_type
                    )
                except NotImplementedError:
                    response = response_method_not_allowed()
                except NameError:
                    response = response_not_found()

                conn.sendall(response)
            except:
                traceback.print_exc()
            finally:
                conn.close()

    except KeyboardInterrupt:
        sock.close()
        return
    except:
        traceback.print_exc()


if __name__ == '__main__':
    server()
    sys.exit(0)


