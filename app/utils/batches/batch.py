from app.interactive_imports import *
from app.models import BatchNumber, Department


def add_batch(date, department_name, beg_number, end_number):
    print(department_name)
    mozzarella_department = (
        db.session.query(Department).filter(Department.name == department_name).first()
    )
    print(mozzarella_department)
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