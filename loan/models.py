"""
Module: Defines the LoanApplication model representing user loan requests.
"""


from django.conf import settings
from typing import Any
from django.db import models


class LoanApplication(models.Model):
    """
    Django model representing a user's loan application.

    Attributes:
        user (ForeignKey): User who applied for the loan.
        amount (Decimal): Requested loan amount.
        status (str): Application status ('PENDING', 'APPROVED', 'REJECTED').
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last modification timestamp.
    """

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("APPROVED", "Approved"),
        ("REJECTED", "Rejected"),
        ("FLAGGED", "Flagged"),
        ("WITHDRAWN", "Withdrawn"),
    ]
    id: int
    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    amount: models.DecimalField = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    status: models.CharField = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING",
    )
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)
    updated_at: models.DateTimeField = models.DateTimeField(auto_now=True)

    class Meta:
        """
        Default ordering for LoanApplication queries to
        prevent pagination warnings.
        """

        ordering = ["id"]

    def withdraw(self) -> None:
        """
        Withdraw a pending LoanApplication, changing its status to WITHDRAWN.

        Raises:
            ValueError: If the loan is not in PENDING status.
        """
        if self.status != "PENDING":
            raise ValueError("Only pending loans can be withdrawn")
        self.status = "WITHDRAWN"
        self.save(update_fields=["status"])

    def __str__(self) -> str:
        """
        Return a string representation of the LoanApplication instance.
    
        Returns:
            str: Formatted string containing loan id and user.
        """
        return f"Loan {self.id} - {self.user}"

