"""
Module: Defines the FraudFlag model for storing fraud-related flags on
loan applications.

Attributes:
    loan (ForeignKey[LoanApplication]): Reference to the flagged
        LoanApplication.
    reason (str): Explanation for why the loan was flagged.
    flagged_at (datetime.datetime): Timestamp when the flag was created.
"""

from django.db import models


class FraudFlag(models.Model):
    """
    Stores a reason why a specific LoanApplication was flagged as
    potential fraud.

    Methods:
        __str__: Returns formatted string representation.
    """

    id: int

    loan: models.ForeignKey = models.ForeignKey(
        "loan.LoanApplication",
        on_delete=models.CASCADE,
        related_name="fraud_flags",
    )
    reason: models.CharField = models.CharField(max_length=255)
    flagged_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        """
        Return a string representation of the FraudFlag instance.

        Returns:
            str: Formatted string containing flag id and loan reference.
        """
        return f"Flag {self.id} - {self.loan}"
