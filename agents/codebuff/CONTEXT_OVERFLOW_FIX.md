# Context Overflow Fix - Spec-Kit Workflow

## Problem
The spec-kit workflow was hitting the 400K token context limit (1.4M tokens attempted) when running, causing `ModelHTTPError` with message:
```
This endpoint's maximum context length is 400000 tokens.
However, you requested about 1433179 tokens...
```

## Root Cause
The workflow was accumulating massive amounts of context through:
1. **Unbounded exploration**: File explorer agent gathering too much codebase context
2. **No truncation**: Codebase context passed to multiple LLM calls without size limits
3. **Web scraping bloat**: Failed web requests (404 pages) adding massive HTML to context
4. **Accumulated state**: Multiple phases building on previous context without cleanup

## Fixes Applied

### Constants Defined (`speckit_workflow.py`)
- `MAX_EXPLORATION_CHARS = 5000` - Limit for exploration output
- `MAX_CONTEXT_CHARS = 8000` - Limit for context passed to LLM phases
- `MAX_SAVED_CONTEXT_CHARS = 10000` - Limit for saved state (currently unused)

### 1. Exploration Phase (`speckit_workflow.py:explore_codebase`)
- Limited explorer prompt to request concise output (<500 words)
- Added 5,000 character hard limit on exploration output using `MAX_EXPLORATION_CHARS`
- Changed `logging.error()` to `logging.exception()` for better debugging
- Added error handling with minimal fallback context
- Prevents unbounded context growth from file exploration

### 2. Constitution Generation (`speckit_workflow.py:create_constitution`)
- Added 8,000 character limit on codebase context input using `MAX_CONTEXT_CHARS`
- Truncates with warning before LLM call
- Prevents overflow in Phase 1

### 3. Spec Generation (`speckit_workflow.py:create_spec`)
- Added 8,000 character limit on task description using `MAX_CONTEXT_CHARS`
- Truncates with warning before LLM call
- Prevents overflow in Phase 2

### 4. Task Planning (`speckit_workflow.py:create_task_plan`)
- Added 8,000 character limit on codebase context input using `MAX_CONTEXT_CHARS`
- Truncates with warning before LLM call
- Prevents overflow in Phase 3

### 5. Main Workflow (`agent.py:run_speckit_workflow`)
- Removed redundant 10k truncation (exploration already limits to 5k)
- Wrapped exploration in try/catch with minimal fallback
- Added comment explaining exploration already has internal limits
- Prevents cascading failures from exploration errors

## Testing Recommendations

1. **Monitor context sizes**: Check logs for truncation warnings
2. **Test with large repos**: Ensure limits work for big codebases
3. **Verify quality**: Confirm truncated context still produces good results
4. **Adjust limits**: May need to tune character limits based on real usage

## Future Improvements

1. **Smart truncation**: Instead of simple character limits, intelligently summarize context
2. **Progressive loading**: Load context in stages as needed rather than all upfront
3. **Context pruning**: Remove old/irrelevant context between phases
4. **Better exploration**: Use more targeted file selection instead of broad exploration
5. **Caching**: Reuse exploration results across multiple runs

## Configuration

Current hard limits (defined as constants in `speckit_workflow.py`):
- `MAX_EXPLORATION_CHARS = 5000` - Exploration output limit
- `MAX_CONTEXT_CHARS = 8000` - Context limit for all LLM phases
- `MAX_SAVED_CONTEXT_CHARS = 10000` - Reserved for future use

To adjust limits, modify the constants at the top of `agents/codebuff/src/codebuff/orchestrator/speckit_workflow.py`.

## Code Review Findings Addressed

✅ Added `import logging` (was already present)
✅ Changed `logging.error()` to `logging.exception()` for full tracebacks
✅ Defined character limits as named constants
✅ Removed redundant truncation in main workflow
✅ Added context limit to `create_spec()` function
