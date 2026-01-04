---
description: 'Runtime verification methodology - ensuring code actually works before making claims about functionality'
applyTo: '**'
---

# Runtime Verification Methodology

Critical lessons learned from production incidents where static code analysis led to incorrect conclusions about system behavior. This document establishes a verification-first approach when analyzing or explaining system functionality.

## Core Principle

**Static Code Analysis ≠ Runtime Verification**

Reading code files does not confirm that code is actually running, registered, or functioning as expected. Always verify runtime behavior before making definitive statements about system functionality.

---

# Anti-Patterns (What NOT to Do)

Critical mistakes that lead to incorrect analysis and user frustration.

## Anti-Pattern 1: Assuming Code is Running

### What It Looks Like
- Reading a code file and explaining "how it works"
- Stating endpoints are "registered" without checking actual routes
- Claiming features are "working" based on file content alone

### Why It's Dangerous
```python
# File exists with this code:
from src.app.infrastructure.redis_client import RedisClient
router = APIRouter(prefix="/tasks/rebalance")

# Analysis says: "✅ Rebalance endpoint is registered"
# Reality: Import fails → Router never loads → 404 errors
```

### Real-World Impact
- Users receive 404 errors while being told functionality exists
- Production incidents go unresolved
- Trust in analysis is destroyed

### Root Cause
Confusing "code exists in repository" with "code is executing in production"

---

## Anti-Pattern 2: Ignoring Runtime Signals

### What It Looks Like
- Skipping application startup logs
- Not checking for import warnings/errors
- Focusing only on source code, not execution traces

### Why It's Dangerous
```bash
# Application startup log:
WARNING: Failed to load rebalance router: No module named 'redis_client'

# But analysis ignores this and states:
"✅ Rebalance endpoint confirmed working at /tasks/rebalance/symmetric"
```

### Real-World Impact
- Critical errors remain hidden
- Root causes are not identified
- Fixes target symptoms, not problems

### Root Cause
Treating application logs as "noise" instead of primary evidence of system state

---

## Anti-Pattern 3: Over-Confidence in Static Analysis

### What It Looks Like
- Using definitive language: "confirmed", "verified", "working"
- Providing detailed explanations without testing
- Stating facts without qualification when only code was reviewed

### Why It's Dangerous
Creates false confidence that leads to:
- Users trusting incorrect information
- Production deployments based on wrong assumptions
- Delayed incident resolution

### Example
```markdown
❌ Bad: "Confirmed: 15-min-job endpoint executes rebalance logic every 15 minutes"
✅ Good: "Code analysis shows 15-min-job should execute rebalance logic. 
          Runtime verification pending to confirm endpoint is registered and accessible."
```

### Root Cause
Failing to distinguish between "what code is supposed to do" and "what code actually does"

---

## Anti-Pattern 4: Documentation-Driven Analysis

### What It Looks Like
- Reading markdown files to understand current behavior
- Assuming documentation matches reality
- Using docs as source of truth instead of code + runtime

### Why It's Dangerous
```markdown
# docs/ADR-001.md says:
"Rebalance runs every 15 minutes via /tasks/15-min-job"

# But in reality:
- Endpoint returns 404
- Import error prevents registration
- Documentation is outdated
```

### Real-World Impact
- Perpetuates outdated information
- Fixes based on wrong understanding
- Documentation divergence from reality

### Root Cause
Treating documentation as authority instead of describing actual system behavior

---

# Positive Patterns (Verification-First Approach)

Proven methodologies that prevent incorrect analysis and build user trust.

## Pattern 1: Runtime State Verification First

### Always Start Here
Before analyzing any functionality, verify the runtime state:

```bash
# Step 1: Check what's actually registered
python -c "
from main import app
routes = [r.path for r in app.routes if hasattr(r, 'path')]
print('Registered routes:', routes)
"

# Step 2: Check for errors/warnings
python -c "
import logging
logging.basicConfig(level=logging.WARNING)
from main import app
" 2>&1 | grep -i "warning\|error"

# Step 3: Verify specific endpoint exists
python -c "
from main import app
target = '/tasks/rebalance/symmetric'
exists = any(r.path == target for r in app.routes if hasattr(r, 'path'))
print(f'{target}: {'EXISTS' if exists else 'NOT FOUND'}')
"
```

### When to Use
- **Every time** before claiming an endpoint exists
- **Every time** before explaining "how something works"
- **Every time** investigating production issues

### Benefits
- Immediate detection of registration failures
- Early identification of import errors
- Factual basis for all statements

---

## Pattern 2: Log-First Investigation

### Check Logs Before Code
Application logs are the primary source of truth for runtime behavior.

