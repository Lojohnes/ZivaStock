from sqlalchemy.orm import Session
from app.models.product import Product
from app.models.count import FirstCount
from app.models.session import StocktakeSession
from typing import Optional, List
import pandas as pd
from io import BytesIO
from datetime import datetime


class ExportService:
    def __init__(self, db: Session):
        self.db = db
    
    def export_products_to_excel(self, session_id: Optional[int] = None) -> BytesIO:
        """Export products to Excel format"""
        query = self.db.query(Product)
        
        products = query.all()
        
        # Convert to DataFrame
        data = []
        for product in products:
            data.append({
                'Barcode': product.barcode,
                'Product Code': product.product_code,
                'Description': product.description,
                'Unit of Measure': product.unit_of_measure,
                'System Quantity': float(product.system_quantity),
                'Unit Cost': float(product.unit_cost),
                'Total Value': float(product.system_quantity * product.unit_cost)
            })
        
        df = pd.DataFrame(data)
        
        # Create Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Products', index=False)
        
        output.seek(0)
        return output
    
    def export_counts_to_excel(self, session_id: int) -> BytesIO:
        """Export first counts for a session to Excel format"""
        counts = self.db.query(FirstCount).filter(FirstCount.session_id == session_id).all()
        
        # Convert to DataFrame
        data = []
        for count in counts:
            product = self.db.query(Product).filter(Product.id == count.product_id).first()
            data.append({
                'Barcode': product.barcode if product else '',
                'Product Code': product.product_code if product else '',
                'Description': product.description if product else '',
                'Quantity Counted': float(count.quantity),
                'System Quantity': float(product.system_quantity) if product else 0,
                'Variance': float(count.quantity - (product.system_quantity if product else 0)),
                'Counted At': count.counted_at.isoformat()
            })
        
        df = pd.DataFrame(data)
        
        # Create Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Counts', index=False)
        
        output.seek(0)
        return output
    
    def export_session_summary_to_excel(self, session_id: int) -> BytesIO:
        """Export session summary to Excel format"""
        session = self.db.query(StocktakeSession).filter(StocktakeSession.id == session_id).first()
        counts = self.db.query(FirstCount).filter(FirstCount.session_id == session_id).all()
        
        # Session info
        session_data = {
            'Session Name': session.name,
            'Description': session.description,
            'Status': session.status,
            'Start Time': session.start_time.isoformat() if session.start_time else '',
            'End Time': session.end_time.isoformat() if session.end_time else '',
            'Total Counts': len(counts)
        }
        
        # Counts summary
        counts_data = []
        for count in counts:
            product = self.db.query(Product).filter(Product.id == count.product_id).first()
            counts_data.append({
                'Barcode': product.barcode if product else '',
                'Description': product.description if product else '',
                'Quantity Counted': float(count.quantity),
                'System Quantity': float(product.system_quantity) if product else 0,
                'Variance': float(count.quantity - (product.system_quantity if product else 0)),
                'Value Impact': float((count.quantity - (product.system_quantity if product else 0)) * (product.unit_cost if product else 0))
            })
        
        # Create Excel file with multiple sheets
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            pd.DataFrame([session_data]).to_excel(writer, sheet_name='Session Info', index=False)
            pd.DataFrame(counts_data).to_excel(writer, sheet_name='Counts', index=False)
        
        output.seek(0)
        return output
    
    def export_products_to_csv(self, session_id: Optional[int] = None) -> BytesIO:
        """Export products to CSV format"""
        query = self.db.query(Product)
        
        products = query.all()
        
        # Convert to DataFrame
        data = []
        for product in products:
            data.append({
                'Barcode': product.barcode,
                'Product Code': product.product_code,
                'Description': product.description,
                'Unit of Measure': product.unit_of_measure,
                'System Quantity': float(product.system_quantity),
                'Unit Cost': float(product.unit_cost)
            })
        
        df = pd.DataFrame(data)
        
        # Create CSV file
        output = BytesIO()
        df.to_csv(output, index=False)
        
        output.seek(0)
        return output
    
    def export_sage_evolution_format(self, session_id: int) -> BytesIO:
        """Export in Sage Evolution compatible format"""
        counts = self.db.query(FirstCount).filter(FirstCount.session_id == session_id).all()
        
        # Sage Evolution format
        data = []
        for count in counts:
            product = self.db.query(Product).filter(Product.id == count.product_id).first()
            data.append({
                'ItemCode': product.product_code if product else '',
                'Description': product.description if product else '',
                'QtyOnHand': float(count.quantity),
                'Warehouse': 'MAIN'  # Default warehouse
            })
        
        df = pd.DataFrame(data)
        
        # Create Excel file
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='StockCount', index=False)
        
        output.seek(0)
        return output
