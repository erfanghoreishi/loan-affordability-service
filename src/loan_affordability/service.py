"""
Loan Affordability Calculator

A mortgage affordability assessment tool that evaluates loan applications
based on DTI ratios, stress testing, LTI caps, and risk-based pricing.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Tuple, Optional


class Decision(Enum):
    """Loan decision outcomes."""
    APPROVED = "APPROVED"
    REVIEW = "MANUAL_REVIEW"
    DECLINED = "DECLINED"


@dataclass
class LoanApplication:
    """Input data for a loan application."""
    annual_income: float
    monthly_debts: float
    loan_amount: float
    credit_score: int = 700
    base_rate: float = 0.04
    stress_rate: float = 0.052
    term_years: int = 25


@dataclass
class AffordabilityResult:
    """Output data from affordability assessment."""
    max_mortgage: float
    monthly_payment: float
    dti_ratio: float
    stress_test_passed: bool
    decision: Decision
    risk_grade: Optional[str]  # ← None for DECLINED
    recommended_rate: Optional[float]  # ← None for DECLINED


@dataclass
class LendingPolicy:
    """Configurable lending policy thresholds and multipliers."""
    max_dti: float = 0.50
    review_threshold: float = 0.43
    stress_threshold: float = 0.43
    base_market_rate: float = 0.042
    default_review_grade: str = "C"

    # LTI (Loan-to-Income) limits
    max_lti_excess: float = 1.2  # Max 20% over calculated limit
    review_lti_excess: float = 1.1  # Flag for review if 10%+ over

    multipliers: Dict[int, float] = field(default_factory=lambda: {
        750: 4.5, 700: 4.0, 650: 3.5, 0: 3.0
    })
    credit_grades: Dict[int, str] = field(default_factory=lambda: {
        750: "A", 700: "B", 0: "C"
    })
    dti_grades: Dict[float, str] = field(default_factory=lambda: {
        0.30: "A", 0.40: "B", 1.00: "C"
    })
    rate_adjustments: Dict[str, float] = field(default_factory=lambda: {
        "A": -0.004, "B": 0.000, "C": 0.013
    })

    def get_multiplier(self, score: int) -> float:
        """Return income multiplier based on credit score."""
        for threshold in sorted(self.multipliers.keys(), reverse=True):
            if score >= threshold:
                return self.multipliers[threshold]
        return 3.0

    def get_credit_grade(self, score: int) -> str:
        """Return grade based on credit score."""
        for threshold in sorted(self.credit_grades.keys(), reverse=True):
            if score >= threshold:
                return self.credit_grades[threshold]
        return "C"

    def get_dti_grade(self, dti: float) -> str:
        """Return grade based on DTI ratio."""
        for threshold in sorted(self.dti_grades.keys()):
            if dti <= threshold:
                return self.dti_grades[threshold]
        return "C"

    def get_recommended_rate(self, risk_grade: str) -> float:
        """Calculate recommended interest rate based on risk grade."""
        adjustment = self.rate_adjustments.get(risk_grade, 0.0)
        return round(self.base_market_rate + adjustment, 4)


class MortgageCalculator:
    """Static utility methods for mortgage calculations."""

    @staticmethod
    def calculate_monthly_payment(loan: float, rate: float, years: int = 25) -> float:
        """Calculate monthly payment using amortization formula."""
        if years <= 0:
            raise ValueError("Loan term must be positive")

        monthly_rate = rate / 12
        term_months = years * 12

        if monthly_rate == 0:
            return round(loan / term_months, 2)

        payment = loan * (monthly_rate * (1 + monthly_rate) ** term_months) / \
            ((1 + monthly_rate) ** term_months - 1)

        return round(payment, 2)

    @staticmethod
    def calculate_dti(
        annual_income: float,
        monthly_debts: float,
        monthly_mortgage_payment: float
    ) -> float:
        """Calculate Debt-to-Income ratio."""
        if annual_income == 0:
            return 0.0

        monthly_income = annual_income / 12
        total_monthly_debt = monthly_debts + monthly_mortgage_payment
        return round(total_monthly_debt / monthly_income, 4)


class AffordabilityEvaluator:
    """Evaluates loan applications against lending policy."""

    def __init__(self, policy: LendingPolicy):
        self.policy = policy

    def evaluate(
        self,
        app: LoanApplication,
        dti: float,
        dti_stress: float,
        monthly_payment: float
    ) -> AffordabilityResult:
        """Evaluate loan application and return affordability result."""
        stress_passed = dti_stress <= self.policy.stress_threshold

        max_mortgage = app.annual_income * \
            self.policy.get_multiplier(app.credit_score)

        # Determine decision and grade
        decision, risk_grade = self._determine_decision_and_grade(
            credit_score=app.credit_score,
            loan_amount=app.loan_amount,
            max_mortgage=max_mortgage,
            dti=dti,
            stress_passed=stress_passed
        )

        # Calculate recommended rate (only for non-declined apps)
        recommended_rate = None
        if decision != Decision.DECLINED:
            recommended_rate = self.policy.get_recommended_rate(risk_grade)

        return AffordabilityResult(
            max_mortgage=round(max_mortgage, 2),
            monthly_payment=round(monthly_payment, 2),
            dti_ratio=round(dti, 4),
            stress_test_passed=stress_passed,
            decision=decision,
            risk_grade=risk_grade,  # None for declined
            recommended_rate=recommended_rate  # None for declined
        )

    def _determine_decision_and_grade(
        self,
        credit_score: int,
        loan_amount: float,
        max_mortgage: float,
        dti: float,
        stress_passed: bool
    ) -> Tuple[Decision, Optional[str]]:
        """
        Determine decision and risk grade based on policy rules.

        Decision hierarchy:
        1. Check DTI hard limit (> 50%)
        2. Check LTI (Loan-to-Income) cap
        3. Check review thresholds (DTI or stress test)
        4. Calculate grade for approved applications
        """

     # Guard Clause: If they can't borrow anything, it's an immediate decline
        if max_mortgage <= 0 :
            return Decision.DECLINED, None

        # 1. Check DTI hard limit
        if dti > self.policy.max_dti:
            return Decision.DECLINED, None

        # 2. Check Limit Utilization (how much of their max allowed are they asking for?)
        utilization = loan_amount / max_mortgage

        if utilization > self.policy.max_lti_excess:
            return Decision.DECLINED, None

        if utilization > self.policy.review_lti_excess:
            return Decision.REVIEW, self.policy.default_review_grade

        # 3. Check DTI/Stress Review thresholds
        if dti > self.policy.review_threshold or not stress_passed:
            return Decision.REVIEW, self.policy.default_review_grade

        # 4. APPROVED: Calculate combined risk grade
        credit_grade = self.policy.get_credit_grade(credit_score)
        dti_grade = self.policy.get_dti_grade(dti)

        # Take the most conservative (highest letter) grade
        final_grade = max(credit_grade, dti_grade)

        return Decision.APPROVED, final_grade


class MortgageService:
    """Orchestrates the mortgage affordability workflow."""

    def __init__(self, policy: LendingPolicy | None = None):
        self.policy = policy or LendingPolicy()
        self.evaluator = AffordabilityEvaluator(self.policy)

    def execute_workflow(self, app: LoanApplication) -> AffordabilityResult:
        """Execute full affordability assessment workflow."""

        # 1. Calculate monthly payments
        monthly_payment = MortgageCalculator.calculate_monthly_payment(
            app.loan_amount, app.base_rate, app.term_years
        )
        stressed_payment = MortgageCalculator.calculate_monthly_payment(
            app.loan_amount, app.stress_rate, app.term_years
        )

        # 2. Calculate DTI ratios
        dti = MortgageCalculator.calculate_dti(
            app.annual_income, app.monthly_debts, monthly_payment
        )
        dti_stress = MortgageCalculator.calculate_dti(
            app.annual_income, app.monthly_debts, stressed_payment
        )

        # 3. Evaluate and return result
        return self.evaluator.evaluate(app, dti, dti_stress, monthly_payment)


