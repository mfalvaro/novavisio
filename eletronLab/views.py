# coding: utf-8
"""
    Name:        views.py
    Purpose:
    Author:      GPS-PC08
    Created:     28/03/2023
    com implementação de classe listview herdada classificada asc ou desc por qq campo (class TemaListViewSorted)
    com implementação de paginação em todas as classes
"""


##-----------------------------IMPORTS--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
from django.shortcuts import render, redirect, get_object_or_404

from .models import Coment, Tema, Ci, Comp, Info, TemaComent, CiComent, CompComent, InfoComent, TemaCi, TemaComp, TemaInfo, TemaTema
from django.db.models import Count, Case, When, Value, IntegerField
from django.views import generic
from django.db.models import Prefetch
from django.db import transaction

from novavisio import settings

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import Group
from django.contrib.auth import login
from django.core.exceptions import PermissionDenied

import locale

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

#acesso para as caixas de mensagem padrão do windows
import ctypes

from django import forms
from eletronLab.forms import ComentCreateForm
from eletronLab.forms import TemaComentCreateForm
from eletronLab.forms import CiComentCreateForm
from eletronLab.forms import CiComentNovoForm
from eletronLab.forms import CompComentCreateForm
from eletronLab.forms import CompComentNovoForm
from eletronLab.forms import InfoComentCreateForm
from eletronLab.forms import InfoComentNovoForm
from eletronLab.forms import LeitorSignupForm

from django.views import View
from django.http import HttpResponse

from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
from django.core.cache import cache






##-----------------------------GLOBALS--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
paginacao=15
class AdminRequiredMixin(PermissionRequiredMixin):
    raise_exception = True  # devolve 403 (não redireciona pro login)

##--------------------FUNCTIONS AND CLASSES---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##    home_eLab PAGE **********************************************************************************************************************************************************************    HOME PAGE
def home_eLab(request):
    db_server='indefinido'
    #verifica a fonte de dados
    a=settings.DATABASES['default']['HOST']
    if 'mysql.uhserver.com' in a:
        db_server='UOL Host'
    if '127.0.0.1' in a:
        db_server= r'Local Host (C:\xampp\mysql\data\)'
    if 'pythonanywhere-services.com' in a:
        db_server='Python Anywhere Host'
    db_db=settings.DATABASES['default']['NAME']

    """View function for home page of site."""

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1


    # Generate counts of some of the main objects
    num_temas = Tema.objects.all().count()
    num_coments = Coment.objects.all().count()

    # temas ja estudados (todos - aqueles cujo campo status = estudado
    num_temas_estudados = Tema.objects.filter(status="estudado").count()
    percentual_temas_estudados = "{0:,.1f}%".format((num_temas_estudados/num_temas)*100) if num_temas else "0,0%"
    # temas ja revisados (todos - aqueles cujo campo status = revisado
    num_temas_revisados = Tema.objects.filter(status="revisado").count()
    percentual_temas_revisados = "{0:,.1f}%".format((num_temas_revisados/num_temas)*100) if num_temas else "0,0%"    # The 'all()' is implied by default.

    tmp1=Coment.objects.aggregate(Count('assunto', distinct=True))
    num_assuntos = tmp1['assunto__count']

    num_cis = Ci.objects.all().count()

    cis = Ci.objects.all()

    context = {
        'num_temas': num_temas,
        'num_coments': num_coments,
        'num_assuntos': num_assuntos,
        'num_temas_estudados': num_temas_estudados,
        'percentual_temas_estudados': percentual_temas_estudados,
        'num_temas_revisados': num_temas_revisados,
        'percentual_temas_revisados': percentual_temas_revisados,
        'num_cis': num_cis,
        'num_visits': num_visits,
        'db_server': db_server,
        'db_db': db_db,
        'cis': cis,
    }
  # Render the HTML template index.html with the data in the context variable
    return render(request, 'eletronLab/home_eLab.html', context=context)


