﻿import django_filters
# from django_filters import filters
from comcodes.models import TypeCode, Proposal


class ProposeFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains',
    )

    class Meta:
        model = TypeCode
        fields = ['name', ]
