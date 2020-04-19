import json
import logging
import multiprocessing
import random
import socket
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Client(multiprocessing.Process):

    def __init__(self, host, port, rtt, p3):
        super().__init__()
        self._client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._host = host
        self._port = port
        self._file = ''
        self._time = rtt / 2
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
            self._client.send(json.dumps({
                'data': list(ch),
                'num': count,
                'status': '1'
            }).encode())
            logger.info(f'发送第 {count} 帧')
            resp = {}
            # 循环发送剩余部分
            while True:
                self._client.settimeout(2 * self._time)
                try:
                    resp = json.loads(self._client.recv(64).decode())
                except Exception as e:
                    resp['status'] = '2'
                # 数据帧丢失
                if resp['status'] == '0':
                    logger.error(f'第 {count} 帧\t数据帧接收出错')
                    logger.info(f'第 {count} 帧\t重新发送')
                # 接收到 ack
                elif resp['status'] == '1':
                    if random.random() > self._p3:
                        ch = f.read(64)
                        logger.info(f'第 {count} 帧\t数据帧确认')
                        count += 1
                        logger.info(f'第 {count} 帧\t发送')
                    else:
                        logger.error(f'第 {count} 帧\t未收到确认信息')
                        logger.info(f'第 {count} 帧\t重新发送')
                elif resp['status'] == '2':
                    logger.error(f'第 {count} 帧\t数据帧超时')
                    logger.info(f'第 {count} 帧\t重新发送')
                time.sleep(self._time)
                if ch:
                    self._client.send(json.dumps({
                        'data': list(ch),
                        'num': count,
                        'status': '1'
                    }).encode())
                else:
                    logger.info(f'文件发送完毕，共耗时{time.time() - start_time}')
                    self._client.send(json.dumps({
                        'data': '',
                        'mun': count,
                        'status': '0'
                    }).encode())
                    f.close()
                    break

        self._client.close()




