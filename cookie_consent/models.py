from __future__ import annotations

import re
from collections.abc import Callable
from typing import ClassVar, ParamSpec, TypedDict, TypeVar

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

COOKIE_NAME_RE = re.compile(r"^[-_a-zA-Z0-9]+$")
validate_cookie_name = RegexValidator(
    COOKIE_NAME_RE,
    _(
        "Enter a valid 'varname' consisting of letters, numbers"
        ", underscores or hyphens."
    ),
    "invalid",
)

P = ParamSpec("P")
T = TypeVar("T")


def clear_cache_after(func: Callable[P, T]) -> Callable[P, T]:
    def wrapper(*args: P.args, **kwargs: P.kwargs):
        from .cache import delete_cache

        return_value = func(*args, **kwargs)
        delete_cache()
        return return_value

    return wrapper


class CookieGroupDict(TypedDict):
    varname: str
    name: str
    description: str
    is_required: bool
    # The version is deliberately not included because it requires page/view cache
    # busting if a new cookie gets added to the group, which we don't control.


class BaseQueryset(models.query.QuerySet):
    @clear_cache_after
    def delete(self):
        return super().delete()

    @clear_cache_after
    def update(self, **kwargs):
        return super().update(**kwargs)


class CookieGroupManager(models.Manager.from_queryset(BaseQueryset)):
    def get_by_natural_key(self, varname: str) -> CookieGroup:
        return self.get(varname=varname)


class CookieGroup(models.Model):
    varname = models.CharField(
        _("Variable name"),
        max_length=32,
        unique=True,
        validators=[validate_cookie_name],
    )
    name = models.CharField(_("Name"), max_length=100, blank=True)
    description = models.TextField(_("Description"), blank=True)
    is_required = models.BooleanField(
        _("Is required"),
        help_text=_("Are cookies in this group required."),
        default=False,
    )
    is_deletable = models.BooleanField(
        _("Is deletable?"),
        help_text=_("Can cookies in this group be deleted."),
        default=True,
    )
    ordering = models.IntegerField(_("Ordering"), default=0)
    created = models.DateTimeField(_("Created"), auto_now_add=True, blank=True)

    objects: ClassVar[CookieGroupManager] = CookieGroupManager()  # pyright: ignore[reportIncompatibleVariableOverride]
    cookie_set: ClassVar[CookieManager]

    class Meta:
        verbose_name = _("Cookie Group")
        verbose_name_plural = _("Cookie Groups")
        ordering = ["ordering"]

    def __str__(self):
        return self.name

    @clear_cache_after
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @clear_cache_after
    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)

    def natural_key(self) -> tuple[str]:
        return (self.varname,)

    def get_version(self) -> str:
        try:
            # this relies on the cookie set being ordered by most-recently created
            # first.
            # Note that we don't use `.first()` as that's a new query and bypasses
            # the cache.
            return str(self.cookie_set.all()[0].get_version())
        except IndexError:
            return ""

    def for_json(self) -> CookieGroupDict:
        return {
            "varname": self.varname,
            "name": self.name,
            "description": self.description,
            "is_required": self.is_required,
            # "version": self.get_version(),
        }


class CookieManager(models.Manager.from_queryset(BaseQueryset)):
    def get_by_natural_key(self, name: str, domain: str, cookiegroup: str) -> Cookie:
        group = CookieGroup.objects.get_by_natural_key(cookiegroup)
        return self.get(cookiegroup=group, name=name, domain=domain)


class Cookie(models.Model):
    cookiegroup = models.ForeignKey(
        CookieGroup,
        verbose_name=CookieGroup._meta.verbose_name,
        on_delete=models.CASCADE,
    )
    name = models.CharField(_("Name"), max_length=250)
    description = models.TextField(_("Description"), blank=True)
    path = models.TextField(_("Path"), blank=True, default="/")
    domain = models.CharField(_("Domain"), max_length=250, blank=True)
    created = models.DateTimeField(_("Created"), auto_now_add=True, blank=True)

    objects = CookieManager()

    class Meta:
        verbose_name = _("Cookie")
        verbose_name_plural = _("Cookies")
        constraints = [
            models.UniqueConstraint(
                fields=("cookiegroup", "name", "domain"),
                name="natural_key",
            ),
        ]
        ordering = ["-created"]

    def __str__(self):
        return f"{self.name} {self.domain}{self.path}"

    @clear_cache_after
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    @clear_cache_after
    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)

    def natural_key(self) -> tuple[str, str, str]:
        return (self.name, self.domain) + self.cookiegroup.natural_key()

    natural_key.dependencies = ["cookie_consent.cookiegroup"]  # pyright: ignore[reportFunctionMemberAccess]

    @property
    def varname(self) -> str:
        group_varname = self.cookiegroup.varname
        return f"{group_varname}={self.name}:{self.domain}"

    def get_version(self) -> str:
        return self.created.isoformat()


ACTION_ACCEPTED = 1
ACTION_DECLINED = -1
ACTION_CHOICES = (
    (ACTION_DECLINED, _("Declined")),
    (ACTION_ACCEPTED, _("Accepted")),
)


class LogItem(models.Model):
    action = models.IntegerField(_("Action"), choices=ACTION_CHOICES)
    cookiegroup = models.ForeignKey(
        CookieGroup,
        verbose_name=CookieGroup._meta.verbose_name,
        on_delete=models.CASCADE,
    )
    version = models.CharField(_("Version"), max_length=32)
    created = models.DateTimeField(_("Created"), auto_now_add=True, blank=True)

    class Meta:
        verbose_name = _("Log item")
        verbose_name_plural = _("Log items")
        ordering = ["-created"]

    def __str__(self):
        return f"{self.cookiegroup.name} {self.version}"