##    TEMA ***************************************************************************************************************************************************************************    TEMA
#  LISTA VISUALIZAÇÃO  #################################################################################################################  LISTA VISUALIZAÇÃO
class TemaListViewSorted(LoginRequiredMixin, generic.ListView):
    model = Tema
    template_name = 'eletronLab/tema_list.html'

    #SISTEMA DE CLASSIFICAÇÃO (SORT)**********************************************************
    sort_url='1a'
    sort_str = ''
    #mapemento das colunas/campos da tabela Tema (sort,field,sorted
    sort_mapa = [
            ['1a', 'semana', '0'],
            ['2a', 'ordem', '0'],
            ['3a', 'titulo', '0'],
            ['4a', 'categoria', '0'],
            ['5a', 'pagina', '0'],
            ['6a', 'status', '0'],
    ]

    #SISTEMA DE PAGINAÇÃO**********************************************************
    paginate_by = paginacao

    #SISTEMA DE FILTRAGEM (FILTRO)**********************************************************
    filtro_url=''
    filtro_sem_url=''
    filtro_cat_url=''

    #Lista exclusiva de categorias criando uma lista exclusiva a partir da função set do python
    filtro_cat_lst=list(set(Tema.objects.values_list("categoria"))) #lista de tuples
    #transforma em uma lista de valores
    for i in range(len(filtro_cat_lst)):
        filtro_cat_lst[i]=filtro_cat_lst[i][0]
    #classifica filtro_cat_lst
    #note que para que os caracteres utf-8 sejam considerados há qe se usar o módulo locale
    locale.setlocale(locale.LC_ALL, '')
    filtro_cat_lst=sorted(filtro_cat_lst,key=locale.strxfrm)
    #insere o valor 'vazio' como primeiro item da lista
    filtro_cat_lst.insert(0,"")

    # fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff----get_queryset
    def get_queryset(self):
        #SISTEMA DE CLASSIFICAÇÃO (SORT)************************************************************************************
        #Define ou pega o parâmetro da session 'tema_list_sort'. Usa-se session para não perder as escolhas do usuário
        tema_list_sort = self.request.session.get('tema_list_sort', '1a')
        # Captura do parâmetro col da URL da coluna clasificada pelo usuário, contendo o número da coluna e a ordem, asc ou desc
        self.sort_url=self.request.GET.get('col',tema_list_sort) #caso não encontre retorna o padrão, tema_list_sort
        #Redefine o parâmetro da session 'tema_list_sort' como o parâmetro passado pela url, parâmetro 'col'
        self.request.session['tema_list_sort'] = self.sort_url

        # pega/converte em número a coluna (base 0) passada pela parâmetro col da url da coluna escolhida pelo usuário
        tmp=int(self.sort_url[0])-1

        #reseta a classificação para nenhuma
        for i in range(6):
            self.sort_mapa[i][2]='0'

        #Verifica se a classificação é ascendente (a) ou descendente (d)
        if self.sort_url[1]=='a':
            self.sort_str = self.sort_mapa[tmp][1]
            #atualizar as variáves de contexto
            self.sort_mapa[tmp][0]= f"{tmp+1}d"
            self.sort_mapa[tmp][2]='1'
        elif self.sort_url[1]=='d':
            self.sort_str = '-' + self.sort_mapa[tmp][1]
            #atualizar as variáves de contexto
            self.sort_mapa[tmp][0]= f"{tmp+1}a"
            self.sort_mapa[tmp][2]='1'

        #SISTEMA DE FILTRAGEM (FILTRO) POR SEMANA OU CATEGORIA **********************************************************
        #Define ou pega o parâmetro da session 'temalist_filtro_sem'. Usa-se session para não perder as escolhas do usuário
        temalist_filtro_sem = self.request.session.get('temalist_filtro_sem', '')
        # Captura os parâmetros para filtragem contidos na URL quando se clica em "filtrar"
        self.filtro_sem_url=self.request.GET.get('semana',temalist_filtro_sem) #caso não encontre retorna o padrão, temalist_filtro_sem
        #Redefine o parâmetro da session 'temalist_filtro_sem' como o parâmetro passado pela url, parâmetro 'semana'
        self.request.session['temalist_filtro_sem'] = self.filtro_sem_url

        #torna o valor do filtro de semana um valor inteiro
        if self.filtro_sem_url != '':
            self.filtro_sem_url=int(self.filtro_sem_url)

        #Define ou pega o parâmetro da session 'temalist_filtro_cat'. Usa-se session para não perder as escolhas do usuário
        temalist_filtro_cat = self.request.session.get('temalist_filtro_cat', '')
        self.filtro_cat_url=self.request.GET.get('categoria',temalist_filtro_cat) #caso não encontre retorna o padrão, temalist_filtro_cat

        #Redefine o parâmetro da session 'temalist_filtro_cat' como o parâmetro passado pela url, parâmetro 'categoria'
        self.request.session['temalist_filtro_cat'] = self.filtro_cat_url

        #Verifica e configura o tipo de filtragem e classificação escolhida pelo usuário
        if self.filtro_sem_url != '':
            queryset=Tema.objects.filter(semana__exact=int(self.filtro_sem_url))#.order_by(self.sort_str)
            self.filtro_url=f"&semana={self.filtro_sem_url}"
        elif self.filtro_cat_url !='':
            queryset=Tema.objects.filter(categoria__exact=f'{self.filtro_cat_url}')#.order_by(self.sort_str)
            self.filtro_url=f"&categoria={self.filtro_cat_url}"
        else:
            queryset=Tema.objects.all()#.order_by(self.sort_str)


        # aplicar ordenação no final (para permitir status custom)
        field_name = self.sort_mapa[tmp][1]  # ex.: 'status', 'semana', etc.

        if field_name == "status":
            weight = Case(
                When(status="revisado", then=Value(0)),
                When(status="estudado", then=Value(1)),
                When(status="nenhum", then=Value(2)),
                default=Value(3),
                output_field=IntegerField(),
            )
            if self.sort_url[1] == 'a':
                queryset = queryset.annotate(_status_w=weight).order_by('_status_w')
            else:
                queryset = queryset.annotate(_status_w=weight).order_by('-_status_w')
        else:
            queryset = queryset.order_by(self.sort_str)

        return queryset

    # fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff----get_context_data
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        # Create any data and add it to the context
        context['sort_mapa1'] = f'{self.sort_mapa[0][0]}{self.sort_mapa[0][2]}'
        context['sort_mapa2'] = f'{self.sort_mapa[1][0]}{self.sort_mapa[1][2]}'
        context['sort_mapa3'] = f'{self.sort_mapa[2][0]}{self.sort_mapa[2][2]}'
        context['sort_mapa4'] = f'{self.sort_mapa[3][0]}{self.sort_mapa[3][2]}'
        context['sort_mapa5'] = f'{self.sort_mapa[4][0]}{self.sort_mapa[4][2]}'
        context['sort_mapa6'] = f'{self.sort_mapa[5][0]}{self.sort_mapa[5][2]}'
        context['sort_url'] = self.sort_url
        context['filtro_url'] = self.filtro_url
        context['filtro_sem_url'] = self.filtro_sem_url
        context['filtro_cat_url'] = self.filtro_cat_url
        context['filtro_cat_lst'] = self.filtro_cat_lst
        return context

#  INDIVIDUAL VISUALIZAÇÃO ############################################################################################################   INDIVIDUAL VISUALIZAÇÃO
class TemaDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = 'eletronLab/tema_detail.html'
    model = Tema
    context_object_name = "tema"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tema = self.object

        # Comentários reais (exclui vínculos antigos)
        ctx["comentarios"] = (
            TemaComent.objects
            .filter(tema=tema)
            .exclude(coment__assunto__in=["ci", "comp", "outro tema", "info"])
            .select_related("coment")
            .order_by("coment__assunto", "coment__detalhe")
        )

        # Relações novas
        ctx["tema_cis"] = TemaCi.objects.filter(tema=tema).select_related("ci")
        ctx["tema_comps"] = TemaComp.objects.filter(tema=tema).select_related("comp")
        ctx["tema_infos"] = TemaInfo.objects.filter(tema=tema).select_related("info")

        # ATENÇÃO AQUI: usa related_name
        ctx["tema_temas"] = tema.relacoes_origem.select_related("tema_rel")

        # Para os selects
        ctx["all_cis"] = Ci.objects.all()
        ctx["all_comps"] = Comp.objects.all()
        ctx["all_infos"] = Info.objects.all()

        return ctx

