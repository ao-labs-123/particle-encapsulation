# src/factory.py

import uuid
from typing import List, Dict, Any
from src.particle import Particle

class ParticleFactory:
    @staticmethod
    def _is_unspecified(value: Any) -> bool:
        return str(value).strip().casefold() in {
            "unknown",
            "unspecified",
            "undetermined",
            "unresolved",
            "n/a",
            "he/she/they",
        }

    @staticmethod
    def _particle_id(item: Dict[str, Any], item_index: int, entity_type: str) -> str:
        identity = item.get("timestamp") or item.get("input") or "entry"
        stable_key = f"{identity}:{item_index}:{entity_type}"
        suffix = uuid.uuid5(uuid.NAMESPACE_URL, stable_key).hex[:12]
        return f"p_{entity_type.lower()}_{suffix}"

    @classmethod
    def from_log_json(cls, log_data: List[Dict[str, Any]]) -> List[Particle]:
        """
        log.json (辞書型データ) を受け取り、
        解析結果に対応する Particle オブジェクトのリストを生成して返す
        """
        particles: List[Particle] = []

            # -------------------------------------------------------------
            # 1. Agent (主語) 粒子の抽出 (Stage1から)
            # -------------------------------------------------------------
        for item_index, item in enumerate(log_data):
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
                agent_state = "unspecified" if cls._is_unspecified(agent_label) else "determined"
                agent_particle_id = cls._particle_id(item, item_index, "Agent")
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

                event = structure.get("event")
                if isinstance(event, dict):
                    event_particle_id = cls._particle_id(item, item_index, "Event")
                    structure["event_particle_id"] = event_particle_id
                    event_label = event.get("verb") or event.get("state") or event.get("category")
                    particles.append(
                        Particle(
                            id=event_particle_id,
                            label=str(event_label or "Unspecified"),
                            entity_type="Event",
                            state="unspecified" if not event_label else "determined",
                            constraints=[stage2.get("process", "event")],
                            properties={"event": event}
                        )
                    )
                elif has_contextual_relation and event:
                    event_particle_id = cls._particle_id(item, item_index, "Event")
                    structure["event_particle_id"] = event_particle_id
                    particles.append(
                        Particle(
                            id=event_particle_id,
                            label=str(event),
                            entity_type="Event",
                            state="determined",
                            constraints=[stage2.get("process", "event")]
                        )
                    )

                for field, entity_type in (("concession", "Concession"), ("outcome", "Outcome")):
                    label = structure.get(field)
                    if label:
                        particles.append(
                            Particle(
                                id=cls._particle_id(item, item_index, entity_type),
                                label=str(label),
                                entity_type=entity_type,
                                state="determined",
                                constraints=[stage2.get("process", "stage2_relation")]
                            )
                        )

                # Cause (原因) 粒子の生成
                if "cause" in structure:
                    cause_particle_id = cls._particle_id(item, item_index, "Cause")
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
                effect_label = None if has_contextual_relation else structure.get("effect")

                if effect_label:
                    effect_particle_id = cls._particle_id(item, item_index, "Effect")
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
                    context_particle_id = cls._particle_id(item, item_index, relation)
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
            if stage3_process and stage3_process not in {"Standard", "No modification structure found"}:
                stage3_result = stage3.get("result") or stage3.get("structure")
                particles.append(
                    Particle(
                        id=cls._particle_id(
                            item,
                            item_index,
                            "RelativeClause"
                            if stage3_process in {"Defining clause", "Non-defining clause"}
                            else "Modifier"
                        ),
                        label=stage3_process,
                        entity_type=(
                            "RelativeClause"
                            if stage3_process in {"Defining clause", "Non-defining clause"}
                            else "Modifier"
                        ),
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
                        id=cls._particle_id(item, item_index, "Morphology"),
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
                state = "unspecified" if cls._is_unspecified(label) else "determined"
                particles.append(
                    Particle(
                        id=cls._particle_id(item, item_index, dimension.capitalize()),
                        label=label,
                        entity_type=dimension.capitalize(),
                        state=state,
                        constraints=[stage5.get("stage", "Stage 5 - 5W1H Synthesis")]
                    )
                )

        return particles
