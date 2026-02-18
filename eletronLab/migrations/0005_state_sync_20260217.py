# Generated manually to sync Django migration state with existing DB schema.

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('eletronLab', '0004_merge_20260203_2325'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[

                migrations.AddField(
                    model_name='ci',
                    name='coment',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        db_column='Coment',
                        help_text='Coment único associado ao ci',
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to='eletronLab.coment',
                    ),
                ),

                migrations.AddField(
                    model_name='cicoment',
                    name='ci',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        db_column='ci_id',
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to='eletronLab.ci',
                    ),
                ),
                migrations.AddField(
                    model_name='cicoment',
                    name='coment',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        db_column='coment_id',
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to='eletronLab.coment',
                    ),
                ),

                migrations.AddField(
                    model_name='comp',
                    name='coment',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        db_column='coment_id',
                        help_text='Coment único associado ao comp',
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to='eletronLab.coment',
                    ),
                ),

                migrations.AddField(
                    model_name='compcoment',
                    name='coment',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        db_column='coment_id',
                        help_text='Comentário',
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to='eletronLab.coment',
                    ),
                ),
                migrations.AddField(
                    model_name='compcoment',
                    name='comp',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        db_column='comp_id',
                        help_text='Componente',
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to='eletronLab.comp',
                    ),
                ),

                migrations.AddField(
                    model_name='temacoment',
                    name='coment',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        db_column='Coment',
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to='eletronLab.coment',
                    ),
                ),
                migrations.AddField(
                    model_name='temacoment',
                    name='tema',
                    field=models.ForeignKey(
                        blank=True, null=True,
                        db_column='Tema',
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        to='eletronLab.tema',
                    ),
                ),

                migrations.AlterField(
                    model_name='cicoment',
                    name='codci_coment',
                    field=models.AutoField(db_column='codci_coment', primary_key=True, serialize=False),
                ),
                migrations.AlterField(
                    model_name='cicoment',
                    name='data',
                    field=models.DateTimeField(auto_now_add=True, db_column='data', null=True),
                ),

                migrations.AlterField(
                    model_name='comp',
                    name='codcomp',
                    field=models.CharField(
                        blank=True, db_column='codcomp',
                        help_text='Nome do componente',
                        max_length=15, primary_key=True, serialize=False
                    ),
                ),
                migrations.AlterField(
                    model_name='comp',
                    name='sobre',
                    field=models.CharField(
                        blank=True, null=True,
                        db_column='sobre',
                        help_text='Descrição do componente',
                        max_length=75
                    ),
                ),

                migrations.AlterField(
                    model_name='compcoment',
                    name='codcomp_coment',
                    field=models.AutoField(db_column='codcomp_coment', primary_key=True, serialize=False),
                ),
                migrations.AlterField(
                    model_name='compcoment',
                    name='data',
                    field=models.DateTimeField(auto_now_add=True, db_column='data', null=True),
                ),

                migrations.AlterField(
                    model_name='tema',
                    name='categoria',
                    field=models.CharField(blank=True, null=True, db_column='Categoria', help_text='Uma categoria do lab', max_length=15),
                ),
                migrations.AlterField(
                    model_name='tema',
                    name='ordem',
                    field=models.SmallIntegerField(blank=True, null=True, db_column='Ordem', help_text='Sequencia no fascículo'),
                ),
                migrations.AlterField(
                    model_name='tema',
                    name='pagina',
                    field=models.IntegerField(blank=True, null=True, db_column='Pagina', help_text='Sequencia de pgs por categoria'),
                ),
                migrations.AlterField(
                    model_name='tema',
                    name='semana',
                    field=models.SmallIntegerField(blank=True, null=True, db_column='Semana', help_text='Semana do fascículo'),
                ),
                migrations.AlterField(
                    model_name='tema',
                    name='status',
                    field=models.BooleanField(db_column='Status', default=False, help_text='Tema estudado sim ou não?', null=True),
                ),
                migrations.AlterField(
                    model_name='tema',
                    name='titulo',
                    field=models.CharField(blank=True, null=True, db_column='Titulo', help_text='Título do tema', max_length=255),
                ),

                migrations.AlterUniqueTogether(
                    name='cicoment',
                    unique_together={('ci', 'coment')},
                ),
                migrations.AlterUniqueTogether(
                    name='coment',
                    unique_together={('assunto', 'detalhe')},
                ),
                migrations.AlterUniqueTogether(
                    name='compcoment',
                    unique_together={('comp', 'coment')},
                ),
                migrations.AlterUniqueTogether(
                    name='temacoment',
                    unique_together={('tema', 'coment')},
                ),
            ],
        ),
    ]
