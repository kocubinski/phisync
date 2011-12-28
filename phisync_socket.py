import socket, os, yaml, hashlib

SERVER_IP='192.168.1.185'
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
        data = open(self._state_path).read()
        self.state = yaml.load(data)
        if not self.state:
            self.state = dict()
            self.projects = []
            return
        
        self.projects = self.state.keys()
        print "Head(s):"
        for proj in self.state:
            print proj, '-', self.state[proj]['head'], self.state[proj]['head_name']

    def push_head(self, project, name, data):
        if not project in self.projects:
            self.projects.append(project)
            self.state[project] = dict()
            
        h = hashlib.md5(data).hexdigest()
        hash_path = '.phisync/' + h
        name_path = '.phisync/' + name
        writefile(data, hash_path)
        writefile(data, name_path)
        self.state[project]['head'] = h
        self.state[project]['head_name'] = name
        self.write_state()
        
        print "Finished writing file."
        print "New head: " + h

    def write_state(self):
        f = open(self._state_path, 'w')
        f.write(yaml.dump(self.state, default_flow_style=False))
