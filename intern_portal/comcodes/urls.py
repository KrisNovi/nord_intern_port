from django.urls import path
from . import views

app_name = 'comcodes'

urlpatterns = [
    path('', views.index, name='index'),
    path('new_code/', views.add_typecode, name='new_code'),
    path('new_proposal/', views.create_proposal, name='new_proposal'),
    path('typecode_list/', views.typecode_list, name='typecode_list'),
    path('proposal_list/', views.proposal_list, name='proposal_list'),
    path('proposal_list/<int:proposal_id>/', views.proposal_detail, name='proposal_detail'),
    path('generatepdf', views.generate_pdf, name='generate_pdf'),
]