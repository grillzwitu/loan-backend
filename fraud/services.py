"""
Module: Fraud detection services with rule-based checks.

This module implements the core fraud detection logic for loan applications.
"""

import datetime
from django.utils import timezone
from django.contrib.auth import get_user_model

from loan.models import LoanApplication
from .models import FraudFlag

import logging
from typing import List
logger: logging.Logger = logging.getLogger(__name__)

User = get_user_model()

def run_fraud_checks(loan: LoanApplication) -> List[str]:
    """
    Run rule-based fraud detection checks on a LoanApplication instance.

    Flags loans if any of the following conditions are met:
      - More than 3 loan applications in the past 24 hours
      - Requested amount exceeds NGN 5,000,000
      - User’s email domain is used by more than 10 different users

    Args:
        loan (LoanApplication): The loan application to examine.

    Returns:
        list[str]: Reasons for which fraud flags were created.
    """
    # Clear existing flags for a fresh evaluation
    FraudFlag.objects.filter(loan=loan).delete()

    reasons: list[str] = []

    # Rule: more than 3 loans in the past 24 hours
    one_day_ago: datetime.datetime = timezone.now() - datetime.timedelta(days=1)
    recent_loan_count: int = LoanApplication.objects.filter(
        user=loan.user, created_at__gte=one_day_ago
    ).count()
    if recent_loan_count > 3:
        reasons.append("More than 3 loans in 24 hours")

    # Rule: amount exceeds threshold
    if loan.amount > 5000000:
        reasons.append("Amount exceeds threshold")

    # Rule: email domain usage
    domain: str = loan.user.email.split("@")[-1]
    domain_user_count: int = User.objects.filter(
        email__iendswith=domain
    ).distinct().count()
    if domain_user_count > 10:
        reasons.append("Email domain used by more than 10 users")

    # Persist flags
    if reasons:
        logger.warning(
            "Loan id=%s flagged for reasons: %s", loan.id, reasons
        )
    for reason in reasons:
        FraudFlag.objects.create(loan=loan, reason=reason)

    # Update loan status if flagged
    if reasons:
        logger.info("Setting status FLAGGED for loan id=%s", loan.id)
        loan.status = "FLAGGED"
        loan.save(update_fields=["status"])

    return reasons