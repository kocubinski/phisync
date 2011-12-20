import socket, os, yaml, hashlib

SERVER_IP='192.168.1.55'
SERVER_PORT=9000

class phi_socket:
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self):
        self.sock.connect((SERVER_IP, SERVER_PORT))

    def recv_all(self):
        recvd = ''
        while True:
            data = self.sock.recv(1024)
            if not data: break
            recvd += data
        return recvd

    def send_all(self, data):
        self.sock.sendall(data)
        self.sock.shutdown(socket.SHUT_WR)
        
    def parse_cmd(self, cmd):
        if cmd == "push_head":
            print "Pushing new head..."
        elif cmd == "sync_head":
            print "Syncing to current head..."
            
def writefile(d, path):
    f = open(path, 'wb')
    f.write(d)
    f.flush()

class phi_state:
    _state_path = '.phisync/state'
    
    def __init__(self):
        if not os.path.exists('.phisync'):
            os.makedirs('.phisync')
        if not os.path.exists(self._state_path):
            f = open(self._state_path, 'w')
            f.write("""
                    head: none
                    head_name: none
                    """)
            f.flush()
        data = open(self._state_path).read()
        self.state = yaml.load(data)
        if self.state:
            print "Head is: " + self.state['head'] + self.state['head_name']

    def push_head(self, name, data):
        h = hashlib.md5(data).hexdigest()
        path = '.phisync/' + h
        writefile(data, path)
        print "Finished writing file."
        print "New head: " + h
        print self.state
        self.state['head'] = h
        self.state['head_name'] = name
        self.write_state()

    def write_state(self):
        f = open(self._state_path, 'w')
        f.write(yaml.dump(self.state, default_flow_style=False))