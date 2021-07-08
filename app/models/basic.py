import binascii
import hashlib

from flask_login import UserMixin
from sqlalchemy import func, extract
from sqlalchemy.orm import backref

from app.imports.runtime import *


class User(mdb.Model, UserMixin):
    __tablename__ = 'users'
    id = mdb.Column(mdb.Integer, primary_key=True)
    username = mdb.Column(mdb.String, unique=True)
    email = mdb.Column(mdb.String, unique=True)
    password = mdb.Column(mdb.Binary)

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            if hasattr(value, '__iter__') and not isinstance(value, str):
                value = value[0]
            if property == 'password':
                value = self.hash_pass(value)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)

    @staticmethod
    def hash_pass(password):
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwd_hash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
        pwd_hash = binascii.hexlify(pwd_hash)
        return salt + pwd_hash

    @staticmethod
    def verify_pass(provided_password, stored_password):
        stored_password = stored_password.decode('ascii')
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        pwd_hash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000)
        pwd_hash = binascii.hexlify(pwd_hash).decode('ascii')
        return pwd_hash == stored_password


@login_manager.user_loader
def user_loader(id):
    return mdb.session.query(User).filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = mdb.session.query(User).filter_by(username=username).first()
    return user if user else None


class Department(mdb.Model):
    __tablename__ = "departments"
    id = mdb.Column(mdb.Integer, primary_key=True)
    name = mdb.Column(mdb.String)

    batch_numbers = mdb.relationship(
        "BatchNumber",
        backref=backref(
            "department",
            uselist=False,
        ),
    )
    lines = mdb.relationship(
        "Line",
        backref=backref(
            "department",
            uselist=False,
        ),
    )
    washer = mdb.relationship("Washer", backref=backref("department", uselist=False))

    def serialize(self):
        return {"id": self.id, "name": self.name}


class SKU(mdb.Model):
    __tablename__ = "skus"
    id = mdb.Column(mdb.Integer, primary_key=True)
    name = mdb.Column(mdb.String)
    brand_name = mdb.Column(mdb.String)
    weight_netto = mdb.Column(mdb.Float)
    shelf_life = mdb.Column(mdb.Integer)
    code = mdb.Column(mdb.String)
    collecting_speed = mdb.Column(mdb.Integer, nullable=True)
    packing_speed = mdb.Column(mdb.Integer, nullable=True)
    in_box = mdb.Column(mdb.Integer)

    group_id = mdb.Column(mdb.Integer, mdb.ForeignKey("groups.id"), nullable=True)
    line_id = mdb.Column(mdb.Integer, mdb.ForeignKey("lines.id"), nullable=True)
    form_factor_id = mdb.Column(
        mdb.Integer, mdb.ForeignKey("form_factors.id"), nullable=True
    )
    pack_type_id = mdb.Column(
        mdb.Integer, mdb.ForeignKey("pack_types.id"), nullable=True
    )

    type = mdb.Column(mdb.String)
    __mapper_args__ = {"polymorphic_identity": "skus", "polymorphic_on": type}

    @property
    def packers_str(self):
        return "/".join([x.name for x in self.packers])

    @property
    def colour(self):
        COLOURS = {
            "Для пиццы": "#E5B7B6",
            "Моцарелла": "#DAE5F1",
            "Фиор Ди Латте": "#CBC0D9",
            "Чильеджина": "#E5DFEC",
            "Качокавалло": "#F1DADA",
            "Сулугуни": "#F1DADA",
            "Рикотта": "#A3D5D2",
            "Терка": "#FFEBE0",
            "Маскарпоне": "#E5B7B6",
            "Кремчиз": "#DAE5F1",
            "Творожный": "#CBC0D9",
            "Робиола": "#E5DFEC",
            "Сливки": "#F1DADA",
            "Масло": "#F3B28E",
            "Четук": "#CDFCB2",
            "Качорикотта": "#D8EEFF",
            "Кавказский": "#E5B7B6",
            "Черкесский": "#CBC0D9",
        }
        if "Терка" not in self.form_factor.name:
            return COLOURS[self.group.name]
        else:
            return COLOURS["Терка"]


