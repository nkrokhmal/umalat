from .models_new import *
from .enum import LineName


def read_params(fn='app/data/params_1020.xlsx'):
    df = pd.read_excel(fn, index_col=0)
    return df


def fill_db():
    fill_simple_data()
    fill_boiling_technologies()
    fill_cooling_technologies()
    fill_boilings()
    fill_form_factors()
    fill_sku()
    fill_termizator()
    fill_made_from()


def fill_simple_data():
    Department.generate_departments()
    Line.generate_lines()
    Packer.generate_packer()
    PackType.generate_types()
    Group.generate_group()


def fill_boiling_technologies():
    df = read_params()
    boiling_technologies_columns = ['Время налива', 'Время отвердевания', 'Время нарезки', 'Время слива', 'Дополнительное время']
    bt_data = df[boiling_technologies_columns]
    bt_data = bt_data.drop_duplicates()
    bt_data = bt_data.to_dict('records')
    for bt in bt_data:
        technology = BoilingTechnology(
            pouring_time=bt['Время налива'],
            soldification_time=bt['Время отвердевания'],
            cutting_time=bt['Время нарезки'],
            pouring_off_time=bt['Время слива'],
            extra_time=bt['Дополнительное время']
        )

        db.session.add(technology)
        db.session.commit()


def fill_cooling_technologies():
    df = read_params()
    data = df[['Охлаждение 1(для воды)', 'Охлаждение 2(для воды)', 'Время посолки']]
    data = data.drop_duplicates()
    data = data.to_dict('records')
    for value in data:
        if any([not np.isnan(x) for x in value.values()]):
            technology = CoolingTechnology(
                first_cooling_time=value['Охлаждение 1(для воды)'],
                second_cooling_time=value['Охлаждение 2(для воды)'],
                salting_time=value['Время посолки']
            )

            db.session.add(technology)
    db.session.commit()


def fill_boilings():
    df = read_params()
    lines = db.session.query(Line).all()
    bts = db.session.query(BoilingTechnology).all()
    columns = ['Тип закваски', 'Процент', 'Наличие лактозы', 'Линия',
               'Время налива', 'Время отвердевания', 'Время нарезки', 'Время слива',
               'Дополнительное время']
    b_data = df[columns]
    b_data = b_data.drop_duplicates()
    b_data = b_data.to_dict('records')
    for b in b_data:
        if b['Линия'] == 'Соль':
            line_id = [x for x in lines if x.name == LineName.SALT][0].id
        else:
            line_id = [x for x in lines if x.name == LineName.WATER][0].id
        bt_id = [x for x in bts if (x.pouring_time == b['Время налива']) &
                 (x.soldification_time == b['Время отвердевания']) &
                 (x.cutting_time == b['Время нарезки']) &
                 (x.pouring_off_time == b['Время слива']) &
                 (x.extra_time == b['Дополнительное время'])][0].id
        boiling = Boiling(
            percent=b['Процент'],
            is_lactose=True if b['Наличие лактозы'] == 'Да' else False,
            ferment=b['Тип закваски'],
            boiling_technology_id=bt_id,
            line_id=line_id
        )
        db.session.add(boiling)
        db.session.commit()


def fill_form_factors():
    lines = db.session.query(Line).all()
    df = read_params()
    mass_ff = FormFactor(name='Масса')
    db.session.add(mass_ff)
    db.session.commit()

    columns = ['Название форм фактора', 'Вес форм фактора', 'Охлаждение 1(для воды)', 'Охлаждение 2(для воды)', 'Время посолки', 'Линия']
    df = df[columns]
    df['Название форм фактора'] = df['Название форм фактора'].apply(lambda x: x if 'Терка' in x else None)
    df = df.drop_duplicates()
    values = df.to_dict('records')
    for value in values:
        line_name = LineName.SALT if value['Линия'] == 'Соль' else LineName.WATER
        if value['Вес форм фактора'] == 1:
            name = value['Название форм фактора']
        elif value['Вес форм фактора'] == 15:
            name = 'Палочки 15г'
        elif value['Вес форм фактора'] == 30:
            name = 'Палочки 30г'
        else:
            name = str(value['Вес форм фактора'] / 1000)

        form_factor = FormFactor(name=name, relative_weight=value['Вес форм фактора'])
        form_factor.line = [x for x in lines if x.name == line_name][0]
        cooling_technologies = db.session.query(CoolingTechnology).all()
        if 'Терка' not in name:
            form_factor.default_cooling_technology = [
                x for x in cooling_technologies if
                all([x.first_cooling_time == _cast_non_nan(value['Охлаждение 1(для воды)']),
                     x.second_cooling_time == _cast_non_nan(value['Охлаждение 2(для воды)']),
                     x.salting_time == _cast_non_nan(value['Время посолки'])])][0]

        db.session.add(form_factor)
    db.session.commit()

    form_factors = db.session.query(FormFactor).all()
    mass_ff = [x for x in form_factors if x.name == 'Масса'][0]
    for form_factor in form_factors:
        form_factor.add_made_from(form_factor)
        form_factor.add_made_from(mass_ff)
    db.session.commit()


