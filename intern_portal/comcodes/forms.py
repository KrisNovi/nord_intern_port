from django import forms
from .models import TypeCode, Proposal, TypeCodeInProposal
from django.forms import inlineformset_factory, formset_factory
from django.forms.models import BaseInlineFormSet

class CodeForm(forms.ModelForm):
    class Meta:
        model = TypeCode
        fields = ('name', 'code', 'vendor', 'price')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'vendor': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'})
        }

class TypeCodeInProposalForm(forms.ModelForm):
    typecodes = forms.ModelChoiceField(
        queryset=TypeCode.objects.all(),
        label='Типовой код',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = TypeCodeInProposal
        fields = ['typecodes', 'qty']
        widgets = {
            'qty': forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'qty': 'Количество',
        }

class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ['company', 'person', 'supply_per', 'payment',]
        labels = {
            'company': 'Название организации',
            'person': 'Контактное лицо',
            'supply_per': 'Срок поставки',
            'payment': 'Условия оплаты',
        }
        widgets = {
            'company': forms.TextInput(attrs={'class': 'form-control'}),
            'person': forms.TextInput(attrs={'class': 'form-control'}),
            'supply_per': forms.TextInput(attrs={'class': 'form-control'}),
            'payment': forms.TextInput(attrs={'class': 'form-control'}),
        }

# TypeCodeInProposalFormSet = inlineformset_factory(
#     Proposal,
#     TypeCodeInProposal,
#     form=TypeCodeInProposalForm,
#     extra=1,
#     can_delete=True,
#     can_delete_extra=True,
# )

TypeCodeInProposalFormSet = formset_factory(TypeCodeInProposalForm, extra=1)