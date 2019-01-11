import socket
  
def handle_request(client):
    # buf = client.recv(1024)
    # client.send("HTTP/1.1 200 OK\r\n\r\n")
    # client.send("Hello, World")
    buf = client.recv(1024)
    print(buf)
    client.send(b"t")
    
def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.bind(('0.0.0.0',8080))
    sock.bind(('0.0.0.0',8080))
    sock.listen(5)
    print("wating for connection...")
    connection, address = sock.accept()
    print(address)
    while True:
        handle_request(connection)
  
if __name__ == '__main__':
  main()