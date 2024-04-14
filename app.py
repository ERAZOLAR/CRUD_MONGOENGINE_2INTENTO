from flask import Flask, jsonify, redirect, request, render_template, session
import pymongo
import yagmail
import base64
from bson.errors import InvalidId
from io import BytesIO
import os
import threading
from tkinter import Image
from bson import ObjectId

from mongoengine import connect



#CONEXION MONGOENGINE

app = Flask(__name__)
app.config['MONGODB_SETTINGS'] = {
    'db': 'GESTIONPRODUCTOS',
    'host': 'localhost',
    'port': 27017
}
connect(**app.config['MONGODB_SETTINGS'])

#TRAEMOS models.py de la carpeta MODELS
from models.models import Usuarios,Productos,Categorias



@app.route('/')
def inicio():
    return render_template('agregarProducto.html') #ingreso.html


@app.route('/users', methods=['GET'])
def get_users():
    users = Usuarios.objects()
    return jsonify([user.to_json() for user in users]), 200


@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    user = Usuarios(
        usuario=data['usuario'],
        password=data['password'],
        nombre=data['nombres'],
        email=data['correo']
    )
    user.save()
    return 'Usuario creado correctamente', 201


@app.route('/iniciarSesion', methods=['POST'])
def iniciarSesion():
    mensaje = None
    estado = False
    try:
        usuario = request.form['usuario']
        password = request.form['password']
        user = Usuarios.objects(usuario=usuario, password=password).first()
        if user:
            email = yagmail.SMTP("erazolar@gmail.com", open(".password").read(), encoding='UTF-8')
            asunto = 'Ingreso al sistema de usuario'
            mensaje = f"Se informa que  <b>'{user.nombre} {user.apellido}'</b> ingreso al aplicativo"
            thread = threading.Thread(target=enviarCorreo, args=(email, [user.email], asunto, mensaje ))
            thread. start()
            estado = True
            return redirect("/ingreso")  
        else:
            mensaje = 'Credenciales no autorizadas'            
    except pymongo.errors.PyMongoError as error: 
        mensaje = error
    return render_template('ingreso.html', estado=estado, mensaje=mensaje)

def enviarCorreo(email=None, destinatario=None, asunto=None, mensaje=None):
    email. send (to=destinatario, subject=asunto, contents=mensaje)




@app.route('/ingreso')
def home():
    listaProductos = Productos.objects.all()
    listaP = []
    for p in listaProductos:
        categoria = Categorias.objects.get(id=p.categoria.id)
        p.nombreCategoria = categoria.nombre
        listaP.append(p)
    return render_template('listaProducto.html', Productos=listaP)



@app.route('/listaProductos')
def listaProductos():
    if "user" in session:
        listaProductos = Productos.objects()
        return render_template("listaProducto.html", productos=listaProductos)
    else:
        mensaje = "Debe primero ingresar con sus credenciales"
        return render_template("ingreso.html", mensaje=mensaje)


@app.route('/vistaAgregarProducto')
def vistaAgregarProducto():
    if "user" in session:
        #OBTENER CATEGORIAS
        listaCategorias = Categorias.objects()
        return render_template("agregarProducto.html", categorias=listaCategorias)
    else:
        mensaje = "Debe primero ingresar con sus credenciales"
        return render_template("ingreso.html", mensaje=mensaje)


