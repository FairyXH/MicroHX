# -*- coding:utf-8 -*-
import logging
from DormRobber import DormRobber
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s"
)
users = [
    {
        "name":"椰子桶",
        "cookie":"PHPSESSID=rscnjm3bahpc03pfh9qhul3jb6",
        "price":"3000"
    },
]
robber = DormRobber(
    users=users,
    start_time="12:00:00",
    interval=5.0
)
robber.start()