import traceback
from app.services.analyzer import analyze_stock
try:
    print(analyze_stock("600519"))
except Exception:
    traceback.print_exc()
