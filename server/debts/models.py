from django.db import models
from django.contrib.auth.models import User

class Debt(models.Model):
    debtor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='debts_owed')
    creditor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='debts_lent')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        unique_together = ('debtor', 'creditor')

    def __str__(self):
        return f"{self.debtor.username} owes {self.creditor.username} {self.amount}"