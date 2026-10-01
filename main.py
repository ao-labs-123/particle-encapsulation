import json
import sys
import urllib.request
from dataclasses import asdict
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.factory import ParticleFactory

# テスト用の log.json の Raw URL
URL = "https://raw.githubusercontent.com/ao-labs-123/input-parser/main/data/log.json"
LOCAL_FILE = "log.json"  # 保存先のローカルファイル名
PARTICLES_FILE = "particles.json"  # 粒子群の保存先


def main():
    print("Fetching log.json from GitHub...")

    # 1. GitHubからデータを取得
    with urllib.request.urlopen(URL) as response:
        raw_data = response.read().decode("utf-8")
        log_data = json.loads(raw_data)

    # 2. 粒子群を生成し、Stage 3 の構造に粒子IDを反映
    particles = ParticleFactory.from_log_json(log_data)

    # 3. IDを反映したログを保存
    with open(LOCAL_FILE, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

    print(f"Successfully saved to {LOCAL_FILE}!")

    with open(PARTICLES_FILE, "w", encoding="utf-8") as f:
        json.dump([asdict(p) for p in particles], f, ensure_ascii=False, indent=2)

    print(f"Successfully saved to {PARTICLES_FILE}!")
    print(f"\n--- Generated Particle Cloud ({len(particles)} particles) ---")
    for p in particles:
        print(p)


if __name__ == "__main__":
    main()
