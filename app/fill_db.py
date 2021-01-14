from .models_new import *

def read_params(fn='app/data/params.xlsx'):
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


def fill_simple_data():
    Department.generate_departments()
    Line.generate_lines()
    Packer.generate_packer()
    PackType.generate_types()
    Group.generate_group()


def fill_boiling_technologies():
    df = read_params()
    boiling_technologies_columns = ['Время налива', 'Время отвердевания', 'Время нарезки', 'Время слива',
                                    'Дополнительное время']
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
            line_id = [x for x in lines if x.name == 'salt'][0].id
        else:
            line_id = [x for x in lines if x.name == 'water'][0].id
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
    df = read_params()
    groups = db.session.query(Group).all()
    mass = [x for x in groups if x.name == 'Масса'][0].id
    mass_ff = FormFactor(
        relative_weight=100000,
        group_id=mass
    )
    db.session.add(mass_ff)
    db.session.commit()

    columns = ['Вес форм фактора', 'Название форм фактора']
    ff_data = df[columns]
    ff_data = ff_data.drop_duplicates()
    ff_data = ff_data.to_dict('records')
    for ff in ff_data:
        group_id = [x for x in groups if x.name == ff['Название форм фактора']][0].id
        form_factor = FormFactor(
            relative_weight=ff['Вес форм фактора'],
            group_id=group_id
        )
        db.session.add(form_factor)
    db.session.commit()

    form_factors = db.session.query(FormFactor).all()
    mass_ff = [x for x in form_factors if x.relative_weight == 100000][0]
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
    cooling_tecnhologies = db.session.query(CoolingTechnology).all()

    columns = ['Название SKU', 'Процент', 'Наличие лактозы', 'Тип закваски', 'Имя бренда', 'Вес нетто', 'Срок хранения',
               'Является ли SKU теркой', 'Упаковщик', 'Скорость упаковки', 'Линия', 'Вес форм фактора', 'Название форм фактора', 'Охлаждение 1(для воды)', 'Охлаждение 2(для воды)', 'Время посолки']

    sku_data = df[columns]
    sku_data = sku_data.drop_duplicates()
    sku_data = sku_data.to_dict('records')
    for sku in sku_data:
        is_lactose = True if sku['Наличие лактозы'] == 'Да' else False
        add_sku = SKU(
            name=sku['Название SKU'],
            brand_name=sku['Имя бренда'],
            weight_netto=sku['Вес нетто'],
            shelf_life=sku['Срок хранения'],
            packing_speed=sku['Скорость упаковки']
        )

        add_sku.packer = [x for x in packer if x.name == sku['Упаковщик']][0]

        line_name = 'salt' if sku['Линия'] == 'Соль' else 'water'
        add_sku.line = [x for x in lines if x.name == line_name][0]

        add_sku.made_from_boilings = [x for x in boilings if
                   (x.percent == sku['Процент']) &
                   (x.is_lactose == is_lactose) &
                   (x.ferment == sku['Тип закваски']) &
                   (x.line_id == add_sku.line.id)]

        add_sku.form_factor = [x for x in form_factors if x.relative_weight == sku['Вес форм фактора'] and x.group.name == sku['Название форм фактора']][0]

        add_sku.cooling_technology = [x for x in cooling_tecnhologies if all([x.first_cooling_time == _cast_non_nan(sku['Охлаждение 1(для воды)']),
                                                                              x.second_cooling_time == _cast_non_nan(sku['Охлаждение 2(для воды)']),
                                                                              x.salting_time == _cast_non_nan(sku['Время посолки'])])][0]

        db.session.add(add_sku)
    db.session.commit()


def fill_termizator():
    termizator = Termizator()
    termizator.name = 'термизатор'
    termizator.short_cleaning_time = 40
    termizator.long_cleaning_time = 80
    db.session.add(termizator)
    db.session.commit()
