# 供应商爬虫系统 — 谷歌云盘（Google Drive + GAS）保姆级实现规范

> **致后续执行的 AI 模型（重要指令）**：  
> 本文档已将所有环境路径、数据库表结构、SQL 语句、前后端完整代码模板全部验证完毕。**请严格按照本文档中的【任务 1】→【任务 2】→【任务 3】→【任务 4】顺序直接创建/修改对应文件，不要自行猜测表名或路径。**

---

## 零、 已验证的固定环境常量（直接硬编码使用，切勿修改）

| 参数项 | 已验证真实值 | 说明 |
| :--- | :--- | :--- |
| **项目根目录** | `d:\projects\supplier_crawler` | Windows 本地工作区 |
| **MySQL 连接参数** | `host=localhost, port=3306, user=root, password=admin123, database=supplier_crawler` | 见 `api/main.py` |
| **本地云盘同步目录** | `G:\我的云端硬盘\Supplier_Crawler_Cloud` | 已创建并挂载就绪 |
| **云盘主目录 Folder ID** | `1uM4bqickgGQjoAf7v1cdlJ16mDhMDvxP` | Google Drive 云端真实 ID |
| **云端网页应用线上地址** | `https://script.google.com/macros/s/AKfycbwhyUaIKBTL_sdtmnC5zOLBdOcVSyXcF02hbGk75a2oD51AXHAMWwERI1dBHgHFwF9d/exec` | 苹果/安卓/家里电脑访问网址 |
| **部署 Deployment ID** | `AKfycbwhyUaIKBTL_sdtmnC5zOLBdOcVSyXcF02hbGk75a2oD51AXHAMWwERI1dBHgHFwF9d` | Google Apps Script 部署 ID |
| **DriveFS 本地 SQLite 路径** | `C:\Users\Administrator\AppData\Local\Google\DriveFS\110723887289889288645\metadata_sqlite_db` | 只读模式打开可获取上传文件的云端 `fileId` |
| **DriveFS 未上传完的临时 ID 前缀** | `local-`（例如 `local-105`，注意是中划线 `-`） | 只有当 `items.id NOT LIKE 'local-%'` 时，才是已同步上云的真实 Google Drive `fileId` |

### 关键数据现状说明（已实测）：
- `products` 表共有约 `47,034` 条商品：
  1. **网页爬虫供应商（约 30,540 条）**：`image_url` 为公网 `https://...` 链接，`image_local` 为 `images/{supplier}/{md5}.jpg`。
  2. **PDF 导入供应商（约 15,231 条）**：`image_url` 为本地路径 `/images/{folder}/{file}.jpg`（无公网 URL），必须上传到 Google Drive 获取 `drive_file_id` 才能在外网手机/家里电脑显示图片！

---

## 任务 1：扩展 MySQL 数据库字段 (`database/db_manager.py`)

