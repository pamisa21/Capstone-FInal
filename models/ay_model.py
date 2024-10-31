from models.extensions import db  

class AY_SEM(db.Model):
    __tablename__ = 'AY_SEM'

    ay_id = db.Column(db.String(20), primary_key=True)
    ay_name = db.Column(db.String(100), nullable=False)  

    def __repr__(self):
        return f'<AY_SEM {self.ay_id} - {self.ay_name}>'