class Line(mdb.Model):
    __tablename__ = "lines"
    id = mdb.Column(mdb.Integer, primary_key=True)
    name = mdb.Column(mdb.String)
    department_id = mdb.Column(
        mdb.Integer, mdb.ForeignKey("departments.id"), nullable=True
    )

    skus = mdb.relationship(
        "SKU", backref=backref("line", uselist=False, lazy="subquery")
    )
    form_factors = mdb.relationship(
        "FormFactor", backref=backref("line", uselist=False, lazy="subquery")
    )
    boilings = mdb.relationship("Boiling", backref=backref("line", uselist=False))
    steam_consumption = mdb.relationship(
        "SteamConsumption", backref=backref("line", uselist=False)
    )

    type = mdb.Column(mdb.String)
    __mapper_args__ = {"polymorphic_identity": "lines", "polymorphic_on": type}

    def serialize(self):
        return {"id": self.id, "name": self.name}


class Washer(mdb.Model):
    __tablename__ = "washer"
    id = mdb.Column(mdb.Integer, primary_key=True)
    name = mdb.Column(mdb.String)
    time = mdb.Column(mdb.Integer)
    department_id = mdb.Column(
        mdb.Integer, mdb.ForeignKey("departments.id"), nullable=True
    )


class Group(mdb.Model):
    __tablename__ = "groups"
    id = mdb.Column(mdb.Integer, primary_key=True)
    name = mdb.Column(mdb.String)
    short_name = mdb.Column(mdb.String)

    skus = mdb.relationship("SKU", backref="group")


parent_child = mdb.Table(
    "FormFactorMadeFromMadeTo",
    mdb.Column("ParentChildId", mdb.Integer, primary_key=True),
    mdb.Column("ParentId", mdb.Integer, mdb.ForeignKey("form_factors.id")),
    mdb.Column("ChildId", mdb.Integer, mdb.ForeignKey("form_factors.id")),
)


class FormFactor(mdb.Model):
    __tablename__ = "form_factors"
    id = mdb.Column(mdb.Integer, primary_key=True)
    name = mdb.Column(mdb.String)
    relative_weight = mdb.Column(mdb.Integer)
    skus = mdb.relationship(
        "SKU", backref=backref("form_factor", uselist=False, lazy="subquery")
    )
    line_id = mdb.Column(mdb.Integer, mdb.ForeignKey("lines.id"), nullable=True)

    made_from = mdb.relationship(
        "FormFactor",
        secondary=parent_child,
        primaryjoin=id == parent_child.c.ChildId,
        secondaryjoin=id == parent_child.c.ParentId,
        backref=backref("made_to"),
    )

    type = mdb.Column(mdb.String)
    __mapper_args__ = {"polymorphic_identity": "form_factors", "polymorphic_on": type}

    def add_made_from(self, ff):
        if ff not in self.made_from:
            self.made_from.append(ff)

    @property
    def weight_with_line(self):
        if self.line:
            return "{}: {}".format(self.line.name_short, self.relative_weight)
        else:
            return "{}".format(self.name)

    @property
    def full_name(self):
        return "{}, {}".format("Форм фактор", self.name)


sku_boiling = mdb.Table(
    "sku_boiling",
    mdb.Column(
        "boiling_id", mdb.Integer, mdb.ForeignKey("boilings.id"), primary_key=True
    ),
    mdb.Column("sku_id", mdb.Integer, mdb.ForeignKey("skus.id"), primary_key=True),
)


