from django.contrib import admin
from .models import Proposal, TypeCode


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = (
        'amount',
    )
    search_fields = ('typecode', 'prop_id')
    filter_horizontal = ('typecode',)
    # autocomplete_fields = ('typecode',)
    # inlines = (TypecodeInline, )
    empty_value_display = '-пусто-'


@admin.register(TypeCode)
class TypeCodeAdmin(admin.ModelAdmin):
    fields = (
        'name',
        'code',
        'vendor',
        'price',
    )
