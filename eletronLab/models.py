# coding: utf-8
"""
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
"""
##-----------------------------IMPORTS------------------------------------------
from django.db import models
# Used to generate URLs by reversing the URL patterns
from django.urls import reverse

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

##----------------------CLASSES AND FUNCTIONS ----------------------------------
# ########################################################################################################################################################################################
class Coment(models.Model):
    codcoment = models.AutoField(db_column='Codcoment', primary_key=True)  # Field name made lowercase.
    assunto = models.CharField(db_column='Assunto', max_length=255, blank=True, null=True, help_text='De maneira geral, do que trata o comentário?')  # Field name made lowercase.
    detalhe = models.CharField(db_column='Detalhe', max_length=255, blank=True, null=True, help_text='Descreva detalhes ...')  # Field name made lowercase.


    # NOVO
    obs = models.TextField(
        db_column='Obs',
        blank=True,
        null=True,
        help_text='Observação adicional (link ou texto livre).'
    )

    class Meta:
        #managed = False
        db_table = 'coment'
        ordering = ['assunto', 'detalhe']

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.assunto} :: {self.detalhe}'

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('coment-detail', args=[str(self.codcoment)])

# ########################################################################################################################################################################################
class Tema(models.Model):
    codtema = models.AutoField(db_column='Codtema', primary_key=True)
    semana = models.SmallIntegerField(db_column='Semana', blank=True, null=True, help_text='Semana do fascículo')
    ordem = models.SmallIntegerField(db_column='Ordem', blank=True, null=True, help_text='Sequencia no fascículo')
    categoria = models.CharField(db_column='Categoria', max_length=15, blank=True, null=True, help_text='Uma categoria do lab')
    titulo = models.CharField(db_column='Titulo', max_length=255, blank=True, null=True, help_text='Título do tema')
    pagina = models.IntegerField(db_column='Pagina', blank=True, null=True, help_text='Sequencia de pgs por categoria')


    # Campo novo (temporário)
    STATUS_REVISADO = "revisado"
    STATUS_ESTUDADO = "estudado"
    STATUS_NENHUM   = "nenhum"

    STATUS_CHOICES = [
        (STATUS_REVISADO, "Revisado"),
        (STATUS_ESTUDADO, "Estudado"),
        (STATUS_NENHUM,   "Nenhum"),
    ]

    status = models.CharField(
        db_column='Status',
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_NENHUM,
        null=False,
        blank=False,
        db_index=True,
        help_text='Status do tema (texto)',
    )

    class Meta:
        db_table = 'tema'
        ordering = ['semana', 'ordem']

    def __str__(self):
        return f'{self.semana}.{self.ordem} {self.titulo} ({self.categoria} {self.pagina})'

    def get_absolute_url(self):
        return reverse('tema-detail', args=[str(self.codtema)])

# ########################################################################################################################################################################################
class Ci(models.Model):
    codci = models.CharField(db_column='Codci', primary_key=True, max_length=15, blank=True, null=False, help_text='Nome do circuito integrado')
    semana = models.IntegerField(db_column='Semana', blank=True, null=True, help_text='Semana que apareceu pela primeira vez')
    sobre = models.CharField(db_column='Sobre', max_length=75, blank=True, null=True, help_text='Descrição do circuito integrado')

    class Meta:
        #managed = False
        db_table = 'ci'
        ordering = ['semana']

    def __str__(self):
        """String for representing the Model object."""
        return f'semana {self.semana} | ci {self.codci} - {self.sobre}'

    def get_absolute_url(self):
        """Returns the url to access a detail record for a ci."""
        return reverse('ci-detail', args=[str(self.codci)])

# ########################################################################################################################################################################################
class Comp(models.Model):
    codcomp = models.CharField(db_column='codcomp', primary_key=True, max_length=15, blank=True, null=False, help_text='Nome do componente')
    sobre = models.CharField(db_column='sobre', max_length=75, blank=True, null=True, help_text='Descrição do componente')

    class Meta:
        #managed = False
        db_table = 'comp'
        ordering = ['codcomp']

    def __str__(self):
        """String for representing the Model object."""
        return f'Componente {self.codcomp} - {self.sobre}'

    def get_absolute_url(self):
        """Returns the url to access a detail record."""
        #return f"comp/{str(self.codcomp)}"
        return reverse('comp-detail', args=[str(self.codcomp)])

