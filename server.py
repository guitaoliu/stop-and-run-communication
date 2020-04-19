import socket
import random
import time
import logging
import multiprocessing

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Server(multiprocessing.Process):

    def __init__(self, host, port, rtt, p1, p2):
        super().__init__()
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._host = host
        self._port = port
        self._file = ''
        self._rtt = rtt
        self._p1 = p1
        self._p2 = p2
        self._recv = {}

    def save_file(self, file):
        self._file = file

    def run(self):
        start_time = time.time()
        self._server.bind(('', self._port))
        self._server.listen(1)
        conn, addr = self._server.accept()
        logger.info('服务器启动完毕')
        last_resp = ''
        count = 0
        with open(self._file, 'wb+') as f:
            while True:
                resp = conn.recv(64)
                try:
                    resp_decoded = resp.decode()
                except:
                    resp_decoded = '1'

                if resp_decoded == '0':
                    f.close()
                    logger.info(f'接收耗时{time.time()-start_time}秒')
                    break
                else:
                    # 接收失败
                    if random.random() < self._p2:
                        continue
                    # 数据帧出错
                    elif random.random() < self._p1:
                        count += 1
                        self._recv[count] = False
                        logger.error(f'第 {count} 帧\t接收错误')
                        time.sleep(self._rtt)
                        conn.send('0'.encode())
                        count -= 1
                    else:
                        count += 1
                        try:
                            if not self._recv[count]:
                                logger.info(f'第 {count} 帧\t接收成功')
                                self._recv[count] = True
                        except:
                            self._recv[count] = True
                            logger.info(f'第 {count} 帧\t接收成功')
                        finally:
                            f.write(resp)
                        time.sleep(self._rtt)
                        conn.send('1'.encode())
                last_resp = resp
        conn.close()
