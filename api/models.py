from app import db

class FaceEncoding(db.Model):
    __tablename__ = 'face_encodings'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    encoding = db.Column(db.PickleType, nullable=False)

    def __repr__(self):
        return f"<FaceEncoding {self.name}>"