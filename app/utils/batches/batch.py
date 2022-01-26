from app.imports.runtime import *
from app.models import BatchNumber, Department


def add_batch(date, department_name, beg_number, end_number, group=None):
    department = (
        db.session.query(Department).filter(Department.name == department_name).first()
    )
    batch = BatchNumber.get_batch_by_date(date, department.id, group)

    if batch is not None:
        batch.beg_number = beg_number
        batch.end_number = end_number
    else:
        batch = BatchNumber(
            datetime=date,
            department_id=department.id,
            group=group,
            beg_number=beg_number,
            end_number=end_number,
        )
        db.session.add(batch)
    db.session.commit()
