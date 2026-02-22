from django.db import migrations

def forward(apps, schema_editor):
    Tema = apps.get_model("eletronLab", "Tema")
    # True -> estudado
    Tema.objects.filter(status=True).update(status_txt="estudado")
    # False -> nenhum
    Tema.objects.filter(status=False).update(status_txt="nenhum")
    # NULL -> nenhum (se existir)
    Tema.objects.filter(status__isnull=True).update(status_txt="nenhum")

def backward(apps, schema_editor):
    Tema = apps.get_model("eletronLab", "Tema")
    Tema.objects.filter(status_txt="estudado").update(status=True)
    Tema.objects.exclude(status_txt="estudado").update(status=False)

class Migration(migrations.Migration):

    dependencies = [
        ("eletronLab", "0007_tema_status_txt"),
    ]
    operations = [
        migrations.RunPython(forward, backward),
    ]