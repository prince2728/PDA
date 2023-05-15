from main import flask_bcrypt

print(flask_bcrypt.generate_password_hash('Admin@123', rounds=12))