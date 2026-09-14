# src/particle.py

from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class Particle:
    id: str                         # 粒子の一意な識別子 (例: "p_agent_01")
    label: str                      # 概念や言葉のテキスト (例: "I", "you helped")
    entity_type: str                # 粒子の種別 (例: "Agent", "Cause", "Effect")
    state: str = "unspecified"      # 確定状態 ("determined" または "unspecified")
    constraints: List[str] = field(default_factory=list) # 制約ルールや条件
    properties: Dict[str, Any] = field(default_factory=dict) # 5W1H等の補足データ

    def __repr__(self) -> str:
        """print(particle) した時に見やすく表示するためのフォーマット"""
        return f"Particle(id='{self.id}', label='{self.label}', type='{self.entity_type}', state='{self.state}')"
