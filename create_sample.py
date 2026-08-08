import openpyxl
wb = openpyxl.Workbook()
ws = wb.active
ws.append(['barcode','product_code','description','system_quantity','unit_cost'])
ws.append(['111111111','P001','Sample A',100,5.50])
ws.append(['222222222','P002','Sample B',200,12.00])
wb.save('test_products.xlsx')
print('xlsx saved')
