#!/usr/bin/env python3
"""
Pair Programming Mode - DEV + REVIEWER Interleaved Collaboration

Real-time collaboration between DEV and REVIEWER where:
- DEV implements in small chunks
- REVIEWER provides immediate feedback
- DEV addresses feedback before continuing
- Results in higher quality, fewer iterations

Features:
- Chunk-based development
- Real-time feedback loops
- Incremental refinement
- Shared context maintenance
- Automatic issue tracking

Usage:
    from lib.pair_programming import PairSession, start_pair_session

    session = start_pair_session(story_key="3-5", task="Implement user login")
    result = session.run()
"""

import os
import sys
import re
import subprocess
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Generator, Tuple
from enum import Enum

# Import dependencies
try:
    from shared_memory import get_shared_memory, get_knowledge_graph
    from agent_handoff import HandoffGenerator
except ImportError:
    from lib.shared_memory import get_shared_memory, get_knowledge_graph
    from lib.agent_handoff import HandoffGenerator


PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
CLAUDE_CLI = "claude.cmd" if sys.platform == 'win32' else "claude"


class ChunkType(Enum):
    """Types of code chunks."""
    DESIGN = "design"          # Architecture/design decision
    IMPLEMENTATION = "implementation"  # Core code
    TEST = "test"              # Test code
    REFACTOR = "refactor"      # Refactoring
    FIX = "fix"                # Bug fix
    DOCUMENTATION = "documentation"  # Docs/comments


class FeedbackType(Enum):
    """Types of reviewer feedback."""
    APPROVE = "approve"        # Good to proceed
    MINOR = "minor"            # Minor issues, can proceed
    MAJOR = "major"            # Major issues, must fix
    BLOCKING = "blocking"      # Cannot proceed until fixed
    QUESTION = "question"      # Needs clarification


@dataclass
class CodeChunk:
    """A chunk of code being developed."""
    chunk_id: str
    chunk_type: ChunkType
    description: str
    content: str
    file_path: Optional[str] = None
    line_range: Optional[Tuple[int, int]] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id,
            "chunk_type": self.chunk_type.value,
            "description": self.description,
            "content": self.content[:500] + "..." if len(self.content) > 500 else self.content,
            "file_path": self.file_path,
            "line_range": self.line_range,
            "timestamp": self.timestamp
        }


@dataclass
class ReviewFeedback:
    """Feedback from reviewer on a chunk."""
    chunk_id: str
    feedback_type: FeedbackType
    comments: List[str]
    suggestions: List[str] = field(default_factory=list)
    must_fix: List[str] = field(default_factory=list)
    nice_to_have: List[str] = field(default_factory=list)
    approved: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return {
            "chunk_id": self.chunk_id,
            "feedback_type": self.feedback_type.value,
            "comments": self.comments,
            "suggestions": self.suggestions,
            "must_fix": self.must_fix,
            "nice_to_have": self.nice_to_have,
            "approved": self.approved,
            "timestamp": self.timestamp
        }
    
    def has_blocking_issues(self) -> bool:
        return self.feedback_type in [FeedbackType.MAJOR, FeedbackType.BLOCKING]


@dataclass
class PairExchange:
    """A single exchange in the pair programming session."""
    exchange_id: int
    chunk: CodeChunk
    feedback: Optional[ReviewFeedback] = None
    revision: Optional[CodeChunk] = None
    resolved: bool = False
    
    def to_dict(self) -> dict:
        return {
            "exchange_id": self.exchange_id,
            "chunk": self.chunk.to_dict(),
            "feedback": self.feedback.to_dict() if self.feedback else None,
            "revision": self.revision.to_dict() if self.revision else None,
            "resolved": self.resolved
        }


@dataclass
class PairSessionResult:
    """Result of a pair programming session."""
    story_key: str
    task: str
    exchanges: List[PairExchange]
    final_code: str
    files_created: List[str]
    files_modified: List[str]
    total_chunks: int
    total_revisions: int
    approval_rate: float
    start_time: str
    end_time: str
    
    def to_dict(self) -> dict:
        return {
            "story_key": self.story_key,
            "task": self.task,
            "exchanges": [e.to_dict() for e in self.exchanges],
            "final_code": self.final_code[:1000] if len(self.final_code) > 1000 else self.final_code,
            "files_created": self.files_created,
            "files_modified": self.files_modified,
            "total_chunks": self.total_chunks,
            "total_revisions": self.total_revisions,
            "approval_rate": self.approval_rate,
            "start_time": self.start_time,
            "end_time": self.end_time
        }
    
    def to_summary(self) -> str:
        """Generate human-readable summary."""
        lines = [
            f"## Pair Programming Result: {self.story_key}",
            f"",
            f"**Task**: {self.task}",
            f"**Exchanges**: {len(self.exchanges)}",
            f"**Chunks**: {self.total_chunks}",
            f"**Revisions**: {self.total_revisions}",
            f"**Approval Rate**: {self.approval_rate:.0%}",
            f"",
            f"### Files Created",
        ]
        
        for f in self.files_created:
            lines.append(f"- `{f}`")
        
        if self.files_modified:
            lines.append("")
            lines.append("### Files Modified")
            for f in self.files_modified:
                lines.append(f"- `{f}`")
        
        return "\n".join(lines)


