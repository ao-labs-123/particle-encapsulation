# src/factory.py

import uuid
from typing import List, Dict, Any
from src.particle import Particle

class ParticleFactory:
    @classmethod
    def from_log_json(cls, log_data: Dict[str, Any]) -> List[Particle]:
        """
        log.json (辞書型データ) を受け取り、
        解析結果に対応する Particle オブジェクトのリストを生成して返す
        """
        particles: List[Particle] = []

        # -------------------------------------------------------------
        # 1. Agent (主語) 粒子の抽出 (Stage 1 / Stage 2 から)
        # -------------------------------------------------------------
        stage1 = log_data.get("stage1", {})
        stage2 = log_data.get("stage2", {})
        
        # Stage 2 で解決された Agent があればそれを優先、無ければ Stage 1 を参照
        agent_label = stage2.get("resolved_agent") or stage1.get("agent")
        
        if agent_label:
            particles.append(
                Particle(
                    id=f"p_agent_{uuid.uuid4().hex[:6]}",
                    label=agent_label,
                    entity_type="Agent",
                    state="determined",
                    constraints=[stage1.get("process", "explicit_subject")],
                    properties={"decision": stage1.get("decision")}
                )
            )

        # -------------------------------------------------------------
        # 2. Stage 3 (因果関係: Cause / Effect) 粒子の抽出
        # -------------------------------------------------------------
        stage3 = log_data.get("stage3", {})
        structure = stage3.get("structure", {})

        if isinstance(structure, dict):
            # Cause (原因) 粒子の生成
            if "cause" in structure:
                particles.append(
                    Particle(
                        id=f"p_cause_{uuid.uuid4().hex[:6]}",
                        label=structure["cause"],
                        entity_type="Cause",
                        state="determined",
                        constraints=[stage3.get("process", "cause_effect_rule")]
                    )
                )
            
            # Effect (結果) 粒子の生成
            if "effect" in structure:
                particles.append(
                    Particle(
                        id=f"p_effect_{uuid.uuid4().hex[:6]}",
                        label=structure["effect"],
                        entity_type="Effect",
                        state="determined",
                        constraints=[stage3.get("process", "cause_effect_rule")]
                    )
                )

        return particles
