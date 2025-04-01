import mysql.connector


dataBase = mysql.connector.connect(
    host ='localhost',
    user = 'root',
    passwd = 'Saiddeagle8')


cursorObject = dataBase.cursor()

cursorObject.execute("CREATE DATABASE habbit_tr_db")
    
print("DB CREATED")

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#          'NAME': 'habbit_tr_db',
#          'USER':'root',
#          'PASSWORD':'saiddeagle8',
#          'HOST':'localhost',
#          'PORT':'3306',
#     }
# }