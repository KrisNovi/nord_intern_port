from django.shortcuts import render, redirect
from django.shortcuts import render, get_object_or_404
import os
from comcodes.models import TypeCode, Proposal, TypeCodeInProposal
from django.core.paginator import Paginator
from .forms import CodeForm, ProposalForm, TypeCodeInProposalFormSet
from django.http import HttpResponseRedirect, FileResponse
import io
from django.template.defaultfilters import date as date_filter
from django.conf import settings
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import reportlab.rl_config
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Spacer, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from PIL import Image as PILImage
from reportlab.lib.units import cm
reportlab.rl_config.warnOnMissingFontGlyphs = 0


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
    }
    return render(request, 'comcodes/proposal_list.html', context)


def proposal_detail(request, proposal_id):
    proposal = get_object_or_404(Proposal, pk=proposal_id)
    form = ProposalForm(request.POST or None)
    
    if request.method == 'POST':
        if request.POST.get('download_pdf'):
            pdf_response = generate_pdf(request, proposal)
            return pdf_response    
    context = {
        'proposal': proposal,
        'form': form,
    }
    return render(request, 'comcodes/proposal_detail.html', context)


def generate_pdf(request, proposal):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=20, leftMargin=20, topMargin=30, bottomMargin=30)
    story = []

    pdfmetrics.registerFont(TTFont('DejaVuSans', os.path.join(settings.BASE_DIR, 'static', 'fonts', 'DejaVuSans.ttf')))

    # Создание стилей
    styles = {
        'default': ParagraphStyle(
            'normal',
            fontName='DejaVuSans',
            fontSize=8,
            alignment=0,
            leading=12,
        ),
        'header1': ParagraphStyle(
            'header',
            fontName='DejaVuSans',
            fontSize=12,
            alignment=0,
            leading=14,
            textColor=colors.black,
        ),
        'header2': ParagraphStyle(
            'header',
            fontName='DejaVuSans',
            fontSize=10,
            alignment=0,
            leading=14,
            textColor=colors.black,
        ),
    }

    # Получение данных из модели Proposal
    table_data = [
        [Paragraph('№', styles['header2']),
         Paragraph('Наименование оборудования или код', styles['header2']),
         Paragraph('Код вендора', styles['header2']),
         Paragraph('Кол-во, шт.', styles['header2']),
         Paragraph('Стоимость без учёта НДС, рубли', styles['header2']),
         Paragraph('Сумма без учёта НДС, рубли', styles['header2'])],
    ]


    # Добавление данных из связанных с Proposal моделей TypeCode и TypeCodeInProposal в таблицу
    for i, typecode_in_proposal in enumerate(proposal.typecode_in_proposals.all(), start=1):
        typecode_info = [
            str(i),
            Paragraph(typecode_in_proposal.typecodes.name, styles['default']),
            Paragraph(typecode_in_proposal.typecodes.code, styles['default']),
            str(typecode_in_proposal.qty),
            str(typecode_in_proposal.typecodes.price),
            str(typecode_in_proposal.qty * typecode_in_proposal.typecodes.price),
        ]
        table_data.append(typecode_info)

    # Создание таблицы
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, -1), 'DejaVuSans'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOX', (0, 0), (-1, -1), 0.5, colors.black),
    ])
    table = Table(table_data, colWidths=[0.5 * cm, 6.5 * cm, 2.5 * cm, 1.8 * cm, 3 * cm, 3.5 * cm], style=table_style)
    # Открытие изображения с использованием PIL.Image
    image_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'top.png')
    img = Image(image_path, width=16.37 * cm, height=4.31 * cm)
    story.append(img)

    # Создание строки с использованием элемента Paragraph для даты
    date_paragraph = Paragraph(f'Дата: {proposal.publication_date.strftime("%d.%m.%Y")}', styles['default'])

    story.append(date_paragraph)
    story.append(Spacer(1, 0.2 * cm))

    # Создание строки с использованием элемента Paragraph для заголовка коммерческого предложения
    prop_id_paragraph = Paragraph(f'Коммерческое предложение {proposal.prop_id}', styles['header1'])
    story.append(prop_id_paragraph)
    story.append(Spacer(1, 1.5 * cm))

    # Добавление таблицы в историю
    story.append(table)

    # Генерация документа
    doc.build(story)

    buf.seek(0)

    filename = f'КП {proposal.prop_id}.pdf'
    return FileResponse(buf, as_attachment=True, filename=filename)


def add_typecode(request):
    if request.method == 'POST':
        form = CodeForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/new_code')
    else:
        form = CodeForm()
    return render(request, 'comcodes/create_code.html', {'form': form})


def create_proposal(request):
    form = ProposalForm()
    formset = TypeCodeInProposalFormSet(prefix='typecodes', data=request.POST or None)

    if request.method == 'POST':
        form = ProposalForm(request.POST)
        formset = TypeCodeInProposalFormSet(request.POST, prefix='typecodes')

        if form.is_valid() and formset.is_valid():
            proposal = form.save()
            for form_data in reversed(formset.forms):
                if form_data.cleaned_data:
                    typecode = form_data.cleaned_data['typecodes']
                    qty = form_data.cleaned_data['qty']
                    TypeCodeInProposal.objects.create(proposal=proposal, typecodes=typecode, qty=qty)
            return HttpResponseRedirect('/new_proposal')

    context = {
        'form': form,
        'formset': formset,
    }
    return render(request, 'comcodes/create_proposal.html', context)