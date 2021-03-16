import openpyxl
from openpyxl.styles import Alignment
from app.models import MozzarellaSKU
from app.utils.features.openpyxl_wrapper import ExcelBlock
import pandas as pd
from flask import current_app
import os
from shutil import copyfile


class Cell:
    def __init__(self, row, column, name):
        self.row = row
        self.column = column
        self.name = name


CELLS = {
    "Boiling": Cell(1, 1, "Тип варки"),
    "FormFactor": Cell(1, 2, "Форм фактор"),
    "Brand": Cell(1, 3, "Бренд"),
    "SKU": Cell(1, 4, "Номенклатура"),
    "FactRemains": Cell(1, 5, "Факт.остатки, заявка"),
    "NormativeRemains": Cell(1, 6, "Нормативные остатки"),
    "ProductionPlan": Cell(1, 7, "План производства"),
    "ExtraPacking": Cell(1, 8, "Дополнительная фасовка"),
    "Volume": Cell(1, 10, "Объем варки"),
    "Estimation": Cell(1, 11, "Расчет"),
    "Plan": Cell(1, 12, "План"),
    "BoilingVolumes": Cell(1, 13, "Объемы варок"),
    "Name1": Cell(1, 15, "Фактические остатки на складах - Заявлено, кг:"),
    "Name2": Cell(2, 15, "Нормативные остатки, кг"),
}

COLUMNS = {"BoilingVolume": 10, "SKUS_ID": 18, "BOILING_ID": 19}