def _cast_non_nan(obj):
    if obj is None:
        return
    elif np.isnan(obj):
        return
    else:
        return obj


def fill_sku():
    df = read_params()
    lines = db.session.query(Line).all()
    packer = db.session.query(Packer).all()
    boilings = db.session.query(Boiling).all()
    form_factors = db.session.query(FormFactor).all()
    groups = db.session.query(Group).all()

    columns = ['Название SKU', 'Процент', 'Наличие лактозы', 'Тип закваски', 'Имя бренда', 'Вес нетто', 'Срок хранения',
               'Является ли SKU теркой', 'Упаковщик', 'Скорость сборки', 'Скорость упаковки', 'Линия', 'Вес форм фактора', 'Название форм фактора', 'Охлаждение 1(для воды)', 'Охлаждение 2(для воды)', 'Время посолки']

    sku_data = df[columns]
    sku_data = sku_data.drop_duplicates()
    sku_data = sku_data.to_dict('records')
    for sku in sku_data:
        is_lactose = sku['Наличие лактозы'] == 'Да'
        add_sku = SKU(
            name=sku['Название SKU'],
            brand_name=sku['Имя бренда'],
            weight_netto=sku['Вес нетто'],
            shelf_life=sku['Срок хранения'],
            collecting_speed=_cast_non_nan(sku['Скорость сборки']) or _cast_non_nan(sku['Скорость упаковки']),
            packing_speed=sku['Скорость упаковки']
        )

        sku_packers = [x for x in packer if x.name in sku['Упаковщик'].split('/')]
        add_sku.packers += sku_packers

        line_name = LineName.SALT if sku['Линия'] == 'Соль' else LineName.WATER
        add_sku.line = [x for x in lines if x.name == line_name][0]

        add_sku.made_from_boilings = [x for x in boilings if
                   (x.percent == sku['Процент']) &
                   (x.is_lactose == is_lactose) &
                   (x.ferment == sku['Тип закваски']) &
                   (x.line_id == add_sku.line.id)]
        add_sku.group = [x for x in groups if x.name == sku['Название форм фактора']][0]
        if add_sku.group.name != 'Качокавалло':
            add_sku.production_by_request = True
            add_sku.packing_by_request = True
        elif add_sku.name == 'Качокавалло "Unagrande", 45%, 0,26 кг, в/у, (8 шт)':
            add_sku.production_by_request = False
            add_sku.packing_by_request = True
        else:
            add_sku.production_by_request = False
            add_sku.packing_by_request = False
        add_sku.form_factor = [x for x in form_factors if x.relative_weight == sku['Вес форм фактора'] and x.line.name == line_name][0]

        db.session.add(add_sku)
    db.session.commit()


def fill_termizator():
    termizator = Termizator()
    termizator.name = 'термизатор'
    termizator.short_cleaning_time = 40
    termizator.long_cleaning_time = 80
    db.session.add(termizator)
    db.session.commit()


def fill_made_from():
    skus = db.session.query(SKU).all()
    form_factors = db.session.query(FormFactor).all()
    sul_rubber = [x for x in form_factors if x.name == 'Терка Сулугуни'][0]
    moz_rubber = [x for x in form_factors if x.name == 'Терка Моцареллы'][0]
    sul_ffs = set([x.form_factor for x in skus if 'сулугуни' in x.name.lower()])
    moz_ffs = set([x.form_factor for x in skus if 'моцарелла' in x.name.lower()])
    for sul_ff in sul_ffs:
        sul_rubber.add_made_from(sul_ff)
    for moz_ff in moz_ffs:
        moz_rubber.add_made_from(moz_ff)
    db.session.commit()

