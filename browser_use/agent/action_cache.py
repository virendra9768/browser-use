import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


CACHE_PATH_ENV = "BROWSER_USE_ACTION_CACHE_PATH"


def get_action_cache_path() -> Path | None:
    cache_path = os.getenv(CACHE_PATH_ENV)

    if not cache_path:
        return None

    return Path(cache_path).expanduser()


def cache_executed_actions(
    *,
    agent_id: str,
    step: int,
    url_before: str,
    actions: list[Any],
    interacted_elements: list[Any],
    results: list[Any],
) -> int:
    """Append executed browser actions to an optional JSONL cache."""

    cache_path = get_action_cache_path()

    if cache_path is None:
        return 0

    cache_path.parent.mkdir(parents=True, exist_ok=True)

    cached_count = 0

    with cache_path.open("a", encoding="utf-8") as cache_file:
        for action, interacted_element, result in zip(
            actions,
            interacted_elements,
            results,
        ):
            record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "agent_id": agent_id,
                "step": step,
                "url_before": url_before,
                "action": action.model_dump(
                    mode="json",
                    exclude_none=True,
                ),
                "interacted_element": (
                    interacted_element.to_dict()
                    if interacted_element is not None
                    else None
                ),
                "result": (
                    result.model_dump(
                        mode="json",
                        exclude_none=True,
                    )
                    if result is not None
                    else None
                ),
            }

            cache_file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    default=str,
                )
                + "\n"
            )

            cached_count += 1

    return cached_count