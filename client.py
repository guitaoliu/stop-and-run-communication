import socket
import random
import time
import logging
import multiprocessing

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Client(multiprocessing.Process):

    def __init__(self, host, port, rtt, p3):
        super().__init__()
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._host = host
        self._port = port
        self._file = ''
        self._rtt = rtt
        self._p3 = p3

    def load_file(self, file):
        self._file = file

    def run(self):
        start_time = time.time()
        self._client.connect((self._host, self._port))
        count = 0
        with open(self._file, 'rb+') as f:
            # 发送第一帧
            count += 1
            ch = f.read(64)
            self._client.send(ch)
            logger.info(f'发送第 1 帧')

            # 循环发送剩余部分
            while True:
                # 模拟数据帧丢失
                self._client.settimeout(2 * self._rtt)
                try:
                    resp = self._client.recv(64).decode()
                except Exception as e:
                    resp = '2'
                # 数据帧丢失
                if resp == '0':
                    logger.error(f'第 {count} 帧\t数据帧接收出错')
                    logger.info(f'第 {count} 帧\t重新发送')
                # 接收到 ack
                elif resp == '1':
                    if random.random() > self._p3:
                        ch = f.read(64)
                        logger.info(f'第 {count} 帧\t数据帧确认')
                        count += 1
                        logger.info(f'第 {count} 帧\t发送')
                    else:
                        logger.error(f'第 {count} 帧\t未收到确认信息')
                        logger.info(f'第 {count} 帧\t重新发送')
                elif resp == '2':
                    logger.error(f'第 {count} 帧\t数据帧超时')
                    logger.info(f'第 {count} 帧\t重新发送')
                time.sleep(self._rtt)
                if ch:
                    self._client.send(ch)
                else:
                    logger.info(f'文件发送完毕，共耗时{time.time() - start_time}')
                    self._client.send('0'.encode())
                    f.close()
                    break

        self._client.close()




