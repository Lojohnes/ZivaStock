import sys
sys.path.insert(0, 'backend')
import bcrypt
from app.core.database import SyncSessionLocal
from app.models.user import User

h = bcrypt.hashpw('Laugh@2012'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print('hash', h)
db = SyncSessionLocal()
try:
    user = db.query(User).filter(User.email == 'admin@zivastock.com').first()
    if user:
        user.password_hash = h
        db.commit()
        print('updated')
    else:
        print('not found')
finally:
    db.close()