class SkuPlanClient:
    def __init__(self, date, remainings, skus_grouped, template_path):
        self.filename = "{} План по SKU.xlsx".format(date.strftime("%Y-%m-%d"))
        self.filepath = os.path.join(
            current_app.config["SKU_PLAN_FOLDER"], self.filename
        )
        self.skus_grouped = skus_grouped
        self.remainings = remainings
        self.space_rows = 2
        self.template_path = template_path
        self.wb = self.create_file()

    def create_file(self):
        copyfile(self.template_path, self.filepath)
        return openpyxl.load_workbook(self.filepath)

    def fill_remainigs_list(self):
        with pd.ExcelWriter(self.filepath, engine="openpyxl") as writer:
            writer.book = self.wb
            writer.sheets = dict((ws.title, ws) for ws in self.wb.worksheets)
            self.remainings.to_excel(
                writer, sheet_name=current_app.config["SHEET_NAMES"]["remainings"]
            )
            writer.save()
        self.wb = openpyxl.load_workbook(self.filepath)

    def _set_production_plan(self, obj, value):
        if isinstance(obj, MozzarellaSKU):
            return value if obj.production_by_request else 0
        return value

    def _set_extra_packing(self, obj, value):
        if isinstance(obj, MozzarellaSKU):
            return 0 if obj.packing_by_request else value
        return 0

    def fill_skus(self, sku_grouped, excel_client, cur_row, space_factor, sorted_by_weight=False):
        beg_row = cur_row
        formula_group = []
        for group_name in current_app.config["ORDER"]:
            block_skus = [
                x for x in sku_grouped.skus if x.sku.group.name == group_name
            ]
            if block_skus:
                if sorted_by_weight:
                    block_skus = sorted(
                        block_skus, key=lambda k: k.sku.form_factor.relative_weight
                    )
                beg_block_row = cur_row
                for block_sku in block_skus:
                    formula_plan = "=IFERROR(INDEX('{0}'!$A$5:$DK$265,MATCH($O$1,'{0}'!$A$5:$A$228,0),MATCH({1},'{0}'!$A$5:$DK$5,0)), 0)".format(
                        current_app.config["SHEET_NAMES"]["remainings"],
                        excel_client.sheet.cell(
                            cur_row, CELLS["SKU"].column
                        ).coordinate,
                    )
                    formula_remains = "=IFERROR(INDEX('{0}'!$A$5:$DK$265,MATCH($O$2,'{0}'!$A$5:$A$228,0),MATCH({1},'{0}'!$A$5:$DK$5,0)), 0)".format(
                        current_app.config["SHEET_NAMES"]["remainings"],
                        excel_client.sheet.cell(
                            cur_row, CELLS["SKU"].column
                        ).coordinate,
                    )

                    excel_client.colour = block_sku.sku.colour[1:]
                    excel_client.draw_cell(
                        row=cur_row,
                        col=CELLS["Brand"].column,
                        value=block_sku.sku.brand_name,
                    )
                    excel_client.draw_cell(
                        row=cur_row, col=CELLS["SKU"].column, value=block_sku.sku.name
                    )
                    excel_client.draw_cell(
                        row=cur_row, col=CELLS["FactRemains"].column, value=formula_plan
                    )
                    excel_client.draw_cell(
                        row=cur_row,
                        col=CELLS["NormativeRemains"].column,
                        value=formula_remains,
                    )
                    excel_client.draw_cell(
                        row=cur_row,
                        col=CELLS["ProductionPlan"].column,
                        value=self._set_production_plan(block_sku.sku, "=MIN({}, 0)".format(
                            excel_client.sheet.cell(
                                cur_row, CELLS["FactRemains"].column
                            ).coordinate))
                    )
                    excel_client.draw_cell(
                        row=cur_row,
                        col=CELLS["ExtraPacking"].column,
                        value=self._set_extra_packing(block_sku.sku, "=MIN({}, 0)".format(
                            excel_client.sheet.cell(
                                cur_row, CELLS["FactRemains"].column
                            ).coordinate
                        ))
                    )

                    formula_group.append(
                        excel_client.sheet.cell(
                            cur_row, CELLS["ProductionPlan"].column
                        ).coordinate
                    )
                    cur_row += 1
                end_block_row = cur_row - 1
                if beg_block_row <= end_block_row:
                    excel_client.merge_cells(
                        beg_row=beg_block_row,
                        end_row=end_block_row,
                        beg_col=CELLS["FormFactor"].column,
                        end_col=CELLS["FormFactor"].column,
                        value=group_name,
                        alignment=Alignment(
                            horizontal="center", vertical="center", wrapText=True
                        ),
                    )
        end_row = cur_row - 1
        excel_client.colour = current_app.config["COLOURS"]["DefaultGray"][1:]
        excel_client.merge_cells(
            beg_row=beg_row,
            end_row=end_row,
            beg_col=CELLS["Boiling"].column,
            end_col=CELLS["Boiling"].column,
            value=sku_grouped.boiling.to_str(),
            alignment=Alignment(
                horizontal="center", vertical="center", wrapText=True
            ),
        )
        excel_client.draw_cell(
            row=beg_row, col=CELLS["Volume"].column, value=sku_grouped.volume
        )
        formula_boiling_count = "{}".format(
            str(formula_group)
                .strip("[]")
                .replace(",", " +")
                .replace("'", "")
                .upper()
        )

        excel_client.draw_cell(
            row=beg_row,
            col=CELLS["Estimation"].column,
            value="=-({}) / {}".format(
                formula_boiling_count,
                excel_client.sheet.cell(
                    beg_row, CELLS["Volume"].column
                ).coordinate.upper(),
            ),
        )

        excel_client.draw_cell(
            row=beg_row,
            col=CELLS["Plan"].column,
            value="=ROUND({}, 0)".format(
                excel_client.sheet.cell(
                    beg_row, CELLS["Estimation"].column
                ).coordinate.upper()
            ),
        )

        excel_client.draw_cell(
            row=beg_row,
            col=COLUMNS["SKUS_ID"],
            value=str([x.sku.id for x in sku_grouped.skus]),
        )
        excel_client.draw_cell(
            row=beg_row, col=COLUMNS["BOILING_ID"], value=sku_grouped.boiling.id
        )
        if space_factor:
            cur_row += self.space_rows
        return cur_row

    def fill_mozzarella_sku_plan(self):
        self.skus_grouped = sorted(
            self.skus_grouped, key=lambda x: (x.boiling.is_lactose, x.boiling.percent)
        )
        sheet = self.wb[current_app.config["SHEET_NAMES"]["schedule_plan"]]
        cur_row = 2
        is_lactose = False
        for sku_grouped in self.skus_grouped:
            if sku_grouped.boiling.is_lactose != is_lactose:
                cur_row += self.space_rows
            is_lactose = sku_grouped.boiling.is_lactose
            excel_client = ExcelBlock(sheet=sheet)
            cur_row = self.fill_skus(sku_grouped, excel_client, cur_row, is_lactose, True)

        for sheet_number, sheet_name in enumerate(self.wb.sheetnames):
            if sheet_number != 1:
                self.wb[sheet_name].views.sheetView[0].tabSelected = False
        self.wb.active = 1
        self.wb.save(self.filepath)

    def fill_ricotta_sku_plan(self):
        sheet = self.wb[current_app.config["SHEET_NAMES"]["schedule_plan"]]
        cur_row = 2
        for sku_grouped in self.skus_grouped:
            excel_client = ExcelBlock(sheet=sheet)
            cur_row = self.fill_skus(sku_grouped, excel_client, cur_row, False)
            cur_row += self.space_rows

        for sheet_number, sheet_name in enumerate(self.wb.sheetnames):
            if sheet_number != 1:
                self.wb[sheet_name].views.sheetView[0].tabSelected = False
        self.wb.active = 1
        self.wb.save(self.filepath)
