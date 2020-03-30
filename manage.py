from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from app import app, db

app.config["DEVELOPMENT"] = True
app.config["DEBUG"] = True

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)

# from video: https://www.youtube.com/watch?v=SB5BfYYpXjE
db.create_all()

if __name__ == '__main__':
    manager.run()
