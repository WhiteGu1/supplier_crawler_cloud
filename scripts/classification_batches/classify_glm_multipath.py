# -*- coding: utf-8 -*-
"""
全库在售商品多路径分类脚本 (智谱 BigModel Free: glm-4.7-flash + glm-4.6v-flash)
- 严格锁定标准三级分类库 (standard_categories.json，共 487 条标准路径)，严禁AI自创野路径
- 优先处理：1) 无分类商品 -> 2) 西语原分类商品 -> 3) 仅1级分类商品 -> 4) 仅单路径商品
- 双模型并发：
  * Worker 1: glm-4.7-flash (文本批量多路径分类)
  * Worker 2: glm-4.6v-flash (文本批量多路径分类 + 视觉识图分类队列优先处理)
- 写入：
  * product_categories 表（写入所有 2~5 条并列标准分类路径，清理旧西语/单级残留）
  * products.category 字段（若原为空/西语/单级，则更新为主分类路径，保持 updated_at 不变以免影响PDF缺货判断）
- 支持断点续传：通过 classify_cache/glm_multipath/processed_ids.txt 记录已处理商品ID
"""
import base64
import io
import json
import os
import queue
import re
import sys
import threading
import time
from datetime import datetime
import pymysql
import requests
from PIL import Image

sys.stdout.reconfigure(encoding='utf-8')

API_URL = "https://open.bigmodel.cn/api/paas/v4/chat/completions"
API_KEY = os.getenv("ZHIPU_API_KEY", "")

DB_CONFIG = {
    'host': 'localhost', 'port': 3306, 'user': 'root',
    'password': 'admin123', 'database': 'supplier_crawler', 'charset': 'utf8mb4'
}

IMAGE_BASE = r"D:\projects\supplier_crawler"
CACHE_DIR = r"D:\projects\supplier_crawler\classify_cache\glm_multipath"
PROCESSED_FILE = os.path.join(CACHE_DIR, "processed_ids.txt")
STATUS_FILE = os.path.join(CACHE_DIR, "status.json")
STANDARD_CATS_FILE = r"D:\projects\supplier_crawler\scripts\classification_batches\standard_categories.json"

TEXT_BATCH_SIZE = 35
VISION_BATCH_SIZE = 6

VALID_L1 = {
    '厨房用品', '家居生活', '摆件礼品', '文具', '玩具',
    '化妆品饰品', '箱包皮具', '电子电器', '运动户外',
    '母婴用品', '宠物', '五金', '服装鞋帽'
}

L2_MERGE_MAP = {
    ("家居生活", "家纺"): "家纺毛巾",
    ("家居生活", "浴室用品"): "卫浴用品",
    ("家居生活", "日用百货"): "日用杂货",
    ("文具", "办公文具"): "文具办公",
    ("摆件礼品", "派对用品"): "派对节庆",
    ("厨房用品", "烘焙器具"): "炊具",
    ("服装鞋帽", "鞋帽"): "服装服饰",
    ("箱包皮具", "箱包"): "箱包配件",
    ("母婴用品", "喂养用品"): "婴幼儿用品",
}

with open(STANDARD_CATS_FILE, "r", encoding="utf-8") as _f:
    ALLOWED_LIST = json.load(_f)

ALLOWED_SET = set(ALLOWED_LIST)
BY_L1_L2 = {}
BY_L1 = {}
for _c in ALLOWED_LIST:
    _l1, _l2, _l3 = _c.split(" > ")
    BY_L1_L2.setdefault((_l1, _l2), []).append((_l3, _c))
    BY_L1.setdefault(_l1, []).append((_l2, _l3, _c))

