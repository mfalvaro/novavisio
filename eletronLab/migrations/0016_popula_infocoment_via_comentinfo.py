from django.db import migrations, transaction


def _norm(s):
    return (s or "").strip()


def forwards(apps, schema_editor):
    Coment = apps.get_model("eletronLab", "Coment")
    ComentInfo = apps.get_model("eletronLab", "ComentInfo")
    Info = apps.get_model("eletronLab", "Info")
    InfoComent = apps.get_model("eletronLab", "InfoComent")

    created_info = 0
    created_links = 0
    skipped = 0

    qs = (
        ComentInfo.objects
        .select_related("coment")
        .exclude(coment__isnull=True)
    )

    with transaction.atomic():
        for ci in qs.iterator():
            c = ci.coment
            if c is None:
                skipped += 1
                continue

            # Só faz sentido se o Coment for do tipo "info"
            if _norm(c.assunto).lower() != "info":
                continue

            titulo_info = _norm(c.detalhe)
            if not titulo_info:
                skipped += 1
                continue

            info, created = Info.objects.get_or_create(titulo=titulo_info)
            if created:
                created_info += 1

            _, created2 = InfoComent.objects.get_or_create(info=info, coment=c)
            if created2:
                created_links += 1

    print("=== Migração D (via coment_info) ===")
    print(f"Info criados: {created_info}")
    print(f"Links InfoComent criados: {created_links}")
    print(f"Pulados (coment ausente / detalhe vazio): {skipped}")


def backwards(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("eletronLab", "0015_auto_20260224_2141"),  # ajuste pro seu último
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]