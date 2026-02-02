"""
Simple pytest tests for MortgageService.
"""

from loan_affordability.service import (
    LoanApplication,
    MortgageService,
    LendingPolicy,
    Decision
)


def test_approved_applicant():
    """Test that a high income applicant with no debt gets approved."""
    service = MortgageService()

    app = LoanApplication(
        annual_income=100000,
        loan_amount=300000,
        credit_score=800,
        monthly_debts=0
    )

    result = service.execute_workflow(app)

    assert result.decision == Decision.APPROVED

def test_lti_decline():
    """
    Tripwire: LTI Utilization.
    Keep the income high, but push the loan amount past the multiplier limit.
    """
    service = MortgageService()
    
    # 100k income * 4.0 multiplier = 400k limit. 
    # We ask for 500k (1.25x utilization), which triggers a DECLINE (>1.20).
    app = LoanApplication(
        annual_income=100000, 
        loan_amount=500000, 
        credit_score=700, 
        monthly_debts=0
    )

    result = service.execute_workflow(app)
    assert result.decision == Decision.DECLINED


def test_dti_review():
    """
    Tripwire: DTI Threshold.
    Keep the income and loan the same as the 'Approved' case, 
    but add enough monthly debt to cross the 43% threshold.
    """
    service = MortgageService()

    app = LoanApplication(
        annual_income=100000,
        loan_amount=300000,
        credit_score=800,
        monthly_debts=2400  # Added debt to push DTI into the 43-50% 'Review' zone
    )

    result = service.execute_workflow(app)
    assert result.decision == Decision.REVIEW
def test_stress_test_failure():
    """Test that an applicant who fails the stress test gets manual review."""
    service = MortgageService()

    app = LoanApplication(
        annual_income=50000,
        loan_amount=180000,
        credit_score=700,
        monthly_debts=800,
        base_rate=0.04,
        stress_rate=0.07  # Higher stress rate to trigger failure
    )

    result = service.execute_workflow(app)

    assert result.decision == Decision.REVIEW
    assert result.stress_test_passed is False


def test_zero_income():
    """Test that an applicant with zero income is declined."""
    service = MortgageService()

    app = LoanApplication(
        annual_income=0,
        loan_amount=200000,
        credit_score=750,
        monthly_debts=0
    )

    result = service.execute_workflow(app)

    assert result.decision == Decision.DECLINED