EXACT_SYNONYM_MAP = {
    "五金 > 五金工具 > 其他五金": "五金 > 五金工具 > 五金工具",
    "五金 > 五金工具 > 润滑/保养": "五金 > 五金工具 > 五金工具",
    "五金 > 五金工具 > 标线绳": "五金 > 五金工具 > 五金工具",
    "五金 > 五金工具 > 硅胶条": "五金 > 五金工具 > 五金工具",
    "五金 > 缝纫针线 > 针/别针": "五金 > 缝纫针线 > 缝纫线",
    "化妆品饰品 > 时尚配饰 > 发饰/头饰": "化妆品饰品 > 时尚配饰 > 发箍/发饰",
    "化妆品饰品 > 时尚配饰 > 胸针": "化妆品饰品 > 时尚配饰 > 首饰",
    "化妆品饰品 > 时尚配饰 > 手表": "化妆品饰品 > 时尚配饰 > 首饰",
    "化妆品饰品 > 美妆个护 > 发梳": "化妆品饰品 > 美妆个护 > 梳子/发刷",
    "化妆品饰品 > 美妆个护 > 发刷/梳子": "化妆品饰品 > 美妆个护 > 梳子/发刷",
    "化妆品饰品 > 美妆个护 > 梳子": "化妆品饰品 > 美妆个护 > 梳子/发刷",
    "化妆品饰品 > 美妆个护 > 婴儿护理": "化妆品饰品 > 美妆个护 > 护肤/化妆品",
    "化妆品饰品 > 美妆个护 > 剃须刀": "化妆品饰品 > 美妆个护 > 按摩/脱毛",
    "厨房用品 > 储物保鲜 > 储物罐": "厨房用品 > 储物保鲜 > 保鲜盒/储物罐",
    "厨房用品 > 储物保鲜 > 茶叶罐": "厨房用品 > 储物保鲜 > 保鲜盒/储物罐",
    "厨房用品 > 储物保鲜 > 食品袋": "厨房用品 > 储物保鲜 > 保鲜盒/储物罐",
    "厨房用品 > 储物保鲜 > 玻璃瓶": "厨房用品 > 储物保鲜 > 玻璃储物罐",
    "厨房用品 > 储物保鲜 > 储物架": "厨房用品 > 储物保鲜 > 收纳架",
    "厨房用品 > 储物保鲜 > 旋转调料架": "厨房用品 > 储物保鲜 > 收纳架",
    "厨房用品 > 储物保鲜 > 锅具收纳": "厨房用品 > 储物保鲜 > 收纳架",
    "厨房用品 > 储物保鲜 > 水槽收纳套装": "厨房用品 > 储物保鲜 > 水槽置物架",
    "厨房用品 > 清洁用品 > 烧烤刷": "厨房用品 > 清洁用品 > 清洁刷",
    "厨房用品 > 炊具 > 烘焙模具": "厨房用品 > 炊具 > 模具/烤模",
    "厨房用品 > 炊具 > 制冰模具": "厨房用品 > 炊具 > 模具/烤模",
    "厨房用品 > 炊具 > 擀面杖": "厨房用品 > 炊具 > 烘焙工具",
    "厨房用品 > 炊具 > 蛋糕铲": "厨房用品 > 炊具 > 烘焙工具",
    "厨房用品 > 炊具 > 烤架/冷却架": "厨房用品 > 炊具 > 烘焙工具",
    "厨房用品 > 炊具 > 竹铲": "厨房用品 > 炊具 > 竹制铲勺",
    "厨房用品 > 炊具 > 去皮器": "厨房用品 > 炊具 > 削皮器",
    "厨房用品 > 炊具 > 大蒜压": "厨房用品 > 炊具 > 压蒜器",
    "厨房用品 > 炊具 > 蒜压": "厨房用品 > 炊具 > 压蒜器",
    "厨房用品 > 炊具 > 捣泥器": "厨房用品 > 炊具 > 压泥器",
    "厨房用品 > 炊具 > 肉锤": "厨房用品 > 炊具 > 压泥器",
    "厨房用品 > 炊具 > 嫩肉锤": "厨房用品 > 炊具 > 压泥器",
    "厨房用品 > 炊具 > 主厨刀": "厨房用品 > 炊具 > 刀具",
    "厨房用品 > 炊具 > 多功能刀": "厨房用品 > 炊具 > 刀具",
    "厨房用品 > 炊具 > 三德刀": "厨房用品 > 炊具 > 刀具",
    "厨房用品 > 炊具 > 磨刀石": "厨房用品 > 炊具 > 刀具",
    "厨房用品 > 炊具 > 平底锅": "厨房用品 > 炊具 > 平底锅/煎锅",
    "厨房用品 > 炊具 > 煎锅": "厨房用品 > 炊具 > 平底锅/煎锅",
    "厨房用品 > 炊具 > 汤锅": "厨房用品 > 炊具 > 汤锅/炖锅",
    "厨房用品 > 炊具 > 炖锅": "厨房用品 > 炊具 > 汤锅/炖锅",
    "厨房用品 > 炊具 > 锅盖": "厨房用品 > 炊具 > 锅具",
    "厨房用品 > 炊具 > 蒸笼": "厨房用品 > 炊具 > 锅具",
    "厨房用品 > 炊具 > 烧烤用具": "厨房用品 > 炊具 > 烤架/烧烤",
    "厨房用品 > 炊具 > 炉具配件": "厨房用品 > 炊具 > 烤架/烧烤",
    "厨房用品 > 炊具 > 砧板": "厨房用品 > 炊具 > 切菜板",
    "厨房用品 > 炊具 > 漏勺": "厨房用品 > 炊具 > 滤网/漏勺",
    "厨房用品 > 炊具 > 开罐器": "厨房用品 > 炊具 > 开瓶器/开罐器",
    "厨房用品 > 炊具 > 厨房夹": "厨房用品 > 炊具 > 厨房工具",
    "厨房用品 > 炊具 > 调味架套装": "厨房用品 > 炊具 > 厨具套装",
    "厨房用品 > 炊具 > 胡椒研磨器": "厨房用品 > 炊具 > 厨房工具",
    "厨房用品 > 炊具 > 油醋瓶": "厨房用品 > 炊具 > 厨房工具",
    "厨房用品 > 炊具 > 去核器": "厨房用品 > 炊具 > 厨房工具",
    "厨房用品 > 炊具 > 切薯器": "厨房用品 > 炊具 > 切菜器",
    "厨房用品 > 炊具 > 厨房秤": "厨房用品 > 炊具 > 厨房工具",
    "厨房用品 > 炊具 > 喷枪": "厨房用品 > 炊具 > 厨房工具",
    "厨房用品 > 炊具 > 隔热手套": "厨房用品 > 炊具 > 厨房工具",
    "厨房用品 > 炊具 > 其他炊具": "厨房用品 > 炊具 > 烹饪工具",
    "厨房用品 > 餐具 > 茶杯杯子": "厨房用品 > 餐具 > 杯子",
    "厨房用品 > 餐具 > 茶饮配件": "厨房用品 > 餐具 > 茶具水具",
    "厨房用品 > 餐具 > 饮料器": "厨房用品 > 餐具 > 壶/水罐",
    "厨房用品 > 餐具 > 竹制餐勺": "厨房用品 > 餐具 > 刀叉勺",
    "厨房用品 > 餐具 > 竹筷": "厨房用品 > 餐具 > 筷子",
    "厨房用品 > 餐具 > 竹餐具": "厨房用品 > 餐具 > 竹制套装",
    "厨房用品 > 餐具 > 不锈钢碗": "厨房用品 > 餐具 > 碗/盆",
    "厨房用品 > 餐具 > 餐碗盘": "厨房用品 > 餐具 > 盘子",
    "厨房用品 > 餐具 > 西餐盘": "厨房用品 > 餐具 > 盘子",
    "厨房用品 > 餐具 > 不锈钢餐盘": "厨房用品 > 餐具 > 不锈钢盘",
    "厨房用品 > 餐具 > 面包篮": "厨房用品 > 餐具 > 果盘",
    "厨房用品 > 餐具 > 糖果盒/零食盒": "厨房用品 > 餐具 > 果盘",
    "厨房用品 > 餐具 > 玻璃转盘": "厨房用品 > 餐具 > 盘子",
    "厨房用品 > 餐具 > 竹制托盘": "厨房用品 > 餐具 > 托盘",
    "厨房用品 > 餐具 > 双层饭盒": "厨房用品 > 餐具 > 分格饭盒",
    "厨房用品 > 餐具 > 桌布": "厨房用品 > 餐具 > 桌布餐垫",
    "厨房用品 > 餐具 > 封口夹": "厨房用品 > 餐具 > 夹子",
    "厨房用品 > 餐饮水具 > 保温壶/保温杯": "厨房用品 > 餐饮水具 > 保温杯",
    "厨房用品 > 餐饮水具 > 保温瓶": "厨房用品 > 餐饮水具 > 保温杯",
    "厨房用品 > 餐饮水具 > 玻璃杯": "厨房用品 > 餐饮水具 > 玻璃杯/保温杯",
    "厨房用品 > 餐饮水具 > 塑料水壶": "厨房用品 > 餐饮水具 > 水瓶/水壶",
    "厨房用品 > 餐饮水具 > 茶杯碟套装": "厨房用品 > 餐饮水具 > 茶杯杯子",
    "厨房用品 > 餐饮水具 > 摩卡壶": "厨房用品 > 餐饮水具 > 咖啡器具",
    "厨房用品 > 餐饮水具 > 酒瓶": "厨房用品 > 餐饮水具 > 酒具",
    "厨房用品 > 餐饮水具 > 调酒器具": "厨房用品 > 餐饮水具 > 酒具",
    "厨房用品 > 餐饮水具 > 酒精": "厨房用品 > 餐饮水具 > 酒具",
    "厨房用品 > 餐饮水具 > 厨房工具": "厨房用品 > 餐饮水具 > 茶饮配件",
    "厨房用品 > 餐饮水具 > 冰格": "厨房用品 > 餐饮水具 > 茶饮配件",
    "宠物 > 宠物用品 > 便携宠物碗": "宠物 > 宠物用品 > 宠物食具",
    "宠物 > 宠物用品 > 宠物护理": "宠物 > 宠物用品 > 宠物护理/玩具",
    "宠物 > 宠物用品 > 牵引绳/项圈": "宠物 > 宠物用品 > 宠物用品",
    "家居生活 > 个人防护 > 创可贴/纱布": "家居生活 > 个人防护 > 防护用品",
    "家居生活 > 卫浴用品 > 热水袋": "家居生活 > 卫浴用品 > 其他卫浴",
    "家居生活 > 卫浴用品 > 浴帽": "家居生活 > 卫浴用品 > 沐浴用品",
    "家居生活 > 卫浴用品 > 防滑地垫": "家居生活 > 卫浴用品 > 浴室地垫",
    "家居生活 > 卫浴用品 > 防滑垫": "家居生活 > 卫浴用品 > 浴室地垫",
    "家居生活 > 卫浴用品 > 毛巾": "家居生活 > 卫浴用品 > 毛巾套装",
    "家居生活 > 园艺户外 > 风车装饰": "家居生活 > 园艺户外 > 园艺工具",
    "家居生活 > 家具 > 凳子": "家居生活 > 家具 > 椅子",
    "家居生活 > 家具 > 衣帽架": "家居生活 > 家具 > 置物架",
    "家居生活 > 家纺毛巾 > 家纺": "家居生活 > 家纺毛巾 > 毯子/床品",
    "家居生活 > 家纺毛巾 > 其他家纺": "家居生活 > 家纺毛巾 > 毯子/床品",
    "家居生活 > 家纺毛巾 > 枕头/枕套": "家居生活 > 家纺毛巾 > 靠垫抱枕",
    "家居生活 > 家纺毛巾 > 旅行枕": "家居生活 > 家纺毛巾 > 靠垫抱枕",
    "家居生活 > 家纺毛巾 > 眼罩": "家居生活 > 家纺毛巾 > 睡眠眼罩",
    "家居生活 > 收纳整理 > 亚克力收纳": "家居生活 > 收纳整理 > 收纳盒",
    "家居生活 > 收纳整理 > 急救箱": "家居生活 > 收纳整理 > 收纳盒",
    "家居生活 > 收纳整理 > 多功能收纳": "家居生活 > 收纳整理 > 收纳盒",
    "家居生活 > 收纳整理 > 收纳筐": "家居生活 > 收纳整理 > 收纳篮",
    "家居生活 > 收纳整理 > 衣物收纳篮": "家居生活 > 收纳整理 > 收纳篮",
    "家居生活 > 收纳整理 > 网眼收纳袋": "家居生活 > 收纳整理 > 收纳工具",
    "家居生活 > 收纳整理 > 压缩袋": "家居生活 > 收纳整理 > 收纳工具",
    "家居生活 > 收纳整理 > 清洁抹布": "家居生活 > 收纳整理 > 收纳工具",
    "家居生活 > 收纳整理 > 鞋架": "家居生活 > 收纳整理 > 收纳架",
    "家居生活 > 收纳整理 > 浴帘杆": "家居生活 > 收纳整理 > 收纳架",
    "家居生活 > 收纳整理 > 衣架挂钩": "家居生活 > 收纳整理 > 挂钩/衣架",
    "家居生活 > 收纳整理 > 衣帽架": "家居生活 > 收纳整理 > 挂钩/衣架",
    "家居生活 > 日用杂货 > 日用小百货": "家居生活 > 日用杂货 > 其他杂货",
    "家居生活 > 日用杂货 > 烟灰缸": "家居生活 > 日用杂货 > 其他杂货",
    "家居生活 > 日用杂货 > 驱蚊用品": "家居生活 > 日用杂货 > 其他杂货",
    "家居生活 > 日用杂货 > 汽车用品": "家居生活 > 日用杂货 > 其他杂货",
    "家居生活 > 日用杂货 > 晾衣夹": "家居生活 > 日用杂货 > 晾衣架",
    "家居生活 > 日用杂货 > 火机/火柴/燃料": "家居生活 > 日用杂货 > 打火机",
    "家居生活 > 清洁用品 > 水桶垃圾桶": "家居生活 > 清洁用品 > 垃圾袋/垃圾桶",
    "家居生活 > 清洁用品 > 玻璃刮": "家居生活 > 清洁用品 > 清洁工具",
    "家居生活 > 清洁用品 > 清洁手套": "家居生活 > 清洁用品 > 清洁工具",
    "家居生活 > 清洁用品 > 门垫": "家居生活 > 清洁用品 > 其他清洁",
    "摆件礼品 > 派对节庆 > 圣诞彩灯": "摆件礼品 > 派对节庆 > 圣诞装饰",
    "摆件礼品 > 派对节庆 > 圣诞老人": "摆件礼品 > 派对节庆 > 圣诞装饰",
    "摆件礼品 > 派对节庆 > LED灯串": "摆件礼品 > 派对节庆 > 节庆灯饰",
    "摆件礼品 > 派对节庆 > 叶饰灯串": "摆件礼品 > 派对节庆 > 节庆灯饰",
    "摆件礼品 > 派对节庆 > 派对装饰": "摆件礼品 > 派对节庆 > 派对用品",
    "摆件礼品 > 派对节庆 > 万圣节": "摆件礼品 > 派对节庆 > 万圣节装饰",
    "摆件礼品 > 装饰摆件 > 装饰件": "摆件礼品 > 装饰摆件 > 装饰摆件",
    "摆件礼品 > 装饰摆件 > 水晶球": "摆件礼品 > 装饰摆件 > 装饰摆件",
    "摆件礼品 > 装饰摆件 > 自粘装饰膜": "摆件礼品 > 装饰摆件 > 装饰摆件",
    "摆件礼品 > 装饰摆件 > 冬季保暖": "摆件礼品 > 装饰摆件 > 装饰摆件",
    "摆件礼品 > 装饰摆件 > 夏季/水上": "摆件礼品 > 装饰摆件 > 装饰摆件",
    "摆件礼品 > 装饰摆件 > 毯子/抱枕": "摆件礼品 > 装饰摆件 > 装饰摆件",
    "摆件礼品 > 装饰摆件 > 地毯/地垫": "摆件礼品 > 装饰摆件 > 装饰摆件",
    "摆件礼品 > 装饰摆件 > 收纳整理": "摆件礼品 > 装饰摆件 > 收纳篮",
    "摆件礼品 > 装饰摆件 > 香薰扩散器": "摆件礼品 > 装饰摆件 > 香薰/加湿器",
    "摆件礼品 > 装饰摆件 > 户外装饰灯": "摆件礼品 > 装饰摆件 > LED装饰树",
    "文具 > 文具办公 > 创意笔": "文具 > 文具办公 > 笔类",
    "文具 > 文具办公 > 卡通圆珠笔": "文具 > 文具办公 > 圆珠笔",
    "文具 > 文具办公 > 金属圆珠笔": "文具 > 文具办公 > 圆珠笔",
    "文具 > 文具办公 > 蜡笔": "文具 > 文具办公 > 绘画用品",
    "文具 > 文具办公 > 风琴文件袋": "文具 > 文具办公 > 本册/文件夹",
    "文具 > 文具办公 > 弹力绑带本": "文具 > 文具办公 > 便携记事本",
    "文具 > 文具办公 > 弹性带本": "文具 > 文具办公 > 便携记事本",
    "文具 > 文具办公 > 周计划本": "文具 > 文具办公 > 便携记事本",
    "文具 > 文具办公 > 线圈本": "文具 > 文具办公 > 便携记事本",
    "文具 > 文具办公 > 方格本": "文具 > 文具办公 > 便携记事本",
    "文具 > 文具办公 > 商务笔记本": "文具 > 文具办公 > 便携记事本",
    "文具 > 文具办公 > 修正带": "文具 > 文具办公 > 修正工具",
    "文具 > 文具办公 > 惊喜橡皮": "文具 > 文具办公 > 橡皮擦",
    "文具 > 文具办公 > 文具包": "文具 > 文具办公 > 笔筒/笔袋",
    "文具 > 文具办公 > 胶棒": "文具 > 文具办公 > 胶水/胶带",
    "文具 > 文具办公 > 订书机": "文具 > 文具办公 > 办公文具",
    "文具 > 文具办公 > 白板/黑板": "文具 > 文具办公 > 办公文具",
    "文具 > 文具办公 > 磁吸本": "文具 > 文具办公 > 便签本",
    "文具 > 文具办公 > 印刷用品": "文具 > 文具办公 > 贴纸/标签",
    "文具 > 文具办公 > 热敏打印纸": "文具 > 文具办公 > 贴纸/标签",
    "文具 > 文具办公 > 热敏标签": "文具 > 文具办公 > 贴纸/标签",
    "服装鞋帽 > 服装服饰 > 鞋帽": "服装鞋帽 > 服装服饰 > 帽子",
    "服装鞋帽 > 服装服饰 > 巫师帽": "服装鞋帽 > 服装服饰 > 帽子",
    "服装鞋帽 > 服装服饰 > 女巫服饰": "服装鞋帽 > 服装服饰 > 雨衣/外套",
    "服装鞋帽 > 服装服饰 > 睡衣": "服装鞋帽 > 服装服饰 > 内衣",
    "服装鞋帽 > 服装服饰 > 套装": "服装鞋帽 > 服装服饰 > 雨衣/外套",
    "服装鞋帽 > 服装服饰 > 裤子": "服装鞋帽 > 服装服饰 > 内衣",
    "服装鞋帽 > 鞋履护理 > 鞋配件": "服装鞋帽 > 鞋履护理 > 鞋带",
    "服装鞋帽 > 鞋履护理 > 鞋套": "服装鞋帽 > 鞋履护理 > 鞋带",
    "母婴用品 > 婴幼儿用品 > 儿童用品": "母婴用品 > 婴幼儿用品 > 婴幼儿用品",
    "母婴用品 > 婴幼儿用品 > 婴儿用品": "母婴用品 > 婴幼儿用品 > 婴幼儿用品",
    "母婴用品 > 婴幼儿用品 > 婴儿毛巾": "母婴用品 > 婴幼儿用品 > 婴幼儿用品",
    "母婴用品 > 婴幼儿用品 > 儿童饭盒": "母婴用品 > 婴幼儿用品 > 儿童餐具",
    "母婴用品 > 婴幼儿用品 > 奶嘴/牙胶": "母婴用品 > 婴幼儿用品 > 奶瓶/奶嘴",
    "玩具 > 玩具游戏 > 积木/拼装": "玩具 > 玩具游戏 > 拼装积木",
    "玩具 > 玩具游戏 > 博彩游戏": "玩具 > 玩具游戏 > 桌游",
    "玩具 > 玩具游戏 > 记忆游戏": "玩具 > 玩具游戏 > 桌游",
    "玩具 > 玩具游戏 > 骰子游戏": "玩具 > 玩具游戏 > 桌游",
    "玩具 > 玩具游戏 > 贴纸书": "玩具 > 玩具游戏 > 手工DIY",
    "电子电器 > 小家电 > 其他小家电": "电子电器 > 小家电 > 小家电",
    "电子电器 > 小家电 > 健康秤": "电子电器 > 小家电 > 小家电",
    "电子电器 > 小家电 > 电热水壶": "电子电器 > 小家电 > 小家电",
    "电子电器 > 小家电 > 电池": "电子电器 > 小家电 > 小家电",
    "电子电器 > 小家电 > LED灯": "电子电器 > 小家电 > 小家电",
    "电子电器 > 数码配件 > 手机壳": "电子电器 > 数码配件 > 其他数码配件",
    "电子电器 > 数码配件 > 手机支架": "电子电器 > 数码配件 > 其他数码配件",
    "电子电器 > 数码配件 > 耳机": "电子电器 > 数码配件 > 其他数码配件",
    "电子电器 > 数码配件 > 体重秤": "电子电器 > 数码配件 > 其他数码配件",
    "电子电器 > 数码配件 > 智能手表": "电子电器 > 数码配件 > 其他数码配件",
    "电子电器 > 数码配件 > 门铃": "电子电器 > 数码配件 > 其他数码配件",
    "电子电器 > 数码配件 > 自拍杆": "电子电器 > 数码配件 > 其他数码配件",
    "电子电器 > 数码配件 > 音箱": "电子电器 > 数码配件 > 其他数码配件",
    "电子电器 > 照明灯具 > 床头灯": "电子电器 > 照明灯具 > 台灯/落地灯",
    "电子电器 > 照明灯具 > 水晶球灯": "电子电器 > 照明灯具 > 台灯/落地灯",
    "电子电器 > 照明灯具 > 吸顶灯": "电子电器 > 照明灯具 > LED灯",
    "箱包皮具 > 旅行用品 > 旅行手提袋": "箱包皮具 > 旅行用品 > 旅行包",
    "箱包皮具 > 旅行用品 > 购物车/行李箱": "箱包皮具 > 旅行用品 > 旅行包",
    "箱包皮具 > 旅行用品 > 旅行套装/其他": "箱包皮具 > 旅行用品 > 旅行收纳",
    "箱包皮具 > 旅行用品 > 眼罩": "箱包皮具 > 旅行用品 > 旅行枕",
    "箱包皮具 > 箱包配件 > 洗漱包": "箱包皮具 > 箱包配件 > 化妆品包",
    "箱包皮具 > 箱包配件 > 旅行洗漱包": "箱包皮具 > 箱包配件 > 化妆品包",
    "箱包皮具 > 箱包配件 > 印花化妆包": "箱包皮具 > 箱包配件 > 化妆品包",
    "箱包皮具 > 箱包配件 > 手提洗漱包": "箱包皮具 > 箱包配件 > 化妆品包",
    "箱包皮具 > 箱包配件 > 尼龙化妆包": "箱包皮具 > 箱包配件 > 化妆品包",
    "箱包皮具 > 箱包配件 > 牛津布洗漱包": "箱包皮具 > 箱包配件 > 化妆品包",
    "箱包皮具 > 箱包配件 > 单肩斜挎包": "箱包皮具 > 箱包配件 > 手提包/斜挎包",
    "箱包皮具 > 箱包配件 > 帆布手提袋": "箱包皮具 > 箱包配件 > 手提包/斜挎包",
    "箱包皮具 > 箱包配件 > 包袋": "箱包皮具 > 箱包配件 > 手提包/斜挎包",
    "箱包皮具 > 箱包配件 > 涤纶通勤包": "箱包皮具 > 箱包配件 > 手提包/斜挎包",
    "箱包皮具 > 箱包配件 > 灯芯绒挎包": "箱包皮具 > 箱包配件 > 手提包/斜挎包",
    "箱包皮具 > 箱包配件 > 零钱包": "箱包皮具 > 箱包配件 > 零钱包/腰包",
    "箱包皮具 > 箱包配件 > 短款钱包": "箱包皮具 > 箱包配件 > 零钱包/腰包",
    "箱包皮具 > 箱包配件 > 长款钱包": "箱包皮具 > 箱包配件 > 零钱包/腰包",
    "运动户外 > 运动健身 > 足球": "运动户外 > 运动健身 > 球类",
    "运动户外 > 运动健身 > 骑行/其他": "运动户外 > 运动健身 > 自行车",
    "运动户外 > 运动健身 > 跳绳": "运动户外 > 运动健身 > 健身器材",
    "运动户外 > 运动健身 > 儿童户外": "运动户外 > 运动健身 > 户外露营"
}

