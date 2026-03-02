from django.db import migrations, transaction


def _is_empty(val):
    return val is None or str(val).strip() == ""


def forwards(apps, schema_editor):
    Coment = apps.get_model("eletronLab", "Coment")
    CiComent = apps.get_model("eletronLab", "CiComent")
    CompComent = apps.get_model("eletronLab", "CompComent")

    # Vamos atualizar Coment.obs quando estiver vazio,
    # usando CiComent.obs / CompComent.obs.
    to_update = {}  # {codcoment: new_obs}

    # 1) ci_coment -> coment.obs
    qs_ci = (
        CiComent.objects
        .select_related("coment")
        .exclude(obs__isnull=True)
        .exclude(obs__exact="")
        .exclude(coment__isnull=True)
    )
    for cc in qs_ci.iterator():
        c = cc.coment
        if c is None:
            continue
        if _is_empty(getattr(c, "obs", None)) and not _is_empty(cc.obs):
            # Não sobrescreve se já coletamos algo pra esse Coment
            to_update.setdefault(c.codcoment, cc.obs.strip())

    # 2) comp_coment -> coment.obs
    qs_comp = (
        CompComent.objects
        .select_related("coment")
        .exclude(obs__isnull=True)
        .exclude(obs__exact="")
        .exclude(coment__isnull=True)
    )
    for cp in qs_comp.iterator():
        c = cp.coment
        if c is None:
            continue
        if _is_empty(getattr(c, "obs", None)) and not _is_empty(cp.obs):
            to_update.setdefault(c.codcoment, cp.obs.strip())

    if not to_update:
        return

    # Aplica as alterações em lote
    with transaction.atomic():
        # Busca os Coment afetados e atualiza
        objs = list(Coment.objects.filter(codcoment__in=list(to_update.keys())))
        for obj in objs:
            obj.obs = to_update.get(obj.codcoment)
        Coment.objects.bulk_update(objs, ["obs"])


def backwards(apps, schema_editor):
    # Conservador: não desfaz automaticamente
    # (para não apagar obs que você possa ter preenchido manualmente depois)
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("eletronLab", "0010_auto_20260224_2019"),  # ajuste se o seu último for outro
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]