# coding: utf-8
"""
    Name:        forms.py
    Purpose:
    Author:      GPS-PC08
    Created:     01/05/2023
"""
##-----------------------------IMPORTS------------------------------------------
from django import forms
from eletronLab.models import Coment, CiComent, CompComent
from eletronLab.models import TemaComent
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


##--------------------FUNCTIONS AND CLASSES-------------------------------------
# ##################################################################################################################################
class ComentCreateForm(forms.ModelForm):
    detalhe = forms.CharField(widget=forms.Textarea, required=False)
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
    #coment = forms.ModelMultipleChoiceField(queryset = Coment.objects.all(),)
    coment = forms.ModelChoiceField(queryset=Coment.objects.all())
    class Meta:
        model = TemaComent
        fields = ['tema', 'coment']

# ##################################################################################################################################
class CiComentCreateForm(forms.ModelForm):
    obs = forms.CharField(widget=forms.Textarea, required=False)
    coment = forms.ModelChoiceField(
        queryset=Coment.objects.all(),
        label='Comentário'
    )

    class Meta:
        model = CiComent
        fields = ['ci','coment', 'obs']   # ← tira 'ci'


# ##################################################################################################################################
class CiComentNovoForm(forms.Form):
    assunto = forms.CharField(max_length=75)
    detalhe = forms.CharField(widget=forms.Textarea, required=False)
    obs = forms.CharField(widget=forms.Textarea, required=False)

# ##################################################################################################################################
class CompComentCreateForm(forms.ModelForm):
    obs = forms.CharField(widget=forms.Textarea, required=False)
    coment = forms.ModelChoiceField(
        queryset=Coment.objects.all(),
        label='Comentário'
    )

    class Meta:
        model = CompComent
        fields = ['comp','coment', 'obs']   # ← tira 'comp'


# ##################################################################################################################################
class CompComentNovoForm(forms.Form):
    assunto = forms.CharField(max_length=75)
    detalhe = forms.CharField(widget=forms.Textarea, required=False)
    obs = forms.CharField(widget=forms.Textarea, required=False)

class LeitorSignupForm(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")