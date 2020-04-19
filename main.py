import client
import server

if __name__ == '__main__':
    host = '127.0.0.1'
    port = 34567
    p1 = 0.01
    p2 = 0.01
    p3 = 0.01
    rtt = 0.01
    send_file = 'lena.bmp'
    recv_file = 'recv.bmp'
    client = client.Client(host, port, rtt, p3)
    server = server.Server(host, port, rtt, p1, p2)

    server.save_file(recv_file)
    client.load_file(send_file)

    server.start()
    client.start()

    server.join()
    client.join()