### 1.1 修改位置与具体代码
打开 [`database/db_manager.py`](file:///d:/projects/supplier_crawler/database/db_manager.py)，在第 `158-171` 行的 `init_schema(self)` 迁移列表中添加 `drive_file_id` 字段及索引：

```python
        # 迁移：补充字段（在 database/db_manager.py 第 166 行 sub_pack_qty 下方追加两行）
        for sql in [
            "ALTER TABLE suppliers ADD COLUMN cron_expr VARCHAR(50) DEFAULT '0 2 * * *'",
            "ALTER TABLE suppliers ADD COLUMN price_adjustment FLOAT DEFAULT 0",
            "ALTER TABLE suppliers ADD COLUMN use_chrome_cookies TINYINT(1) DEFAULT 0",
            "ALTER TABLE products ADD COLUMN unit VARCHAR(50) DEFAULT ''",
            "ALTER TABLE products ADD COLUMN min_qty INT DEFAULT 1",
            "ALTER TABLE products ADD COLUMN package_qty INT DEFAULT 1",
            "ALTER TABLE products ADD COLUMN sub_pack_qty INT DEFAULT 1",
            "ALTER TABLE products ADD COLUMN drive_file_id VARCHAR(64) DEFAULT NULL",
            "ALTER TABLE products ADD INDEX idx_drive_file_id (drive_file_id)",
        ]:
```

### 1.2 任务 1 验证命令
修改后运行以下命令确保字段已创建成功：
```powershell
$env:PYTHONPATH="."; $env:PYTHONIOENCODING="utf-8"; python -c "from database.db_manager import DatabaseManager; db=DatabaseManager('localhost',3306,'root','admin123','supplier_crawler'); db.init_schema(); print('OK')"
```

---

## 任务 2：创建本地云盘同步与编码器 (`scripts/cloud_sync.py`)

### 2.1 新建文件 `d:\projects\supplier_crawler\scripts\cloud_sync.py`
请直接将以下完整代码写入 `d:\projects\supplier_crawler\scripts\cloud_sync.py`：

```python
"""
scripts/cloud_sync.py
将本地 MySQL 商品数据库与图片增量同步至 Google Drive (G:\我的云端硬盘\Supplier_Crawler_Cloud)，
并从 DriveFS 本地 SQLite 库自动回填 Google Drive File ID，生成压缩编码包 catalog_db.dat。
"""
import os
import sys
import json
import gzip
import base64
import shutil
import sqlite3
import tempfile
from datetime import datetime

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from database.db_manager import DatabaseManager

CLOUD_DIR = r"G:\我的云端硬盘\Supplier_Crawler_Cloud"
CLOUD_IMG_DIR = os.path.join(CLOUD_DIR, "images")
DRIVEFS_DB_PATH = r"C:\Users\Administrator\AppData\Local\Google\DriveFS\110723887289889288645\metadata_sqlite_db"
CLOUD_FOLDER_ID = "1uM4bqickgGQjoAf7v1cdlJ16mDhMDvxP"


def get_db() -> DatabaseManager:
    return DatabaseManager(
        os.getenv("DB_HOST", "localhost"),
        int(os.getenv("DB_PORT", 3306)),
        os.getenv("DB_USER", "root"),
        os.getenv("DB_PASSWORD", "admin123"),
        os.getenv("DB_NAME", "supplier_crawler"),
    )


def resolve_local_image_path(image_local: str, image_url: str) -> str:
    """根据 products 表的 image_local 和 image_url 解析本地磁盘真实图片路径"""
    for rel in (image_local, image_url):
        if not rel or rel.startswith("http://") or rel.startswith("https://"):
            continue
        clean_rel = rel.lstrip("/\\").replace("/", os.sep)
        full_path = os.path.join(ROOT_DIR, clean_rel)
        if os.path.isfile(full_path):
            return full_path
    return ""


def harvest_drive_file_ids(db: DatabaseManager) -> int:
    """
    从 Google Drive 桌面版 (DriveFS) 本地 SQLite 数据库读取已上传成功的图片云端 fileId，
    图片在云盘中的命名格式固定为：p_{product_id}.jpg
    注意：必须过滤 id NOT LIKE 'local-%'（未上传完的临时 ID 以 'local-' 开头）。
    """
    if not os.path.exists(DRIVEFS_DB_PATH):
        print(f"[WARN] 未找到 DriveFS 数据库: {DRIVEFS_DB_PATH}")
        return 0

    tmp_db = tempfile.mktemp(suffix=".db")
    try:
        shutil.copy2(DRIVEFS_DB_PATH, tmp_db)
        con = sqlite3.connect(tmp_db)
        cur = con.cursor()
        cur.execute("""
            SELECT local_title, id
            FROM items
            WHERE trashed = 0
              AND is_folder = 0
              AND local_title LIKE 'p_%'
              AND id NOT LIKE 'local-%'
        """)
        rows = cur.fetchall()
        con.close()
    finally:
        if os.path.exists(tmp_db):
            try:
                os.remove(tmp_db)
            except OSError:
                pass

    id_map = []
    for title, cloud_id in rows:
        # 文件名格式: p_40345.jpg
        stem = os.path.splitext(title)[0]
        if stem.startswith("p_"):
            pid_str = stem[2:]
            if pid_str.isdigit():
                id_map.append((cloud_id, int(pid_str)))

    if not id_map:
        return 0

    updated = 0
    with db.connection() as conn:
        cursor = conn.cursor()
        # 分批更新那些 drive_file_id 为空或变化的记录
        batch_size = 1000
        for i in range(0, len(id_map), batch_size):
            batch = id_map[i : i + batch_size]
            cursor.executemany(
                "UPDATE products SET drive_file_id = %s WHERE id = %s AND (drive_file_id IS NULL OR drive_file_id != %s)",
                [(cid, pid, cid) for cid, pid in batch],
            )
            updated += cursor.rowcount
    return updated


def copy_missing_images_to_drive(db: DatabaseManager, max_copy: int = 2000) -> dict:
    """
    将尚未拥有 drive_file_id 的商品本地图片增量复制到 G:\我的云端硬盘\Supplier_Crawler_Cloud\images\{supplier_id}\p_{id}.jpg
    优先复制 PDF 供应商（无 http 外链图片的商品），再复制普通供应商。
    """
    os.makedirs(CLOUD_IMG_DIR, exist_ok=True)
    with db.connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("""
            SELECT id, supplier_id, sku, name, price, category, image_url, image_local
            FROM products
            WHERE is_available = 1
              AND (drive_file_id IS NULL OR drive_file_id = '')
              AND (image_local != '' OR image_url LIKE '/images/%')
            ORDER BY (image_url LIKE 'http%') ASC, id DESC
        """)
        candidates = cur.fetchall()

    copied = 0
    already_in_g = 0
    missing_disk = 0

    for p in candidates:
        if copied >= max_copy:
            break
        sup_dir = os.path.join(CLOUD_IMG_DIR, str(p["supplier_id"]))
        os.makedirs(sup_dir, exist_ok=True)
        target_file = os.path.join(sup_dir, f"p_{p['id']}.jpg")
        if os.path.exists(target_file):
            already_in_g += 1
            continue
        src_path = resolve_local_image_path(p.get("image_local") or "", p.get("image_url") or "")
        if not src_path:
            missing_disk += 1
            continue
        shutil.copy2(src_path, target_file)
        copied += 1

    return {
        "candidates": len(candidates),
        "copied_now": copied,
        "already_in_gdrive_folder": already_in_g,
        "missing_on_local_disk": missing_disk,
    }


def export_catalog_bundle(db: DatabaseManager) -> dict:
    """
    导出全量供应商、商品、以及待写备注的图片元数据到 G:\我的云端硬盘\Supplier_Crawler_Cloud：
    1. catalog_db.dat: Gzip + Base64 编码的紧凑型全量商品库
    2. image_descriptions.json: 供 Google Apps Script 为云盘图片写入 Description 备注（SKU/价格/品名）
    3. cloud_state.json: 若云端不存在则初始化购物车与收藏夹状态文件
    """
    os.makedirs(CLOUD_DIR, exist_ok=True)

    with db.connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, name, base_url, price_adjustment, is_active FROM suppliers WHERE is_active = 1 ORDER BY id")
        suppliers = cur.fetchall()

        cur.execute("""
            SELECT id, supplier_id, sku, name, category, price, unit, min_qty, package_qty,
                   image_url, product_url, is_available, drive_file_id
            FROM products
            ORDER BY supplier_id, id DESC
        """)
        products = cur.fetchall()

        cur.execute("SELECT product_id, quantity FROM cart_items")
        local_cart = {str(r["product_id"]): int(r["quantity"]) for r in cur.fetchall()}

        cur.execute("SELECT product_id FROM favorites")
        local_favs = [int(r["product_id"]) for r in cur.fetchall()]

    # Columnar 紧凑数组格式：大幅减小 JSON 体积
    # 字段顺序: [0:id, 1:sid, 2:sku, 3:name, 4:cat, 5:price, 6:pkg, 7:avail, 8:did, 9:img_http, 10:purl]
    fields = ["id", "sid", "sku", "name", "cat", "price", "pkg", "avail", "did", "img_http", "purl"]
    rows = []
    desc_items = []

    sup_map = {s["id"]: s["name"] for s in suppliers}

    for p in products:
        img_u = p["image_url"] or ""
        http_img = img_u if img_u.startswith("http") else ""
        did = p["drive_file_id"] or ""
        price_val = float(p["price"] or 0)
        rows.append([
            int(p["id"]),
            int(p["supplier_id"]),
            p["sku"] or "",
            p["name"] or "",
            p["category"] or "",
            price_val,
            int(p["package_qty"] or 1),
            int(p["is_available"] if p["is_available"] is not None else 1),
            did,
            http_img,
            p["product_url"] or "",
        ])
        if did:
            desc_items.append({
                "did": did,
                "desc": f"SKU: {p['sku'] or '-'} | 店铺: {sup_map.get(p['supplier_id'], '')} | 价格: ${price_val:,.2f} | 品名: {p['name']} | 分类: {p['category'] or '-'}"
            })

    version_ts = int(datetime.now().timestamp())
    payload = {
        "version": version_ts,
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "folder_id": CLOUD_FOLDER_ID,
        "suppliers": [
            {
                "id": int(s["id"]),
                "name": s["name"],
                "adj": float(s["price_adjustment"] or 0),
            }
            for s in suppliers
        ],
        "fields": fields,
        "rows": rows,
    }

    raw_json = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    compressed = gzip.compress(raw_json, compresslevel=9)
    b64_data = base64.b64encode(compressed).decode("ascii")

    dat_path = os.path.join(CLOUD_DIR, "catalog_db.dat")
    with open(dat_path, "w", encoding="ascii") as f:
        f.write(b64_data)

    # 写入元信息文件，方便 GAS 快速比对版本号
    meta_path = os.path.join(CLOUD_DIR, "catalog_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            "version": version_ts,
            "generated_at": payload["generated_at"],
            "total_products": len(rows),
            "total_suppliers": len(suppliers),
            "dat_size_kb": round(len(b64_data) / 1024, 1),
        }, f, ensure_ascii=False, indent=2)

    # 写入图片备注映射表（供 GAS 批量写云盘图片备注 Description）
    desc_path = os.path.join(CLOUD_DIR, "image_descriptions.json")
    with open(desc_path, "w", encoding="utf-8") as f:
        json.dump(desc_items[:3000], f, ensure_ascii=False)

    # 同步或初始化 cloud_state.json（购物车与收藏夹）
    state_path = os.path.join(CLOUD_DIR, "cloud_state.json")
    if not os.path.exists(state_path):
        with open(state_path, "w", encoding="utf-8") as f:
            json.dump({
                "updated_at": payload["generated_at"],
                "cart": local_cart,
                "favorites": local_favs,
            }, f, ensure_ascii=False, indent=2)

    return {
        "version": version_ts,
        "total_products": len(rows),
        "products_with_drive_id": len(desc_items),
        "dat_size_kb": round(len(b64_data) / 1024, 1),
        "dat_path": dat_path,
    }


def run_full_cloud_sync(max_copy: int = 2000) -> dict:
    db = get_db()
    db.init_schema()
    harvested_before = harvest_drive_file_ids(db)
    copy_stats = copy_missing_images_to_drive(db, max_copy=max_copy)
    harvested_after = harvest_drive_file_ids(db)
    bundle_stats = export_catalog_bundle(db)
    return {
        "harvested_drive_ids": harvested_before + harvested_after,
        "image_copy": copy_stats,
        "bundle": bundle_stats,
    }


if __name__ == "__main__":
    res = run_full_cloud_sync(max_copy=1000)
    print(json.dumps(res, ensure_ascii=False, indent=2))
```

### 2.2 任务 2 验证命令
运行以下命令测试同步并生成 `catalog_db.dat`：
```powershell
$env:PYTHONPATH="."; $env:PYTHONIOENCODING="utf-8"; python scripts/cloud_sync.py
```

---

## 任务 3：在后端 API 与前端面板挂载“一键同步云盘”按钮

### 3.1 在 [`api/main.py`](file:///d:/projects/supplier_crawler/api/main.py) 添加接口
在 `api/main.py` 末尾（约第 `1630` 行 `@app.on_event("startup")` 之前）添加以下两个接口：

```python
@app.post("/api/cloud/sync")
async def sync_to_google_drive(max_copy: int = 1500):
    """一键将数据库与新增图片同步到 Google Drive (G:\我的云端硬盘\Supplier_Crawler_Cloud)"""
    from scripts.cloud_sync import run_full_cloud_sync
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, run_full_cloud_sync, max_copy)
    return {"success": True, "data": result}

@app.post("/api/cloud/pull-cart")
async def pull_cart_from_google_drive():
    """从 Google Drive 的 cloud_state.json 拉取手机端修改的购物车与收藏夹到本地 MySQL"""
    from scripts.cloud_sync import CLOUD_DIR
    state_path = os.path.join(CLOUD_DIR, "cloud_state.json")
    if not os.path.exists(state_path):
        raise HTTPException(404, "云盘尚未生成 cloud_state.json")
    with open(state_path, "r", encoding="utf-8") as f:
        state = json.load(f)
    cart_dict = state.get("cart") or {}
    fav_list = state.get("favorites") or []
    with db.connection() as conn:
        cur = conn.cursor()
        for pid_str, qty in cart_dict.items():
            if int(qty) > 0:
                cur.execute(
                    "INSERT INTO cart_items (product_id, quantity) VALUES (%s, %s) ON DUPLICATE KEY UPDATE quantity=%s",
                    (int(pid_str), int(qty), int(qty))
                )
        for pid in fav_list:
            cur.execute("INSERT IGNORE INTO favorites (product_id) VALUES (%s)", (int(pid),))
    return {"success": True, "cart_synced": len(cart_dict), "favorites_synced": len(fav_list)}
```

---

## 任务 4：创建 Google Apps Script 云端解码器 (`cloud_app/`)

新建目录 `d:\projects\supplier_crawler\cloud_app\`，并在其中创建以下两个文件，供用户直接复制粘贴到浏览器打开的 **https://script.new** 中。

### 4.1 新建 `d:\projects\supplier_crawler\cloud_app\Code.gs`
请将以下完整代码写入 `d:\projects\supplier_crawler\cloud_app\Code.gs`：

```javascript
/**
 * Google Apps Script 云端解码服务 (Code.gs)
 * 绑定的 Google Drive 主目录: Supplier_Crawler_Cloud (1uM4bqickgGQjoAf7v1cdlJ16mDhMDvxP)
 */
const FOLDER_ID = '1uM4bqickgGQjoAf7v1cdlJ16mDhMDvxP';
const ACCESS_PIN = '8888'; // 默认访问PIN码，可自行修改

function doGet(e) {
  return HtmlService.createHtmlOutputFromFile('Index')
    .setTitle('云端商品与采购系统')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

function checkPin_(pin) {
  if (String(pin || '').trim() !== ACCESS_PIN) {
    throw new Error('PIN 密码错误');
  }
}

function getFileInFolder_(filename) {
  const folder = DriveApp.getFolderById(FOLDER_ID);
  const files = folder.getFilesByName(filename);
  return files.hasNext() ? files.next() : null;
}

/**
 * 1. 获取云盘数据库元信息与购物车状态（轻量级，每次打开页面秒调）
 */
function getCloudBootstrap(pin) {
  checkPin_(pin);
  let meta = { version: 0 };
  const metaFile = getFileInFolder_('catalog_meta.json');
  if (metaFile) {
    meta = JSON.parse(metaFile.getBlob().getDataAsString('UTF-8'));
  }
  let state = { cart: {}, favorites: [] };
  const stateFile = getFileInFolder_('cloud_state.json');
  if (stateFile) {
    state = JSON.parse(stateFile.getBlob().getDataAsString('UTF-8'));
  }
  return { meta: meta, state: state };
}

/**
 * 2. 拉取压缩编码的全量商品数据库 (catalog_db.dat)
 */
function getCatalogDat(pin) {
  checkPin_(pin);
  const datFile = getFileInFolder_('catalog_db.dat');
  if (!datFile) {
    throw new Error('云盘中尚未找到 catalog_db.dat，请先在电脑端运行 scripts/cloud_sync.py');
  }
  return datFile.getBlob().getDataAsString('ASCII');
}

/**
 * 3. 保存手机/家里电脑修改的购物车与收藏夹状态到云盘 cloud_state.json
 */
function saveCloudState(pin, stateJsonStr) {
  checkPin_(pin);
  const folder = DriveApp.getFolderById(FOLDER_ID);
  const existing = getFileInFolder_('cloud_state.json');
  if (existing) {
    existing.setContent(stateJsonStr);
  } else {
    folder.createFile('cloud_state.json', stateJsonStr, MimeType.PLAIN_TEXT);
  }
  return { ok: true, saved_at: new Date().toISOString() };
}

/**
 * 4. 后台工具函数：将商品备注 (SKU/价格/品名) 批量写入云盘图片的 Description 字段，
 *    并设置图片文件夹为“知道链接的人可查看”以确保苹果/安卓手机缩略图免登录直显。
 */
function syncImageDescriptionsBatch() {
  const folder = DriveApp.getFolderById(FOLDER_ID);
  const imgFolders = folder.getFoldersByName('images');
  if (imgFolders.hasNext()) {
    const imgRoot = imgFolders.next();
    imgRoot.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);
  }
  const descFile = getFileInFolder_('image_descriptions.json');
  if (!descFile) return 'No image_descriptions.json';
  const list = JSON.parse(descFile.getBlob().getDataAsString('UTF-8'));
  let count = 0;
  for (let i = 0; i < Math.min(list.length, 200); i++) {
    try {
      const f = DriveApp.getFileById(list[i].did);
      if (f.getDescription() !== list[i].desc) {
        f.setDescription(list[i].desc);
        count++;
      }
    } catch (e) {}
  }
  return 'Updated descriptions: ' + count;
}
```

### 4.2 新建 `d:\projects\supplier_crawler\cloud_app\Index.html`
请创建一个完整的单文件响应式前端 `d:\projects\supplier_crawler\cloud_app\Index.html`，必须包含以下完整特性：
1. 引入 `<script src="https://cdnjs.cloudflare.com/ajax/libs/pako/2.1.0/pako.min.js"></script>` 用于在浏览器端将 `catalog_db.dat`（Base64 -> Uint8Array -> `pako.inflate` -> UTF-8 JSON）解压还原为内存商品表。
2. **IndexedDB 本地持久化缓存**（库名 `SupplierCloudDB`，对象仓库 `cache`）：
   - 页面启动时先读 `IndexedDB` 中的 `catalog_payload`；若有缓存，**0.1 秒直接渲染商品列表**；
   - 同时调用 `google.script.run.withSuccessHandler(...).getCloudBootstrap(pin)` 获取云端最新 `meta.version` 与 `state`；
   - 若云端 `meta.version` 大于本地缓存的 `version`（或本地无缓存），自动调用 `getCatalogDat(pin)` 拉取最新数据包，解压后更新 `IndexedDB` 并刷新列表。
3. **图片智能降级渲染逻辑**：
   - 若商品有 `did`（即 `drive_file_id`），图片地址使用：`https://drive.google.com/thumbnail?id=${did}&sz=w500`；
   - 否则若商品有 `img_http`（公网 `http` 链接），使用 `img_http`；
   - 支持点击图片放大预览。
4. **核心功能交互（适配 iPhone Safari / 安卓 Chrome / 家里电脑）**：
   - 顶部栏：PIN 码锁（首次输入默认 `8888` 后保存在 `localStorage`）、供应商下拉选择、分类下拉选择、关键词搜索框（支持多词空格分词匹配 `sku` + `name`）、“仅看有货/全部”切换、批发折扣率/加价倍率输入框。
   - 底部悬浮栏 / 抽屉：当前购物车商品数与折后总金额，点击展开购物车明细（支持加减数量、按供应商分组复制下单文本、一键保存到云盘 `saveCloudState`）。

---

## 五、 最终交付检查清单（供执行模型自检）

完成上述 4 个任务后，请确认：
1. [ ] `database/db_manager.py` 中已包含 `drive_file_id` 迁移语句并执行成功。
2. [ ] `python scripts/cloud_sync.py` 已成功运行，`G:\我的云端硬盘\Supplier_Crawler_Cloud\catalog_db.dat` 和 `catalog_meta.json` 已生成。
3. [ ] `d:\projects\supplier_crawler\cloud_app\Code.gs` 和 `d:\projects\supplier_crawler\cloud_app\Index.html` 已生成完毕。
4. [ ] 向用户输出简单 3 步部署指引（打开 `https://script.new` -> 粘贴 `Code.gs` 与 `Index.html` -> 点击右上角“部署 -> 新建部署 -> 网页应用 -> 执行身份选‘我’，访问权限选‘任何人’” -> 获得苹果/安卓/家里电脑通用网址）。
