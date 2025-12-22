#!/usr/bin/env python3
"""
Swarm Orchestrator - Multi-Agent Collaboration System

Orchestrates multiple agents working together with:
- Debate/consensus loops
- Automatic iteration on feedback
- Parallel agent execution
- Conflict resolution
- Convergence detection

Features:
- Swarm mode: Multiple agents debate until consensus
- Iteration loops: DEV → REVIEWER → DEV cycles
- Parallel execution: Independent agents run simultaneously
- Voting mechanisms for decisions
- Automatic termination on convergence

Usage:
    from lib.swarm_orchestrator import SwarmOrchestrator, SwarmConfig

    orchestrator = SwarmOrchestrator(story_key="3-5")
    result = orchestrator.run_swarm(
        agents=["ARCHITECT", "DEV", "REVIEWER"],
        task="Design and implement user authentication",
        max_iterations=3
    )
"""

import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional

# Import dependencies
try:
    from agent_handoff import HandoffGenerator
    from agent_router import AgentRouter
    from shared_memory import get_knowledge_graph, get_shared_memory
except ImportError:
    from lib.agent_handoff import HandoffGenerator
    from lib.agent_router import AgentRouter
    from lib.shared_memory import get_knowledge_graph, get_shared_memory


PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CLAUDE_CLI = "claude.cmd" if sys.platform == 'win32' else "claude"


class SwarmState(Enum):
    """State of the swarm orchestration."""
    INITIALIZING = "initializing"
    RUNNING = "running"
    DEBATING = "debating"
    CONVERGING = "converging"
    CONSENSUS = "consensus"
    COMPLETED = "completed"
    FAILED = "failed"
    MAX_ITERATIONS = "max_iterations"


class ConsensusType(Enum):
    """Types of consensus mechanisms."""
    UNANIMOUS = "unanimous"      # All must agree
    MAJORITY = "majority"        # >50% agree
    QUORUM = "quorum"           # N of M agree
    REVIEWER_APPROVAL = "reviewer_approval"  # REVIEWER must approve


@dataclass
class AgentResponse:
    """Response from an agent."""
    agent: str
    model: str
    content: str
    timestamp: str
    iteration: int
    tokens_used: int = 0
    cost_usd: float = 0.0
    issues_found: list[str] = field(default_factory=list)
    approvals: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    vote: Optional[str] = None  # approve, reject, abstain

    def to_dict(self) -> dict:
        return {
            "agent": self.agent,
            "model": self.model,
            "content": self.content[:500] + "..." if len(self.content) > 500 else self.content,
            "timestamp": self.timestamp,
            "iteration": self.iteration,
            "tokens_used": self.tokens_used,
            "cost_usd": self.cost_usd,
            "issues_found": self.issues_found,
            "approvals": self.approvals,
            "suggestions": self.suggestions,
            "vote": self.vote
        }


@dataclass
class SwarmIteration:
    """One iteration of the swarm."""
    iteration_num: int
    responses: list[AgentResponse] = field(default_factory=list)
    consensus_reached: bool = False
    issues_remaining: list[str] = field(default_factory=list)
    decisions_made: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "iteration_num": self.iteration_num,
            "responses": [r.to_dict() for r in self.responses],
            "consensus_reached": self.consensus_reached,
            "issues_remaining": self.issues_remaining,
            "decisions_made": self.decisions_made
        }