# ########################################################################################################################################################################################
class Info(models.Model):
    codinfo = models.AutoField(db_column='Codinfo', primary_key=True)
    titulo = models.CharField(db_column='Titulo', max_length=150, blank=True, null=True)
    sobre = models.CharField(db_column='Sobre', max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'info'
        ordering = ['titulo']

    def __str__(self):
        return f'{self.titulo}'

    def get_absolute_url(self):
        return reverse('info-detail', args=[str(self.codinfo)])

# ########################################################################################################################################################################################
class TemaComent(models.Model):
    codtema_coment = models.AutoField(db_column='Codtema_coment', primary_key=True)  # Field name made lowercase.
    tema = models.ForeignKey(Tema, models.DO_NOTHING, db_column='Tema', blank=True, null=True)  # Field name made lowercase.
    coment = models.ForeignKey(Coment, models.DO_NOTHING, db_column='Coment', blank=True, null=True)  # Field name made lowercase.
    data = models.DateTimeField(db_column='Data', blank=True, null=True, auto_now_add=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'tema_coment'
        unique_together = (('tema', 'coment'),)
        ordering = ['tema', 'coment']

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.tema.semana}.{self.tema.ordem} {self.tema.categoria} {self.tema.pagina}-{self.coment.assunto}::{self.coment.detalhe}'

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('temacoment-detail', args=[str(self.codtema_coment)])

# ########################################################################################################################################################################################
class CiComent(models.Model):
    codci_coment = models.AutoField(db_column='codci_coment', primary_key=True)  # Field name made lowercase.
    ci = models.ForeignKey(Ci, models.DO_NOTHING, db_column='ci_id', blank=True, null=True)  # Field name made lowercase.
    coment = models.ForeignKey(Coment, models.DO_NOTHING, db_column='coment_id', blank=True, null=True)  # Field name made lowercase.
    data = models.DateTimeField(db_column='data', blank=True, null=True, auto_now_add=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'ci_coment'
        unique_together = (('ci', 'coment'),)
        ordering = ['ci', 'coment']

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.ci.semana}.{self.ci.sobre}-{self.coment.assunto}::{self.coment.detalhe}'

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('cicoment-detail', args=[str(self.codci_coment)])

# ########################################################################################################################################################################################
class CompComent(models.Model):
    codcomp_coment = models.AutoField(db_column='codcomp_coment', primary_key=True)  # Field name made lowercase.
    comp = models.ForeignKey(Comp, models.DO_NOTHING, db_column='comp_id', blank=True, null=True, help_text='Componente')  # Field name made lowercase.
    coment = models.ForeignKey(Coment, models.DO_NOTHING, db_column='coment_id', blank=True, null=True, help_text='Comentário')  # Field name made lowercase.
    data = models.DateTimeField(db_column='data', blank=True, null=True, auto_now_add=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'comp_coment'
        unique_together = (('comp', 'coment'),)
        ordering = ['comp', 'coment']

    def __str__(self):
        """String for representing the Model object."""
        return f'{self.comp.codcomp}.{self.comp.sobre}-{self.coment.assunto}::{self.coment.detalhe}'

    def get_absolute_url(self):
        """Returns the url to access a detail record for this book."""
        return reverse('compcoment-detail', args=[str(self.codcomp_coment)])

# ########################################################################################################################################################################################
class InfoComent(models.Model):
    codinfo_coment = models.AutoField(db_column='Codinfo_coment', primary_key=True)
    info = models.ForeignKey('Info', models.DO_NOTHING, db_column='Info', blank=True, null=True)
    coment = models.ForeignKey('Coment', models.DO_NOTHING, db_column='Coment', blank=True, null=True)
    data = models.DateTimeField(db_column='Data', blank=True, null=True, auto_now_add=True)

    class Meta:
        db_table = 'info_coment'
        unique_together = (('info', 'coment'),)
        ordering = ['info', 'coment']

    def __str__(self):
        return f'{self.info} - {self.coment.assunto}::{self.coment.detalhe}'

# ########################################################################################################################################################################################
class TemaCi(models.Model):
    codtema_ci = models.AutoField(db_column='Codtema_ci', primary_key=True)
    tema = models.ForeignKey(Tema, models.DO_NOTHING, db_column='Tema', blank=True, null=True)
    ci = models.ForeignKey(Ci, models.DO_NOTHING, db_column='Ci', blank=True, null=True)
    data = models.DateTimeField(db_column='Data', blank=True, null=True, auto_now_add=True)

    class Meta:
        db_table = 'tema_ci'
        unique_together = (('tema', 'ci'),)
        ordering = ['tema', 'ci']

    def __str__(self):
        return f'{self.tema} ↔ CI {self.ci.codci}'

# ########################################################################################################################################################################################
class TemaComp(models.Model):
    codtema_comp = models.AutoField(db_column='Codtema_comp', primary_key=True)
    tema = models.ForeignKey(Tema, models.DO_NOTHING, db_column='Tema', blank=True, null=True)
    comp = models.ForeignKey(Comp, models.DO_NOTHING, db_column='Comp', blank=True, null=True)
    data = models.DateTimeField(db_column='Data', blank=True, null=True, auto_now_add=True)

    class Meta:
        db_table = 'tema_comp'
        unique_together = (('tema', 'comp'),)
        ordering = ['tema', 'comp']

    def __str__(self):
        return f'{self.tema} ↔ COMP {self.comp.codcomp}'

# ########################################################################################################################################################################################
class TemaInfo(models.Model):
    codtema_info = models.AutoField(db_column='Codtema_info', primary_key=True)
    tema = models.ForeignKey(Tema, models.DO_NOTHING, db_column='Tema', blank=True, null=True)
    info = models.ForeignKey(Info, models.DO_NOTHING, db_column='Info', blank=True, null=True)
    data = models.DateTimeField(db_column='Data', blank=True, null=True, auto_now_add=True)

    class Meta:
        db_table = 'tema_info'
        unique_together = (('tema', 'info'),)
        ordering = ['tema', 'info']

    def __str__(self):
        return f'{self.tema} ↔ INFO {self.info.titulo}'

# ########################################################################################################################################################################################
class TemaTema(models.Model):
    codtema_tema = models.AutoField(db_column='Codtema_tema', primary_key=True)
    tema = models.ForeignKey(Tema, models.DO_NOTHING, db_column='Tema', related_name='relacoes_origem', blank=True, null=True)
    tema_rel = models.ForeignKey(Tema, models.DO_NOTHING, db_column='Tema_rel', related_name='relacoes_destino', blank=True, null=True)
    data = models.DateTimeField(db_column='Data', blank=True, null=True, auto_now_add=True)

    class Meta:
        db_table = 'tema_tema'
        unique_together = (('tema', 'tema_rel'),)
        ordering = ['tema', 'tema_rel']

    def __str__(self):
        return f'{self.tema} ↔ {self.tema_rel}'

### ########################################################################################################################################################################################
##class ComentInfo(models.Model):
##    codinfo = models.AutoField(db_column='Codinfo', primary_key=True)
##
##    coment = models.ForeignKey(
##        Coment,
##        on_delete=models.CASCADE,
##        db_column='Coment',
##        related_name='infos',
##        null=False,
##        blank=False,
##    )
##
##    titulo = models.CharField(
##        db_column='Titulo',
##        max_length=150,
##        blank=True,
##        null=True,
##        help_text='Título curto (bom para renderizar links).'
##    )
##
##    info = models.TextField(
##        db_column='Info',
##        null=False,
##        blank=False,
##        help_text='Texto longo ou URL.'
##    )
##
##    class Meta:
##        db_table = 'coment_info'
##        ordering = ['codinfo']
##
##    @property
##    def is_link(self) -> bool:
##        val = (self.info or "").strip()
##        if not val:
##            return False
##        v = URLValidator(schemes=["http", "https"])
##        try:
##            v(val)
##            return True
##        except ValidationError:
##            return False
##
##    def __str__(self):
##        return f'{self.coment.assunto} :: {self.titulo or self.info[:50]}'