#AGREGAR PRODUCTO A BASE DE DATOS
@app.route("/agregarProductoJson", methods=['POST'])
def agregarProductoJson():
    
    if "user" in session:
        mensaje = ""
        estado = False
        try:
            #LECTURA DATOS QUE VIENE FORMULARIO
            datos = request.json
            print(datos)
            datosProducto = datos.get('producto')
            print(datosProducto)
            fotoBase64 = datos.get('foto')["foto"]
            
            #CREAR OBJETO TIPO Producto
            producto = Productos(**datosProducto)
            print(producto.precio)

            #SE GUARDA EN BASEDATOS
            producto.save()

            #VALIDACION SI GUARDA O NO PRODCUCTO
            if producto.id:
                #IMAGEN BASE 64
                rutaImagen = f"{os.path.join(app.config['UPLOAD_FOLDER'], str(producto.id))}.jpg"
                fotoBase64 = fotoBase64[fotoBase64.index(',') + 1:]

                #IMAGEN BASE 64 DECODIFICADA
                imegenDecodificada = base64.b64decode(fotoBase64)

                imagen = image.open(bytesIO(imegenDecodificada))

                #IMAGEN A TIPO FORMATO
                imagenJpg = imagen.convert("RGB")

                #GUARDAR IMAGEN EN RUTA CREADA
                imagenJpg.save(rutaImagen)
                estado = True
                mensaje = "Producto Agregado Correctamente"               

                
            else:
                mensaje = "Problemas al agregar el producto"
                estado = False
        except Exception as error:
            
            mensaje = str(error)
            retorno = {"estado": estado, "mensaje": mensaje}
            return jsonify(retorno)
    else:
        mensaje = "Debe primero ingresar con sus credenciales"
        return render_template("ingreso.html", mensaje = mensaje)

    
# CONULTAR CODIGO
@app.route("/consultar/<codigo>", methods=["GET"])
def consultar(codigo):
    if "user" in session:
        # HACER CONSULTA
        producto = Productos.objects(codigo=codigo).first()
        listaCategorias = Categorias.objects()
        return render_template("editarProducto.html", categorias=listaCategorias, producto=producto)
    
    else:
        mensaje = "Se Deben Ingresar sus Credenciales"
        return render_template("ingreso.html", mensaje = mensaje)
    

# EDITAR PRODUCTO   
@app.route("/editarProductoJson", methods=["PUT"])
def editarProductoJson():
    
    if "user" in session:
        estado = False
        mensaje = None
        try:
            datos = request.json
            datosProducto = datos.get('producto')
            fotoBase64 = datos.get('foto')["foto"]
            idProducto = ObjectId(datosProducto['id'])
            producto = Productos.objects(id=idProducto).first()
            if (producto):
                producto.codigo = int(datosProducto['codigo'])
                producto.nombre = datosProducto['nombre']
                producto.precio = int(datosProducto['precio'])
                producto.categoria = ObjectId(datosProducto['categoria'])
                producto.save()
                if (fotoBase64):
                    
                    rutaImagen = f"{os.path.join(app.config['UPLOAD_FOLDER'])}/{producto.id}.jpg"
                    #SELECCIONAR FORMATO B64
                    fotoBase64 = fotoBase64[fotoBase64.index(',') + 1:]
                    imagenDecondificada = base64.b64decode(fotoBase64)
                    imagen = Image.open(BytesIO(imagenDecondificada))
                    imagenJpg = imagen.convert("RGB")
                    imagenJpg.save(rutaImagen)
                mensaje = "Producto Actualizado Correctamente"
                estado = True
            else: 
                mensaje = "Producto no existe con  codigo"
        except Exception as error:
            mensaje = str(error)
        retorno = {"estado": estado, "mensaje": mensaje}
        return jsonify(retorno)
    else:
        mensaje = "Debe primero ingresar con sus credenciales"
        return render_template("ingreso.html", mensaje = mensaje)

    



@app.route("/eliminarJson/<id>", methods=["DELETE"])
def eliminarJson(id):
    
    if "user" in session:
        estado = False
        mensaje = None
        try:
            #CONSULTA PRODUCTO POR ID
            producto = Productos.objects(id=id).first()
            if producto:
                #ELIMINAR PRODUCTO
                producto.delete()
                mensaje = "Producto Eliminado Correctamente"
                estado = True
            else:
                mensaje = "No existe producto con ese Id"
        except Exception as error:
            mensaje = str(error)

        retorno = {"estado": estado, "mensaje": mensaje}
        return jsonify(retorno)

    else:
        mensaje = "Debe primero ingresar con sus credenciales"
        return render_template("ingreso.html", mensaje = mensaje)

    

app.secret_key = 'your_secret_key_here'  #  CLAVE DE GMAIL
@app.route('/salir')
def salir():
  session.clear() # LIMPIA SESSION
  mensaje = 'Ha cerrado la sesión' # AL FINALIZAR SESION
  return render_template('/ingreso.html', mensaje=mensaje) # REGRESA A PAGINA ingreso




if __name__ == "__main__":
    app.run(debug=True)