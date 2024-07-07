# coding: utf-8
"""
    Name:        forms.py
    Purpose:
    Author:      GPS-PC08
    Created:     01/05/2023
"""
##-----------------------------IMPORTS------------------------------------------
from django import forms
from eletronLab.models import Coment
from eletronLab.models import TemaComent
#from django.core.exceptions import ValidationError

##--------------------FUNCTIONS AND CLASSES-------------------------------------
# ##################################################################################################################################
class ComentCreateForm(forms.ModelForm):
    class Meta:
        model = Coment
        fields = ['assunto', 'detalhe']

    def clean_assunto(self):
        data = self.cleaned_data["assunto"]
        data = data.lower().strip()
        return data # sempre retorne o valor, mesmo que não tenha sido modificado

    def clean_detalhe(self):
        data = self.cleaned_data['detalhe']
        data = data.lower().strip()
        if 'transistor' in data:
            #raise ValidationError("Corrrija a acentuação!")
            data = data.replace('transistor','transístor')
        return data # sempre retorne o valor, mesmo que não tenha sido modificado


# ##################################################################################################################################
class TemaComentCreateForm(forms.ModelForm):
    coment = forms.ModelMultipleChoiceField(queryset = Coment.objects.all(),)
    class Meta:
        model = TemaComent
        fields = ['tema', 'coment']
##        widgets = {
##            'coment': forms.ModelMultipleChoiceField(widget = forms.CheckboxSelectMultiple, queryset = Coment.objects.all(),),
##        }

