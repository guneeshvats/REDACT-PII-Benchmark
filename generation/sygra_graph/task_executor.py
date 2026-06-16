import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml
from langchain_core.messages import AIMessage, HumanMessage

from sygra.core.graph.functions.edge_condition import EdgeCondition
from sygra.core.graph.functions.node_processor import NodePostProcessor, NodePreProcessor
from sygra.core.graph.sygra_message import SygraMessage
from sygra.core.graph.sygra_state import SygraState


HERE = Path(__file__).resolve().parent
PROMPT_YAML = HERE.parent / "pii_generation" / "generation_prompt_v3.yaml"


def _load_prompt_data() -> dict[str, Any]:
    if not PROMPT_YAML.exists():
        raise FileNotFoundError(f"Prompt file not found: {PROMPT_YAML}")
    data = yaml.safe_load(PROMPT_YAML.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("generation_prompt_v3.yaml must parse to a mapping")
    return data


PROMPT_DATA = _load_prompt_data()


def _build_few_shot_messages(few_shots: list[dict[str, Any]]) -> list[Any]:
    messages: list[Any] = []
    for fs in few_shots:
        axes = fs.get("axes", {})
        user_msg = (
            "Generate ONE benchmark record under the following axis configuration:\n\n"
            + json.dumps(axes, indent=2, ensure_ascii=False)
            + "\n\nReturn ONLY the JSON object per the output schema. No commentary."
        )
        messages.append(HumanMessage(content=user_msg))
        messages.append(AIMessage(content=str(fs.get("output", "")).strip()))
    return messages


def _render_user_prompt(template: str, state: SygraState) -> str:
    axes = state.get("axes") or {}
    if not isinstance(axes, dict):
        axes = {}

    repl = {
        "domain": axes.get("domain", "-"),
        "format": axes.get("format", "-"),
        "difficulty": axes.get("difficulty", "-"),
        "length": axes.get("length", "-"),
        "density": axes.get("density", "-"),
        "code_switching": axes.get("code_switching", "-"),
        "language": axes.get("language", "-"),
        "adjacency": axes.get("adjacency", "-"),
        "co_pattern_or_none": axes.get("co_occurrence_pattern", "none"),
        "target_entity_type": state.get("target_entity_type", "-"),
        "target_pattern_id": state.get("target_pattern_id", "-"),
        "target_pattern_desc": state.get("target_pattern_desc", "-"),
        "target_pattern_example": state.get("target_pattern_example", "-"),
        "behavioral_frame": state.get("behavioral_frame", "isolation"),
        "prior_passages_summary": "(none - first record in this batch)",
        "mode": state.get("mode", "coverage"),
        "scenario_seed": state.get("scenario_seed", ""),
        "anchor_id": state.get("anchor_id", "n/a"),
        "sweep_axis": state.get("sweep_axis", "n/a"),
        "sweep_value": state.get("sweep_value", "n/a"),
        "frozen_entity_values": json.dumps(
            state.get("frozen_entity_values", []), ensure_ascii=False
        ),
        "persona": state.get("persona", "n/a"),
        "narrative": state.get("narrative", "n/a"),
    }

    rendered = template
    for key, value in repl.items():
        rendered = rendered.replace("{{ " + key + " }}", str(value))
    return rendered


def _extract_json_object(content: str) -> dict[str, Any]:
    text = (content or "").strip()
    if not text:
        return {}

    candidates = [text]
    if text.startswith("```"):
        stripped = re.sub(r"^```\w*\n?", "", text)
        stripped = re.sub(r"\n?```$", "", stripped).strip()
        candidates = [stripped, text]

    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict):
                return parsed
            if isinstance(parsed, list):
                return {"entities": parsed}
        except json.JSONDecodeError:
            pass

    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        try:
            parsed = json.loads(m.group())
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

    m = re.search(r"\[.*\]", text, re.DOTALL)
    if m:
        try:
            parsed = json.loads(m.group())
            if isinstance(parsed, list):
                return {"entities": parsed}
        except json.JSONDecodeError:
            pass

    return {}


def _coerce_entities(raw: Any) -> list[dict[str, Any]]:
    if isinstance(raw, list):
        return [r for r in raw if isinstance(r, dict)]
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list):
                return [r for r in parsed if isinstance(r, dict)]
        except json.JSONDecodeError:
            return []
    return []


