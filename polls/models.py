from django.db import models

class Polls(models.Model):
    """
    Polls model.
    Follows Single Responsibility Principle - manages polls only.
    """
    description = models.CharField(max_length=255, verbose_name="Description")
    rate = models.DecimalField(max_digits=3, decimal_places=1, verbose_name="Rate")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    
    class Meta:
        ordering = ['rate', 'created_at']
        verbose_name = "Poll"
        verbose_name_plural = "Polls"
    
    def __str__(self):
        return f"{self.description} ({self.rate})"
    
    def get_description(self):
        """Return the description of the poll"""
        return f"{self.description}"

    def get_rate(self):
        """Return the rate of the poll"""
        return f"{self.rate}"