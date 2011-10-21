import xlwt

def export_lines( wb, budget_name ):
	green = xlwt.easyxf(
		"""
		pattern:
			fore_color: green
		"""
	)
	red = xlwt.easyxf(
		"""
		pattern:
			fore_color: red
		"""
	)
	
	ws = wb.add_sheet(budget_name)
	
	ws.write(0,0,'BUDGET')
	ws.write(0,1,'N°CMDE')
	ws.write(0,2,'DATE')
	ws.write(0,3,'NATURE')
	ws.write(0,4,'TUTELLE')
	ws.write(0,5,'ORIGINE')
	ws.write(0,6,'FOURNISSEUR')
	ws.write(0,7,'OFFRE')
	ws.write(0,8,'DESIGNATION')
	ws.write(0,9,'REFERENCE')
	ws.write(0,10,'CREDIT')
	ws.write(0,11,'DEBIT')
	ws.write(0,12,'QUANTITE')
	ws.write(0,13,'TOTAL')
	ws.write(0,14,'MONTANT DISPO')
	
	row = 1
	for bl in budget_lines.filter( budget = budget_name ):
		ws.write( row, 0, budget_name )
		ws.write( row, 1, bl.number )
		ws.write( row, 2, bl.date )
		ws.write( row, 3, bl.nature )
		ws.write( row, 4, bl.get_budget_type_display() )
		ws.write( row, 5, bl.origin )
		ws.write( row, 6, bl.provider )
		ws.write( row, 7, bl.offer )
		ws.write( row, 8, bl.product )
		ws.write( row, 9, bl.ref )
		ws.write( row, 10, bl.credit )
		ws.write( row, 11, bl.debit )
		ws.write( row, 12, bl.quantity )
		ws.write( row, 13, bl.product_price )
		ws.write( row, 14, bl.get_amount_left )
		row += 1

