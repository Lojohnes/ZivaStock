import sys
sys.path.insert(0, r'C:\Users\Administrator\Desktop\ZivaStock\backend')
try:
    import app.main
    print('import ok')
except Exception as e:
    import traceback
    traceback.print_exc()