TEXT_SYSTEM_PROMPT = """你是一个专业的跨境百货商品多维分类API。输入商品列表（西班牙语/中文名称、SKU、品牌、原分类），输出严格的JSON分类结果。

分类规则：
1. 分类层级格式：一级 > 二级 > 三级（使用 " > " 分隔，两侧各一个空格）。
2. 【严格锁定分类库（核心铁律）】：你必须且只能从用户消息提供的【标准分类库】中选择已存在的完整三级路径！严禁自创任何不在【标准分类库】中的一级、二级或三级分类名称！如果标准三级名称中含有斜杠（如“便当盒/午餐盒”、“发夹/发卡”、“门吸/门塞”），必须原样完整输出，不得拆分！
3. 【多路径要求（核心重点）】：允许且强烈鼓励为每个商品从【标准分类库】中分配多个分类路径（建议每个商品分配 2~5 条并列的标准路径，排在第1条的作为主分类）！
   请从商品的【功能用途、使用场景、目标人群、材质形态、收纳/礼品/节庆属性】等多个维度，在【标准分类库】中尽可能多地挑选所有沾边的合理路径，确保采购员从不同分类目录筛选时都能找到该商品。
4. 常见阿根廷西语百货词汇提示：
   - ALFOMBRA / FELPUDO = 地毯/地垫/防滑垫（绝不是花盆）
   - ESCOBILLA DE BAÑO / INODORO = 马桶刷/卫浴清洁刷
   - MATE / BOMBILLA = 马黛茶杯/吸管（归入 厨房用品 > 餐饮水具 > 马黛茶具）
   - CONSERVADORA = 保温箱/冰桶（归入 运动户外 > 户外装备 > 保温箱、厨房用品 > 餐具 > 保温容器）
   - ADORNO = 装饰摆件/节日摆件
5. 视觉兜底规则：如果某商品的 name 仅为纯数字/货号/无意义代码，且无法从原分类或品牌推断具体是什么商品，请将该商品的 categories 设为空数组 []，并设置 "need_vision": true，交由视觉模型看图分类。

输出格式（严格JSON，不含Markdown代码块及任何多余文字）：
{"assignments":[{"id":12345,"categories":["标准路径1","标准路径2","标准路径3"],"need_vision":false}]}"""

