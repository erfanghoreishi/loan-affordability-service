"""
CLI entry point for Loan Affordability Service.

Provides a command-line interface to evaluate mortgage applications
using the MortgageService.
"""

import sys
from pathlib import Path

# Allow direct script execution by adding src to path
if __name__ == "__main__":
    src_path = Path(__file__).parent.parent
    sys.path.insert(0, str(src_path))

import click
from loan_affordability.service import (
    MortgageService,
    LoanApplication,
    Decision
)


@click.command()
@click.option(
    '--income',
    type=float,
    required=True,
    help='Annual income of the applicant'
)
@click.option(
    '--debts',
    type=float,
    required=True,
    help='Monthly debt obligations'
)
@click.option(
    '--loan',
    type=float,
    required=True,
    help='Requested loan amount'
)
@click.option(
    '--credit',
    type=int,
    default=700,
    help='Credit score (default: 700)'
)
def evaluate_affordability(income: float, debts: float, loan: float, credit: int):
    """
    Evaluate mortgage affordability for a loan application.

    This tool assesses whether an applicant qualifies for a mortgage
    based on their income, debts, loan amount, and credit score.
    """
    # Display applicant profile
    click.echo("\n" + "=" * 60)
    click.echo("LOAN AFFORDABILITY ASSESSMENT")
    click.echo("=" * 60)
    click.echo(f"Annual Income:    £{income:,.2f}")
    click.echo(f"Monthly Debts:    £{debts:,.2f}")
    click.echo(f"Loan Amount:      £{loan:,.2f}")
    click.echo(f"Credit Score:     {credit}")
    click.echo("=" * 60)

    # Create loan application
    app = LoanApplication(
        annual_income=income,
        monthly_debts=debts,
        loan_amount=loan,
        credit_score=credit
    )

    # Execute workflow
    service = MortgageService()
    result = service.execute_workflow(app)

    # Display results
    click.echo(f"\nDebt-to-Income Ratio: {result.dti_ratio:.2%}")
    click.echo(f"Monthly Payment:      £{result.monthly_payment:,.2f}")
    click.echo(f"Max Mortgage:         £{result.max_mortgage:,.2f}")
    click.echo(
        f"Stress Test:          {'PASSED' if result.stress_test_passed else 'FAILED'}")

    if result.risk_grade:
        click.echo(f"Risk Grade:           {result.risk_grade}")

    if result.recommended_rate:
        click.echo(f"Recommended Rate:     {result.recommended_rate:.2%}")

    # Display decision with color coding
    click.echo("\n" + "=" * 60)

    if result.decision == Decision.APPROVED:
        click.secho(
            f"✓ DECISION: {result.decision.value}",
            fg='green',
            bold=True
        )
        click.echo("=" * 60)
        click.echo("The application has been approved.")

    elif result.decision == Decision.REVIEW:
        click.secho(
            f"⚠ DECISION: {result.decision.value}",
            fg='yellow',
            bold=True
        )
        click.echo("=" * 60)
        click.echo("The application requires manual review.")

    elif result.decision == Decision.DECLINED:
        click.secho(
            f"✗ DECISION: {result.decision.value}",
            fg='red',
            bold=True
        )
        click.echo("=" * 60)
        click.echo("The application has been declined.")

    click.echo("")


if __name__ == "__main__":
    evaluate_affordability()
