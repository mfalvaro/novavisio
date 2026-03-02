from django.db import migrations, transaction


def _norm(s):
    return (s or "").strip()


def forwards(apps, schema_editor):
    Coment = apps.get_model("eletronLab", "Coment")
    Info = apps.get_model("eletronLab", "Info")
    InfoComent = apps.get_model("eletronLab", "InfoComent")

    created_info = 0
    created_link = 0

    qs = Coment.objects.filter(assunto="info").exclude(detalhe__isnull=True).exclude(detalhe__exact="")

    with transaction.atomic():
        for c in qs.iterator():
            titulo = _norm(c.detalhe)
            if not titulo:
                continue

            info, created = Info.objects.get_or_create(titulo=titulo)
            if created:
                created_info += 1

            _, created2 = InfoComent.objects.get_or_create(info=info, coment=c)
            if created2:
                created_link += 1

    print("=== Migração C (Info + InfoComent) ===")
    print(f"Info criados: {created_info}")
    print(f"Links InfoComent criados: {created_link}")


def backwards(apps, schema_editor):
    # Conservador: não desfaz automaticamente
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("eletronLab", "0013_infocoment"),  # ajuste se seu último nome for outro
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]