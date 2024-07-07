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
from django.shortcuts import render

from .models import Coment, Tema, TemaComent, Ci
from django.db.models import Count
from django.views import generic

from novavisio import settings
#
from django.contrib.auth.mixins import LoginRequiredMixin

import locale

from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import redirect
#acesso para as caixas de mensagem padrão do windows
import ctypes

from eletronLab.forms import ComentCreateForm
from eletronLab.forms import TemaComentCreateForm

import sys
#Importa funções comuns reunidas no módulo aux1
#sys.path.append(r'C:\Users\GPS-PC08\Documents\_Particular\Books\tec_mat\2021_05_Estudo_NumeroComplexo')
#import aux1 as aux

from django.views import View
from django.http import HttpResponse


##-----------------------------GLOBALS--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
paginacao=15

##--------------------FUNCTIONS AND CLASSES---------------------------------------------------------------------------------------------------------------------------------------------------------------------------
##    home_eLab PAGE **********************************************************************************************************************************************************************    HOME PAGE
def home_eLab(request):
    #verifica a fonte de dados
    a=settings.DATABASES['default']['HOST']
    if 'mysql.uhserver.com' in a:
        db_server='UOL Host'
    if 'localhost' in a:
        db_server='localhost'
    db_db=settings.DATABASES['default']['NAME']

    """View function for home page of site."""

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1


    # Generate counts of some of the main objects
    num_temas = Tema.objects.all().count()
    num_coments = Coment.objects.all().count()

    # temas ja estudados (todos - aqueles cujo campo ordem = NULL
    num_temas_estudados = Tema.objects.filter(status__exact=True).count()

    # The 'all()' is implied by default.
    tmp1=Coment.objects.aggregate(Count('assunto', distinct=True))
    num_assuntos = tmp1['assunto__count']

    percentual_temas_estudados = "{0:,.1f}%".format((num_temas_estudados/num_temas)*100)

    num_cis = Ci.objects.all().count()

    cis = Ci.objects.all()

    context = {
        'num_temas': num_temas,
        'num_coments': num_coments,
        'num_temas_estudados': num_temas_estudados,
        'num_assuntos': num_assuntos,
        'percentual_temas_estudados': percentual_temas_estudados,
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
class TemaListViewSorted(generic.ListView):
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
##    page_url=1
##    page_obj=''

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
##        resp1=ctypes.windll.user32.MessageBoxW(0, f"{self.request.path}", "Mensagem Python", 0)# 0 : OK
##        resp1=ctypes.windll.user32.MessageBoxW(0, f"{self.request.GET.getlist('categoria', default=None)}", "Mensagem Python", 0)# 0 : OK
##        resp1=ctypes.windll.user32.MessageBoxW(0, f"{self.request.get_full_path_info()}", "Mensagem Python", 0)# 0 : OK

        #Redefine o parâmetro da session 'temalist_filtro_cat' como o parâmetro passado pela url, parâmetro 'categoria'
        self.request.session['temalist_filtro_cat'] = self.filtro_cat_url

        #Verifica e configura o tipo de filtragem e classificação escolhida pelo usuário
        if self.filtro_sem_url != '':
            queryset=Tema.objects.filter(semana__exact=int(self.filtro_sem_url)).order_by(self.sort_str)
            self.filtro_url=f"&semana={self.filtro_sem_url}"
        elif self.filtro_cat_url !='':
            queryset=Tema.objects.filter(categoria__exact=f'{self.filtro_cat_url}').order_by(self.sort_str)
            self.filtro_url=f"&categoria={self.filtro_cat_url}"
        else:
            queryset=Tema.objects.all().order_by(self.sort_str)

##        #SISTEMA DE PAGINAÇÃO **********************************************************
##        #Define ou pega o parâmetro da session 'tema_list_page'. Usa-se session para não perder as escolhas do usuário
##        tema_list_page = self.request.session.get('tema_list_page', 1)
##        # Captura do parâmetro page da URL da paginação automática
##        self.page_url=self.request.GET.get('page',tema_list_page) #caso não encontre retorna o padrão, tema_list_page
##        #Redefine o parâmetro da session 'tema_list_sort' como o parâmetro passado pela url, parâmetro 'col'
##        self.request.session['tema_list_page'] = self.page_url
##        paginator = Paginator(queryset, self.paginate_by)
##        self.page_obj = paginator.get_page(self.page_url)
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
##        context['page_obj'] = self.page_obj
        return context


#  INDIVIDUAL VISUALIZAÇÃO ############################################################################################################   INDIVIDUAL VISUALIZAÇÃO
class TemaDetailView(generic.DetailView):
    template_name = 'eletronLab/tema_detail.html'  # Specify your own template name/location
    model = Tema


#  INDIVIDUAL UPDATE ###################################################################################################################   INDIVIDUAL UPDATE
class TemaUpdate(UpdateView):
    model = Tema
    fields = ['semana', 'ordem', 'titulo', 'categoria', 'pagina', 'status']


##    COMENT *************************************************************************************************************************************************************************    COMENT
#  LISTA VISUALIZAÇÃO  ################################################################################################################          LISTA VISUALIZAÇÃO
class ComentListView(generic.ListView):
    model = Coment
    template_name = 'eletronLab/coment_list.html'  # Specify your own template name/location

    #SISTEMA DE PAGINAÇÃO**********************************************************
    paginate_by = paginacao

    #SISTEMA DE FILTRAGEM (FILTRO)**********************************************************
    filtro_url=''
    filtro_ass_url=''
    filtro_det_url=''

    #Lista exclusiva de assuntos criando uma lista exclusiva a partir da função set do python
    filtro_ass_lst=list(set(Coment.objects.values_list("assunto"))) #lista de tuples
    #transforma em uma lista de valores
    for i in range(len(filtro_ass_lst)):
        filtro_ass_lst[i]=filtro_ass_lst[i][0]
    #classifica filtro_ass_lst
    #note que para que os caracteres utf-8 sejam considerados há qe se usar o módulo locale
    locale.setlocale(locale.LC_ALL, '')
    filtro_ass_lst=sorted(filtro_ass_lst,key=locale.strxfrm)
    #insere o valor 'vazio' como primeiro item da lista
    filtro_ass_lst.insert(0,"")

    # fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff----get_queryset
    def get_queryset(self):

        #SISTEMA DE FILTRAGEM (FILTRO) POR ASSUNTO E/OU DETALHE **********************************************************
        #Define ou pega o parâmetro da session 'comentlist_filtro_ass'. Usa-se session para não perder as escolhas do usuário
        comentList_filtro_ass = self.request.session.get('comentList_filtro_ass', '')
        # Captura os parâmetros para filtragem contidos na URL quando se clica em "filtrar"
        self.filtro_ass_url=self.request.GET.get('assunto',comentList_filtro_ass) #caso não encontre retorna o padrão, comentList_filtro_ass
        #Redefine o parâmetro da session 'comentList_filtro_ass' como o parâmetro passado pela url, parâmetro 'assunto'
        self.request.session['comentList_filtro_ass'] = self.filtro_ass_url

##        #torna o valor do filtro de assunto um valor inteiro
##        if self.filtro_ass_url != '':
##            self.filtro_ass_url=int(self.filtro_ass_url)

        #Define ou pega o parâmetro da session 'comentlist_filtro_det'. Usa-se session para não perder as escolhas do usuário
        comentlist_filtro_det = self.request.session.get('comentlist_filtro_det', '')
        self.filtro_det_url=self.request.GET.get('detalhe',comentlist_filtro_det) #caso não encontre retorna o padrão, comentlist_filtro_det
        #Redefine o parâmetro da session 'comentlist_filtro_det' como o parâmetro passado pela url, parâmetro 'categoria'
        self.request.session['comentlist_filtro_det'] = self.filtro_det_url

        #Verifica e configura o tipo de filtragem escolhida pelo usuário
        if self.filtro_ass_url != '' and self.filtro_det_url == '':
            queryset=Coment.objects.filter(assunto__exact=self.filtro_ass_url)#.order_by(self.sort_str)
            self.filtro_url=f"&assunto={self.filtro_ass_url}"
        elif self.filtro_det_url !='' and self.filtro_ass_url == '':
            queryset=Coment.objects.filter(detalhe__icontains=self.filtro_det_url)#.order_by(self.sort_str)
            self.filtro_url=f"&detalhe={self.filtro_det_url}"
        elif self.filtro_det_url !='' and self.filtro_ass_url != '':
            queryset=Coment.objects.filter(assunto__exact=self.filtro_ass_url).filter(detalhe__icontains=self.filtro_det_url)#.order_by(self.sort_str)
            self.filtro_url=f"&assunto={self.filtro_ass_url}&detalhe={self.filtro_det_url}"
        else:
            queryset=Coment.objects.all()#.order_by(self.sort_str)

##        #SISTEMA DE PAGINAÇÃO **********************************************************
##        #Define ou pega o parâmetro da session 'tema_list_page'. Usa-se session para não perder as escolhas do usuário
##        tema_list_page = self.request.session.get('tema_list_page', 1)
##        # Captura do parâmetro page da URL da paginação automática
##        self.page_url=self.request.GET.get('page',tema_list_page) #caso não encontre retorna o padrão, tema_list_page
##        #Redefine o parâmetro da session 'tema_list_sort' como o parâmetro passado pela url, parâmetro 'col'
##        self.request.session['tema_list_page'] = self.page_url
##        paginator = Paginator(queryset, self.paginate_by)
##        self.page_obj = paginator.get_page(self.page_url)
        return queryset


    # fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff----get_context_data
    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super().get_context_data(**kwargs)
        # Create any data and add it to the context
        context['filtro_ass_lst'] = self.filtro_ass_lst
        context['filtro_ass_url'] = self.filtro_ass_url
        context['filtro_det_url'] = self.filtro_det_url
        context['filtro_url'] = self.filtro_url
        return context

#  INDIVIDUAL VISUALIZAÇÃO ############################################################################################################     INDIVIDUAL VISUALIZAÇÃO
class ComentDetailView(generic.DetailView):
    model = Coment
    template_name = 'eletronLab/coment_detail.html'  # Specify your own template name/location


#  INDIVIDUAL CREATE ###################################################################################################################          INDIVIDUAL CREATE
class ComentCreate(CreateView):
    def get(self, request, *args, **kwargs):
        context = {'form': ComentCreateForm()}
        return render(request, 'eletronLab/coment_form.html', context)

    def post(self, request, *args, **kwargs):
        form = ComentCreateForm(request.POST)
        if form.is_valid():
            self.object = form.save()
            self.object.save()
            if self.request.GET.get('coment','')=='criar':
                tc1 = TemaComent.objects.create(coment=self.object, tema=Tema.objects.get(pk=int(self.request.GET.get('tema',''))))
                return redirect(reverse_lazy('tema-detail', kwargs={'pk': self.request.GET.get('tema',1)}))
            return redirect(reverse_lazy('coment-detail', kwargs={'pk': self.object.codcoment}))
#            return redirect(reverse_lazy('coments'))
        return render(request, 'eletronLab/coment_form.html', {'form': form})


# INDIVIDUAL UPDATE ###################################################################################################################           INDIVIDUAL UPDATE
class ComentUpdate(UpdateView):
    model = Coment
    fields = ['assunto', 'detalhe']


# INDIVIDUAL DELETE ####################################################################################################################          INDIVIDUAL DELETE
class ComentDelete(DeleteView):
    model = Coment
    success_url = reverse_lazy('coments')


##    TEMACOMENT *********************************************************************************************************************************************************************    TEMACOMENT
#  LISTA VISUALIZAÇÃO  ##############################################################################################################      LISTA VISUALIZAÇÃO
class SearchListView(generic.ListView):
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

#  INDIVIDUAL VISUALIZAÇÃO ##########################################################################################################  INDIVIDUAL VISUALIZAÇÃO
class TemaComentDetailView(generic.DetailView):
    model = TemaComent
    template_name = 'eletronLab/temacoment_detail.html'  # Specify your own template name/location


#  INDIVIDUAL CREATE MULTIPLE ################################################################################################################        INDIVIDUAL CREATE MULTIPLE
def TemaComentCreate(request):
    #Guarda o id do tema para criar os TemaComents de comentários já existentes selecionados (select multiple)
    tmpTema=request.GET.get('tema',1)
    #verifica o método de chamada GET ou POST
    if request.method == 'GET':
        context = {'form': TemaComentCreateForm(initial={'tema':tmpTema},)}#inicializa o formulário em branco
        return render(request, 'eletronLab/temacoment_form.html', context)
    elif request.method == 'POST':
        form = TemaComentCreateForm(request.POST) #iniciliza o formulário com os dados selecionadas pelo usuário
        #insere os registros dos comentários selecionados pelo usuário para o tema (tmpTema)
        for cmt in form['coment'].data:
            tmpTemaCmt, created = TemaComent.objects.get_or_create(tema= Tema.objects.get(pk=tmpTema), coment= Coment.objects.get(pk=cmt))
            #tmpTemaCmt = TemaComent(tema= Tema.objects.get(pk=tmpTema), coment= Coment.objects.get(pk=cmt))
            #tmpTemaCmt.save()
        return redirect(reverse_lazy('tema-detail', kwargs={'pk': tmpTema}))

#        resp1=ctypes.windll.user32.MessageBoxW(0, f"Request method: GET", "Mensagem Python", 0)# 0 : OK
#        resp1=ctypes.windll.user32.MessageBoxW(0, f"Request method: POST", "Mensagem Python", 0)# 0 : OK
#        resp1=ctypes.windll.user32.MessageBoxW(0, f"{form['coment'].data}\n{type(form['coment'].data)}", "Mensagem Python", 0)# 0 : OK

#  INDIVIDUAL DELETE ################################################################################################################        INDIVIDUAL DELETE
class TemaComentDelete(DeleteView):
    model = TemaComent

    # fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff----get_success_url
    def get_success_url(self):
        if self.request.GET.get('tema','')=='':
            return reverse_lazy('searchs')
        else:
            return reverse_lazy('tema-detail', kwargs={'pk': self.request.GET.get('tema',1)})


##    OUTRO TEMA **********************************************************************************************************************************************************************    OUTRO TEMA
def OutroTema(request):

    # Captura do parâmetro outrotema da URL onde está a categoria do tema e sua respectiva página separadas por um espaço em branco
    #A categoria em especial, "O laboratório 11" (por exemplo) deve ser parseada de forma distinta das demais,
    #pois tem um len() igual a 3 e as demais tem um len() igual a dois
    outrotema = request.GET.get('outrotema',"teoria 1") #caso não encontre retorna o padrão, Teoria 1
    tmp1=outrotema.split()
    if len(tmp1)==3:
        tmpcat=tmp1[0]+ ' ' + tmp1[1] # categoria "O Laboratório"
        tmppag=int(tmp1[2]) #página
    else:
        tmpcat=tmp1[0]# demais categoria
        tmppag=int(tmp1[1])# página

    #queryset que recupera o respectivo tema a partir de sua categoria/pg
    tmptema = Tema.objects.filter(categoria__iexact=tmpcat).filter(pagina__exact=tmppag)

    #em caso de algum problema retorna um queryset com o primeiro tema "Teoria 1"
    if len(tmptema)!=1:
        tmptema = Tema.objects.filter(categoria__iexact='teoria').filter(pagina__exact=1)


    # Render the HTML template e redireciona para o tema recuperado tema/id que por sua vez é
    #direcionada para TemaDetailView()
    return redirect(tmptema[0])

##    CI *********************************************************************************************************************************************************************    CI
#  INDIVIDUAL CREATE ################################################################################################################        INDIVIDUAL CREATE
class CiCreate(CreateView):
    model = Ci
    fields = ['codci', 'semana', 'sobre']
    success_url = reverse_lazy('home')

# INDIVIDUAL DELETE ####################################################################################################################          INDIVIDUAL DELETE
class CiDelete(DeleteView):
    model = Ci
    success_url = reverse_lazy('home')

# INDIVIDUAL UPDATE ###################################################################################################################           INDIVIDUAL UPDATE
class CiUpdate(UpdateView):
    model = Ci
    fields = ['codci', 'semana', 'sobre']
    success_url = reverse_lazy('home')
