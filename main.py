# main.py

import json
import urllib.request
from src.factory import ParticleFactory

# テスト用の log.json の Raw URL
URL = "https://raw.githubusercontent.com/ao-labs-123/input-parser/main/data/log.json"



def main():
    print("Fetching log.json from GitHub...")
    with urllib.request.urlopen(URL) as response:
        log_data = json.loads(response.read().decode())
    
    # log.json から粒子群を生成！
    particles = ParticleFactory.from_log_json(log_data)
    
    print(f"\n--- Generated Particle Cloud ({len(particles)} particles) ---")
    for particle in particles:
        print(particle)

if __name__ == "__main__":
    main()