def _normalize_entities(raw_entities: Any, text: str) -> list[dict[str, Any]]:
    entities = _coerce_entities(raw_entities)
    seen_mentions: dict[tuple[str, str], int] = defaultdict(int)
    normalized: list[dict[str, Any]] = []

    for ent in entities:
        entity_type = str(ent.get("entity_type", "")).strip()
        entity_string = str(ent.get("entity_string", ent.get("text", ""))).strip()
        if not entity_type or not entity_string:
            continue

        mention_index = ent.get("mention_index")
        if not isinstance(mention_index, int):
            key = (entity_type, entity_string)
            mention_index = seen_mentions[key]
            seen_mentions[key] += 1

        disclosed = ent.get("disclosed")
        if not isinstance(disclosed, bool):
            disclosed = True

        disclosure_form = str(ent.get("disclosure_form", "complete")).strip() or "complete"
        sensitivity_tier = str(ent.get("sensitivity_tier", "")).strip()

        normalized.append(
            {
                "entity_type": entity_type,
                "entity_string": entity_string,
                "mention_index": mention_index,
                "disclosed": disclosed,
                "disclosure_form": disclosure_form,
                "sensitivity_tier": sensitivity_tier,
            }
        )

    if text:
        normalized.sort(key=lambda e: text.find(e["entity_string"]))

    return normalized


class PiiV32PromptBuilder(NodePreProcessor):
    def apply(self, state: SygraState) -> SygraState:
        user_template = str(PROMPT_DATA.get("user_prompt", ""))
        few_shots = PROMPT_DATA.get("few_shots", [])
        few_shot_messages = _build_few_shot_messages(few_shots if isinstance(few_shots, list) else [])

        user_prompt = _render_user_prompt(user_template, state)
        messages = [*few_shot_messages, HumanMessage(content=user_prompt)]

        state["system_prompt"] = str(PROMPT_DATA.get("system_prompt", ""))
        state["messages"] = messages
        state["rendered_user_prompt"] = user_prompt
        return state


class PiiV32RecordPostProcessor(NodePostProcessor):
    def apply(self, resp: SygraMessage) -> SygraState:
        content = resp.message.content if resp.message else ""
        parsed = _extract_json_object(content)

        text = str(parsed.get("text", "")).strip()
        entities = _normalize_entities(parsed.get("entities", []), text)

        return {
            "text": text,
            "entities": entities,
            "entity_count": len(entities),
            "self_check_emitted": parsed.get("self_check", {}),
            "language_primary": parsed.get("language_primary", ""),
            "language_embedded": parsed.get("language_embedded", []),
            "format_compliance_notes": parsed.get("format_compliance_notes", []),
            "generation_status": "ok" if parsed else "json_error",
        }


def _check_frozen_values_present(state: SygraState, text: str) -> bool:
    if state.get("mode") != "paired_sweep":
        return True

    frozen_vals = state.get("frozen_entity_values", [])
    if not isinstance(frozen_vals, list):
        return False

    for item in frozen_vals:
        if not isinstance(item, dict):
            return False
        value = str(item.get("entity_string", "")).strip()
        if value and value not in text:
            return False
    return True


def run_self_check(node_config: dict, state: SygraState) -> dict[str, Any]:
    text = str(state.get("text", ""))
    entities = _normalize_entities(state.get("entities", []), text)

    failures: list[str] = []
    if not text:
        failures.append("empty_text")
    if not entities:
        failures.append("no_entities")

    for idx, ent in enumerate(entities):
        entity_string = ent.get("entity_string", "")
        if entity_string and entity_string not in text:
            failures.append(f"entity_not_in_text[{idx}]")

    if not _check_frozen_values_present(state, text):
        failures.append("frozen_entity_missing")

    return {
        "entities": entities,
        "entity_count": len(entities),
        "self_check_passed": len(failures) == 0,
        "self_check_failures": failures,
    }


class SelfCheckRoute(EdgeCondition):
    @staticmethod
    def apply(state: SygraState) -> str:
        return "enrich" if bool(state.get("self_check_passed")) else "verify"


