# **README_verification.md**

```markdown
# Phase 3.5 Verification Tools

**Purpose:** Verify constitutional compliance without expanding capability  
**Phase:** 3.5 (Trust, Visibility & Interpretive Awareness)  
**Authority:** NON-BINDING verification only  
**Effect on System:** Read-only, no state changes  

---

## 🔍 OVERVIEW

This directory contains verification tools for Phase 3.5. These tools exist to **prove governance is structurally real**, not to add capability or authority.

**Constitutional Principle:**  
Verification must remain:
- Read-only
- Non-invasive
- Phase-aligned
- Transparent in operation

---

## 🛠 TOOLS

### 1. Quarantine Verification (`check_quarantine_fixed.ps1`)

**Purpose:** Verify legacy execution code is properly isolated and cannot be imported.

**What it checks:**
- Legacy brain file exists only in quarantine directory
- No copies exist in active runtime paths
- No imports of quarantined code in active runtime
- Quarantine directory not in Python import path
- Dynamic import attempts fail as expected

**Run:**
```powershell
cd /path/to/repository/root
./verification/check_quarantine_fixed.ps1
```

**Expected Outcome:**  
✅ All checks pass with exit code 0

**Exit Codes:**
- `0`: Quarantine intact, no bypass paths
- `1`: Critical failure (legacy code in runtime path)
- `2`: Configuration issue (file not found, paths invalid)

---

### 2. Governor Mediation Proof (`governor_proof.py`)

**Purpose:** Verify all execution flows through Governor as single choke point.

**What it checks:**
- Governor module exists and contains execution functions
- No execution patterns outside Governor modules
- No imports from quarantine directories
- Static analysis of potential bypass paths

**Run:**
```bash
cd /path/to/repository/root
python verification/governor_proof.py
```

**Expected Outcome:**  
✅ Verification passes with exit code 0

**Exit Codes:**
- `0`: Governor mediation verified
- `1`: Governor missing or bypass detected

**Analysis Types:**
- **Static analysis only** - no code execution
- **AST parsing** - not regex, understands Python syntax
- **Conservative matching** - errs toward manual review

---

## 📋 INTEGRATION

### CI/CD Pipeline

These tools are integrated into the CI pipeline:

```yaml
# .github/workflows/phase-3.5-verification.yml
jobs:
  verify:
    steps:
      - name: Quarantine Verification
        run: ./verification/check_quarantine_fixed.ps1
      
      - name: Governor Mediation Proof
        run: python verification/governor_proof.py
