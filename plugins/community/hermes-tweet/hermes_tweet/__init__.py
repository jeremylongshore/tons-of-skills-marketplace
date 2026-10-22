# SPDX-FileCopyrightText: 2026 Xquik Contributors
# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from . import schemas
from .tools import (
    action_enabled,
    call_action,
    call_read,
    check_api_available,
    explore,
    xstatus,
    xtrends,
)

logger = logging.getLogger(__name__)

TOOLSET = "hermes-tweet"


def _register_bundled_skills(ctx: Any) -> None:
    skills_dir = Path(__file__).parent / "skills"
    for child in sorted(skills_dir.iterdir()):
        skill_md = child / "SKILL.md"
        if child.is_dir() and skill_md.exists():
            ctx.register_skill(child.name, skill_md)


def register(ctx: Any) -> None:
    ctx.register_tool(
        name="tweet_explore",
        toolset=TOOLSET,
        schema=schemas.TWEET_EXPLORE,
        handler=explore,
        is_async=False,
        description="Search the bundled Xquik endpoint catalog.",
        emoji="🔎",
    )

    ctx.register_tool(
        name="tweet_read",
        toolset=TOOLSET,
        schema=schemas.TWEET_READ,
        handler=call_read,
        check_fn=check_api_available,
        requires_env=["XQUIK_API_KEY"],
        is_async=False,
        description="Call catalog-listed read-only Xquik routes.",
        emoji="📖",
    )

    ctx.register_tool(
        name="tweet_action",
        toolset=TOOLSET,
        schema=schemas.TWEET_ACTION,
        handler=call_action,
        check_fn=action_enabled,
        requires_env=["XQUIK_API_KEY", "HERMES_TWEET_ENABLE_ACTIONS"],
        is_async=False,
        description="Call catalog-listed write-like or private Xquik routes.",
        emoji="✍️",
    )

    ctx.register_command(
        "xstatus",
        handler=xstatus,
        description="Show Xquik account and usage status",
    )
    ctx.register_command("xtrends", handler=xtrends, description="Show current X trends")

    _register_bundled_skills(ctx)
    logger.info(
        "Hermes Tweet loaded. actions_enabled=%s",
        os.getenv("HERMES_TWEET_ENABLE_ACTIONS", "false"),
    )


__all__ = ["register"]
