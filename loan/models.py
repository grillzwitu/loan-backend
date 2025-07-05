"""
Module: Defines the LoanApplication model representing user loan requests.
"""
import datetime
import decimal
from django.contrib.auth import get_user_model

User = get_user_model()
from django.db import models
from django.conf import settings

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
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('FLAGGED', 'Flagged'),
        ('WITHDRAWN', 'Withdrawn'),
    ]
    user: User = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount: decimal.Decimal = models.DecimalField(max_digits=10, decimal_places=2)
    status: str = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at: datetime.datetime = models.DateTimeField(auto_now_add=True)
    updated_at: datetime.datetime = models.DateTimeField(auto_now=True)

    def withdraw(self) -> None:
        """
        Withdraw a pending LoanApplication, changing its status to WITHDRAWN.

        Raises:
            ValueError: If the loan is not in PENDING status.
        """
        if self.status != 'PENDING':
            raise ValueError("Only pending loans can be withdrawn")
        self.status = 'WITHDRAWN'
        self.save(update_fields=['status'])

    def __str__(self) -> str:
        """
        Return a string representation of the LoanApplication instance.

        Returns:
            str: Formatted string containing loan id and user.
        """
        return f'Loan {self.id} - {self.user}'