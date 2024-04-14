
async function visualizarFoto(event) {
    const files = event.target.files;
    const archivo = files[0];
    const filename = archivo.name;
    const extension = filename.split('.').pop().toLowerCase();
  
    try {
      if (extension !== 'jpg') {
        fileFoto.value = "";
        swal.fire("Seleccionar", "Imagen en formato JPG", "warning");
        return;
      }
  
      const base64URL = await encodeFileAsBase64URL(archivo);
      const objectURL = URL.createObjectURL(archivo);
  
      imagenProducto.setAttribute("src", objectURL);
    } catch (error) {
      console.error("Error processing image:", error);
      // Handle potential errors gracefully
    }
  }
  
  /**
   * Returns a file in Base64URL format.
   * @param {File} file
   * @return {Promise<string>}
   */
  async function encodeFileAsBase64URL(file) {
    return new Promise((resolve) => {
      const reader = new FileReader();
      reader.addEventListener('loadend', () => {
        resolve(reader.result); // Resolve with Base64-encoded data
      });
      reader.readAsDataURL(file);
    });
  }

  function editarProducto() {
    const producto = {
      id: idProducto.value,
      codigo: codigo.value,
      nombre: nombre.value,
      precio: precio.value,
      categoria: cbCategoria.value
    }
    const foto = {
      foto: base64URL
    }
    const datos = {
      producto: producto,
      foto: foto
    }
    const url = "/editarProductoJson"
    fetch(url, {
      method: "PUT",
      body: JSON.stringify(datos),
      headers: {
        "Content-Type": "application/json",
      }
    })
      .then(respuesta => respuesta.json())
      .then(resultado => {
        console.log(resultado)
        if (resultado.estado) {
          Swal.fire({
            title: resultado.mensaje,
            confirmButtonText: "Continuar",
            icon: "success",
          }).then((result) => {
            if (result.isConfirmed) {
              location.href = "/listaProducto"
            }
          })
        } else {
          swal.fire("Editar Producto", resultado.mensaje, "warning")
        }
      })
  }


  
  function eliminarJson(id) {
    Swal.fire({
      title: "Seguro de eliminar el producto",
      showDenyButton: true,
      confirmButtonText: "SI",
      denyButtonText: "NO"
    }).then((result) => {
      if (result.isConfirmed) {
        url = "/eliminarJson/" + id
        fetch(url, {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
          }
        })
          .then(respuesta => respuesta.json())
          .then(resultado => {
            
            if (resultado.estado) {
              Swal.fire({
                title: resultado.mensaje,
                confirmButtonText: "CONFIRMAR",
                icon: "success",
              }).then((result) => {
                if (result.isConfirmed) {
                  location.href = "/listaProducto"
                } 
              })
            } else {
              swal.fire("Eliminar Producto", resultado.mensaje, "info")
            }
          }).catch(error => {
            console.error(error)
          })
      }
    })
  }