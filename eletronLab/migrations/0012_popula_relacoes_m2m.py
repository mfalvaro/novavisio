from django.db import migrations, transaction


def _norm(s):
    return (s or "").strip()


def _parse_outro_tema(detalhe):
    """
    Espera algo tipo: "áudio 10" ou "teoria 53"
    Retorna (categoria, pagina_int) ou (None, None)
    """
    txt = _norm(detalhe)
    if not txt:
        return None, None
    try:
        cat, pag = txt.rsplit(" ", 1)
        return _norm(cat), int(pag)
    except Exception:
        return None, None


def forwards(apps, schema_editor):
    Tema = apps.get_model("eletronLab", "Tema")
    Coment = apps.get_model("eletronLab", "Coment")
    TemaComent = apps.get_model("eletronLab", "TemaComent")

    Ci = apps.get_model("eletronLab", "Ci")
    Comp = apps.get_model("eletronLab", "Comp")
    Info = apps.get_model("eletronLab", "Info")

    TemaCi = apps.get_model("eletronLab", "TemaCi")
    TemaComp = apps.get_model("eletronLab", "TemaComp")
    TemaInfo = apps.get_model("eletronLab", "TemaInfo")
    TemaTema = apps.get_model("eletronLab", "TemaTema")

    created_tema_ci = 0
    created_tema_comp = 0
    created_tema_info = 0
    created_tema_tema = 0
    skipped_ci = 0
    skipped_comp = 0
    skipped_info = 0
    skipped_outro_tema = 0

    # Pega só os vínculos que interessam (reduz custo)
    qs = (
        TemaComent.objects
        .select_related("tema", "coment")
        .exclude(tema__isnull=True)
        .exclude(coment__isnull=True)
    )

    with transaction.atomic():
        # -----------------------------------------
        # 1) tema_ci e tema_comp
        # -----------------------------------------
        for tc in qs.iterator():
            tema = tc.tema
            coment = tc.coment
            assunto = _norm(coment.assunto).lower()
            detalhe = _norm(coment.detalhe)

            if assunto == "ci":
                if not detalhe:
                    skipped_ci += 1
                    continue
                ci = Ci.objects.filter(codci=detalhe).first()
                if not ci:
                    skipped_ci += 1
                    continue
                obj, created = TemaCi.objects.get_or_create(tema=tema, ci=ci)
                if created:
                    created_tema_ci += 1

            elif assunto == "comp":
                if not detalhe:
                    skipped_comp += 1
                    continue
                comp = Comp.objects.filter(codcomp=detalhe).first()
                if not comp:
                    skipped_comp += 1
                    continue
                obj, created = TemaComp.objects.get_or_create(tema=tema, comp=comp)
                if created:
                    created_tema_comp += 1

        # -----------------------------------------
        # 2) tema_info (assunto == "info")
        # Cria Info se não existir, usando detalhe como título
        # -----------------------------------------
        for tc in qs.iterator():
            tema = tc.tema
            coment = tc.coment
            assunto = _norm(coment.assunto).lower()
            detalhe = _norm(coment.detalhe)

            if assunto != "info":
                continue
            if not detalhe:
                skipped_info += 1
                continue

            info, _ = Info.objects.get_or_create(titulo=detalhe)
            obj, created = TemaInfo.objects.get_or_create(tema=tema, info=info)
            if created:
                created_tema_info += 1

        # -----------------------------------------
        # 3) tema_tema (assunto == "outro tema")
        # Cria vínculo A->B e também B->A
        # -----------------------------------------
        for tc in qs.iterator():
            tema_a = tc.tema
            coment = tc.coment
            assunto = _norm(coment.assunto).lower()
            detalhe = _norm(coment.detalhe)

            if assunto != "outro tema":
                continue

            categoria, pagina = _parse_outro_tema(detalhe)
            if not categoria or pagina is None:
                skipped_outro_tema += 1
                continue

            tema_b = Tema.objects.filter(categoria=categoria, pagina=pagina).first()
            if not tema_b:
                skipped_outro_tema += 1
                continue

            if tema_a.codtema == tema_b.codtema:
                continue

            # A -> B
            obj1, created1 = TemaTema.objects.get_or_create(tema=tema_a, tema_rel=tema_b)
            if created1:
                created_tema_tema += 1

            # B -> A (simétrico)
            obj2, created2 = TemaTema.objects.get_or_create(tema=tema_b, tema_rel=tema_a)
            if created2:
                created_tema_tema += 1

    # Logs (aparecem no migrate)
    print("=== Migração B (M2M) ===")
    print(f"TemaCi criados: {created_tema_ci} | pulados (CI não encontrado/detalhe vazio): {skipped_ci}")
    print(f"TemaComp criados: {created_tema_comp} | pulados (Comp não encontrado/detalhe vazio): {skipped_comp}")
    print(f"TemaInfo criados: {created_tema_info} | pulados (detalhe vazio): {skipped_info}")
    print(f"TemaTema criados: {created_tema_tema} | pulados (parse/tema destino não encontrado): {skipped_outro_tema}")


def backwards(apps, schema_editor):
    # Conservador: não desfaz automaticamente
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("eletronLab", "0011_migra_obs_para_coment"),  # ajuste para o nome real da migration A
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]