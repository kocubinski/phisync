import phisync_socket as phisock;
import argparse, os, yaml, hashlib, socket, zipfile


def writefile(d, path):
    f = open(path, 'wb')
    f.write(d)
    f.flush()
    return f

def inflate_zip(f):
    headdir = os.getcwd() + '/head'
    if not os.path.exists(headdir):
        os.makedirs(headdir)
    zipfile.ZipFile(f).extractall(headdir)
    
def send_data(data, sock=None):
    s = phisock.phi_socket(sock)
    if sock is None:
        s.connect()
    s.send_all(data)
        
def startserver():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 9000))
    s.listen(5)
    state = phisock.phi_state()
    print "Ok"

    while 1:
        c, a = s.accept()
        print "Connected: " + str(a)
        cmd_sock = phisock.phi_socket(c)
        cmd = cmd_sock.recv_all()

        if cmd == "push_head":
            print "Waiting for file..."
            c, a = s.accept()
            sock = phisock.phi_socket(c)
            name = sock.recv_all()
            c, a = s.accept()
            sock = phisock.phi_socket(c)
            data = sock.recv_all() 
            state.push_head(name, data)

        elif cmd == "get_head":
            print "Sending head..."
            c, a = s.accept()
            send_data(state.state['head_name'], c)
            d = open('.phisync/' + state.state['head'], 'rb').read()
            c, a = s.accept()
            send_data(d, c)

def client_getdata():
    s = phisock.phi_socket()
    s.connect()
    return s.recv_all()

def client_pushfile(path):
    f = open(path, 'rb')
    data = f.read()
    send_data('push_head')
    send_data(os.path.basename(path))
    send_data(data)

def client_gethead():
    send_data('get_head')
    filename = client_getdata()
    d = client_getdata()
    f = writefile(d, '.phisync/' + filename)
    inflate_zip(filename)
    

def main():
    parser = argparse.ArgumentParser(description='Send/Receive files with PyShare')
    parser.add_argument('-s', dest='server', action='store_true')
    parser.add_argument('-g', dest='gethead', action='store_true')
    parser.add_argument('-p', '--push')
    args = parser.parse_args()
    if (args.server):
        print "Starting server..."
        startserver()
    elif (args.push):
        print "Pushing file..."
        client_pushfile(args.push)
    elif (args.gethead):
        print "Getting head..."
        client_gethead()
    

if __name__ == "__main__":
    #startserver()
    main()