VISION_SYSTEM_PROMPT = """你是一个专业的跨境百货商品视觉多维分类API。输入商品列表（包含商品图片、西班牙语名称、SKU、品牌），请结合【商品图片内容】与文字信息，输出严格的JSON分类结果。

分类规则：
1. 分类层级格式：一级 > 二级 > 三级（使用 " > " 分隔，两侧各一个空格）。
2. 【严格锁定分类库（核心铁律）】：你必须且只能从用户消息提供的【标准分类库】中选择已存在的完整三级路径！严禁自创任何不在【标准分类库】中的一级、二级或三级分类名称！如果标准三级名称中含有斜杠（如“便当盒/午餐盒”、“发夹/发卡”），必须原样完整输出！
3. 【多路径要求（核心重点）】：允许且强烈鼓励为每个商品从【标准分类库】中分配多个分类路径（建议每个商品分配 2~5 条并列路径，排在第1条的作为主分类）！
4. 请重点依据图片中展示的实际物品形态与名称判断，只要在【标准分类库】中合理相关，尽量多给路径（每个商品建议 2~5 条真实相关的标准路径）。

输出格式（严格JSON，不含Markdown代码块及任何多余文字）：
{"assignments":[{"id":12345,"categories":["标准路径1","标准路径2","标准路径3"]}]}"""


