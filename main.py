# main.py

import json
import urllib.request
from src.factory import ParticleFactory

# 1. 別リポジトリの log.json のURLを指定
URL = "https://raw.githubusercontent.com/ao-labs-123/input-parser/main/log.json"

def main():
    # 2. ネット経由で log.json を取得
    print("Fetching log.json from GitHub...")
    with urllib.request.urlopen(URL) as response:
        log_data = json.loads(response.read().decode())
    
    # 3. 取得した辞書データを ParticleFactory に渡して粒子化！
    particles = ParticleFactory.from_log_json(log_data)
    
    # 4. 生成された粒子群を確認
    print(f"\n--- Generated Particles ({len(particles)}) ---")
    for p in particles:
        print(p)

if __name__ == "__main__":
    main()
