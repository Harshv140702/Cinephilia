from cs50 import SQL
from werkzeug.security import check_password_hash, generate_password_hash
db = SQL("sqlite:///project.db")
name = "admin"
password = "admin@123"
email = "admin@gmail.com"
contact = "1234567891"
db.execute("INSERT INTO users (username, password, email, contact, category) VALUES(:username, :password, :email, :contact, :category)",
                                username = name,
                                password = generate_password_hash(password),
                                email = email,
                                contact = contact,
                                category = 1)