class PiiV32VerifyPromptBuilder(NodePreProcessor):
    def apply(self, state: SygraState) -> SygraState:
        verify_payload = {
            "text": state.get("text", ""),
            "entities": state.get("entities", []),
            "self_check_failures": state.get("self_check_failures", []),
            "target_entity_type": state.get("target_entity_type", ""),
            "target_pattern_id": state.get("target_pattern_id", ""),
        }

        state["messages"] = []
        state["verify_system_prompt"] = (
            "You are a strict verifier for PII benchmark JSON. "
            "Return ONLY valid JSON with key 'entities' as a list."
        )
        state["verify_user_prompt"] = (
            "Given this record and failed checks, fix entities and return JSON only.\n\n"
            + json.dumps(verify_payload, ensure_ascii=False, indent=2)
        )
        return state


class PiiV32VerifyPostProcessor(NodePostProcessor):
    def apply(self, resp: SygraMessage) -> SygraState:
        content = resp.message.content if resp.message else ""
        parsed = _extract_json_object(content)
        entities = _normalize_entities(parsed.get("entities", []), "")
        return {
            "entities_verified": entities,
            "entities": entities,
            "entity_count": len(entities),
            "verify_status": "ok" if parsed else "json_error",
        }


class VerifyRoute(EdgeCondition):
    @staticmethod
    def apply(state: SygraState) -> str:
        entities = _coerce_entities(state.get("entities", []))
        return "repair" if len(entities) == 0 else "enrich"


def repair_zero_entities(node_config: dict, state: SygraState) -> dict[str, Any]:
    entities = _coerce_entities(state.get("entities", []))
    if entities:
        return {"entities_repaired": entities, "entities": entities, "repair_status": "skipped"}

    text = str(state.get("text", ""))
    target_type = str(state.get("target_entity_type", "")).strip() or "Full_Name"
    examples_raw = str(state.get("target_pattern_example", ""))

    candidates = [p.strip() for p in re.split(r"\||,|;", examples_raw) if p.strip()]
    recovered: list[dict[str, Any]] = []
    for candidate in candidates:
        if candidate in text:
            recovered.append(
                {
                    "entity_type": target_type,
                    "entity_string": candidate,
                    "mention_index": 0,
                    "disclosed": True,
                    "disclosure_form": "complete",
                    "sensitivity_tier": "",
                }
            )
            break

    return {
        "entities_repaired": recovered,
        "entities": recovered,
        "entity_count": len(recovered),
        "repair_status": "recovered" if recovered else "no_recovery",
    }


_DIRECT_TYPES = {
    "Full_Name",
    "First_Given_Name",
    "Last_Family_Name",
    "Preferred_Name",
    "Work_Email_Address",
    "Personal_Email_Address",
    "Telephone_Numbers_Work",
    "Telephone_Numbers_Personal",
    "National_Identification_Number",
    "Passport_Number",
    "Driving_License_Number",
    "Credit_Card_Numbers",
    "Password",
}


_HIGH_SENSITIVITY = {
    "National_Identification_Number",
    "Passport_Number",
    "Driving_License_Number",
    "Credit_Card_Numbers",
    "Password",
    "Medical_Information",
    "Sex_Orientation",
    "Religion",
    "Crime",
}


def enrich_latent_schema(node_config: dict, state: SygraState) -> dict[str, Any]:
    entities = _coerce_entities(state.get("entities", []))

    classification = []
    policy = []

    for ent in entities:
        entity_type = str(ent.get("entity_type", "")).strip()
        entity_string = str(ent.get("entity_string", ent.get("text", ""))).strip()
        if not entity_type or not entity_string:
            continue

        identifier_class = "direct" if entity_type in _DIRECT_TYPES else "indirect"
        disclosure = "must_hide" if entity_type in _HIGH_SENSITIVITY else "may_disclose"

        classification.append(
            {
                "entity_type": entity_type,
                "entity_string": entity_string,
                "identifier_class": identifier_class,
            }
        )
        policy.append(
            {
                "entity_type": entity_type,
                "entity_string": entity_string,
                "policy": disclosure,
            }
        )

    return {
        "direct_indirect_classification": classification,
        "disclosure_policy": policy,
    }
