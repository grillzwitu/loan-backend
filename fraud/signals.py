"""
Module: Signal handlers for fraud app.

Defines post-save hook to trigger fraud checks on newly created
LoanApplication instances.
"""

import logging
from typing import Any, Type

from django.db.models.signals import post_save
from django.dispatch import receiver

from loan.models import LoanApplication

from .services import run_fraud_checks

logger: logging.Logger = logging.getLogger(__name__)


@receiver(post_save, sender=LoanApplication)
def loan_post_save(
    sender: Type[LoanApplication],
    instance: LoanApplication,
    created: bool,
    **kwargs: Any,
) -> None:
    """
    Signal handler that runs fraud checks whenever a new
    LoanApplication is created.

    Args:
        sender (Type[LoanApplication]): The model class.
        instance (LoanApplication): The instance that was saved.
        created (bool): True if a new record was created.
        **kwargs: Additional keyword arguments.
    """
    if created:
        logger.info(
            "LoanApplication created; running fraud checks for id=%s",
            instance.id,
        )
        run_fraud_checks(instance)
