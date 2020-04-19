import json
import logging
import multiprocessing
import random
import socket
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Server(multiprocessing.Process):

    def __init__(self, host, port, rtt, p1, p2):
        super().__init__()
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._host = host
        self._port = port
        self._file = ''
        self._time = rtt / 2
        self._p1 = p1
        self._p2 = p2
        self._recv = {1: False}

    def save_file(self, file):
        self._file = file

    def run(self):
        start_time = time.time()
        self._server.bind(('', self._port))
        self._server.listen(1)
        conn, addr = self._server.accept()
        logger.info('服务器启动完毕')
        with open(self._file, 'wb+') as f:
            while True:
                try:
                    resp = json.loads(conn.recv(1024).decode())
                except:
                    resp['status'] = '1'

                if resp['status'] == '0':
                    f.close()
                    logger.info(f'接收耗时{time.time() - start_time}秒')
                    break
                else:
                    if self._recv[resp['num']]:
                        conn.send(json.dumps({
                            'status': '1'
                        }).encode())
                    else:
                        # 接收失败
                        if random.random() < self._p2:
                            continue
                        # 数据帧出错
                        elif random.random() < self._p1:
                            logger.error(f'第 {resp["num"]} 帧\t接收错误')
                            time.sleep(self._time)
                            conn.send(json.dumps({
                                'status': 0,
                            }).encode())
                        else:
                            if not self._recv[resp['num']]:
                                self._recv[resp['num']] = True
                                self._recv[resp['num'] + 1] = False
                                logger.info(f'第 {resp["num"]} 帧\t接收成功')
                                f.write(bytes(resp['data']))
                                time.sleep(self._time)
                                conn.send(json.dumps({
                                    'status': '1'
                                }).encode())
        conn.close()