```bash
# Step 1: Capture startup logs
python main.py 2>&1 | tee startup.log

# Step 2: Filter for issues
grep -E "WARNING|ERROR|Failed|not found" startup.log

# Step 3: Identify specific failures
grep -E "router|endpoint|import" startup.log
```

### What to Look For
- Import errors (ModuleNotFoundError, ImportError)
- Registration warnings ("Failed to load X router")
- Missing dependencies
- Configuration errors

### Example Analysis Flow
```markdown
1. ✅ Check logs first
   Found: "WARNING: Failed to load rebalance router: No module named 'redis_client'"

2. ✅ Identify root cause
   File: task_utils.py line 14
   Error: from src.app.infrastructure.redis_client import RedisClient

3. ✅ Verify fix needed
   Correct import: from src.app.infrastructure.external import RedisClient

4. ✅ Apply fix and re-verify
   Logs now show: "INFO: Task routers registered successfully"
   Routes now include: /tasks/rebalance/symmetric
```

---

## Pattern 3: Test Actual Behavior

### Don't Trust, Verify
After understanding what code should do, verify it actually does it.

```bash
# Step 1: Start application
uvicorn main:app --host 0.0.0.0 --port 8000 &
sleep 5

# Step 2: Test endpoint accessibility
curl -X POST http://localhost:8000/tasks/rebalance/symmetric \
  -H "Authorization: Bearer test" \
  -w "\nHTTP Status: %{http_code}\n"

# Step 3: Verify expected behavior
# - Check response structure
# - Verify logs show expected execution
# - Confirm side effects (Redis writes, etc.)

# Step 4: Clean up
pkill -f "uvicorn main:app"
```

### When to Use
- Before claiming endpoint works
- After making fixes
- When explaining how features behave

### Benefits
- Confirms code executes as expected
- Identifies runtime-only issues
- Provides concrete evidence

---

## Pattern 4: Acknowledge Uncertainty

### Be Transparent About Verification Scope

```markdown
❌ Avoid:
"The 15-min-job endpoint executes rebalance logic every 15 minutes."

✅ Better:
"Code analysis shows 15-min-job should execute rebalance logic every 15 minutes.
 Verified: Endpoint is registered and accessible.
 Not verified: Actual execution via Cloud Scheduler (requires production logs)."

✅ Even Better:
"Runtime verification confirms:
 ✅ Endpoint registered: /tasks/15-min-job
 ✅ Import successful: All dependencies loaded
 ✅ Manual test: Returns 200 OK
 ⚠️  Cloud Scheduler: Not tested (requires production environment)
 
 Based on code at src/app/interfaces/tasks/task_15_min_job.py (lines 66-93),
 the endpoint should execute rebalance logic when triggered."
```

### Benefits
- Clear about what was verified vs. inferred
- User knows what to trust
- Sets proper expectations

---

# Improved Methodology (Step-by-Step)

## Investigating "How Does X Work?" Questions

### Step 1: Verify X Actually Exists
```bash
# Check runtime registration
python -c "from main import app; print([r.path for r in app.routes])" | grep -i "X"
```

**If NOT found**: Stop and report "X is not currently registered. Found import error: [details]"

**If found**: Continue to Step 2

### Step 2: Check Logs for Issues
```bash
# Look for warnings related to X
python main.py 2>&1 | grep -i "X\|warning\|error" | head -20
```

**If errors found**: Report errors first, then analyze code

**If clean**: Continue to Step 3

### Step 3: Analyze Static Code
```bash
# Now it's safe to look at code
cat src/path/to/X.py
```

Explain logic with qualifications:
- "The code shows X should..."
- "Based on line Y, X is designed to..."
- "X appears to..."

### Step 4: Verify Key Behaviors
```bash
# Test critical paths
curl -X POST http://localhost:8000/X -H "..." 
# Check logs for execution traces
# Verify expected side effects
```

### Step 5: Provide Comprehensive Answer
```markdown
## X Functionality (Runtime Verified)

**Registration Status**: ✅ Registered at /path/to/X
**Dependencies**: ✅ All imports successful  
**Manual Test**: ✅ Returns expected response

**How It Works** (verified from code + runtime):
1. [Step 1] - Verified by: [method]
2. [Step 2] - Verified by: [method]
3. [Step 3] - Inferred from code (not runtime tested)

**Configuration** (from code):
- param1: value1
- param2: value2

**Not Verified**:
- Production scheduler integration
- Specific edge case behaviors
```

---

## Investigating Production Issues