@dataclass
class SwarmResult:
    """Result of swarm orchestration."""
    story_key: str
    task: str
    state: SwarmState
    iterations: list[SwarmIteration]
    final_output: str
    agents_involved: list[str]
    total_tokens: int
    total_cost_usd: float
    start_time: str
    end_time: str
    consensus_type: ConsensusType

    def to_dict(self) -> dict:
        return {
            "story_key": self.story_key,
            "task": self.task,
            "state": self.state.value,
            "iterations": [i.to_dict() for i in self.iterations],
            "final_output": self.final_output,
            "agents_involved": self.agents_involved,
            "total_tokens": self.total_tokens,
            "total_cost_usd": self.total_cost_usd,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "consensus_type": self.consensus_type.value
        }

    def to_summary(self) -> str:
        """Generate a human-readable summary."""
        lines = [
            f"## Swarm Result: {self.story_key}",
            "",
            f"**Task**: {self.task}",
            f"**State**: {self.state.value}",
            f"**Iterations**: {len(self.iterations)}",
            f"**Agents**: {', '.join(self.agents_involved)}",
            f"**Total Cost**: ${self.total_cost_usd:.4f}",
            "",
        ]

        if self.state == SwarmState.CONSENSUS:
            lines.append("✅ **Consensus reached!**")
        elif self.state == SwarmState.MAX_ITERATIONS:
            lines.append("⚠️ **Max iterations reached without full consensus**")

        lines.append("")
        lines.append("### Final Output")
        lines.append(self.final_output[:1000] if len(self.final_output) > 1000 else self.final_output)

        return "\n".join(lines)


@dataclass
class SwarmConfig:
    """Configuration for swarm orchestration."""
    max_iterations: int = 3
    consensus_type: ConsensusType = ConsensusType.REVIEWER_APPROVAL
    quorum_size: int = 2  # For QUORUM type
    timeout_seconds: int = 300
    parallel_execution: bool = False
    auto_fix_enabled: bool = True  # DEV automatically addresses REVIEWER issues
    verbose: bool = True
    budget_limit_usd: float = 20.0

    def to_dict(self) -> dict:
        return {
            "max_iterations": self.max_iterations,
            "consensus_type": self.consensus_type.value,
            "quorum_size": self.quorum_size,
            "timeout_seconds": self.timeout_seconds,
            "parallel_execution": self.parallel_execution,
            "auto_fix_enabled": self.auto_fix_enabled,
            "budget_limit_usd": self.budget_limit_usd
        }


