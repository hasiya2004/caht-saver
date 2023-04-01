import socket
import select
import sys


def broadcast_message(sock, message):
    global CONNECTION_LIST
    for loop_sock in CONNECTION_LIST:
        if loop_sock != server_socket and loop_sock != sock:
            try:
                loop_sock.send(bytes(message, 'UTF-8'))
            except:
                loop_sock.close()
                CONNECTION_LIST.remove(socket)


def print_usage():
    print("Usage:\n\tpython server.py <hostname> <port> <recv_amount>\n")
    print("\thostname - name of the host to listen on (typically localhost or '', use local host for '')")
    print("\tport - port to listen to")
    print("\trecv_amt - max bytes received by the server 4096 is plenty for simple chat")


if __name__ == "__main__":
    global CONNECTION_LIST
    CONNECTION_LIST = []
    if len(sys.argv) != 4:
        print_usage()
        exit()
    RECV_BUFFER = int(sys.argv[3])
    HOST = ''
    if sys.argv[1] != 'localhost':
        HOST = sys.argv[1]
    PORT = int(sys.argv[2])

    print(HOST, PORT)
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(15)

    CONNECTION_LIST.append(server_socket)

    print("Chat server started on port " + str(PORT))

    while True:
        read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, [], [])
        for sock in read_sockets:
            if sock == server_socket:
                sockfd, addr = server_socket.accept()
                CONNECTION_LIST.append(sockfd)
                print("Client (%s, %s) connected." % (addr[0], addr[1]))
                new_connect = "[%s:%s] entered the room" % (addr[0], addr[1])
                broadcast_message(sockfd, new_connect)
            else:
                try:
                    data = sock.recv(RECV_BUFFER)
                    msg = str(data)
                    msg = msg.replace('b\'', '')
                    msg = msg.replace('\'', '')
                    if 'immediate termination passphrase: plsstop' in msg:
                        broadcast_message(sock, 'Connection terminated, server shutting down..')
                        server_socket.close()
                        exit()
                    elif data:
                        broadcast_message(sock, msg)
                        print('Data received: ' + str(data))
                except:
                    print("Client (%s, %s) is offline" % (addr[0], addr[1]))
                    broadcast_message(sock, "Client (%s, %s) is offline" % (addr[0], addr[1]))
                    sock.close()
                    if sock in CONNECTION_LIST:
                        CONNECTION_LIST.remove(sock)
                    continue
    server_socket.close()