```

**Phase Gate:** Both checks must pass for Phase 3.5 to be considered complete.

---

## 🧪 TESTING STRATEGY

### Verification Categories

| Category | Method | Phase Relevance |
|----------|--------|----------------|
| **Static Compliance** | AST analysis, pattern matching | Phase 3.5 Core |
| **Import Isolation** | Path checking, import simulation | Phase 3.5 Core |
| **Configuration Validation** | File existence, path validation | Phase 3.5 Core |
| **Runtime Behavior** | NOT INCLUDED (Phase 4+) | Future phases |

### Why No Runtime Tests in Phase 3.5

Phase 3.5 focuses on **structural verification**, not behavioral testing. Runtime tests imply execution capability, which Phase 3 intentionally lacks.

---

## 📊 INTERPRETING RESULTS

### Pass Conditions

**Phase 3.5 Completion requires:**

1. ✅ Quarantine verification passes (exit 0)
2. ✅ Governor proof passes (exit 0)
3. ✅ CI runs both checks on all commits

### Failure Modes

| Failure | Meaning | Required Action |
|---------|---------|----------------|
| **Quarantine breach** | Legacy code importable | Fix import paths, verify isolation |
| **Governor missing** | No Governor module found | Implement Governor mediation layer |
| **Execution bypass** | Code outside Governor can execute | Move execution to Governor or remove |
| **False positive** | Tool incorrectly flags issue | Review and adjust verification rules |

---

## 🔒 SECURITY & SAFETY

### Verification Tool Constraints

These tools are intentionally constrained:

1. **No execution authority** - cannot run arbitrary code
2. **No network access** - operate entirely locally
3. **No state mutation** - read-only file analysis
4. **No inference** - deterministic pattern matching only
5. **No persistence** - results not saved between runs

### Constitutional Alignment

All verification tools:
- Respect Phase 3.5 boundaries (no Phase 4 work)
- Maintain offline-first posture (no network calls)
- Are transparent in operation (no hidden behavior)
- Fail conservatively (err toward manual review)

---

## 🚀 PHASE PROGRESSION

### Current Status: Phase 3.5 Active

**Verification Requirements Met:**
- [x] Quarantine isolation verified
- [x] Governor mediation verified
- [x] CI enforcement established

**Next Phase (4) Prerequisites:**
1. Phase 3.5 completion certificate signed
2. Governance review of Phase 4 proposals
3. Constitutional compliance verification
4. No automatic progression

### Phase Transition Rules

1. **No skipping** - Phase 4 remains blocked until 3.5 complete
2. **Governance review required** - not automatic
3. **Verification preserved** - all checks remain active
4. **Documentation updated** - phase reality reflected

---

## 📝 MAINTENANCE

### Adding New Verification

New verification tools must:
1. Remain read-only and non-invasive
2. Focus on structural verification, not capability
3. Maintain Phase 3.5 alignment (no execution testing)
4. Include clear documentation in this README
5. Be integrated into CI pipeline

### Tool Updates

When modifying verification tools:
1. **Test thoroughly** - avoid breaking existing verification
2. **Document changes** - update this README
3. **Preserve constraints** - maintain constitutional alignment
4. **Review phase impact** - ensure no Phase 4 capability creep

---

## 🧭 NAVIGATION

### Repository Context

```
nova_lis/
├── verification/              ← YOU ARE HERE
│   ├── check_quarantine_fixed.ps1
│   ├── governor_proof.py
│   └── README_verification.md
├── nova_backend/             # Active runtime
├── NovaLIS-Governance/       # Governance documents
└── .github/workflows/        # CI/CD pipelines
```

### Related Documentation

- [FINAL CANONICAL TRUTH-NovaLIS.txt](../FINAL%20CANONICAL%20TRUTH-NovaLIS.txt) - Supreme authority
- [REPO_MAP.md](../REPO_MAP.md) - Repository navigation
- [CONTRIBUTING.md](../CONTRIBUTING.md) - Contribution rules
- [PHASE_3_COMPLETION.md](../docs/PHASE_3_COMPLETION.md) - Phase 3 status

---

## ⚠️ DISCLAIMERS

### Authority Limitations

These tools:
- **Do not** grant execution authority
- **Do not** bypass governance layers
- **Do not** constitute Phase 4 work
- **Do not** replace manual review

### Phase Boundaries

Verification is scoped to Phase 3.5:
- **Includes:** Structural verification, import isolation, static analysis
- **Excludes:** Runtime testing, execution capability, behavioral verification
- **Blocks:** Phase 4 progression until verification complete

### Constitutional Compliance

All verification activities must respect:
- 8 Constitutional Invariants
- Phase-gated capability model
- Single Master Governor requirement
- Non-autonomous identity

---

## 🔍 TROUBLESHOOTING

### Common Issues

| Issue | Solution |
|-------|----------|
| **PowerShell execution policy** | Run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| **Python import errors** | Ensure running from repository root directory |
| **False positives** | Review flagged code, adjust verification patterns if needed |
| **CI failures** | Check exit codes, review tool output in CI logs |

### Debug Mode

Add verbose output:
```powershell
# PowerShell
$VerbosePreference = "Continue"
./verification/check_quarantine_fixed.ps1

# Python
python verification/governor_proof.py --verbose
```

---

## 📞 SUPPORT

### Questions & Issues

1. **Review documentation** - Start with FINAL CANONICAL TRUTH
2. **Check phase alignment** - Ensure question respects phase boundaries
3. **Document thoroughly** - Include exact commands, outputs, and context
4. **Escalate to governance** - Constitutional questions require governance review

### Emergency Procedures

If verification reveals constitutional violation:
1. **Stop all work** - Do not proceed with changes
2. **Document violation** - Capture exact evidence
3. **Notify governance** - Escalate immediately
4. **Do not attempt fix** - Wait for governance review

---

**Last Updated:** 2026-02-05  
**Phase:** 3.5 Active  
**Next Review:** Phase 4 proposal gate  
**Document Authority:** Verification-only (non-binding)

---

> *"Verification without execution, proof without power."*  
> — Phase 3.5 Principle
```

## **KEY FEATURES OF THIS README:**

1. **Phase-aligned** - Clearly states Phase 3.5 scope and boundaries
2. **Constitutionally sound** - Respects all 8 constitutional invariants
3. **Practical guidance** - Exact commands and troubleshooting
4. **No capability expansion** - Verification only, no execution
5. **Clear boundaries** - What's included vs excluded in Phase 3.5
6. **CI/CD integration** - Shows how tools fit into automation
7. **Emergency procedures** - What to do if violations are found
8. **Non-binding authority** - Correctly framed as verification tools only

## **PLACEMENT:**
```
/verification/README_verification.md
```

This README serves as the definitive guide to Phase 3.5 verification, maintaining the constitutional principles while providing practical utility. It's ready to commit as-is.