class SwarmOrchestrator:
    """Orchestrates multi-agent collaboration."""

    def __init__(self, story_key: str, config: Optional[SwarmConfig] = None):
        self.story_key = story_key
        self.config = config or SwarmConfig()
        self.project_root = PROJECT_ROOT
        self.shared_memory = get_shared_memory(story_key)
        self.knowledge_graph = get_knowledge_graph(story_key)
        self.handoff_generator = HandoffGenerator(story_key)
        self.router = AgentRouter()

        self.state = SwarmState.INITIALIZING
        self.iterations: list[SwarmIteration] = []
        self.total_tokens = 0
        self.total_cost = 0.0

        # Agent model mapping
        self.agent_models = {
            "SM": "sonnet",
            "DEV": "opus",
            "REVIEWER": "opus",
            "ARCHITECT": "sonnet",
            "BA": "sonnet",
            "PM": "sonnet",
            "WRITER": "sonnet",
            "MAINTAINER": "sonnet",
            "SECURITY": "opus",
        }

    def _log(self, message: str, level: str = "INFO"):
        """Log a message with timestamp."""
        if self.config.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            emoji = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️",
                    "ERROR": "❌", "DEBUG": "🔍"}.get(level, "•")
            print(f"[{timestamp}] {emoji} {message}")

    def _invoke_agent(self, agent: str, prompt: str,
                      iteration: int = 0) -> AgentResponse:
        """Invoke a single agent with Claude CLI."""
        model = self.agent_models.get(agent, "sonnet")

        self._log(f"Invoking {agent} (model: {model})...")

        # Build the full prompt with context
        context = self.handoff_generator.generate_context_for_agent(agent)
        full_prompt = f"{context}\n\n---\n\n{prompt}"

        try:
            result = subprocess.run(
                [CLAUDE_CLI, "--print", "--model", model, "-p", full_prompt],
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                cwd=str(self.project_root)
            )

            content = result.stdout + result.stderr

            # Parse response for issues, approvals, suggestions
            issues = self._extract_issues(content)
            approvals = self._extract_approvals(content)
            suggestions = self._extract_suggestions(content)
            vote = self._determine_vote(content, issues, approvals)

            # Estimate tokens (rough)
            tokens = len(full_prompt.split()) + len(content.split())
            cost = self._estimate_cost(tokens, model)

            self.total_tokens += tokens
            self.total_cost += cost

            return AgentResponse(
                agent=agent,
                model=model,
                content=content,
                timestamp=datetime.now().isoformat(),
                iteration=iteration,
                tokens_used=tokens,
                cost_usd=cost,
                issues_found=issues,
                approvals=approvals,
                suggestions=suggestions,
                vote=vote
            )

        except subprocess.TimeoutExpired:
            self._log(f"{agent} timed out", "WARNING")
            return AgentResponse(
                agent=agent,
                model=model,
                content="[TIMEOUT]",
                timestamp=datetime.now().isoformat(),
                iteration=iteration,
                vote="abstain"
            )
        except Exception as e:
            self._log(f"{agent} failed: {e}", "ERROR")
            return AgentResponse(
                agent=agent,
                model=model,
                content=f"[ERROR: {str(e)}]",
                timestamp=datetime.now().isoformat(),
                iteration=iteration,
                vote="abstain"
            )

    def _extract_issues(self, content: str) -> list[str]:
        """Extract issues/problems from response."""
        issues = []
        patterns = [
            r'(?:issue|problem|bug|error|fix needed|must fix|should fix):\s*(.+)',
            r'❌\s*(.+)',
            r'\[ISSUE\]\s*(.+)',
            r'- (?:Issue|Problem|Bug):\s*(.+)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            issues.extend(matches)

        return list(set(issues))[:10]  # Limit to 10

    def _extract_approvals(self, content: str) -> list[str]:
        """Extract approvals/LGTMs from response."""
        approvals = []
        patterns = [
            r'(?:lgtm|approved|looks good|well done|excellent)[\s:]*(.+)?',
            r'✅\s*(.+)',
            r'\[APPROVED\]\s*(.+)?',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                approvals.append(match if match else "Approved")

        return list(set(approvals))[:5]

    def _extract_suggestions(self, content: str) -> list[str]:
        """Extract suggestions from response."""
        suggestions = []
        patterns = [
            r'(?:suggest|consider|recommend|might want to|could):\s*(.+)',
            r'💡\s*(.+)',
            r'\[SUGGESTION\]\s*(.+)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
            suggestions.extend(matches)

        return list(set(suggestions))[:5]

    def _determine_vote(self, content: str, issues: list[str],
                       approvals: list[str]) -> str:
        """Determine agent's vote based on response."""
        content_lower = content.lower()

        # Explicit votes
        if any(word in content_lower for word in ['approved', 'lgtm', 'ship it', 'looks good to me']):
            return "approve"
        if any(word in content_lower for word in ['rejected', 'do not merge', 'needs work', 'blocking']):
            return "reject"

        # Implicit from issues/approvals
        if len(issues) > len(approvals):
            return "reject"
        if len(approvals) > 0 and len(issues) == 0:
            return "approve"

        return "abstain"

    def _estimate_cost(self, tokens: int, model: str) -> float:
        """Estimate cost in USD."""
        # Approximate pricing per 1M tokens
        pricing = {
            "opus": {"input": 15.0, "output": 75.0},
            "sonnet": {"input": 3.0, "output": 15.0},
            "haiku": {"input": 0.8, "output": 4.0},
        }

        rates = pricing.get(model, pricing["sonnet"])
        # Assume 50/50 input/output split
        cost = (tokens / 2 / 1_000_000 * rates["input"]) + \
               (tokens / 2 / 1_000_000 * rates["output"])
        return cost

    def _check_consensus(self, responses: list[AgentResponse]) -> bool:
        """Check if consensus is reached based on config."""
        votes = [r.vote for r in responses if r.vote]
        approvals = votes.count("approve")
        rejects = votes.count("reject")
        total = len(votes)

        if total == 0:
            return False

        if self.config.consensus_type == ConsensusType.UNANIMOUS:
            return approvals == total

        elif self.config.consensus_type == ConsensusType.MAJORITY:
            return approvals > total / 2

        elif self.config.consensus_type == ConsensusType.QUORUM:
            return approvals >= self.config.quorum_size

        elif self.config.consensus_type == ConsensusType.REVIEWER_APPROVAL:
            reviewer_responses = [r for r in responses if r.agent == "REVIEWER"]
            if not reviewer_responses:
                return approvals > rejects
            return reviewer_responses[0].vote == "approve"

        return False

    def _collect_issues(self, responses: list[AgentResponse]) -> list[str]:
        """Collect all unique issues from responses."""
        all_issues = []
        for r in responses:
            all_issues.extend(r.issues_found)
        return list(set(all_issues))

    def _build_iteration_prompt(self, agent: str, task: str,
                                 iteration: int,
                                 previous_responses: list[AgentResponse],
                                 issues_to_fix: list[str]) -> str:
        """Build prompt for a specific iteration."""

        if iteration == 0:
            # First iteration - just the task
            return f"""You are the {agent} agent. Your task is:

{task}

Please complete this task according to your role and expertise.
At the end, clearly indicate if you APPROVE or have ISSUES with the work.
"""

        # Subsequent iterations - include feedback
        feedback_lines = []
        for r in previous_responses:
            if r.agent == agent:
                continue

            feedback_lines.append(f"### Feedback from {r.agent}")
            if r.issues_found:
                feedback_lines.append("**Issues found:**")
                for issue in r.issues_found:
                    feedback_lines.append(f"- ❌ {issue}")
            if r.suggestions:
                feedback_lines.append("**Suggestions:**")
                for sug in r.suggestions:
                    feedback_lines.append(f"- 💡 {sug}")
            if r.approvals:
                feedback_lines.append("**Approvals:**")
                for app in r.approvals:
                    feedback_lines.append(f"- ✅ {app}")
            feedback_lines.append("")

        prompt = f"""You are the {agent} agent. This is iteration {iteration + 1}.

## Original Task
{task}

## Feedback from Other Agents
{chr(10).join(feedback_lines)}

## Issues to Address
{chr(10).join(f'- {issue}' for issue in issues_to_fix) if issues_to_fix else 'No outstanding issues.'}

Please address the feedback and issues above.
At the end, clearly indicate if you APPROVE the current state or have remaining ISSUES.
"""

        return prompt

    def run_swarm(self, agents: list[str], task: str,
                  max_iterations: Optional[int] = None) -> SwarmResult:
        """Run swarm orchestration with multiple agents."""

        max_iter = max_iterations or self.config.max_iterations
        start_time = datetime.now().isoformat()

        self.state = SwarmState.RUNNING
        self._log(f"Starting swarm with agents: {', '.join(agents)}")
        self._log(f"Task: {task[:100]}...")

        issues_to_fix: list[str] = []
        previous_responses: list[AgentResponse] = []

        for iteration in range(max_iter):
            self._log(f"=== Iteration {iteration + 1}/{max_iter} ===")
            self.state = SwarmState.DEBATING

            # Check budget
            if self.total_cost >= self.config.budget_limit_usd:
                self._log("Budget limit reached!", "WARNING")
                break

            iter_responses: list[AgentResponse] = []

            if self.config.parallel_execution and iteration == 0:
                # Parallel execution for first iteration
                with ThreadPoolExecutor(max_workers=len(agents)) as executor:
                    futures = {}
                    for agent in agents:
                        prompt = self._build_iteration_prompt(
                            agent, task, iteration, previous_responses, issues_to_fix
                        )
                        futures[executor.submit(self._invoke_agent, agent, prompt, iteration)] = agent

                    for future in as_completed(futures):
                        response = future.result()
                        iter_responses.append(response)
            else:
                # Sequential execution
                for agent in agents:
                    prompt = self._build_iteration_prompt(
                        agent, task, iteration, previous_responses, issues_to_fix
                    )
                    response = self._invoke_agent(agent, prompt, iteration)
                    iter_responses.append(response)

                    # Record in shared memory
                    self.shared_memory.add(
                        agent=agent,
                        content=f"Iteration {iteration + 1}: {response.vote or 'no vote'}",
                        tags=["swarm", "iteration"]
                    )

            # Collect issues
            issues_to_fix = self._collect_issues(iter_responses)

            # Check consensus
            consensus = self._check_consensus(iter_responses)

            swarm_iter = SwarmIteration(
                iteration_num=iteration,
                responses=iter_responses,
                consensus_reached=consensus,
                issues_remaining=issues_to_fix,
                decisions_made=[f"{r.agent}: {r.vote}" for r in iter_responses]
            )
            self.iterations.append(swarm_iter)

            previous_responses = iter_responses

            self._log(f"Issues remaining: {len(issues_to_fix)}")
            self._log(f"Consensus: {'✅ Yes' if consensus else '❌ No'}")

            if consensus:
                self.state = SwarmState.CONSENSUS
                self._log("Consensus reached!", "SUCCESS")
                break

        # Determine final state
        if self.state != SwarmState.CONSENSUS:
            self.state = SwarmState.MAX_ITERATIONS

        # Generate final output
        final_output = self._generate_final_output(previous_responses)

        # Create result
        result = SwarmResult(
            story_key=self.story_key,
            task=task,
            state=self.state,
            iterations=self.iterations,
            final_output=final_output,
            agents_involved=agents,
            total_tokens=self.total_tokens,
            total_cost_usd=self.total_cost,
            start_time=start_time,
            end_time=datetime.now().isoformat(),
            consensus_type=self.config.consensus_type
        )

        # Save to knowledge graph
        self.knowledge_graph.add_decision(
            agent="SWARM",
            topic="swarm-result",
            decision=f"Completed with state: {self.state.value}",
            context={"iterations": len(self.iterations), "cost": self.total_cost}
        )

        return result

    def _generate_final_output(self, responses: list[AgentResponse]) -> str:
        """Generate consolidated final output."""
        # Use the DEV response as primary, or last response
        dev_response = next((r for r in responses if r.agent == "DEV"), None)
        primary = dev_response or responses[-1] if responses else None

        if not primary:
            return "No output generated."

        return primary.content

    def run_iteration_loop(self, primary_agent: str, reviewer_agent: str,
                           task: str, max_iterations: Optional[int] = None) -> SwarmResult:
        """Run a simple iteration loop between two agents (e.g., DEV → REVIEWER → DEV)."""
        return self.run_swarm(
            agents=[primary_agent, reviewer_agent],
            task=task,
            max_iterations=max_iterations
        )


# Convenience functions
def run_swarm(story_key: str, agents: list[str], task: str,
              max_iterations: int = 3, **config_kwargs) -> SwarmResult:
    """Quick function to run a swarm."""
    config = SwarmConfig(**config_kwargs)
    orchestrator = SwarmOrchestrator(story_key, config)
    return orchestrator.run_swarm(agents, task, max_iterations)


def run_dev_review_loop(story_key: str, task: str,
                        max_iterations: int = 3) -> SwarmResult:
    """Run a DEV → REVIEWER iteration loop."""
    config = SwarmConfig(
        max_iterations=max_iterations,
        consensus_type=ConsensusType.REVIEWER_APPROVAL
    )
    orchestrator = SwarmOrchestrator(story_key, config)
    return orchestrator.run_iteration_loop("DEV", "REVIEWER", task, max_iterations)


def run_architecture_review(story_key: str, task: str) -> SwarmResult:
    """Run an architecture review swarm."""
    config = SwarmConfig(
        max_iterations=2,
        consensus_type=ConsensusType.MAJORITY,
        parallel_execution=True
    )
    orchestrator = SwarmOrchestrator(story_key, config)
    return orchestrator.run_swarm(["ARCHITECT", "DEV", "REVIEWER"], task)


if __name__ == "__main__":
    print("=== Swarm Orchestrator Demo ===\n")
    print("This module orchestrates multi-agent collaboration.")
    print("\nExample usage:")
    print("""
    from lib.swarm_orchestrator import run_swarm, run_dev_review_loop

    # Full swarm with multiple agents
    result = run_swarm(
        story_key="3-5",
        agents=["ARCHITECT", "DEV", "REVIEWER"],
        task="Design and implement user authentication",
        max_iterations=3
    )
    print(result.to_summary())

    # Simple DEV → REVIEWER loop
    result = run_dev_review_loop(
        story_key="3-5",
        task="Implement login endpoint",
        max_iterations=2
    )
    """)
