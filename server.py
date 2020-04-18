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

    def save_file(self, file):
        self._file = file

    def run(self):
        start_time = time.time()
        self._server.connect((self._host, self._port))
        logger.info('服务器启动完毕')
        last_resp = ''
        count = 0
        with open(self._file, 'wb+') as f:
            while True:
                resp = self._server.recv(64)
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
                        logger.error(f'第 {count} 帧\t接收错误')
                        time.sleep(self._rtt)
                        self._server.send('0'.encode())
                        count -= 1
                    else:
                        if last_resp == resp:
                            logger.info(f'第 {count} 帧\t接收成功')
                        else:
                            count += 1
                            logger.info(f'第 {count} 帧\t接收成功')
                            f.write(resp)
                        time.sleep(self._rtt)
                        self._server.send('1'.encode())
                last_resp = resp
        self._server.close()