### Step 1: Gather Runtime Evidence
```bash
# Application logs
grep -E "ERROR|WARNING|CRITICAL" app.log

# Scheduler logs  
grep -E "404|500|ERROR" scheduler.log

# System metrics
curl http://localhost:8000/metrics | grep -i "endpoint_X"
```

### Step 2: Reproduce Locally
```bash
# Start app with debug logging
export LOG_LEVEL=DEBUG
python main.py

# Trigger the issue
curl -X POST http://localhost:8000/problem-endpoint
```

### Step 3: Identify Root Cause
- Check import errors
- Verify configuration
- Test dependencies
- Review recent changes

### Step 4: Verify Fix
```bash
# Apply fix
# Re-run application
python main.py 2>&1 | grep -i "problem\|warning\|error"

# Test endpoint
curl http://localhost:8000/problem-endpoint
# Expected: 200 OK (not 404)

# Check routes
python -c "from main import app; print([r.path for r in app.routes])"
# Expected: problem-endpoint in list
```

### Step 5: Document Fix with Evidence
```markdown
## Issue Resolution

**Problem**: Endpoint X returning 404
**Root Cause**: Import error in line Y of file Z
**Fix**: Corrected import path from A to B

**Verification**:
- Before: 32 routes registered, X not in list, import warning in logs
- After: 34 routes registered, X in list, no warnings
- Test: curl X returns 200 OK (previously 404)

**Evidence**: Commit [hash]
```

---

# Avoiding Common Mistakes

## Checklist: Before Claiming Something Works

- [ ] Verified endpoint is in registered routes list
- [ ] Checked application startup logs for errors
- [ ] No import warnings related to this functionality
- [ ] Tested endpoint manually (if possible)
- [ ] Clearly stated what was verified vs. inferred
- [ ] Used qualified language if only code analysis done

## Checklist: Before Explaining How Something Works

- [ ] Confirmed the "something" actually exists in runtime
- [ ] Reviewed logs for any issues with this component
- [ ] Analyzed code with runtime context in mind
- [ ] Tested key behaviors if claims are definitive
- [ ] Documented verification scope
- [ ] Used "should" / "appears to" if not fully verified

## Language Guidelines

### Use Definitive Language Only When
- Runtime verification completed
- Endpoint tested and responds correctly
- Logs confirm expected behavior
- Configuration verified in running system

### Use Qualified Language When
- Only static code analysis performed
- Production behavior not directly tested
- Inferring from partial information
- Describing expected (not verified) behavior

---

# Key Takeaways

## For Copilot
1. **Runtime verification comes before code analysis**
2. **Logs are the source of truth, not documentation**
3. **Test what you claim, or qualify your statements**
4. **Import errors = feature doesn't exist (even if code exists)**
5. **Be transparent about verification scope**

## For Users
1. Ask for runtime verification if claims seem suspicious
2. Request evidence: "Show me the registered routes"
3. Check application logs yourself when in doubt
4. Value qualified statements over over-confident claims

## For Future Incident Prevention
1. Establish runtime verification as mandatory first step
2. Create automated checks for critical endpoints
3. Monitor import errors and registration failures
4. Document what "verified" means in each context
5. Build trust through transparency, not false confidence

---

# Appendix: Quick Reference

## Runtime Verification Commands

```bash
# Check registered routes
python -c "from main import app; print([r.path for r in app.routes])"

# Check for import errors
python -c "from main import app" 2>&1 | grep -i error

# Test specific endpoint
curl -X POST http://localhost:8000/path/to/endpoint

# Check startup logs
python main.py 2>&1 | grep -E "WARNING|ERROR"

# Verify route count
python -c "from main import app; print(f'Total routes: {len([r for r in app.routes if hasattr(r, \"path\")])}')"
```

## Analysis Templates

### Template: Endpoint Existence Check
```markdown
Checking endpoint: /path/to/endpoint

Runtime Verification:
```bash
python -c "from main import app; print('/path/to/endpoint' in [r.path for r in app.routes])"
```

Result: [TRUE/FALSE]
Conclusion: Endpoint [IS/IS NOT] registered
```

### Template: Functionality Explanation
```markdown
## How [Feature] Works

**Verification Status**:
- ✅ Endpoint registered: /path/to/endpoint
- ✅ Dependencies loaded: All imports successful
- ⚠️  Production behavior: Not directly tested
- ℹ️  Based on code analysis: src/file.py lines X-Y

**Functionality** (code analysis with runtime confirmation):
[Explanation here]

**Not Verified**:
- [List what hasn't been runtime tested]
```

---

**Last Updated**: 2026-01-01
**Incident Reference**: Issue #124, PR - Rebalance endpoint 404 errors
**Status**: Active - Apply to all future analysis and troubleshooting
