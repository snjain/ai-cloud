"""
Multi-Agent Patterns Reference (Module 7.3)

1. Agent-as-Tool Pattern: One agent invokes another as a tool
2. Agent Handoff Pattern: Complete control transfer between agents
"""

from dataclasses import dataclass
from typing import Union
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from graphs.utils import get_model


@dataclass
class ResearchDeps:
    topic: str


@dataclass
class EmailDeps:
    recipient: str


email_agent = Agent(
    get_model(),
    system_prompt="You are an email drafting specialist. Write professional, concise emails.",
    deps_type=EmailDeps,
)


@email_agent.tool
async def send_email_draft(ctx: RunContext[EmailDeps], subject: str, body: str) -> str:
    return f"Draft created for {ctx.deps.recipient}:\nSubject: {subject}\nBody: {body}"


research_agent = Agent(
    get_model(),
    system_prompt="You are a research assistant. Research topics and compose emails when needed.",
    deps_type=ResearchDeps,
)


@research_agent.tool
async def compose_email(ctx: RunContext[ResearchDeps], recipient: str, subject: str, content: str) -> str:
    email_deps = EmailDeps(recipient=recipient)
    result = await email_agent.run(
        f"Draft an email to {recipient} about {ctx.deps.topic}.\nSubject: {subject}\nKey points: {content}",
        deps=email_deps,
    )
    return f"Email composed via sub-agent:\n{result.output}"


class DirectResponse(BaseModel):
    type: str = "direct"
    response: str


class EmailHandoff(BaseModel):
    type: str = "email_handoff"
    recipient: str
    subject: str
    content: str


handoff_research_agent = Agent(
    get_model(),
    system_prompt="""You are a research assistant. For research queries, respond directly.
For email requests, output an EmailHandoff with recipient, subject, and content.""",
    deps_type=ResearchDeps,
    output_type=Union[DirectResponse, EmailHandoff],
)


async def run_with_handoff(query: str, topic: str) -> str:
    deps = ResearchDeps(topic=topic)
    result = await handoff_research_agent.run(query, deps=deps)

    if isinstance(result.output, DirectResponse):
        return result.output.response
    elif isinstance(result.output, EmailHandoff):
        handoff = result.output
        email_deps = EmailDeps(recipient=handoff.recipient)
        email_result = await email_agent.run(
            f"Draft email to {handoff.recipient}\nSubject: {handoff.subject}\nContent: {handoff.content}",
            deps=email_deps,
        )
        return f"[Handed off to Email Agent]\n{email_result.output}"

    return str(result.output)
