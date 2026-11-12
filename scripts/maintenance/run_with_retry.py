"""自动重试包装器 - 进程中断后自动重启 reclassify_multi_v3.py"""
import subprocess, sys, time, os

PYTHON = r"C:\Users\Administrator\AppData\Local\Programs\Python\Python311\python.exe"
SCRIPT = r"D:\projects\supplier_crawler\reclassify_multi_v3.py"
MAX_RETRIES = 50
RETRY_DELAY = 5

for attempt in range(1, MAX_RETRIES + 1):
    print(f"\n{'='*60}")
    print(f"自动重试 #{attempt} - {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    
    result = subprocess.run(
        [PYTHON, "-u", SCRIPT],
        cwd=r"D:\projects\supplier_crawler",
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
    
    print(f"\n退出码: {result.returncode}")
    
    # 检查是否全部完成
    cache_dir = r"D:\projects\supplier_crawler\classify_cache\multi_v3"
    if os.path.exists(cache_dir):
        batch_files = [f for f in os.listdir(cache_dir) if f.startswith("batch_") and f.endswith(".json")]
        print(f"当前缓存文件数: {len(batch_files)}")
        
        # 如果超过227批说明全部完成了
        if len(batch_files) >= 228:
            print("全部228批完成！退出自动重试。")
            break
    
    if attempt < MAX_RETRIES:
        print(f"等待 {RETRY_DELAY} 秒后重启...")
        time.sleep(RETRY_DELAY)
    else:
        print("达到最大重试次数，退出。")
