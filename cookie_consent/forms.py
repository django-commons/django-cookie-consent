from collections.abc import Collection, Iterator

from django import forms
from django.utils.translation import gettext_lazy as _

from .cache import all_cookie_groups
from .models import CookieGroup


def iter_cookie_group_choices() -> Iterator[tuple[str, str]]:
    """
    Use the cached cookie group instances to get a list of choices.
    """
    for varname, cookie_group in all_cookie_groups().items():
        yield varname, cookie_group.name


class CookieGroupsChoiceField(forms.TypedMultipleChoiceField):
    def __init__(self, **kwargs):
        kwargs["coerce"] = self._coerce_choice
        kwargs["choices"] = iter_cookie_group_choices
        super().__init__(**kwargs)

    def _coerce_choice(self, varname: str) -> CookieGroup:
        all_groups = all_cookie_groups()
        return all_groups[varname]


class ProcessCookiesForm(forms.Form):
    all_groups = forms.BooleanField(
        label=_("Apply to all cookie groups"),
        required=False,
    )
    cookie_groups = CookieGroupsChoiceField(
        label=_("Cookie group varnames"),
        choices=iter_cookie_group_choices,
        required=False,
    )

    def get_cookie_groups(self) -> Collection[CookieGroup]:
        """
        Build the collection of specified cookies.
        """
        match self.cleaned_data:
            case {"all_groups": True}:
                return all_cookie_groups().values()
            case {"cookie_groups": [*groups]}:
                return groups
            case _:
                return []
