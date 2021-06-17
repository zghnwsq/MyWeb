from openpyxl import load_workbook
from MyWeb import settings
import os


def read_all_data(path):
    excel = load_workbook(path)
    data = {}
    sheetnames = excel.sheetnames
    for sheet in excel:
        max_row = sheet.max_row
        max_col = sheet.max_column
        rows = []
        for i in range(max_row):
            row = []
            for j in range(max_col):
                row.append(sheet.cell(i+1, j+1).value)
            rows.append(row)
        data[sheet.title] = rows
    # print(data)
    return sheetnames, data


file_path = os.path.join(settings.BASE_DIR, 'Upload', 'DS', 'Demo_Web', '4641eba4_babb_5235_be5e_6b87a3f0f689.xlsx')
read_all_data(file_path)



