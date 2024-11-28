import os
import re

from django.conf import settings
from django.core.paginator import Paginator
from django.db import models


def list_as_page(data_list, page_no):
    return Paginator(data_list, 25).get_page(page_no)


def itsEmailID(mail):
    mail_regex = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
    if re.fullmatch(mail_regex, mail):
        return True
    return False


class ActiveManager(models.Manager):
    def get_queryset(self):
        return (
            super(ActiveManager, self)
            .get_queryset()
            .filter(is_Active=True, deleted=False)
        )


class InactiveManager(models.Manager):
    def get_queryset(self):
        return (
            super(InactiveManager, self)
            .get_queryset()
            .filter(is_Active=False, deleted=False)
        )


class DactiveManager(models.Manager):
    def get_queryset(self):
        return (
            super(ActiveManager, self)
            .get_queryset()
            .filter(is_Active=True, deleted=True)
        )


class DinactiveManager(models.Manager):
    def get_queryset(self):
        return (
            super(InactiveManager, self)
            .get_queryset()
            .filter(is_Active=False, deleted=True)
        )


def value_or_empty(val):
    """
    nantoblank function
    """
    if val == "" or val == "nan":
        return ""
    else:
        return val


def get_absolute_path(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those resources
    """
    sUrl = settings.STATIC_URL
    if settings.DEBUG:
        sRoot = settings.STATICFILES_DIRS[0]
    else:
        sRoot = settings.STATIC_ROOT
    mUrl = settings.MEDIA_URL
    mRoot = settings.MEDIA_ROOT
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri
    if not os.path.isfile(path):
        raise Exception("media URI must start with %s or %s" % (sUrl, mUrl))
    return path


