# -*- coding: utf-8 -*-
import threading
import time
import datetime
import logging
import MicroHXModule
class DormRobber:
    """
    抢宿舍任务管理器
    支持:
    - 多用户
    - 独立Cookie
    - 定时启动
    - 独立Session
    - 自动重试
    """
    def __init__(
        self,
        users: list,
        start_time: str,
        interval: float = 5.5
    ):
        """
        :param users:
            [
                {
                    "name":"张三",
                    "cookie":"xxx",
                    "price":"3000"
                }
            ]
        :param start_time:
            HH:MM:SS
        :param interval:
            请求间隔
        """
        self.users = users
        self.start_time = start_time
        self.interval = interval
        self.threads = []
    @staticmethod
    def check_success(result):
        """
        判断是否抢到
        """
        try:
            remain = (
                result
                ["data"]
                ["data"]
                ["remain"]
            )
            return remain > 0
        except Exception:
            return False
    def wait_start(self):
        """
        等待指定时间
        """
        while True:
            now = datetime.datetime.now()
            target = datetime.datetime.strptime(
                self.start_time,
                "%H:%M:%S"
            ).replace(
                year=now.year,
                month=now.month,
                day=now.day
            )
            remain = (
                target-now
            ).total_seconds()
            if remain <= 0:
                break
            logging.info(
                f"距离开始还有 {remain:.1f} 秒"
            )
            time.sleep(
                min(remain,5)
            )
    def worker(self,user):
        """
        单用户线程
        """
        name = user["name"]
        cookie = user["cookie"]
        price = user["price"]
        mh = MicroHXModule.MicroHX()
        mh.update_auth(
            cookie
        )
        logging.info(
            f"{name} 登录态加载完成"
        )
        while True:
            try:
                result = mh.api_ssyx(
                    price
                )
                try:
                    msg = result["data"]["msg"]
                except:
                    msg = result["msg"]
                logging.info(
                    f"{name}: {msg}"
                )
                if self.check_success(result):
                    logging.info(
                        f"{name} 抢宿舍成功"
                    )
                    break
            except Exception as e:
                logging.error(
                    f"{name}异常: {e}"
                )
            time.sleep(
                self.interval
            )
    def start(self):
        """
        启动抢宿舍
        """
        self.wait_start()
        logging.info(
            "开始抢宿舍"
        )
        for user in self.users:
            t = threading.Thread(
                target=self.worker,
                args=(user,),
                name=user["name"],
                daemon=True
            )
            t.start()
            self.threads.append(t)
        for t in self.threads:
            t.join()