def get_db():
    return pymysql.connect(**DB_CONFIG)


def normalize_cat(cat: str) -> str:
    if not cat:
        return ""
    cat = re.sub(r'\s*>\s*', ' > ', cat.strip())
    parts = [p.strip() for p in cat.split(' > ') if p.strip()]
    if len(parts) > 3:
        parts = parts[:3]
    if len(parts) >= 2 and (parts[0], parts[1]) in L2_MERGE_MAP:
        parts[1] = L2_MERGE_MAP[(parts[0], parts[1])]
    return ' > '.join(parts)


def resolve_to_standard_cat(cat: str) -> str:
    """将AI输出的分类路径严格对齐到 487 条标准分类库；若无法对齐则拒绝（返回None）"""
    nc = normalize_cat(cat)
    if not nc or ' > ' not in nc:
        return None
    if nc in ALLOWED_SET:
        return nc
    if nc in EXACT_SYNONYM_MAP and EXACT_SYNONYM_MAP[nc] in ALLOWED_SET:
        return EXACT_SYNONYM_MAP[nc]

    parts = nc.split(" > ")
    l1 = parts[0]
    if l1 not in BY_L1:
        return None

    if len(parts) == 2:
        target_l3 = parts[1]
        for std_l2, std_l3, full_c in BY_L1[l1]:
            if target_l3 == std_l3 or target_l3 in std_l3.split("/"):
                return full_c
        return None

    l2, l3 = parts[1], parts[2]
    if (l1, l2) in BY_L1_L2:
        for std_l3, full_c in BY_L1_L2[(l1, l2)]:
            if l3 == std_l3 or l3 in std_l3.split("/"):
                return full_c
        for std_l3, full_c in BY_L1_L2[(l1, l2)]:
            if len(l3) >= 2 and l3 != "其他" and (l3 in std_l3 or std_l3 in l3):
                return full_c

    for std_l2, std_l3, full_c in BY_L1[l1]:
        if l3 == std_l3 or l3 in std_l3.split("/"):
            return full_c

    return None


