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
            # 1. Agent (主語) 粒子の抽出 (Stage1から)
            # -------------------------------------------------------------
        for item in log_data:
            stage1 = item.get("stage1") or {}
            stage2 = item.get("stage2") or {}

            agent_label = (
                stage2.get("resolved_agent")
                or stage2.get("agent")
                or stage1.get("resolved_agent")
                or stage1.get("agent")
            )
            agent_particle_id = None
        
            if agent_label:
                agent_state = (
                    "unspecified"
                    if str(agent_label).strip().casefold() in {"unknown", "unspecified"}
                    else "determined"
                )
                agent_particle_id = f"p_agent_{uuid.uuid4().hex[:6]}"
                particles.append(
                    Particle(
                        id=agent_particle_id,
                        label=agent_label,
                        entity_type="Agent",
                        state=agent_state,
                        constraints=[stage1.get("process", "explicit_subject")],
                        properties={"decision": stage1.get("decision")}
                    )
                )

            # -------------------------------------------------------------
            # 2. Stage 2 (因果関係: Cause / Effect) 粒子の抽出
            # -------------------------------------------------------------
            structure = stage2.get("structure") or {}

            if isinstance(structure, dict):
                relation = structure.get("relation")
                has_contextual_relation = relation in {"Temporal", "Manner"}

                if has_contextual_relation:
                    for particle_id_key in (
                        "agent_particle_id",
                        "effect_particle_id",
                        "event_particle_id",
                        "context_particle_id",
                        f"{relation.lower()}_particle_id",
                    ):
                        structure.pop(particle_id_key, None)
                elif agent_particle_id:
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
                            constraints=[stage2.get("process", "cause_effect_rule")]
                        )
                    )
            
                # Cause/Effect と Temporal/Manner の event を結果粒子として生成
                effect_label = structure.get("event") if has_contextual_relation else structure.get("effect")

                if effect_label:
                    effect_particle_id = f"p_effect_{uuid.uuid4().hex[:6]}"
                    if has_contextual_relation:
                        structure["event_particle_id"] = effect_particle_id
                    else:
                        structure["effect_particle_id"] = effect_particle_id
                    particles.append(
                        Particle(
                            id=effect_particle_id,
                            label=effect_label,
                            entity_type="Effect",
                            state="determined",
                            constraints=[stage2.get("process", "cause_effect_rule")]
                        )
                    )

                if has_contextual_relation and structure.get("context"):
                    context_particle_id = f"p_{relation.lower()}_{uuid.uuid4().hex[:6]}"
                    structure["context_particle_id"] = context_particle_id
                    particles.append(
                        Particle(
                            id=context_particle_id,
                            label=structure["context"],
                            entity_type=relation,
                            state="determined",
                            constraints=[stage2.get("process", "stage2_relation")],
                            properties={
                                "marker": structure.get("marker"),
                                "event": structure.get("event")
                            }
                        )
                    )

            # -------------------------------------------------------------
            # 3. Stage 3 (関係節) 粒子の抽出
            # -------------------------------------------------------------
            stage3 = item.get("stage3") or {}
            stage3_process = stage3.get("process")
            if stage3_process and stage3_process != "Standard":
                stage3_result = stage3.get("result") or stage3.get("structure")
                particles.append(
                    Particle(
                        id=f"p_relative_clause_{uuid.uuid4().hex[:6]}",
                        label=stage3_process,
                        entity_type="RelativeClause",
                        state="determined",
                        constraints=[stage3_process],
                        properties={
                            "decision": stage3.get("decision"),
                            "result": stage3_result
                        }
                    )
                )

            # -------------------------------------------------------------
            # 4. Stage 4 (形態・カテゴリ) 粒子の抽出
            # -------------------------------------------------------------
            stage4 = item.get("stage4") or {}
            morphology = stage4.get("process")
            if morphology:
                particles.append(
                    Particle(
                        id=f"p_morphology_{uuid.uuid4().hex[:6]}",
                        label=morphology,
                        entity_type="Morphology",
                        state="determined",
                        constraints=[morphology],
                        properties={"result": stage4.get("result") or stage4.get("structure")}
                    )
                )

            # -------------------------------------------------------------
            # 5. Stage 5 (5W1H) 粒子の抽出
            # -------------------------------------------------------------
            stage5 = item.get("stage5") or {}
            frame = stage5.get("frame") or stage5
            for dimension in ("who", "what", "when", "where", "why", "how"):
                label = str(frame.get(dimension) or "Unspecified")
                state = "unspecified" if label.strip().casefold() == "unspecified" else "determined"
                particles.append(
                    Particle(
                        id=f"p_{dimension}_{uuid.uuid4().hex[:6]}",
                        label=label,
                        entity_type=dimension.capitalize(),
                        state=state,
                        constraints=[stage5.get("stage", "Stage 5 - 5W1H Synthesis")]
                    )
                )

        return particles
