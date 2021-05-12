from app.models import BatchNumber, Department
from app.globals import db


def add_batch(date, department_name, beg_number, end_number):
    mozzarella_department = (
        db.session.query(Department).filter(Department.name == department_name).first()
    )
    batch = BatchNumber.get_batch_by_date(date, mozzarella_department.id)

    if batch is not None:
        batch.beg_number = beg_number
        batch.end_number = end_number
    else:
        batch = BatchNumber(
            datetime=date,
            department_id=mozzarella_department.id,
            beg_number=beg_number,
            end_number=end_number,
        )
        db.session.add(batch)
    db.session.commit()
