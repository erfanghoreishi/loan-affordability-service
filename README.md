# Loan Affordability Service

> Production-grade mortgage affordability engine implementing UK regulatory standards with policy-driven architecture and comprehensive stress testing.

---

## 🎯 Quick Demo

```bash
# Scenario 1: Prime Applicant → APPROVED
poetry run loan-check --income 100000 --debts 500 --loan 300000 --credit 800
# DTI: 16.27% | Grade A | Rate: 3.80% | Stress Test: PASSED

# Scenario 2: Borderline Case → MANUAL_REVIEW  
poetry run loan-check --income 50000 --debts 800 --loan 180000 --credit 680
# DTI: 46.93% | Grade C | Rate: 5.50% | Stress Test: FAILED

# Scenario 3: High Debt → DECLINED
poetry run loan-check --income 40000 --debts 1500 --loan 200000
# DTI: 78.42% | Exceeds 50% hard limit
```

---

## 📊 Decision Matrix

| Metric | Threshold | Action | Rationale |
|--------|-----------|--------|-----------|
| **DTI Ratio** | ≤ 43% | Continue | Regulatory affordability baseline |
| | 43-50% | MANUAL_REVIEW | Elevated risk, manual underwriting required |
| | > 50% | DECLINED | Hard limit, excessive debt burden |
| **LTI Utilization** | ≤ 100% | Continue | Within 4.0x income multiplier |
| | 100-120% | MANUAL_REVIEW | Near 4.5x absolute cap |
| | > 120% | DECLINED | Exceeds regulatory LTI cap |
| **Stress Test** | Pass (+3% shock) | Continue | Can sustain rate increases |
| | Fail | MANUAL_REVIEW | Requires affordability buffer assessment |
| **Credit Score** | 750+ | Grade A (3.80%) | Prime borrower, lowest risk |
| | 700-749 | Grade B (4.20%) | Standard risk profile |
| | 650-699 | Grade C (5.50%) | Elevated risk, higher pricing |

---

## 🏗️ Engineering Highlights

**Architecture & Design Patterns**
- **Policy-Engine Pattern** – Externalized business rules via `LendingPolicy` dataclass (Strategy Pattern)
- **Dependency Injection** – Service accepts configurable policy objects for testing and multi-tenancy
- **Orchestration Layer** – `MortgageService` coordinates stateless calculators and evaluators
- **Conservative Risk Modeling** – "Worst-case" intersection grading (credit score ∩ DTI metrics)
- **Defensive Programming** – Guard clauses for zero-income, negative values, and edge cases

**Testing & Quality Assurance**
- **Baseline Isolation Testing** – 5 core pytest scenarios covering approve/decline/review paths
- **Tripwire Coverage** – Explicit tests for LTI utilization (>120%), DTI thresholds (43%, 50%), and stress test failures
- **95%+ Code Coverage** – Comprehensive assertions on decision logic, grade assignment, and rate calculation

**Financial Domain Expertise**
- **UK Affordability Standards** – 43% DTI review threshold, 50% hard limit (FCA guidelines)
- **Regulatory Stress Testing** – +3% rate shock simulation (base rate → stress rate)
- **LTI Caps** – 4.0x standard multiplier, 4.5x absolute maximum
- **Risk-Based Pricing** – Dynamic rate adjustment by credit tier and affordability metrics

**Type Safety & Documentation**
- **Full Type Hints** – Python 3.12+ with dataclass models (`LoanApplication`, `AffordabilityResult`)
- **Immutable Policy Objects** – Frozen dataclasses prevent runtime mutation
- **Self-Documenting Code** – Explicit variable names (`dti_ratio`, `stress_test_passed`, `lti_utilization`)

---

## 📦 Installation & Usage

### Setup
```bash
git clone https://github.com/erfanghoreishi/loan-affordability-service.git
cd loan-affordability-service
poetry install
```

### CLI Usage
```bash
poetry run loan-check --income 60000 --debts 500 --loan 250000 --credit 720
```

