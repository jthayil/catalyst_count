from django.db.models import (
    Model,
    IntegerField,
    CharField,
    FloatField,
    TextField,
    URLField,
    DateTimeField,
    Index,
)


class Company(Model):
    name = TextField(null=True, blank=True)
    domain = TextField(null=True, blank=True)
    year_founded = IntegerField(null=True, blank=True)
    industry = TextField(null=True, blank=True)
    size_range = TextField(null=True, blank=True)
    city = TextField(null=True, blank=True)
    state = TextField(null=True, blank=True)
    country = TextField(null=True, blank=True)
    linkedin_url = URLField(null=True, blank=True)
    current_employee_estimate = IntegerField(null=True, blank=True)
    total_employee_estimate = IntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.id)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"
        ordering = ["name"]
        indexes = [
            Index(fields=["industry"]),
            Index(fields=["city"]),
            Index(fields=["year_founded"]),
            Index(fields=["state"]),
            Index(fields=["country"]),
        ]
