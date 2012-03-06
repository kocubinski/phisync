import phisync_socket as phisock;
import argparse, os, yaml, hashlib, socket, zipfile, shutil
import sys, signal

def signal_handler(signal, frame):
   print 'Exiting gracefully...'

signal.signal(signal.SIGINT, signal_handler)

def writefile(d, path):
    f = open(path, 'wb')
    f.write(d)
    f.flush()
    return f

def inflate_zip(project, path):
    projectdir = os.getcwd() + '\\' + project
    if os.path.exists(projectdir):
        shutil.rmtree(projectdir)
    else:
        os.makedirs(projectdir)
    zipfile.ZipFile(path).extractall(projectdir)

def server_getsocket(sock):
    c, a = sock.accept()
    return phisock.phi_socket(c)
    
def server_sendpacket(data, sock):
    s = server_getsocket(sock)
    s.send_all(data)

def server_getpacket(sock):
    s = server_getsocket(sock)
    return s.recv_all()
        
def startserver(debugmode):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', phisock.SERVER_PORT))
    s.listen(5)
    state = phisock.phi_state()

    if (debugmode): server_listen(s, state)
    else:
        while 1:
            server_listen(s, state)
    
def server_listen(s, state):
    c, a = s.accept()
    print "Connected: " + str(a)
    cmd_sock = phisock.phi_socket(c)
    cmd = cmd_sock.recv_all()

    if cmd == "push_head":
        print "Waiting for file..."
        name = server_getpacket(s)
        project = server_getpacket(s)
        data = server_getpacket(s)
        state.push_head(project, name, data)

    elif cmd == "get_head":
        project = server_getpacket(s)
        if not project in state.projects:
            print 'WARN: request for', project, 'not found.'
            return
            #continue

        print "Sending head for", project, '...'
        server_sendpacket(state.state[project]['head_name'], s)
        d = open('.phisync/' + state.state[project]['head'], 'rb').read()
        server_sendpacket(d, s)

def client_getpacket():
    s = phisock.phi_socket()
    s.connect()
    return s.recv_all()

def client_sendpacket(data):
    s = phisock.phi_socket()
    s.connect()
    s.send_all(data)

def client_pushfile(project, path):
    f = open(path, 'rb')
    data = f.read()
    client_sendpacket('push_head')
    client_sendpacket(os.path.basename(path))
    client_sendpacket(project)
    client_sendpacket(data)

def client_gethead(project):
    client_sendpacket('get_head')
    client_sendpacket(project)
    filename = client_getpacket()
    print "Receiving", filename, "..."
    d = client_getpacket()
    phid = os.getcwd() + '\\.phisync\\'
    if not os.path.exists(phid):
        os.makedirs(phid)
    path = phid + filename
    writefile(d, path)
    print "Inflating archive..."
    inflate_zip(project, path)


def checkname(args):
    if not args.name:
        print "error: must supply a project name with -n"
        return False
    return True
    
def main_cli():
    parser = argparse.ArgumentParser(description='Send/Receive files with PyShare')
    parser.add_argument('-s', dest='server', action='store_true')
    parser.add_argument('-d', dest='debugmode', action='store_true')
    parser.add_argument('-g', '--gethead', dest='gethead', action='store_true')
    parser.add_argument('-n', '--name', metavar='project_name')
    parser.add_argument('-p', '--push', metavar='filename')
    args = parser.parse_args()
    if (args.server):
        print "Starting server..."
        startserver(args.debugmode)
    elif (args.push):
        if not checkname(args): return
        print "Pushing file..."
        client_pushfile(args.name, args.push)
    elif (args.gethead):
        if not checkname(args): return
        print "Getting current", args.name, "..."
        client_gethead(args.name)
    

if __name__ == "__main__":
    main_cli()