from django.forms.models import BaseModelForm
from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
from .models import TypeCode, Proposal, TypeCodeInProposal
from django.core.paginator import Paginator
from django.views.generic.edit import CreateView
from django.views.generic import (TemplateView)
from .forms import CodeForm, ProposalForm, TypeCodeInProposalForm, TypeCodeInProposalFormSet
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import messages
from django.db import transaction, IntegrityError
from django.forms import modelformset_factory



QTY1 = 10
QTY2 = 20

def index(request):
    title = 'Норд Индастриз - внутренний портал'
    proposals = Proposal.objects.all().order_by('-id')[:10]
    paginator = Paginator(proposals, QTY1)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': title,
        'proposals': proposals,
    }
    return render(request, 'comcodes/index.html', context)

def typecode_list(request):
    typecodes = TypeCode.objects.all().order_by('-id')
    paginator = Paginator(typecodes, QTY2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'typecodes': typecodes,
        'page_obj': page_obj,
    }
    return render(request, 'comcodes/typecode_list.html', context)


def proposal_list(request):
    title = 'Коммерческие предложения'
    prop_list = Proposal.objects.all().order_by('-id')
    paginator = Paginator(prop_list, QTY2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'title': title,
        'prop_list': prop_list,
    }
    return render(request, 'comcodes/proposal_list.html', context)

def proposal_detail(request, proposal_id):
    proposal = get_object_or_404(Proposal, pk=proposal_id)
    # author_post = post.author.posts.count()
    form = ProposalForm(request.POST or None)
    # comments = post.comments.all()
    context = {
        'proposal': proposal,
        # 'author_post': author_post,
        'form': form,
        # 'comments': comments,
    }
    return render(request, 'comcodes/proposal_detail.html', context)


# class CodeView(CreateView):  # Создаём свой класс, наследуем его от CreateView
#     # C какой формой будет работать этот view-класс
#     form_class = CodeForm

#     # Какой шаблон применить для отображения веб-формы
#     template_name = 'comcodes/create_code.html'  

#     # Куда переадресовать пользователя после того, как он отправит форму
#     success_url = '/thankyou/'   


def add_typecode(request):
    if request.method == 'POST':
        form = CodeForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/new_code')
    else:
        form = CodeForm()
    return render(request, 'comcodes/create_code.html', {'form': form})


# def add_proposal(request):
#     if request.method == 'POST':
#         formset = TypeCodeInProposalFormSet(request.POST)
#         if formset.is_valid():
#             formset.save()
#             return HttpResponseRedirect('/new_proposal')  # Перенаправляем на страницу со списком Proposal
#     else:
#         formset = TypeCodeInProposalFormSet()
#     return render(request, 'comcodes/create_proposal.html', {'form': form})

# class ProposalCreateView(CreateView):
#     model = Proposal
#     template_name = 'create_proposal.html'
#     fields = ['typecodes', 'company', 'person', 'supply_per', 'payment', 'amount', 'prop_id']

#     def form_valid(self, form):

#         messages.add_message(
#             self.request,
#             message.SUCCESS,
#             'КП успешно создано'
#         )

#         return super().form_valid(form)


def create_proposal(request):
    form = ProposalForm()
    formset = TypeCodeInProposalFormSet(queryset=TypeCodeInProposal.objects.none(), prefix='typecodes')

    if request.method == 'POST':
        form = ProposalForm(request.POST)
        formset = TypeCodeInProposalFormSet(request.POST, prefix='typecodes')

        if form.is_valid() and formset.is_valid():
            proposal = form.save()

            for form_data in formset:
                typecode = form_data.cleaned_data.get('typecodes')
                qty = form_data.cleaned_data.get('qty')
                TypeCodeInProposal.objects.create(proposal=proposal, typecodes=typecode, qty=qty)

            return HttpResponseRedirect('/new_proposal') # Создайте URL-шаблон 'proposal_created'

    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'comcodes/create_proposal.html', context)


def delete_variant(request, pk):
    try:
        variant = TypeCodeInProposal.objects.get(id=pk)
    except TypeCodeInProposal.DoesNotExist:
        messages.success(
            request, 'Object Does not exit'
            )
        return redirect('comcodes:update_proposal', pk=variant.typecodes.id)

    variant.delete()
    messages.success(
            request, 'Variant deleted successfully'
            )
    return redirect('comcodes:update_proposal', pk=variant.typecodes.id)


# def create(request):
# 	context = {}
# 	TypeCodeInProposalFormSet = modelformset_factory(TypeCodeInProposal, form=TypeCodeInProposalForm, extra=10)	
# 	form = ProposalForm(request.POST or None)
# 	formset = TypeCodeInProposalFormSet(request.POST or None, queryset= TypeCodeInProposal.objects.none(), prefix='codes')
# 	if request.method == "POST":
# 		if form.is_valid() and formset.is_valid():
# 			try:
# 				with transaction.atomic():
# 					proposal = form.save(commit=False)
# 					proposal.save()

# 					for code in formset:
# 						data = code.save(commit=False)
# 						data.proposal = proposal
# 						data.save()
# 			except IntegrityError:
# 				print("Error Encountered")

# 			return HttpResponseRedirect('/new_proposal')


# 	context['formset'] = formset
# 	context['form'] = form
# 	return render(request, 'comcodes/create_proposal.html', context)