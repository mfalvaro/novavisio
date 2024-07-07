# coding: utf-8

"""Desrição de APP\admin.py"""

##-----------------------------IMPORTS------------------------------------------
from django.contrib import admin

#importa os modelos deste APP
from .models import Coment, Tema, TemaComent

#importa a função built-in F
from django.db.models import F

##----------------------CLASSES AND FUNCTIONS ----------------------------------
# ############################################################################################################
class ComentInstanceInline(admin.TabularInline):
    model = TemaComent

# ############################################################################################################
class TemaInstanceInline(admin.TabularInline):
    model = TemaComent

# ############################################################################################################
# Define the admin class
class ComentAdmin(admin.ModelAdmin):
    list_display = ('codcoment', 'assunto', 'detalhe')
    fields = ['assunto', 'detalhe']
    inlines = [ComentInstanceInline]

# ############################################################################################################
# Define the admin class
class TemaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'categoria', 'pagina', 'semana','ordem')
    list_filter = ('categoria', 'semana')
    inlines = [TemaInstanceInline]
    queryset = Tema.objects.order_by(F('semana').asc(nulls_first=False))

# ############################################################################################################
# Define the admin class
class TemaComentAdmin(admin.ModelAdmin):
    list_display = ('tema', 'coment', 'data')


##----------------------------COMANDS-------------------------------------------
'''# default
# Registros das classes para admin site
#admin.site.register(Coment)
#admin.site.register(Tema)
#admin.site.register(TemaComent)
'''
'''# personalizadas'''
# Register the admin classes with the associated model
admin.site.register(Coment, ComentAdmin)
admin.site.register(Tema, TemaAdmin)
admin.site.register(TemaComent, TemaComentAdmin)