#  INDIVIDUAL UPDATE ###################################################################################################################   INDIVIDUAL UPDATE
class TemaUpdate(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    permission_required = "eletronLab.change_tema"
    model = Tema
    fields = ['semana', 'ordem', 'titulo', 'categoria', 'pagina', 'status']


##    COMENT *************************************************************************************************************************************************************************    COMENT
#  LISTA VISUALIZAÇÃO  ################################################################################################################          LISTA VISUALIZAÇÃO
@method_decorator(never_cache, name='dispatch')
class ComentListView(LoginRequiredMixin, generic.ListView):
    model = Coment
    template_name = 'eletronLab/coment_list.html'
    paginate_by = paginacao

    def get_queryset(self):
        # pega defaults da session
        comentList_filtro_ass = self.request.session.get('comentList_filtro_ass', '')
        comentlist_filtro_det = self.request.session.get('comentlist_filtro_det', '')

        # lê da URL ou usa session
        self.filtro_ass_url = self.request.GET.get('assunto', comentList_filtro_ass)
        self.filtro_det_url = self.request.GET.get('detalhe', comentlist_filtro_det)

        # salva de volta na session
        self.request.session['comentList_filtro_ass'] = self.filtro_ass_url
        self.request.session['comentlist_filtro_det'] = self.filtro_det_url

        # monta queryset + string do filtro (pra paginação/links)
        self.filtro_url = ''
        qs = Coment.objects.all()

        if self.filtro_ass_url:
            qs = qs.filter(assunto__exact=self.filtro_ass_url)
            self.filtro_url += f"&assunto={self.filtro_ass_url}"

        if self.filtro_det_url:
            qs = qs.filter(detalhe__icontains=self.filtro_det_url)
            self.filtro_url += f"&detalhe={self.filtro_det_url}"

        return qs

    def get_assuntos(self):
        key = "coment_assuntos_distintos_v3"
        assuntos = cache.get(key)
        if assuntos is None:
            assuntos = list(
                Coment.objects
                     .order_by()                      # <<< limpa o ordering padrão
                     .values_list("assunto", flat=True)
                     .distinct()
            )

            import locale
            locale.setlocale(locale.LC_ALL, '')
            assuntos = sorted(assuntos, key=locale.strxfrm)
            assuntos.insert(0, "")

            cache.set(key, assuntos, 3600)
        return assuntos

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filtro_ass_lst'] = self.get_assuntos()
        context['filtro_ass_url'] = getattr(self, 'filtro_ass_url', '')
        context['filtro_det_url'] = getattr(self, 'filtro_det_url', '')
        context['filtro_url'] = getattr(self, 'filtro_url', '')
        return context

#  INDIVIDUAL VISUALIZAÇÃO ############################################################################################################     INDIVIDUAL VISUALIZAÇÃO
class ComentDetailView(generic.DetailView):
    model = Coment
    template_name = 'eletronLab/coment_detail.html'  # Specify your own template name/location
    slug_field = 'codcoment'
    slug_url_kwarg = 'codcoment'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # 1) TEMAS associados ao coment (via coment principal do CI)
        qs_temas = self.object.temacoment_set.select_related('tema').all()
        paginator_temas = Paginator(qs_temas, 3)
        ctx['temas_page'] = paginator_temas.get_page(self.request.GET.get('tpage'))

        # 2) CIS associados ao coment (via tabela ci_coment)
        qs_cis = CiComent.objects.filter(coment=self.object).select_related('ci')
        paginator_cis = Paginator(qs_cis, 3)
        ctx['cis_page'] = paginator_cis.get_page(self.request.GET.get('cpage'))

        # 3) COMPONENTES associados ao coment (via tabela comp_coment)
        qs_comps = CompComent.objects.filter(coment=self.object).select_related('comp')
        paginator_comps = Paginator(qs_comps, 3)
        ctx['comps_page'] = paginator_comps.get_page(self.request.GET.get('cnpage'))

        # 4) INFOS complementares associados ao coment (coment_info)
        qs_infos = InfoComent.objects.filter(coment=self.object).order_by("info")
        paginator_infos = Paginator(qs_infos, 3)
        ctx['infos_page'] = paginator_infos.get_page(self.request.GET.get('ipage'))

        return ctx

#  INDIVIDUAL CREATE ###################################################################################################################          INDIVIDUAL CREATE
class ComentCreate(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    permission_required = "eletronLab.add_coment"
    def get(self, request, *args, **kwargs):
        context = {'form': ComentCreateForm()}
        return render(request, 'eletronLab/coment_form.html', context)

    def post(self, request, *args, **kwargs):
        form = ComentCreateForm(request.POST)
        if form.is_valid():
            self.object = form.save()

            # fluxo "criar e associar"
            if self.request.GET.get('coment', '') == 'criar':

                # 1) veio de um TEMA
                tema_pk = self.request.GET.get('tema', '')
                if tema_pk:
                    TemaComent.objects.get_or_create(
                        coment=self.object,
                        tema=Tema.objects.get(pk=int(tema_pk))
                    )
                    return redirect(reverse_lazy('tema-detail', kwargs={'pk': int(tema_pk)}))

                # 2) veio de um CI
                codci = self.request.GET.get('ci', '')
                if codci:
                    CiComent.objects.get_or_create(
                        coment=self.object,
                        ci=Ci.objects.get(pk=codci)  # pk texto OK
                    )
                    return redirect(reverse_lazy('ci-detail', kwargs={'pk': codci}))

            # fluxo normal (só cria comentário)
            return redirect(reverse_lazy('coment-detail', kwargs={'pk': self.object.codcoment}))

        return render(request, 'eletronLab/coment_form.html', {'form': form})

# INDIVIDUAL UPDATE ###################################################################################################################           INDIVIDUAL UPDATE
class ComentUpdate(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    permission_required = "eletronLab.change_coment"
    model = Coment
    fields = ['assunto', 'detalhe', 'obs']

    def get_form_class(self):
        form_class = super().get_form_class()
        form_class.base_fields['detalhe'].widget = forms.Textarea()
        return form_class

# INDIVIDUAL DELETE ####################################################################################################################          INDIVIDUAL DELETE
class ComentDelete(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    permission_required = "eletronLab.delete_coment"
    model = Coment
    success_url = reverse_lazy('coments')


##    TEMACOMENT *********************************************************************************************************************************************************************    TEMACOMENT
#  INDIVIDUAL VISUALIZAÇÃO ##########################################################################################################  INDIVIDUAL VISUALIZAÇÃO
class TemaComentDetailView(LoginRequiredMixin, generic.DetailView):
    model = TemaComent
    template_name = 'eletronLab/temacoment_detail.html'  # Specify your own template name/location

#  INDIVIDUAL CREATE  ################################################################################################################        INDIVIDUAL CREATE
@login_required
@permission_required("eletronLab.add_temacoment", raise_exception=True)
def TemaComentCreate(request):
    # vindo do tema-detail
    tmpTema = request.GET.get('tema', '')

    # vindo do coment-detail
    tmpComent = request.GET.get('coment', '')
    origin = request.GET.get('from', '')  # "coment" ou ""

    if request.method == 'GET':
        initial = {}
        if tmpTema:
            initial['tema'] = tmpTema
        if tmpComent:
            initial['coment'] = tmpComent

        form = TemaComentCreateForm(initial=initial)

        # opcional: se veio do comentário, trava o campo coment
        if tmpComent and 'coment' in form.fields:
            form.fields['coment'].disabled = True

        return render(request, 'eletronLab/temacoment_form.html', {'form': form})

    # POST
    post_data = request.POST.copy()

    # se veio do comentário e o campo estava disabled,
    # ele NÃO vem no POST -> injeta aqui
    if tmpComent:
        post_data['coment'] = tmpComent

    form = TemaComentCreateForm(post_data)

    if not form.is_valid():
        if tmpComent and 'coment' in form.fields:
            form.fields['coment'].disabled = True
        return render(request, 'eletronLab/temacoment_form.html', {'form': form})

    tema_obj = form.cleaned_data['tema']
    coment_obj = form.cleaned_data['coment']

    TemaComent.objects.get_or_create(tema=tema_obj, coment=coment_obj)

    # volta para a origem
    if origin == 'coment' and tmpComent:
        return redirect(reverse_lazy('coment-detail', kwargs={'pk': tmpComent}))

    return redirect(reverse_lazy('tema-detail', kwargs={'pk': tema_obj.pk}))

#  INDIVIDUAL DELETE ################################################################################################################        INDIVIDUAL DELETE
class TemaComentDelete(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    permission_required = "eletronLab.delete_temacoment"
    model = TemaComent

    # fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff----get_success_url
    def get_success_url(self):
        if self.request.GET.get('tema','')=='':
            return reverse_lazy('searchs')
        else:
            return reverse_lazy('tema-detail', kwargs={'pk': self.request.GET.get('tema',1)})

##    CI *********************************************************************************************************************************************************************    CI
#  LISTA VISUALIZAÇÃO  ################################################################################################################          LISTA VISUALIZAÇÃO
def CiListView(request):
    """View function for home ci page of site."""

    num_cis = Ci.objects.all().count()

    cis = Ci.objects.all()

    context = {
        'num_cis': num_cis,
        'cis': cis,
    }
  # Render the HTML template index.html with the data in the context variable
    return render(request, 'eletronLab/ci_list.html', context=context)

#  INDIVIDUAL VISUALIZAÇÃO ############################################################################################################     INDIVIDUAL VISUALIZAÇÃO
class CiDetailView(LoginRequiredMixin, generic.DetailView):
    model = Ci
    template_name = 'eletronLab/ci_detail.html'
    context_object_name = 'ci'
    slug_field = 'codci'
    slug_url_kwarg = 'codci'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # 1) TEMAS associados ao CI (via coment principal do CI)
        qs_temas = self.object.temaci_set.select_related('tema').all()
        paginator_temas = Paginator(qs_temas, 7)
        ctx['temas_page'] = paginator_temas.get_page(self.request.GET.get('tpage'))

        # 2) COMENTÁRIOS associados ao CI (via tabela ci_coment)
        qs_coments = self.object.cicoment_set.select_related('coment').all()
        paginator_coments = Paginator(qs_coments, 7)
        ctx['coments_page'] = paginator_coments.get_page(self.request.GET.get('cpage'))

        return ctx

#  INDIVIDUAL CREATE ################################################################################################################        INDIVIDUAL CREATE
class CiCreate(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    permission_required = "eletronLab.add_ci"
    model = Ci
    fields = ['codci', 'semana', 'sobre']
    success_url = reverse_lazy('cis')

# INDIVIDUAL DELETE ####################################################################################################################          INDIVIDUAL DELETE
class CiDelete(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    permission_required = "eletronLab.delete_ci"
    model = Ci
    success_url = reverse_lazy('cis')

# INDIVIDUAL UPDATE ###################################################################################################################           INDIVIDUAL UPDATE
class CiUpdate(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    permission_required = "eletronLab.change_ci"
    model = Ci
    fields = ['codci', 'semana', 'sobre']
    success_url = reverse_lazy('cis')


##    CI COMENT ***********************************************************************************************************************************************************    CI COMENT
#  INDIVIDUAL VISUALIZAÇÃO ##########################################################################################################  INDIVIDUAL VISUALIZAÇÃO
class CiComentDetailView(LoginRequiredMixin, generic.DetailView):
    model = CiComent
    template_name = 'eletronLab/cicoment_detail.html'  # Specify your own template name/location

#  INDIVIDUAL DELETE ################################################################################################################        INDIVIDUAL DELETE
class CiComentDelete(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    permission_required = "eletronLab.delete_cicoment"
    model = CiComent
    template_name = 'eletronLab/cicoment_confirm_delete.html'
    success_url = reverse_lazy('home')  # fallback

    def get_success_url(self):
        return self.request.GET.get('next') or self.request.POST.get('next') or super().get_success_url()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['next'] = self.request.GET.get('next', '')
        return ctx

#  INDIVIDUAL CREATE  ################################################################################################################        INDIVIDUAL CREATE
@login_required
@permission_required("eletronLab.add_cicoment", raise_exception=True)
def CiComentCreate(request):
    tmpCi = request.GET.get('ci', '')           # vindo do ci-detail
    tmpComent = request.GET.get('coment', '')   # vindo do coment-detail
    origin = request.GET.get('from', '')        # "coment" ou ""

    # tenta obter o objeto CI se veio pelo GET
    ci_obj = None
    if tmpCi:
        ci_obj = get_object_or_404(Ci, pk=tmpCi)

    if request.method == 'GET':
        initial = {}
        if tmpCi:
            initial['ci'] = tmpCi
        if tmpComent:
            initial['coment'] = tmpComent

        form = CiComentCreateForm(initial=initial)

        # se veio do comentário, trava o campo coment (opcional)
        if tmpComent and 'coment' in form.fields:
            form.fields['coment'].disabled = True

        # se veio do ci-detail, trava o campo ci (opcional)
        if tmpCi and 'ci' in form.fields:
            form.fields['ci'].disabled = True

        return render(request, 'eletronLab/cicoment_form.html', {
            'form': form,
            'ci': ci_obj,   # se o template usa isso para título etc.
        })

    # POST
    post_data = request.POST.copy()

    # se o campo estava disabled ele não vem no POST -> injeta
    if tmpComent:
        post_data['coment'] = tmpComent
    if tmpCi:
        post_data['ci'] = tmpCi

    form = CiComentCreateForm(post_data)
    if not form.is_valid():
        # re-disable para continuar travado na tela
        if tmpComent and 'coment' in form.fields:
            form.fields['coment'].disabled = True
        if tmpCi and 'ci' in form.fields:
            form.fields['ci'].disabled = True

        return render(request, 'eletronLab/cicoment_form.html', {
            'form': form,
            'ci': ci_obj,
        })

    ci_obj = form.cleaned_data['ci']
    coment_obj = form.cleaned_data['coment']

    cicoment, created = CiComent.objects.get_or_create(
        ci=ci_obj,
        coment=coment_obj,
    )

    # redirect conforme origem
    if origin == 'coment' and tmpComent:
        return redirect(reverse_lazy('coment-detail', kwargs={'pk': tmpComent}))

    return redirect(reverse_lazy('ci-detail', kwargs={'pk': ci_obj.pk}))


#  INDIVIDUAL CREATE  ALTERNATIVO ################################################################################################################        INDIVIDUAL CREATE ALTERNATIVO
@login_required
@permission_required("eletronLab.add_cicoment", raise_exception=True)
def CiComentNovoCreate(request):
    codci = request.GET.get('ci')
    ci_obj = get_object_or_404(Ci, pk=codci)

    if request.method == 'GET':
        form = CiComentNovoForm()
        return render(request, 'eletronLab/cicoment_form.html', {'form': form, 'ci': ci_obj})

    form = CiComentNovoForm(request.POST)
    if not form.is_valid():
        return render(request, 'eletronLab/cicoment_form.html', {'form': form, 'ci': ci_obj})

    # 1) cria o comentário
    coment_obj = Coment.objects.create(
        assunto=form.cleaned_data['assunto'],
        detalhe=form.cleaned_data.get('detalhe', ''),
        obs=form.cleaned_data.get('obs')
   )

    # 2) cria a associação com obs
    CiComent.objects.create(
        ci=ci_obj,
        coment=coment_obj,
    )

    return redirect(reverse_lazy('ci-detail', kwargs={'pk': ci_obj.pk}))

##    COMPONENTE ******************************************************************************************************************************************************    COMPONENTE
#  LISTA VISUALIZAÇÃO  ################################################################################################################          LISTA VISUALIZAÇÃO
def CompListView(request):
    """View function for home comp page of site."""

    num_comps = Comp.objects.all().count()

    comps = Comp.objects.all()

    context = {
        'num_comps': num_comps,
        'comps': comps,
    }
    return render(request, 'eletronLab/comp_list.html', context=context)

#  INDIVIDUAL VISUALIZAÇÃO ############################################################################################################     INDIVIDUAL VISUALIZAÇÃO
class CompDetailView(LoginRequiredMixin, generic.DetailView):
    model = Comp
    template_name = 'eletronLab/comp_detail.html'
    context_object_name = 'comp'
    slug_field = 'codcomp'
    slug_url_kwarg = 'codcomp'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # 1) TEMAS associados ao Componente (via coment principal do Comp)
        qs_temas = self.object.temacomp_set.select_related('tema').all()
        paginator_temas = Paginator(qs_temas, 7)
        ctx['temas_page'] = paginator_temas.get_page(self.request.GET.get('tpage'))

        # 2) COMENTÁRIOS associados ao Componente (via tabela comp_coment)
        qs_coments = self.object.compcoment_set.select_related('coment').all()
        paginator_coments = Paginator(qs_coments, 7)
        ctx['coments_page'] = paginator_coments.get_page(self.request.GET.get('cpage'))

        return ctx

#  INDIVIDUAL CREATE ################################################################################################################        INDIVIDUAL CREATE
class CompCreate(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    permission_required = "eletronLab.add_comp"
    model = Comp
    fields = ['codcomp', 'sobre']
    success_url = reverse_lazy('comps')

# INDIVIDUAL DELETE ####################################################################################################################          INDIVIDUAL DELETE
class CompDelete(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    permission_required = "eletronLab.delete_comp"
    model = Comp
    success_url = reverse_lazy('comps')

# INDIVIDUAL UPDATE ###################################################################################################################           INDIVIDUAL UPDATE
class CompUpdate(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    permission_required = "eletronLab.change_comp"
    model = Comp
    fields = ['codcomp', 'sobre']
    success_url = reverse_lazy('comps')

    def get_form_class(self):
        form_class = super().get_form_class()
        form_class.base_fields['sobre'].widget = forms.Textarea()
        return form_class

##    COMP COMENT ***********************************************************************************************************************************************************    COMP COMENT
#  INDIVIDUAL VISUALIZAÇÃO ##########################################################################################################  INDIVIDUAL VISUALIZAÇÃO
class CompComentDetailView(LoginRequiredMixin, generic.DetailView):
    model = CompComent
    template_name = 'eletronLab/compcoment_detail.html'  # Specify your own template name/location

#  INDIVIDUAL DELETE ################################################################################################################        INDIVIDUAL DELETE
class CompComentDelete(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    permission_required = "eletronLab.delete_compcoment"
    model = CompComent
    template_name = 'eletronLab/compcoment_confirm_delete.html'
    success_url = reverse_lazy('home')  # fallback

    def get_success_url(self):
        return self.request.GET.get('next') or self.request.POST.get('next') or super().get_success_url()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['next'] = self.request.GET.get('next', '')
        return ctx


#  INDIVIDUAL CREATE  ################################################################################################################        INDIVIDUAL CREATE
@login_required
@permission_required("eletronLab.add_compcoment", raise_exception=True)
def CompComentCreate(request):
    codcomp = request.GET.get('comp', '')        # vindo do comp-detail
    tmpComent = request.GET.get('coment', '')    # vindo do coment-detail
    origin = request.GET.get('from', '')         # "coment" ou ""

    comp_obj = None
    if codcomp:
        comp_obj = get_object_or_404(Comp, pk=codcomp)

    if request.method == 'GET':
        initial = {}
        if codcomp:
            initial['comp'] = codcomp
        if tmpComent:
            initial['coment'] = tmpComent

        form = CompComentCreateForm(initial=initial)

        # opcional: trava os campos quando já vierem definidos
        if codcomp and 'comp' in form.fields:
            form.fields['comp'].disabled = True
        if tmpComent and 'coment' in form.fields:
            form.fields['coment'].disabled = True

        return render(request, 'eletronLab/compcoment_form.html', {
            'form': form,
            'comp': comp_obj,
        })

    # POST
    post_data = request.POST.copy()

    # campos disabled não vão no POST -> injeta
    if codcomp:
        post_data['comp'] = codcomp
    if tmpComent:
        post_data['coment'] = tmpComent

    form = CompComentCreateForm(post_data)
    if not form.is_valid():
        if codcomp and 'comp' in form.fields:
            form.fields['comp'].disabled = True
        if tmpComent and 'coment' in form.fields:
            form.fields['coment'].disabled = True

        return render(request, 'eletronLab/compcoment_form.html', {
            'form': form,
            'comp': comp_obj,
        })

    comp_obj = form.cleaned_data['comp']
    coment_obj = form.cleaned_data['coment']

    compcoment, created = CompComent.objects.get_or_create(
        comp=comp_obj,
        coment=coment_obj,
    )

    # redirect conforme origem
    if origin == 'coment' and tmpComent:
        return redirect(reverse_lazy('coment-detail', kwargs={'pk': tmpComent}))

    return redirect(reverse_lazy('comp-detail', kwargs={'pk': comp_obj.pk}))


#  INDIVIDUAL CREATE  ALTERNATIVO ################################################################################################################        INDIVIDUAL CREATE ALTERNATIVO
@login_required
@permission_required("eletronLab.add_compcoment", raise_exception=True)
def CompComentNovoCreate(request):
    codcomp = request.GET.get('comp')
    comp_obj = get_object_or_404(Comp, pk=codcomp)

    if request.method == 'GET':
        form = CompComentNovoForm()
        return render(request, 'eletronLab/compcoment_form.html', {'form': form, 'comp': comp_obj})

    form = CompComentNovoForm(request.POST)
    if not form.is_valid():
        return render(request, 'eletronLab/compcoment_form.html', {'form': form, 'comp': comp_obj})

    # 1) cria o comentário
    coment_obj = Coment.objects.create(
        assunto=form.cleaned_data['assunto'],
        detalhe=form.cleaned_data.get('detalhe', ''),
        obs=form.cleaned_data.get('obs', '')
   )

    # 2) cria a associação com obs
    CompComent.objects.create(
        comp=comp_obj,
        coment=coment_obj,
    )

    return redirect(reverse_lazy('comp-detail', kwargs={'pk': comp_obj.pk}))

##    INFO ***********************************************************************************************************************************************************    INFO
#  LISTA VISUALIZAÇÃO  ################################################################################################################          LISTA VISUALIZAÇÃO
def InfoListView(request):
    """View function for home comp page of site."""

    num_infos = Info.objects.all().count()

    infos = Info.objects.all()

    context = {
        'num_infos': num_infos,
        'infos': infos,
    }
    return render(request, 'eletronLab/info_list.html', context=context)

#  INDIVIDUAL VISUALIZAÇÃO ############################################################################################################     INDIVIDUAL VISUALIZAÇÃO
class InfoDetailView(LoginRequiredMixin, generic.DetailView):
    model = Info
    template_name = 'eletronLab/info_detail.html'
    context_object_name = 'info'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        qs_temas = self.object.temainfo_set.select_related('tema').all()
        ctx['temas_page'] = Paginator(qs_temas, 7).get_page(self.request.GET.get('tpage'))

        qs_coments = self.object.infocoment_set.select_related('coment').all()
        ctx['coments_page'] = Paginator(qs_coments, 7).get_page(self.request.GET.get('cpage'))

        return ctx


#  INDIVIDUAL CREATE ################################################################################################################        INDIVIDUAL CREATE
class InfoCreate(LoginRequiredMixin, AdminRequiredMixin, CreateView):
    permission_required = "eletronLab.add_info"
    model = Info
    fields = ['codinfo', 'titulo', 'sobre']
    success_url = reverse_lazy('infos')

# INDIVIDUAL DELETE ####################################################################################################################          INDIVIDUAL DELETE
class InfoDelete(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    permission_required = "eletronLab.delete_info"
    model = Info
    success_url = reverse_lazy('infos')

# INDIVIDUAL UPDATE ###################################################################################################################           INDIVIDUAL UPDATE
class InfoUpdate(LoginRequiredMixin, AdminRequiredMixin, UpdateView):
    permission_required = "eletronLab.change_info"
    model = Info
    fields = ['codinfo', 'titulo', 'sobre']
    success_url = reverse_lazy('infos')

##    INFO COMENT ***********************************************************************************************************************************************************    INFO COMENT
#  INDIVIDUAL VISUALIZAÇÃO ##########################################################################################################  INDIVIDUAL VISUALIZAÇÃO
class InfoComentDetailView(LoginRequiredMixin, generic.DetailView):
    model = InfoComent
    template_name = 'eletronLab/infocoment_detail.html'  # Specify your own template name/location

#  INDIVIDUAL DELETE ################################################################################################################        INDIVIDUAL DELETE
class InfoComentDelete(LoginRequiredMixin, AdminRequiredMixin, DeleteView):
    permission_required = "eletronLab.delete_infocoment"
    model = InfoComent
    template_name = 'eletronLab/infocoment_confirm_delete.html'
    success_url = reverse_lazy('home')  # fallback

    def get_success_url(self):
        return self.request.GET.get('next') or self.request.POST.get('next') or super().get_success_url()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['next'] = self.request.GET.get('next', '')
        return ctx


#  INDIVIDUAL CREATE  ################################################################################################################        INDIVIDUAL CREATE
@login_required
@permission_required("eletronLab.add_infocoment", raise_exception=True)
def InfoComentCreate(request):
    codinfo = request.GET.get('info', '')        # vindo do info-detail
    tmpComent = request.GET.get('coment', '')    # vindo do coment-detail
    origin = request.GET.get('from', '')         # "coment" ou ""

    info_obj = None
    if info_obj:
        info_obj = get_object_or_404(Info, pk=codinfo)

    if request.method == 'GET':
        initial = {}
        if codinfo:
            initial['info'] = codinfo
        if tmpComent:
            initial['coment'] = tmpComent

        form = InfoComentCreateForm(initial=initial)

        # opcional: trava os campos quando já vierem definidos
        if codinfo and 'info' in form.fields:
            form.fields['info'].disabled = True
        if tmpComent and 'coment' in form.fields:
            form.fields['coment'].disabled = True

        return render(request, 'eletronLab/compcoment_form.html', {
            'form': form,
            'info': info_obj,
        })

    # POST
    post_data = request.POST.copy()

    # campos disabled não vão no POST -> injeta
    if codinfo:
        post_data['info'] = codinfo
    if tmpComent:
        post_data['coment'] = tmpComent

    form = InfoComentCreateForm(post_data)
    if not form.is_valid():
        if codinfo and 'info' in form.fields:
            form.fields['info'].disabled = True
        if tmpComent and 'coment' in form.fields:
            form.fields['coment'].disabled = True

        return render(request, 'eletronLab/compcoment_form.html', {
            'form': form,
            'info': info_obj,
        })

    info_obj = form.cleaned_data['info']
    coment_obj = form.cleaned_data['coment']

    infocoment, created = InfoComent.objects.get_or_create(
        info=info_obj,
        coment=coment_obj,
    )

    # redirect conforme origem
    if origin == 'coment' and tmpComent:
        return redirect(reverse_lazy('coment-detail', kwargs={'pk': tmpComent}))

    return redirect(reverse_lazy('info-detail', kwargs={'pk': info_obj.pk}))


#  INDIVIDUAL CREATE  ALTERNATIVO ################################################################################################################        INDIVIDUAL CREATE ALTERNATIVO
@login_required
@permission_required("eletronLab.add_infocoment", raise_exception=True)
def InfoComentNovoCreate(request):
    codinfo = request.GET.get('info')
    info_obj = get_object_or_404(Info, pk=codinfo)

    if request.method == 'GET':
        form = InfoComentNovoForm()
        return render(request, 'eletronLab/infocoment_form.html', {'form': form, 'info': info_obj})

    form = InfoComentNovoForm(request.POST)
    if not form.is_valid():
        return render(request, 'eletronLab/infocoment_form.html', {'form': form, 'info': info_obj})

    # 1) cria o comentário
    coment_obj = Coment.objects.create(
        assunto=form.cleaned_data['assunto'],
        detalhe=form.cleaned_data.get('detalhe', ''),
        obs=form.cleaned_data.get('obs')
   )

    # 2) cria a associação com obs
    InfoComent.objects.create(
        info=info_obj,
        coment=coment_obj,
    )

    return redirect(reverse_lazy('info-detail', kwargs={'pk': info_obj.pk}))



##    TEMA2 ***********************************************************************************************************************************************************    TEMA2
#  ################################################################################################################
@login_required
def TemaCiDelete(request, pk):
    obj = get_object_or_404(TemaCi, pk=pk)
    tema_id = obj.tema_id
    obj.delete()
    return redirect("tema-detail", pk=tema_id)

#  ################################################################################################################
@login_required
def TemaCompDelete(request, pk):
    obj = get_object_or_404(TemaComp, pk=pk)
    tema_id = obj.tema_id
    obj.delete()
    return redirect("tema-detail", pk=tema_id)

#  ################################################################################################################
@login_required
def TemaInfoDelete(request, pk):
    obj = get_object_or_404(TemaInfo, pk=pk)
    tema_id = obj.tema_id
    obj.delete()
    return redirect("tema-detail", pk=tema_id)

#  ################################################################################################################
@login_required
def TemaTemaDelete(request, pk):
    obj = get_object_or_404(TemaTema, pk=pk)
    tema_id = obj.tema_id
    tema_rel_id = obj.tema_rel_id

    # apaga o par simétrico também, se existir
    obj.delete()
    TemaTema.objects.filter(tema_id=tema_rel_id, tema_rel_id=tema_id).delete()

    return redirect("tema-detail", pk=tema_id)

#  ################################################################################################################
class TemaCiCreateView(LoginRequiredMixin, generic.CreateView):
    model = TemaCi
    fields = ["ci"]
    template_name = "eletronLab/tema_ci_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.tema = get_object_or_404(Tema, pk=kwargs["tema_pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.tema = self.tema
        return super().form_valid(form)

    def get_success_url(self):
        return self.tema.get_absolute_url()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tema"] = self.tema
        return ctx

#  ################################################################################################################
class TemaCompCreateView(LoginRequiredMixin, generic.CreateView):
    model = TemaComp
    fields = ["comp"]
    template_name = "eletronLab/tema_comp_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.tema = get_object_or_404(Tema, pk=kwargs["tema_pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.tema = self.tema
        return super().form_valid(form)

    def get_success_url(self):
        return self.tema.get_absolute_url()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tema"] = self.tema
        return ctx

#  ################################################################################################################
class TemaInfoCreateView(LoginRequiredMixin, generic.CreateView):
    model = TemaInfo
    fields = ["info"]
    template_name = "eletronLab/tema_info_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.tema = get_object_or_404(Tema, pk=kwargs["tema_pk"])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.tema = self.tema
        return super().form_valid(form)

    def get_success_url(self):
        return self.tema.get_absolute_url()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["tema"] = self.tema
        return ctx

class TemaTemaCreateView(LoginRequiredMixin, generic.CreateView):
    model = TemaTema
    fields = ["tema_rel"]  # NÃO deixe o usuário escolher o "tema" aqui
    template_name = "eletronLab/tema_tema_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.tema = get_object_or_404(Tema, pk=request.GET.get("tema"))
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        return {"tema": self.tema}

    def form_valid(self, form):
        tema = self.tema
        tema_rel = form.cleaned_data["tema_rel"]

        if tema_rel == tema:
            form.add_error("tema_rel", "Não pode relacionar um tema com ele mesmo.")
            return self.form_invalid(form)

        with transaction.atomic():
            TemaTema.objects.get_or_create(tema=tema, tema_rel=tema_rel)
            TemaTema.objects.get_or_create(tema=tema_rel, tema_rel=tema)

        return redirect("tema-detail", pk=tema.pk)

##    LOGIN ***********************************************************************************************************************************************************    LOGIN
#  ##########################################################################################################
class LeitorSignupView(CreateView):
    form_class = LeitorSignupForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("home_eLab")  # ajuste para sua home real

    def form_valid(self, form):
        response = super().form_valid(form)
        grupo, _ = Group.objects.get_or_create(name="Leitor")
        self.object.groups.add(grupo)
        login(self.request, self.object)  # opcional: auto-login
        return response

##    SEARCH *********************************************************************************************************************************************************************    SEARCH
#  LISTA VISUALIZAÇÃO  ##############################################################################################################      LISTA VISUALIZAÇÃO
class SearchListView(LoginRequiredMixin, generic.ListView):
    template_name = 'eletronLab/search_list.html'  # Specify your own template name/location

    #SISTEMA DE PAGINAÇÃO**********************************************************
    paginate_by = 7

    #SISTEMA DE FILTRAGEM (FILTRO)**********************************************************
    filtro_url=''
    filtro_search_url=''

    #SISTEMA DE DA SEGUNDA PAGINAÇÃO********************************************************
    queryset2=Coment.objects.all()
    paginator2 = Paginator(queryset2, 7)
    page_obj2=paginator2.page(1)

    # fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff----get_queryset
    def get_queryset(self):

        #SISTEMA DE FILTRAGEM (FILTRO) POR TERMO QUALQUER **********************************************************
        #Define ou pega o parâmetro da session 'temacomentlist_filtro_search'. Usa-se session para não perder as escolhas do usuário
        temacomentlist_filtro_search = self.request.session.get('temacomentlist_filtro_search', '')
        #resp1=ctypes.windll.user32.MessageBoxW(0, f"{temacomentlist_filtro_search}", "Mensagem Python", 0)# 0 : OK
        # Captura os parâmetros para filtragem contidos na URL quando se clica em "search"
        self.filtro_search_url=self.request.GET.get('search',temacomentlist_filtro_search) #caso não encontre retorna o padrão, temacomentlist_filtro_search
        #resp1=ctypes.windll.user32.MessageBoxW(0, f"{self.filtro_search_url}", "Mensagem Python", 0)# 0 : OK
        #Redefine o parâmetro da session 'temacomentlist_filtro_search' como o parâmetro passado pela url, parâmetro 'search'
        self.request.session['temacomentlist_filtro_search'] = self.filtro_search_url
        #resp1=ctypes.windll.user32.MessageBoxW(0, f"{self.request.session['temacomentlist_filtro_search']}", "self.request.session", 0)# 0 : OK

        #Faz a filtragem do termo escolhido pelo usuário em Temas por títulos; comentários por assunto e detalhe, temas por categoria/pg
        if self.filtro_search_url != '':

            """queryset/paginação gerenciada pelo django (Temas)"""
            #FILTRO EM TEMA/TÍTULOS
            queryset_a=Tema.objects.filter(titulo__icontains=self.filtro_search_url)
            #FILTRO EM TEMA/CATEGORIA/PÁGINA
            queryset_b=Tema.objects.none() #inicializa a variável
            #Verifica se o termo pesquisado é composto de duas palavras
            tmp_split=self.filtro_search_url.split()
            if len(tmp_split) == 2:
                #verifica se o primeiro termo está em "categorias" de temas
                test1=Tema.objects.values_list("categoria").filter(categoria__icontains=tmp_split[0])
                if len(test1)>0:
                    #verifica se o segundo termo é um número inteiro
                    try:
                        pg1=int(tmp_split[1])
                        queryset_b=Tema.objects.filter(categoria__icontains=tmp_split[0]).filter(pagina__exact=pg1)
                    except:
                        pass
            queryset = queryset_a | queryset_b #queryset união dos filtros

            """queryset2/paginação gerenciada manual (Comentários)"""
            queryset2a=Coment.objects.filter(assunto__icontains=self.filtro_search_url)#filtro em assuntos
            queryset2b=Coment.objects.filter(detalhe__icontains=self.filtro_search_url)#filtro em detalhes
            self.queryset2 = queryset2a | queryset2b#queryset união dos filtros

            #SISTEMA DE DA SEGUNDA PAGINAÇÃO********************************************************
            self.paginator2 = Paginator(self.queryset2, 7)
            page2 = self.request.GET.get('page2', 1)
            try:
                self.page_obj2 = self.paginator2.page(page2)
            except PageNotAnInteger:
                self.page_obj2 = self.paginator2.page(1)
            except EmptyPage:
                self.page_obj2 = self.paginator2.page(self.paginator2.num_pages)
            except:
                self.page_obj2 = self.paginator2.page(1)

            self.filtro_url=f"&search={self.filtro_search_url.replace(' ','%20')}"
            #resp1=ctypes.windll.user32.MessageBoxW(0, f"{self.filtro_url.replace(' ','%20')}", "Mensagem Python", 0)# 0 : OK

        else:
            queryset=Tema.objects.all()
            self.queryset2=Coment.objects.all()
            self.paginator2 = Paginator(self.queryset2, 7)
            self.page_obj2=self.paginator2.page(1)

        return queryset

    # fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff----get_context_data
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        # Create any data and add it to the context
        context['filtro_search_url'] = self.filtro_search_url
        context['filtro_url'] = self.filtro_url
        context['page_obj2'] = self.page_obj2
        return context


