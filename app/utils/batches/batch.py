from app.imports.runtime import *
from app.models import BatchNumber, Department


def add_batch(date, department_name, beg_number, end_number, group=None):
    department = db.session.query(Department).filter(Department.name == department_name).first()
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


def add_batch_from_boiling_plan_df(date, department_name, boiling_plan_df):
    try:
        for batch_type, grp in boiling_plan_df.groupby("batch_type"):
            logger.debug(
                "Updating batches",
                date=date,
                department_name=department_name,
                beg=int(grp["absolute_batch_id"].min()),
                end=int(grp["absolute_batch_id"].max()),
            )
            add_batch(
                date=date,
                department_name=department_name,
                beg_number=int(grp["absolute_batch_id"].min()),
                end_number=int(grp["absolute_batch_id"].max()),
                group=batch_type,
            )
    except:
        logger.exception("Failed to add batch", date=date, department_name=department_name)
