from mongoengine import Document,ReferenceField,StringField,IntField,EmailField


#Creacion de la clase que representa el usuario en la db 
class Usuarios(Document):
    usuario = StringField(max_length=30, required=True, unique=True)
    password = StringField(max_length=20,min_length=8,required=True)
    nombres = StringField(max_length=30,required=True)
    correo = EmailField(max_length=40,required=True)


#Creacion de la clase que representa las categorias en la db
class Categorias(Document):
    nombre = StringField(max_length=30,unique=True)


#Creacion de la clase que representa los productos en la db
class Productos(Document):
    codigo = IntField(unique=True)
    nombre = StringField(max_length=30)
    precio = IntField()
    categoria = ReferenceField(Categorias)
    foto = StringField()