@dataclass
class PairConfig:
    """Configuration for pair programming session."""
    max_revisions_per_chunk: int = 3
    timeout_seconds: int = 180
    verbose: bool = True
    auto_apply_fixes: bool = True
    chunk_size_hint: str = "medium"  # small, medium, large
    reviewer_model: str = "opus"
    dev_model: str = "opus"
    
    def to_dict(self) -> dict:
        return {
            "max_revisions_per_chunk": self.max_revisions_per_chunk,
            "timeout_seconds": self.timeout_seconds,
            "auto_apply_fixes": self.auto_apply_fixes,
            "chunk_size_hint": self.chunk_size_hint,
            "reviewer_model": self.reviewer_model,
            "dev_model": self.dev_model
        }


class PairSession:
    """A pair programming session between DEV and REVIEWER."""
    
    def __init__(self, story_key: str, task: str, 
                 config: Optional[PairConfig] = None):
        self.story_key = story_key
        self.task = task
        self.config = config or PairConfig()
        self.project_root = PROJECT_ROOT
        self.shared_memory = get_shared_memory(story_key)
        self.knowledge_graph = get_knowledge_graph(story_key)
        
        self.exchanges: List[PairExchange] = []
        self.files_created: List[str] = []
        self.files_modified: List[str] = []
        self.chunk_counter = 0
        self.exchange_counter = 0
    
    def _log(self, message: str, agent: str = "SYSTEM"):
        """Log a message."""
        if self.config.verbose:
            timestamp = datetime.now().strftime("%H:%M:%S")
            emoji = {"DEV": "💻", "REVIEWER": "👀", "SYSTEM": "⚙️"}.get(agent, "•")
            print(f"[{timestamp}] {emoji} [{agent}] {message}")
    
    def _invoke_agent(self, agent: str, prompt: str) -> str:
        """Invoke an agent with Claude CLI."""
        model = self.config.dev_model if agent == "DEV" else self.config.reviewer_model
        
        try:
            result = subprocess.run(
                [CLAUDE_CLI, "--print", "--model", model, "-p", prompt],
                capture_output=True,
                text=True,
                timeout=self.config.timeout_seconds,
                cwd=str(self.project_root)
            )
            return result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return "[TIMEOUT: Agent did not respond in time]"
        except Exception as e:
            return f"[ERROR: {str(e)}]"
    
    def _generate_chunk_id(self) -> str:
        """Generate unique chunk ID."""
        self.chunk_counter += 1
        return f"chunk_{self.chunk_counter:03d}"
    
    def _parse_dev_output(self, output: str) -> CodeChunk:
        """Parse DEV output into a CodeChunk."""
        # Try to extract file path
        file_match = re.search(r'(?:file|path):\s*[`"]?([^\s`"]+)[`"]?', output, re.IGNORECASE)
        file_path = file_match.group(1) if file_match else None
        
        # Try to extract code blocks
        code_blocks = re.findall(r'```[\w]*\n(.*?)```', output, re.DOTALL)
        content = "\n\n".join(code_blocks) if code_blocks else output
        
        # Determine chunk type
        chunk_type = ChunkType.IMPLEMENTATION
        output_lower = output.lower()
        if 'test' in output_lower:
            chunk_type = ChunkType.TEST
        elif 'refactor' in output_lower:
            chunk_type = ChunkType.REFACTOR
        elif 'design' in output_lower or 'architecture' in output_lower:
            chunk_type = ChunkType.DESIGN
        elif 'fix' in output_lower or 'bug' in output_lower:
            chunk_type = ChunkType.FIX
        
        # Extract description
        desc_match = re.search(r'^#+\s*(.+)$', output, re.MULTILINE)
        description = desc_match.group(1) if desc_match else "Code implementation"
        
        return CodeChunk(
            chunk_id=self._generate_chunk_id(),
            chunk_type=chunk_type,
            description=description[:100],
            content=content,
            file_path=file_path
        )
    
    def _parse_reviewer_output(self, output: str, chunk_id: str) -> ReviewFeedback:
        """Parse REVIEWER output into ReviewFeedback."""
        output_lower = output.lower()
        
        # Determine feedback type
        if any(word in output_lower for word in ['blocking', 'cannot proceed', 'critical']):
            feedback_type = FeedbackType.BLOCKING
        elif any(word in output_lower for word in ['major', 'significant', 'must fix']):
            feedback_type = FeedbackType.MAJOR
        elif any(word in output_lower for word in ['minor', 'small', 'nitpick']):
            feedback_type = FeedbackType.MINOR
        elif any(word in output_lower for word in ['question', 'clarify', 'unclear']):
            feedback_type = FeedbackType.QUESTION
        else:
            feedback_type = FeedbackType.APPROVE
        
        # Extract comments
        comments = []
        comment_patterns = [
            r'[-•]\s*(.+)',
            r'\d+\.\s*(.+)',
        ]
        for pattern in comment_patterns:
            matches = re.findall(pattern, output)
            comments.extend(matches[:10])
        
        # Extract must-fix issues
        must_fix = []
        must_fix_section = re.search(r'(?:must fix|blocking|required).*?:(.*?)(?:\n\n|\Z)', 
                                     output, re.IGNORECASE | re.DOTALL)
        if must_fix_section:
            issues = re.findall(r'[-•]\s*(.+)', must_fix_section.group(1))
            must_fix.extend(issues)
        
        # Extract suggestions
        suggestions = []
        suggestion_section = re.search(r'(?:suggest|consider|recommend).*?:(.*?)(?:\n\n|\Z)',
                                       output, re.IGNORECASE | re.DOTALL)
        if suggestion_section:
            sugs = re.findall(r'[-•]\s*(.+)', suggestion_section.group(1))
            suggestions.extend(sugs)
        
        # Check for approval
        approved = (
            feedback_type == FeedbackType.APPROVE or
            any(word in output_lower for word in ['lgtm', 'approved', 'looks good', 'ship it'])
        )
        
        return ReviewFeedback(
            chunk_id=chunk_id,
            feedback_type=feedback_type,
            comments=comments[:10],
            suggestions=suggestions[:5],
            must_fix=must_fix[:5],
            approved=approved
        )
    
    def _build_dev_prompt(self, task_part: str, context: str,
                          previous_feedback: Optional[ReviewFeedback] = None) -> str:
        """Build prompt for DEV agent."""
        
        base_prompt = f"""You are in a PAIR PROGRAMMING session with a REVIEWER.
Work in small, focused chunks. After each chunk, wait for reviewer feedback.

## Task
{task_part}

## Context
{context}
"""
        
        if previous_feedback:
            feedback_text = "\n".join([
                "## Reviewer Feedback (address these)",
                "",
                "**Issues to Fix:**",
                *[f"- ❌ {issue}" for issue in previous_feedback.must_fix],
                "",
                "**Suggestions:**",
                *[f"- 💡 {sug}" for sug in previous_feedback.suggestions],
            ])
            base_prompt += f"\n\n{feedback_text}\n"
        
        base_prompt += """
## Instructions
1. Implement ONE focused chunk of code
2. Show the file path and code clearly
3. Explain your approach briefly
4. Keep the chunk small enough for quick review
"""
        
        return base_prompt
    
    def _build_reviewer_prompt(self, chunk: CodeChunk, 
                               accumulated_code: str) -> str:
        """Build prompt for REVIEWER agent."""
        
        return f"""You are in a PAIR PROGRAMMING session reviewing DEV's work in real-time.

## Current Chunk to Review
**Type**: {chunk.chunk_type.value}
**Description**: {chunk.description}
**File**: {chunk.file_path or 'Not specified'}

```
{chunk.content}
```

## Accumulated Code So Far
```
{accumulated_code[-2000:] if len(accumulated_code) > 2000 else accumulated_code}
```

## Instructions
1. Review this chunk for:
   - Correctness
   - Code quality
   - Best practices
   - Potential bugs
   - Test coverage needs

2. Categorize issues as:
   - **BLOCKING**: Cannot proceed
   - **MUST FIX**: Required before merge
   - **SUGGESTION**: Nice to have

3. If the code is good, say "LGTM" or "Approved"

4. Be constructive and specific
"""
    
    def run(self) -> PairSessionResult:
        """Run the pair programming session."""
        start_time = datetime.now().isoformat()
        
        self._log(f"Starting pair session for: {self.task[:50]}...")
        
        # Break task into parts (for now, treat as single task)
        task_parts = [self.task]
        
        accumulated_code = ""
        total_revisions = 0
        approved_chunks = 0
        
        for i, task_part in enumerate(task_parts):
            self._log(f"Working on part {i+1}/{len(task_parts)}")
            
            # Get initial context
            context = f"Story: {self.story_key}\n"
            context += self.shared_memory.to_context_string(5)
            
            # DEV creates initial chunk
            self._log("Creating initial implementation...", "DEV")
            dev_prompt = self._build_dev_prompt(task_part, context)
            dev_output = self._invoke_agent("DEV", dev_prompt)
            
            chunk = self._parse_dev_output(dev_output)
            self._log(f"Created chunk: {chunk.description}", "DEV")
            
            # Track file
            if chunk.file_path:
                if chunk.file_path not in self.files_created and \
                   chunk.file_path not in self.files_modified:
                    self.files_created.append(chunk.file_path)
            
            accumulated_code += f"\n\n// {chunk.description}\n{chunk.content}"
            
            # REVIEWER reviews
            self._log("Reviewing chunk...", "REVIEWER")
            reviewer_prompt = self._build_reviewer_prompt(chunk, accumulated_code)
            reviewer_output = self._invoke_agent("REVIEWER", reviewer_prompt)
            
            feedback = self._parse_reviewer_output(reviewer_output, chunk.chunk_id)
            self._log(f"Feedback: {feedback.feedback_type.value}", "REVIEWER")
            
            exchange = PairExchange(
                exchange_id=self.exchange_counter,
                chunk=chunk,
                feedback=feedback,
                resolved=feedback.approved
            )
            self.exchange_counter += 1
            
            # Revision loop if needed
            revision_count = 0
            while feedback.has_blocking_issues() and \
                  revision_count < self.config.max_revisions_per_chunk:
                
                revision_count += 1
                total_revisions += 1
                self._log(f"Revision {revision_count} needed", "SYSTEM")
                
                # DEV revises
                self._log("Addressing feedback...", "DEV")
                dev_prompt = self._build_dev_prompt(task_part, context, feedback)
                dev_output = self._invoke_agent("DEV", dev_prompt)
                
                revised_chunk = self._parse_dev_output(dev_output)
                exchange.revision = revised_chunk
                
                # Update accumulated code
                accumulated_code += f"\n\n// Revision: {revised_chunk.description}\n{revised_chunk.content}"
                
                # REVIEWER re-reviews
                self._log("Re-reviewing...", "REVIEWER")
                reviewer_prompt = self._build_reviewer_prompt(revised_chunk, accumulated_code)
                reviewer_output = self._invoke_agent("REVIEWER", reviewer_prompt)
                
                feedback = self._parse_reviewer_output(reviewer_output, revised_chunk.chunk_id)
                exchange.feedback = feedback
                exchange.resolved = feedback.approved
                
                self._log(f"Feedback: {feedback.feedback_type.value}", "REVIEWER")
            
            if exchange.resolved or feedback.approved:
                approved_chunks += 1
                self._log("✅ Chunk approved!", "SYSTEM")
            else:
                self._log("⚠️ Moving on with unresolved issues", "SYSTEM")
            
            self.exchanges.append(exchange)
            
            # Record in shared memory
            self.shared_memory.add(
                agent="PAIR",
                content=f"Completed chunk: {chunk.description} ({feedback.feedback_type.value})",
                tags=["pair-programming", "chunk"]
            )
        
        # Calculate approval rate
        total_chunks = len(self.exchanges)
        approval_rate = approved_chunks / total_chunks if total_chunks > 0 else 0
        
        self._log(f"Session complete. Approval rate: {approval_rate:.0%}", "SYSTEM")
        
        return PairSessionResult(
            story_key=self.story_key,
            task=self.task,
            exchanges=self.exchanges,
            final_code=accumulated_code,
            files_created=self.files_created,
            files_modified=self.files_modified,
            total_chunks=total_chunks,
            total_revisions=total_revisions,
            approval_rate=approval_rate,
            start_time=start_time,
            end_time=datetime.now().isoformat()
        )


# Convenience functions
def start_pair_session(story_key: str, task: str,
                       **config_kwargs) -> PairSession:
    """Start a new pair programming session."""
    config = PairConfig(**config_kwargs)
    return PairSession(story_key, task, config)


def run_pair_session(story_key: str, task: str,
                     **config_kwargs) -> PairSessionResult:
    """Run a complete pair programming session."""
    session = start_pair_session(story_key, task, **config_kwargs)
    return session.run()


if __name__ == "__main__":
    print("=== Pair Programming Mode Demo ===\n")
    print("This module enables real-time DEV + REVIEWER collaboration.")
    print("\nExample usage:")
    print("""
    from lib.pair_programming import run_pair_session

    result = run_pair_session(
        story_key="3-5",
        task="Implement user authentication endpoint",
        max_revisions_per_chunk=2,
        verbose=True
    )
    
    print(result.to_summary())
    print(f"Approval rate: {result.approval_rate:.0%}")
    """)
