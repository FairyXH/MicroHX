# MicroHX

基于 `requests` 的校园微端（hxxy.edu.cn 移动端）Python SDK，附带一个多用户、定时启动的宿舍预选抢订脚本。

- 统一封装 HTTP 请求：超时、SSL 校验关闭、JSON 解析、异常归一化
- Cookie 登录态管理，接口自动携带登录信息
- 支持查询已参加活动、已获得学分、宿舍预选
- 多用户并发抢宿舍：每用户独立 Session、独立 Cookie、定时启动、自动重试，抢到即停

> 本项目仅用于个人学习与自动化研究，请遵守学校相关规定，Cookie 与账号信息请自行保管。

---

## 目录结构

```
MicroHX/
├── main.py              # 抢宿舍入口示例（配置用户后直接运行）
├── MicroHXModule.py     # MicroHX SDK：登录态管理与业务接口封装
├── DormRobber.py        # DormRobber：多用户抢宿舍任务管理器
├── README.md            # 本文档
└── 接口说明.txt          # 接口说明原始文档
```

---

## 环境要求

- Python 3.8+
- 依赖：`requests`、`urllib3`

```bash
pip install requests urllib3
```

---

## 快速开始

### 1. 使用 SDK 查询活动与学分

```python
import MicroHXModule

hx = MicroHXModule.MicroHX()

# 1. 更新登录态（Cookie 需要自行从已登录的浏览器/客户端中抓取）
hx.update_auth("PHPSESSID=你的会话ID")

# 2. 检查登录态是否有效
if hx.test_auth():
    print("登录态有效")
else:
    print("登录态失效，请重新抓取 Cookie")

# 3. 查询已参加的活动列表
result = hx.api_getvisitedactives()
print(result["data"])

# 4. 查询已获得的学分
result = hx.api_sumhdxfforxflx()
print(result["data"])
```

### 2. 宿舍预选

```python
import MicroHXModule

hx = MicroHXModule.MicroHX()
hx.update_auth("PHPSESSID=你的会话ID")

# price 可选值："1500" / "3000" / "4000"
result = hx.api_ssyx("3000")

if result["code"] == 0:
    remain = result["data"]["data"]["remain"]
    print(f"剩余名额: {remain}")
else:
    print(result["msg"])
```

### 3. 多用户定时抢宿舍

编辑 `main.py`，配置账号列表：

```python
import logging
from DormRobber import DormRobber

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

users = [
    {
        "name": "张三",
        "cookie": "PHPSESSID=用户A的会话ID",
        "price": "3000",
    },
    {
        "name": "李四",
        "cookie": "PHPSESSID=用户B的会话ID",
        "price": "1500",
    },
]

robber = DormRobber(
    users=users,
    start_time="12:00:00",   # 定时启动时间 HH:MM:SS
    interval=5.0             # 每个用户请求间隔（秒）
)
robber.start()
```

运行：

```bash
python main.py
```

运行后日志会显示距离开抢的倒计时，到点后每个用户独立线程开始循环提交预选请求，直至抢到（`remain > 0`）为止。

---

## API 文档

### MicroHX（`MicroHXModule.py`）

#### `MicroHX()`

创建 SDK 实例，内部初始化 `requests.Session`。

```python
hx = MicroHX()
```

#### `set_headers(cookies: str) -> dict`

根据 Cookie 生成请求头（微信内置浏览器 UA 等），同时更新对象内的 `headers` 属性。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `cookies` | `str` | 登录态 Cookie，一般以 `PHPSESSID=` 开头 |

返回请求头字典。

#### `get_headers() -> dict`

返回当前对象的请求头。

#### `update_auth(cookies: str) -> None`

更新登录态：调用 `set_headers()` 并将请求头合并进 Session，后续所有接口自动携带新登录信息。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `cookies` | `str` | 登录态 Cookie，一般以 `PHPSESSID=` 开头 |

```python
hx.update_auth("PHPSESSID=xxxx")
```

#### `test_auth() -> bool`

测试当前登录态是否有效（内部调用 `api_sumhdxfforxflx()`）。

| 返回 | 说明 |
| --- | --- |
| `True` | 登录态有效 |
| `False` | 登录态失效，需要重新 `update_auth()` |

#### `api_getvisitedactives() -> dict`

获取已参加活动列表。

```python
result = hx.api_getvisitedactives()
# result["data"] 为接口原始返回内容
```

#### `api_sumhdxfforxflx() -> dict`

获取已获得学分。

```python
result = hx.api_sumhdxfforxflx()
```

#### `api_ssyx(price: str) -> dict`

宿舍预选接口。

| 参数 | 类型 | 可选值 | 说明 |
| --- | --- | --- | --- |
| `price` | `str` | `"1500"`、`"3000"`、`"4000"` | 宿舍价位 |

```python
result = hx.api_ssyx("1500")
```

返回示例：

```json
{
    "code": 0,
    "msg": "名额已满",
    "data": {
        "remain": 0
    }
}
```

其中 `data.remain` 表示当前剩余名额数量。

### DormRobber（`DormRobber.py`）

#### `DormRobber(users: list, start_time: str, interval: float = 5.5)`

抢宿舍任务管理器。

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `users` | `list` | 用户列表，每项为 `{"name": str, "cookie": str, "price": str}` |
| `start_time` | `str` | 定时启动时间，格式 `HH:MM:SS` |
| `interval` | `float` | 每个用户两次请求之间的间隔（秒），默认 `5.5` |

#### `start()`

等待到 `start_time` 后，为每个用户启动一个独立线程执行抢宿舍任务，并等待所有线程结束。

#### `worker(user: dict)`

单用户抢宿舍线程逻辑：加载该用户 Cookie → 循环调用 `api_ssyx()` → 检测到剩余名额（`remain > 0`）即判定成功并退出线程。

#### `check_success(result: dict) -> bool`（静态方法）

判断一次预选请求是否抢到名额。

| 返回 | 说明 |
| --- | --- |
| `True` | `result["data"]["data"]["remain"] > 0`，抢到名额 |
| `False` | 未抢到或返回结构异常 |

---

## 统一返回格式

所有 SDK 接口（`api_*`）均返回统一结构：

```json
{
    "code": 0,
    "status_code": 200,
    "msg": "请求成功",
    "is_json": true,
    "data": {}
}
```

| 字段 | 类型 | 说明 |
| --- | --- | --- |
| `code` | `int` | SDK 请求状态码，见下表 |
| `status_code` | `int` | HTTP 响应状态码 |
| `msg` | `str` | 请求结果说明 |
| `is_json` | `bool` | 返回内容是否为 JSON |
| `data` | `any` | 接口实际返回的数据 |

### 错误码说明

| `code` | 含义 |
| --- | --- |
| `0` | 请求成功 |
| `1` | 返回数据不是 JSON 格式（`data` 为原始文本） |
| `-101` | 请求超时 |
| `-102` | 请求失败（网络异常等） |
| `-999` | 未知异常 |

---

## 注意事项

1. **Cookie 需自行获取**：SDK 不提供自动登录，需从已登录的浏览器或客户端抓取 Cookie，一般以 `PHPSESSID=` 开头。
2. **Cookie 失效后**：需要重新抓取并调用 `update_auth()` 更新登录态。
3. **请求间隔**：抢宿舍是高频请求，请合理设置 `interval`，避免对服务器造成压力。
4. **SSL 校验**：SDK 内部默认关闭 SSL 证书校验（`verify=False`），仅适用于个人自动化场景。