class Boiling(mdb.Model):
    __tablename__ = "boilings"
    id = mdb.Column(mdb.Integer, primary_key=True)
    output_coeff = mdb.Column(mdb.Float, default=1)
    line_id = mdb.Column(mdb.Integer, mdb.ForeignKey("lines.id"), nullable=True)
    boiling_technologies = mdb.relationship(
        "BoilingTechnology", backref=backref("boiling")
    )

    skus = mdb.relationship("SKU", secondary=sku_boiling, backref="made_from_boilings")

    type = mdb.Column(mdb.String)
    __mapper_args__ = {"polymorphic_identity": "boilings", "polymorphic_on": type}


class BoilingTechnology(mdb.Model):
    __tablename__ = "boiling_technologies"
    id = mdb.Column(mdb.Integer, primary_key=True)
    name = mdb.Column(mdb.String)

    boiling_id = mdb.Column(mdb.Integer, mdb.ForeignKey("boilings.id"), nullable=True)

    type = mdb.Column(mdb.String)
    __mapper_args__ = {
        "polymorphic_identity": "boiling_technologies",
        "polymorphic_on": type,
    }


sku_packer = mdb.Table(
    "sku_packer",
    mdb.Column(
        "packer_id", mdb.Integer, mdb.ForeignKey("packers.id"), primary_key=True
    ),
    mdb.Column("sku_id", mdb.Integer, mdb.ForeignKey("skus.id"), primary_key=True),
)


class Packer(mdb.Model):
    __tablename__ = "packers"
    __table_args__ = {"extend_existing": True}
    id = mdb.Column(mdb.Integer, primary_key=True)
    name = mdb.Column(mdb.String)
    skus = mdb.relationship(
        "SKU", secondary=sku_packer, backref=backref("packers", lazy="subquery")
    )

    def serialize(self):
        return {"id": self.id, "name": self.name}


class PackType(mdb.Model):
    __tablename__ = "pack_types"
    id = mdb.Column(mdb.Integer, primary_key=True)
    name = mdb.Column(mdb.String)
    skus = mdb.relationship("SKU", backref=backref("pack_type", uselist=False))


class SteamConsumption(mdb.Model):
    __tablename__ = "steam_consumption"
    id = mdb.Column(mdb.Integer, primary_key=True)
    params = mdb.Column(mdb.String)
    line_id = mdb.Column(mdb.Integer, mdb.ForeignKey("lines.id"), nullable=True)


class BatchNumber(mdb.Model):
    __tablename__ = "batch_number"
    id = mdb.Column(mdb.Integer, primary_key=True)
    datetime = mdb.Column(mdb.Date)
    beg_number = mdb.Column(mdb.Integer)
    end_number = mdb.Column(mdb.Integer)
    department_id = mdb.Column(
        mdb.Integer, mdb.ForeignKey("departments.id"), nullable=True
    )

    def serialize(self):
        return {
            "id": self.id,
            "datetime": self.datetime.strftime(flask.current_app.config["DATE_FORMAT"]),
            "beg_number": self.beg_number,
            "end_number": self.end_number,
            "department_id": self.department_id,
        }

    @staticmethod
    def last_batch_number(date, department_name):
        department = (
            mdb.session.query(Department)
            .filter(Department.name == department_name)
            .first()
        )
        last_batch = (
            mdb.session.query(BatchNumber)
            .filter(BatchNumber.department_id == department.id)
            .filter(func.DATE(BatchNumber.datetime) < date.date())
            .filter(extract("month", BatchNumber.datetime) == date.month)
            .filter(extract("year", BatchNumber.datetime) == date.year)
            .order_by(BatchNumber.datetime.desc())
            .first()
        )
        if last_batch is not None:
            return last_batch.end_number
        else:
            return 0

    @staticmethod
    def get_batch_by_date(date, department_id):
        return (
            mdb.session.query(BatchNumber)
            .filter(func.DATE(BatchNumber.datetime) == date.date())
            .filter(BatchNumber.department_id == department_id)
            .first()
        )