def load_category_summary() -> str:
    """将 487 条标准分类按【一级 > 二级】组织，三级之间用顿号 '、' 分隔，避免与名称内的 '/' 冲突"""
    lines = []
    for (l1, l2), items in sorted(BY_L1_L2.items()):
        l3_names = "、".join(sorted(l3 for l3, _ in items))
        lines.append(f"【{l1} > {l2}】可选三级：{l3_names}")
    return "\n".join(lines)


def load_processed_ids() -> set:
    if not os.path.exists(PROCESSED_FILE):
        return set()
    ids = set()
    with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.isdigit():
                ids.add(int(line))
    return ids


def fetch_pending_products(processed_ids: set, limit: int = None) -> list:
    conn = get_db()
    cur = conn.cursor(pymysql.cursors.DictCursor)
    cur.execute("""
        SELECT p.id, p.supplier_id, p.name, p.sku, p.brand, p.category, p.image_local
        FROM suppliers s
        JOIN products p ON p.supplier_id = s.id
        WHERE s.is_active = 1 AND p.is_available = 1 AND p.is_missing = 0
        ORDER BY p.id ASC
    """)
    rows = cur.fetchall()
    conn.close()

    pending = []
    for r in rows:
        if r['id'] in processed_ids:
            continue
        cat = (r['category'] or '').strip()
        if not cat:
            prio = 0
        elif not re.search(r'[\u4e00-\u9fff]', cat):
            prio = 1
        elif ' > ' not in cat:
            prio = 2
        else:
            prio = 3
        r['_prio'] = prio
        pending.append(r)

    pending.sort(key=lambda x: (x['_prio'], x['id']))
    if limit:
        pending = pending[:limit]
    return pending


def parse_json_response(content: str):
    if not content:
        return None
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        start = content.find('{')
        end = content.rfind('}')
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(content[start:end + 1])
            except Exception:
                pass
    return None


