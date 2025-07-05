"""Signal handlers for the fraud app."""

from django.db.models.signals import post_save
from django.dispatch import receiver
from typing import Any, Type
from loan.models import LoanApplication
from .services import run_fraud_checks

@receiver(post_save, sender=LoanApplication)
def loan_post_save(sender: Type[LoanApplication], instance: LoanApplication, created: bool, **kwargs: Any) -> None:
    """
    Signal handler that runs fraud checks whenever a new LoanApplication is created.

    Args:
        sender (Type[LoanApplication]): The model class.
        instance (LoanApplication): The instance that was saved.
        created (bool): True if a new record was created.
        **kwargs: Additional keyword arguments.
    """
    if created:
        run_fraud_checks(instance)