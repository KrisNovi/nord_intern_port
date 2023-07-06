from django.contrib import admin
from .models import Proposal, TypeCode, TypeCodeInProposal

@admin.register(TypeCodeInProposal)
class TypeCodeInProposalAdmin(admin.ModelAdmin):
    fields = ('typecodes', 'proposal', 'qty',)
    

class TypeCodeInProposalInline(admin.TabularInline):
    model = TypeCodeInProposal



@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = (
        'amount',
        'prop_id',
        'company',
        'person',
        'supply_per',
        'payment'
    )
    search_fields = ('typecode', 'name',)
    # list_filter = ('author', )
    # filter_horizontal = ('tags',)
    autocomplete_fields = ('typecodes',)
    inlines = (TypeCodeInProposalInline, )
    empty_value_display = '-пусто-'

    def amount(self, obj):
        # return obj.fav.count()
        pass
    amount.short_description = 'Сумма позиций в КП, валюта'


@admin.register(TypeCode)
class TypeCodeAdmin(admin.ModelAdmin):
    fields = (
        'name',
        'code',
        'vendor',
        'price',
    )
    search_fields = ('name',)