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
        for item in log_data:
            stage1 = item.get("stage1") or {}
            stage2 = item.get("stage2") or {}
        
            # Stage 2 で解決された Agent があればそれを優先、無ければ Stage 1 を参照
            agent_label = stage2.get("resolved_agent") or stage1.get("agent")
            agent_particle_id = None
        
            if agent_label:
                agent_particle_id = f"p_agent_{uuid.uuid4().hex[:6]}"
                particles.append(
                    Particle(
                        id=agent_particle_id,
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
            stage3 = item.get("stage3") or {}
            structure = stage3.get("structure") or {}

            if isinstance(structure, dict):
                if agent_particle_id:
                    structure["agent_particle_id"] = agent_particle_id

                # Cause (原因) 粒子の生成
                if "cause" in structure:
                    cause_particle_id = f"p_cause_{uuid.uuid4().hex[:6]}"
                    structure["cause_particle_id"] = cause_particle_id
                    particles.append(
                        Particle(
                            id=cause_particle_id,
                            label=structure["cause"],
                            entity_type="Cause",
                            state="determined",
                            constraints=[stage3.get("process", "cause_effect_rule")]
                        )
                    )
            
                # Cause/Effect と Temporal/Manner の event を結果粒子として生成
                effect_label = structure.get("effect")
                if effect_label is None and structure.get("relation") in {"Temporal", "Manner"}:
                    effect_label = structure.get("event")

                if effect_label:
                    effect_particle_id = f"p_effect_{uuid.uuid4().hex[:6]}"
                    structure["effect_particle_id"] = effect_particle_id
                    particles.append(
                        Particle(
                            id=effect_particle_id,
                            label=effect_label,
                            entity_type="Effect",
                            state="determined",
                            constraints=[stage3.get("process", "cause_effect_rule")]
                        )
                    )

                relation = structure.get("relation")
                if relation in {"Temporal", "Manner"} and structure.get("context"):
                    context_particle_id = f"p_{relation.lower()}_{uuid.uuid4().hex[:6]}"
                    structure["context_particle_id"] = context_particle_id
                    structure[f"{relation.lower()}_particle_id"] = context_particle_id
                    particles.append(
                        Particle(
                            id=context_particle_id,
                            label=structure["context"],
                            entity_type=relation,
                            state="determined",
                            constraints=[stage3.get("process", "stage3_relation")],
                            properties={
                                "marker": structure.get("marker"),
                                "event": structure.get("event")
                            }
                        )
                    )

                if relation in {"Temporal", "Manner"} and structure.get("event"):
                    event_particle_id = f"p_event_{uuid.uuid4().hex[:6]}"
                    structure["event_particle_id"] = event_particle_id
                    particles.append(
                        Particle(
                            id=event_particle_id,
                            label=structure["event"],
                            entity_type="Event",
                            state="determined",
                            constraints=[stage3.get("process", "stage3_relation")]
                        )
                    )

            # -------------------------------------------------------------
            # 3. Stage 4 (関係節) 粒子の抽出
            # -------------------------------------------------------------
            stage4 = item.get("stage4") or {}
            stage4_process = stage4.get("process")
            if stage4_process and stage4_process != "Standard":
                stage4_result = stage4.get("result") or stage4.get("structure")
                particles.append(
                    Particle(
                        id=f"p_relative_clause_{uuid.uuid4().hex[:6]}",
                        label=stage4_process,
                        entity_type="RelativeClause",
                        state="determined",
                        constraints=[stage4_process],
                        properties={
                            "decision": stage4.get("decision"),
                            "result": stage4_result
                        }
                    )
                )

            # -------------------------------------------------------------
            # 4. Stage 5 (形態・カテゴリ) 粒子の抽出
            # -------------------------------------------------------------
            stage5 = item.get("stage5") or {}
            morphology = stage5.get("process")
            if morphology:
                particles.append(
                    Particle(
                        id=f"p_morphology_{uuid.uuid4().hex[:6]}",
                        label=morphology,
                        entity_type="Morphology",
                        state="determined",
                        constraints=[morphology],
                        properties={"result": stage5.get("result")}
                    )
                )

        return particles