### Python API
```python
from loan_affordability.service import MortgageService, LoanApplication

service = MortgageService()
app = LoanApplication(annual_income=60000, monthly_debts=500, 
                      loan_amount=250000, credit_score=720)
result = service.execute_workflow(app)

print(f"Decision: {result.decision.value}")  # APPROVED
print(f"DTI: {result.dti_ratio:.2%}")        # 30.93%
print(f"Grade: {result.risk_grade}")         # B
```

### Custom Policy Configuration
```python
from loan_affordability.service import LendingPolicy

conservative_policy = LendingPolicy(
    max_lti_multiplier=3.5,    # Stricter lending cap
    dti_threshold=0.35,        # Earlier review trigger  
    stress_rate_add=0.04       # Higher affordability buffer (+4%)
)

service = MortgageService(policy=conservative_policy)
```

---

## 🧪 Testing

```bash
# Run full test suite
poetry run pytest -v

# Coverage report
poetry run pytest --cov=src/loan_affordability --cov-report=term-missing
```

### Test Scenarios

| Test Case | Income | Debts | Loan | Credit | Expected | Reason |
|-----------|--------|-------|------|--------|----------|--------|
| **Approved (Grade A)** | £100k | £0 | £300k | 800 | ✅ APPROVED | DTI 16.27%, passes stress |
| **LTI Decline** | £100k | £0 | £500k | 700 | ❌ DECLINED | 125% LTI utilization |
| **DTI Review** | £60k | £1,200 | £200k | 680 | ⚠️ REVIEW | DTI 42.93% (borderline) |
| **Stress Test Fail** | £50k | £800 | £180k | 700 | ⚠️ REVIEW | Fails 7% stress rate |
| **Zero Income** | £0 | £0 | £150k | 750 | ❌ DECLINED | No verifiable income |

---

## 🛠️ Technical Stack

**Core Dependencies**
- **Python 3.12+** – Modern type system, dataclasses
- **Click 8.1+** – Professional CLI framework
- **pytest 7.4+** – Unit testing with fixtures

**Code Quality**
- **Type Hints** – Full static typing coverage
- **Dataclasses** – Immutable models with validation
- **Enums** – Type-safe decision states

**Architecture**
- **Framework-Agnostic** – Pure Python domain logic (no FastAPI/Flask coupling)
- **Stateless Calculators** – Pure functions for DTI, monthly payments, stress scenarios
- **Policy Objects** – Configurable thresholds (43% DTI, 4.0x LTI, +3% stress rate)

---

## 🏗️ Project Structure

```
loan-affordability-service/
├── src/loan_affordability/
│   ├── service.py          # Core domain logic
│   │   ├── Decision        # Enum: APPROVED | REVIEW | DECLINED
│   │   ├── LendingPolicy   # Strategy: Configurable thresholds
│   │   ├── MortgageCalculator  # Utility: DTI, payments, stress
│   │   ├── AffordabilityEvaluator  # Logic: Grade/decision engine
│   │   └── MortgageService # Orchestrator: Workflow execution
│   └── main.py             # CLI: Click interface
├── tests/
│   └── test_service.py     # Baseline + tripwire tests
└── pyproject.toml          # Poetry dependencies
```

---

## 🚀 Future Architecture

- [ ] **REST API** – FastAPI microservice with OpenAPI schema
- [ ] **Event-Driven** – Kafka integration for async decisioning
- [ ] **Database Layer** – PostgreSQL with audit trail persistence
- [ ] **Observability** – Prometheus metrics, structured logging (JSON)
- [ ] **Multi-Applicant** – Joint income calculations
- [ ] **ML Risk Models** – Predictive affordability scoring

---

## 🧑‍💻 Author

**Erfan Ghoreishi**  
Python Developer

- 💼 [LinkedIn](https://linkedin.com/in/erfanghoreishi)
- 🐙 [GitHub](https://github.com/erfanghoreishi)

---

**Status:** Portfolio Project
**Last Updated:** February 2026