def call_glm_api(model: str, messages: list, max_tokens: int = 5500) -> dict:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }
    payload = {
        "model": model,
        "messages": messages,
        "thinking": {"type": "disabled"},
        "temperature": 0.2,
        "max_tokens": max_tokens
    }
    for attempt in range(1, 9):
        try:
            resp = requests.post(API_URL, json=payload, headers=headers, timeout=85)
            if resp.status_code == 200:
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                parsed = parse_json_response(content)
                if parsed and "assignments" in parsed:
                    return parsed
                print(f"  [{model}] JSON解析失败 (attempt {attempt}), 前150字: {str(content)[:150]}", flush=True)
            elif resp.status_code == 429:
                wait_s = min(35, 4 * attempt)
                print(f"  [{model}] HTTP 429 限流 (attempt {attempt}), 等待 {wait_s}s...", flush=True)
                time.sleep(wait_s)
                continue
            else:
                print(f"  [{model}] HTTP {resp.status_code}: {resp.text[:180]}", flush=True)
        except Exception as e:
            print(f"  [{model}] 请求异常 (attempt {attempt}): {e}", flush=True)
        time.sleep(2 * attempt)
    return None


def encode_image_thumbnail(rel_path: str, max_side: int = 384) -> str:
    if not rel_path:
        return None
    full_path = os.path.join(IMAGE_BASE, rel_path)
    if not os.path.exists(full_path):
        return None
    try:
        with Image.open(full_path) as im:
            im = im.convert("RGB")
            im.thumbnail((max_side, max_side), Image.Resampling.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, format="JPEG", quality=80)
            b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
            return f"data:image/jpeg;base64,{b64}"
    except Exception:
        return None


def classify_text_batch(model: str, batch: list, cat_summary: str) -> dict:
    items_payload = []
    for p in batch:
        item = {"id": p["id"], "name": p["name"] or ""}
        if p.get("sku"):
            item["sku"] = p["sku"]
        if p.get("brand"):
            item["brand"] = p["brand"]
        if p.get("category"):
            item["raw_category"] = p["category"]
        items_payload.append(item)

    user_text = (
        f"【标准分类库】（必须严格从以下组合中选择完整三级路径 `一级 > 二级 > 三级`，严禁自创名称）：\n{cat_summary}\n\n"
        f"待分类商品列表（共{len(items_payload)}条，请为每条商品选择 2~5 条合理的标准分类路径）：\n"
        f"{json.dumps(items_payload, ensure_ascii=False)}\n\n"
        f"只输出严格JSON："
    )
    messages = [
        {"role": "system", "content": TEXT_SYSTEM_PROMPT},
        {"role": "user", "content": user_text}
    ]
    return call_glm_api(model, messages, max_tokens=5500)


def classify_vision_batch(batch: list, cat_summary: str) -> dict:
    content_parts = [
        {
            "type": "text",
            "text": f"【标准分类库】（必须严格从以下组合中选择完整三级路径 `一级 > 二级 > 三级`，严禁自创名称）：\n{cat_summary}\n\n待分类商品列表（共{len(batch)}条，请结合图片与名称为每条商品输出2~5条标准分类路径）：\n"
        }
    ]
    for p in batch:
        desc = f"--- 商品 id={p['id']} ---\n名称: {p.get('name') or ''}\nSKU: {p.get('sku') or ''}"
        if p.get("category"):
            desc += f"\n原分类: {p['category']}"
        content_parts.append({"type": "text", "text": desc})
        data_uri = encode_image_thumbnail(p.get("image_local"))
        if data_uri:
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": data_uri}
            })
        else:
            content_parts.append({"type": "text", "text": "(无可用图片，请根据名称与SKU尽可能推断分类)"})

    content_parts.append({"type": "text", "text": "\n只输出严格JSON："})
    messages = [
        {"role": "system", "content": VISION_SYSTEM_PROMPT},
        {"role": "user", "content": content_parts}
    ]
    return call_glm_api("glm-4.6v-flash", messages, max_tokens=3000)


