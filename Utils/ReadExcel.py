from openpyxl import load_workbook
# from MyWeb import settings
# import os


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






