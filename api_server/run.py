from os import unlink
from os.path import exists
import socket

from server import app
import settings


def main():
    try:
        if settings.DEV_ENV:
            app.run(host=settings.API_HOST, port=settings.DEV_PORT, debug=settings.DEBUG)
        else:
            #in case when using sockets
            #try:
                #addr = '/tmp/{}_api_sock'.format(settings.FOLDER)
                #unlink(addr)
            #except OSError:
                    #if exists(addr):
                        #raise
            #sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            #sock.bind(addr)
            #app.run(host=None, port=None, sock=sock, debug=settings.DEBUG, workers=settings.API_WORKERS, log_config=None)
            #ssl = {'cert': "/etc/letsencrypt/live/{}/fullchain.pem".format(settings.API_HOST),
                #'key': "/etc/letsencrypt/live/{}/privkey.pem".format(settings.API_HOST)}
            app.run(host=settings.API_HOST,
                port=settings.PORT,
                sock=None, debug=settings.DEBUG,
                workers=settings.API_WORKERS,
                log_config=None)
    except KeyboardInterrupt:
        pass


main()