def save_assignments_to_db(batch_map: dict, assignments: list) -> tuple:
    conn = get_db()
    cur = conn.cursor()
    saved_pids = []
    total_paths_written = 0
    need_vision_items = []

    for a in assignments:
        pid = a.get("id")
        if not pid or pid not in batch_map:
            continue
        p = batch_map[pid]
        raw_cats = a.get("categories") or []
        need_vis = bool(a.get("need_vision"))

        valid_cats = []
        for c in raw_cats:
            std_c = resolve_to_standard_cat(c)
            if std_c and std_c not in valid_cats:
                valid_cats.append(std_c)

        # 如果原本就有合法的标准三级中文分类，确保保留在列表第1位
        orig_std = resolve_to_standard_cat(p.get("category") or "")
        if orig_std and orig_std not in valid_cats:
            valid_cats.insert(0, orig_std)

        if (need_vis or not valid_cats) and p.get("image_local") and not p.get("_vision_tried"):
            p["_vision_tried"] = True
            need_vision_items.append(p)
            continue

        if not valid_cats:
            continue

        # 清理该商品在 product_categories 中的旧分类，仅写入通过标准分类白名单校验的路径
        cur.execute("DELETE FROM product_categories WHERE product_id=%s", (pid,))

        for vc in valid_cats:
            cur.execute(
                "INSERT IGNORE INTO product_categories (product_id, category) VALUES (%s, %s)",
                (pid, vc)
            )
            total_paths_written += cur.rowcount

        # 如果原主分类不在标准三级库中，则更新为第1条标准主分类（保持 updated_at 不变）
        primary_cat = valid_cats[0]
        if not orig_std:
            cur.execute(
                "UPDATE products SET category=%s, updated_at=updated_at WHERE id=%s",
                (primary_cat, pid)
            )

        saved_pids.append(pid)

    conn.commit()
    conn.close()
    return saved_pids, total_paths_written, need_vision_items


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="限制处理商品数（0表示全部）")
    args = parser.parse_args()

    os.makedirs(CACHE_DIR, exist_ok=True)
    cat_summary = load_category_summary()
    processed_ids = load_processed_ids()

    pending = fetch_pending_products(processed_ids, limit=args.limit if args.limit > 0 else None)
    total_pending = len(pending)
    print(f"============================================================", flush=True)
    print(f"启动全库多路径分类 [严格锁定标准分类库: {len(ALLOWED_SET)} 条路径]", flush=True)
    print(f"已完成商品数: {len(processed_ids)} | 本次待处理商品数: {total_pending}", flush=True)
    prio_counts = {0: 0, 1: 0, 2: 0, 3: 0}
    for p in pending:
        prio_counts[p['_prio']] = prio_counts.get(p['_prio'], 0) + 1
    print(f"优先级分布: P0无分类={prio_counts[0]}, P1西语分类={prio_counts[1]}, P2单级分类={prio_counts[2]}, P3补多路径={prio_counts[3]}", flush=True)
    print(f"============================================================", flush=True)

    if total_pending == 0:
        print("所有在库商品均已处理完毕！", flush=True)
        return

    text_q = queue.Queue()
    vision_q = queue.Queue()

    batches = [pending[i:i + TEXT_BATCH_SIZE] for i in range(0, total_pending, TEXT_BATCH_SIZE)]
    for idx, b in enumerate(batches, 1):
        text_q.put((idx, b))

    lock = threading.Lock()
    stats = {
        "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "initial_done": len(processed_ids),
        "total_target": len(processed_ids) + total_pending,
        "session_done_products": 0,
        "session_new_paths": 0,
        "session_batches_done": 0,
        "total_batches": len(batches),
        "vision_resolved": 0,
        "failed_batches": 0,
    }

    def record_done(pids: list, new_paths: int, batch_tag: str, assignments: list, model_used: str, is_vision: bool = False):
        with lock:
            if pids:
                with open(PROCESSED_FILE, "a", encoding="utf-8") as f:
                    for pid in pids:
                        f.write(f"{pid}\n")
            stats["session_done_products"] += len(pids)
            stats["session_new_paths"] += new_paths
            if is_vision:
                stats["vision_resolved"] += len(pids)
            else:
                stats["session_batches_done"] += 1
            stats["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            stats["total_done"] = stats["initial_done"] + stats["session_done_products"]

            cache_file = os.path.join(CACHE_DIR, f"batch_{batch_tag}.json")
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump({
                    "batch_tag": batch_tag,
                    "model": model_used,
                    "timestamp": stats["updated_at"],
                    "saved_count": len(pids),
                    "new_paths": new_paths,
                    "assignments": assignments
                }, f, ensure_ascii=False, indent=2)

            with open(STATUS_FILE, "w", encoding="utf-8") as f:
                json.dump(stats, f, ensure_ascii=False, indent=2)

            pct = (stats["total_done"] / max(1, stats["total_target"])) * 100
            print(
                f"[{stats['updated_at']}] [{model_used}] Batch {batch_tag}: "
                f"+{len(pids)}商品 (+{new_paths}标准路径) | "
                f"总进度: {stats['total_done']}/{stats['total_target']} ({pct:.1f}%)",
                flush=True
            )

    def worker_loop(model_name: str, is_vision_worker: bool):
        v_counter = 0
        while True:
            if is_vision_worker and not vision_q.empty():
                v_batch = []
                while len(v_batch) < VISION_BATCH_SIZE:
                    try:
                        v_batch.append(vision_q.get_nowait())
                    except queue.Empty:
                        break
                if v_batch:
                    v_counter += 1
                    b_map = {p["id"]: p for p in v_batch}
                    res = classify_vision_batch(v_batch, cat_summary)
                    if res and "assignments" in res:
                        saved_pids, new_paths, _ = save_assignments_to_db(b_map, res["assignments"])
                        record_done(saved_pids, new_paths, f"vis_{v_counter:04d}", res["assignments"], model_name, is_vision=True)
                    for _ in v_batch:
                        vision_q.task_done()
                    time.sleep(1.2)
                    continue

            try:
                batch_idx, batch = text_q.get(timeout=2)
            except queue.Empty:
                if is_vision_worker and not vision_q.empty():
                    continue
                break

            b_map = {p["id"]: p for p in batch}
            res = classify_text_batch(model_name, batch, cat_summary)
            if res and "assignments" in res:
                saved_pids, new_paths, need_vis = save_assignments_to_db(b_map, res["assignments"])
                for vp in need_vis:
                    vision_q.put(vp)
                record_done(saved_pids, new_paths, f"{batch_idx:04d}", res["assignments"], model_name, is_vision=False)
            else:
                mid = max(1, len(batch) // 2)
                for sub_i, sub_b in enumerate([batch[:mid], batch[mid:]], 1):
                    if not sub_b:
                        continue
                    sub_map = {p["id"]: p for p in sub_b}
                    sub_res = classify_text_batch(model_name, sub_b, cat_summary)
                    if sub_res and "assignments" in sub_res:
                        saved_pids, new_paths, need_vis = save_assignments_to_db(sub_map, sub_res["assignments"])
                        for vp in need_vis:
                            vision_q.put(vp)
                        record_done(saved_pids, new_paths, f"{batch_idx:04d}_{sub_i}", sub_res["assignments"], model_name, is_vision=False)
                    else:
                        with lock:
                            stats["failed_batches"] += 1
                        print(f"  [ERROR] [{model_name}] Batch {batch_idx}_{sub_i} 最终失败", flush=True)

            text_q.task_done()
            time.sleep(1.2)

        while is_vision_worker and not vision_q.empty():
            v_batch = []
            while len(v_batch) < VISION_BATCH_SIZE:
                try:
                    v_batch.append(vision_q.get_nowait())
                except queue.Empty:
                    break
            if v_batch:
                v_counter += 1
                b_map = {p["id"]: p for p in v_batch}
                res = classify_vision_batch(v_batch, cat_summary)
                if res and "assignments" in res:
                    saved_pids, new_paths, _ = save_assignments_to_db(b_map, res["assignments"])
                    record_done(saved_pids, new_paths, f"vis_{v_counter:04d}", res["assignments"], model_name, is_vision=True)
                for _ in v_batch:
                    vision_q.task_done()
                time.sleep(1.2)

    t1 = threading.Thread(target=worker_loop, args=("glm-4.7-flash", False), name="Worker-4.7-flash")
    t2 = threading.Thread(target=worker_loop, args=("glm-4.6v-flash", True), name="Worker-4.6v-flash")
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    print("============================================================", flush=True)
    print(f"运行结束！本次处理商品: {stats['session_done_products']} | 新增分类路径: {stats['session_new_paths']}", flush=True)
    print("============================================================", flush=True)


if __name__ == "__main__":
    main()
