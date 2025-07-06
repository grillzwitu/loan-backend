"""
Module: Fraud detection services with rule-based checks.

This module implements the core fraud detection logic for
loan applications.
"""

import datetime
import logging
from typing import List

from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.utils import timezone
from django.core.cache import cache

from loan.models import LoanApplication
from .models import FraudFlag


CACHE_TTL_5_MIN: int = 300  # Cache TTL for 5 minutes
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

    reasons: List[str] = []

    # Rule: more than 3 loans in the past 24 hours
    one_day_ago: datetime.datetime = (
        timezone.now() - datetime.timedelta(days=1)
    )
    cache_key_recent = f"fraud.recent_loans.user_{loan.user_id}"
    recent_loan_count = LoanApplication.objects.filter(
        user_id=loan.user_id, created_at__gte=one_day_ago
    ).count()
    cache.set(cache_key_recent, recent_loan_count, CACHE_TTL_5_MIN)
    if recent_loan_count > 3:
        reasons.append("More than 3 loans in 24 hours")

    # Rule: amount exceeds threshold
    if loan.amount > 5000000:
        reasons.append("Amount exceeds threshold")

    # Rule: email domain usage
    domain: str = loan.user.email.split("@")[-1]  # type: ignore[attr-defined]
    cache_key_domain = f"fraud.domain_user_count_{domain}"
    domain_user_count = cache.get(cache_key_domain)
    if domain_user_count is None:
        domain_user_count = (
            User.objects.filter(email__iendswith=domain)
            .distinct()
            .count()
        )
        cache.set(cache_key_domain, domain_user_count, CACHE_TTL_5_MIN)
    if domain_user_count > 10:
        reasons.append("Email domain used by more than 10 users")

    # Persist flags
    if reasons:
        logger.warning(
            "Loan id=%s flagged for reasons: %s", loan.id, reasons
        )
    for reason in reasons:
        FraudFlag.objects.create(loan=loan, reason=reason)

    # Update loan status based on fraud detection results
    if reasons:
        logger.info("Setting status FLAGGED for loan id=%s", loan.id)
        loan.status = "FLAGGED"
        loan.save(update_fields=["status"])
        # Mock email notification to admin when a loan is flagged
        send_mail(
            subject=f"Loan {loan.id} Flagged",
            message=(
                f"Loan {loan.id} flagged for reasons: "
                f"{', '.join(reasons)}"
            ),
            from_email=None,
            recipient_list=["admin@example.com"],
            fail_silently=True,
        )
    else:
        # Auto-approve loans with no fraud flags
        logger.info(
            "Auto-approving loan id=%s with no fraud flags", loan.id
        )
        loan.status = "APPROVED"
        loan.save(update_fields=["status"])

    return reasons
