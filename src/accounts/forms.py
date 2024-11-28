from django.contrib.auth.forms import UserCreationForm
from django.forms import (
    CharField,
    EmailField,
    Form,
    IntegerField,
    ModelForm,
)
from django.contrib.auth.models import User
from accounts.models import Company
from django.forms import Form


class LoginForm(Form):
    username = CharField(max_length=250)
    password = CharField(max_length=250)


class SignupForm(UserCreationForm):
    email = EmailField()

    class Meta:
        model = User
        fields = ("email", "password", "username", "first_name", "last_name")
        labels = {
            "email": "Email",
        }


class UserModelForm(ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username"]

    def __init__(self, *args, **kwargs):
        super(UserModelForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"


class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = "__all__"


class EmployeeForm(Form):
    keyword = CharField(max_length=250, required=False)
    industry = CharField(max_length=250, required=False)
    year_founded = IntegerField(required=False)
    city = CharField(max_length=250, required=False)
    state = CharField(max_length=250, required=False)
    country = CharField(max_length=250, required=False)
    from_year = IntegerField(required=False)
    to_year = IntegerField(required=False)

    def __str__(self):
        return self.industry


# eof
