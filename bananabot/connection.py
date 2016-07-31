'''
A module for handling IRC client interfacing.
'''


import socket


class Connector:
    '''
    Handles connection, disconnection,
    and sending things to an irc server.
    '''
    def __init__(self, username, nick, channel, host, port):
        self.username = username
        self.nick = nick
        self.channel = channel
        self.host = host
        self.port = port
        self.socket = None
        self.buffer = None

    def connect(self,):
        '''
        Creates socket and connects.
        '''
        self.socket = socket.socket()
        self.socket.connect((self.host, self.port))
    
    def send(self, *data):
        '''
        Packages data for encoding and sends.
        '''
        data = ' '.join(data) + '\r\n'
        self.socket.send(bytes((data), 'utf-8'))

    def recv(self):
        '''
        Feeds incoming lines to buffer and yields them.
        '''
        data = self.socket.recv(4096)
        if self.buffer is not None:
            data = self.buffer + data
            self.buffer = None
        lines = data.split(b'\r\n')
        for line in range(len(lines) -1):
            line = str(lines[line], 'utf-8', 'replace')
            yield line
        last_line = lines[-1]
        if last_line:
            self.buffer = last_line

    def disconnect(self):
        '''
        Closes the socket and reverts it to none.
        '''
        self.socket.close()
        self.socket = None

    def establish_connection(self):
        '''
        Connects to server and begins handshake.
        '''
        self.connect(self.host, self.port)
        self.send('USER ' + (self.user + ' ')*3 + 'python bot')
        self.send('NICK ' + self.nick)
        self.send('JOIN ' + self.channel)
