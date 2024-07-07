import requests
from api_externa import obtener_foto
from database import insertarReserva, selecFecha
from datetime import datetime

class Usuario:
    def __init__(self, nombre, userid, contraseña):
        self.nombre = nombre
        self.user_id = userid
        self.__password = contraseña
        # self.localidad = localidad
    def Saludar(self):
        print("Hola,",self.nombre,"bienvenido")
        

    def set_password(self, new_password):
        self.__password = new_password

    def get_password(self):
        return self.__password


class Profesional(Usuario):
    def __init__(self, nombre, userid, contraseña, servicios, precio, direccion, telefono):
        super().__init__(nombre, userid, contraseña)
        self.servicios = servicios
        self.precio = precio
        self.direccion = direccion
        self.telefono = telefono
    def Saludar(self):
        print("Hola",self.nombre,"en esta aplicacion podras ofrecer tus servicios de",self.servicios)

url = "http://127.0.0.1:4000"

def verContratistas(base_url):
    url = f"{base_url}/contratistas"
    response = requests.get(url)
    if response.status_code == 200:
        rows = response.json()
        print(rows)
        return rows

def verProfesionales(base_url,user_id):
    url = f"{base_url}/profesionales"
    response = requests.get(url)
    prof=[]
    if response.status_code == 200:
        rows = response.json()
        print()
        print("--- SERVICIOS DISPONIBLES ---")
        print("- maquillaje\n- peluqueria\n- barberia\n- manicura\n- pedicura\n- estetica\n")
        servicio = input("Que tipo de servicio estas buscando? ")
        existe = False
        for profesional in rows:
            if servicio == profesional["servicios"]:
                existe = True
                pro=Profesional(profesional["nombre"],profesional["userid"], profesional["contraseña"], profesional["servicios"], profesional["precio"], profesional["direccion"], profesional["telefono"])
                prof.append(pro)
                print ("NOMBRE:",pro.nombre)
                print("SERVICIO:", pro.servicios)
                print("PRECIO",pro.precio)
                direccion=pro.direccion.replace(' ','+')
                print("DIRECCION: ", "https://www.google.com.ar/maps/place/"+direccion)
                foto = obtener_foto()
                print("FOTO: ",foto)
                print(f"MANDARLE MENSAJE: https://api.whatsapp.com/send/?phone={pro.telefono}&text&type=phone_number&app_absent=0")
                print()
       
        if existe:
            reservar=input("Queres reservar algun profesional? (si/no): ")
        else:
            reservar="no"
            print("Servicio inexistente")
        while True:
            if reservar=="si":
                registrarReserva(user_id,prof)
                break
            elif reservar=="no":
                break
            else:
                print("Ingresa una opcion valida")
                break

def registrarReserva(user_id, prof):
    prof_select = input("Ingrese el nombre del profesional con el que quieras reservar: ")
    existe = 0
    for profesional in prof:
        if profesional.nombre == prof_select:
            existe = 1
            res = "si"
            while res == "si":
                fecha = input("Ingrese la fecha que queres reservar (dd/mm/yyyy): ")
                es_valida = formatoFechaCorrecto(fecha)
                if es_valida:
                    if esFechaFutura(fecha):
                        if selecFecha(prof_select, fecha) == 0:
                            res = "n"
                            insertarReserva(user_id, prof_select, fecha)
                            print("Reserva creada exitosamente")
                        else:
                            res = input("Lo sentimos, esa fecha ya está registrada, ¿quieres ingresar otra? (si/no): ")
                    else:
                        print("La fecha ingresada debe ser mayor a la fecha del día de hoy.")
                        res = "si"
                else:
                    print("Fecha inválida, ingrese la fecha con el formato adecuado.")
                    res = "si"
                
    if not existe:
        print("Profesional no encontrado")

def formatoFechaCorrecto(fecha):
    try:
        datetime.strptime(fecha, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def esFechaFutura(fecha):
    try:
        fecha_ingresada = datetime.strptime(fecha, "%d/%m/%Y")
        fecha_actual = datetime.now()
        return fecha_ingresada > fecha_actual
    except ValueError:
        return False

def EsProfesional(base_url,user_id):
    url = f"{base_url}/profesionales"
    response = requests.get(url)
    if response.status_code == 200:
        rows = response.json()
        contador=0
        for profesional in rows:
            if user_id == profesional["userid"]:
                contador=contador+1
        if contador==0:
            return "contratistas"
        else:
            return "profesionales"


def realizar_login(base_url, categoria, userid, contrasenia):
    url = f"{base_url}/login"
    data = {
        "categoria": categoria,
        "userid": userid,
        "contrasenia": contrasenia
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        user_data = response.json()
        print("Login exitoso!")
        return user_data
    else:
        print("Error de login")
        return False
    
def actualizar_perfil(base_url, user_id, campo, nuevo_valor):
    url = f"{base_url}/editar_perfil"
    data = {
        "user_id": user_id,
        "campo": campo,
        "nuevo_valor": nuevo_valor
    }
    response = requests.put(url, json=data)
    if response.status_code == 200:
        print("Perfil actualizado correctamente")
    else:
        print("Error al actualizar el perfil:", response.json())

def configuracion(user_id, password):
    print("-----CONFIGURACION-----")
    opcion = int(input("Elegi la opcion que desees realizar: \n1. Modificar contraseña\n2. Eliminar cuenta\n"))
    if opcion == 1:
        contrasena_actual = input("Ingresa la contraseña actual: ")
        if contrasena_actual == password:
            nueva_contrasena = input("Ingresa la nueva contraseña: ")
            response = requests.post("http://127.0.0.1:4000/configuracion/cambiar_contrasena", json={
                "user_id": user_id,
                "contrasena_actual": contrasena_actual,
                "nueva_contrasena": nueva_contrasena
            })
            print(response.json().get("message"))
        else:
            print("Contraseña incorrecta")

    elif opcion == 2:
        contrasena = input("Ingresa la contraseña: ")
        response = requests.delete("http://127.0.0.1:4000/configuracion/eliminar_cuenta", json={
            "user_id": user_id,
            "contrasena": contrasena
        })
        print(response.json().get("message"))

def cambiar_contraseña(user_id,password):
    contrasena_actual = input("Ingresa la contraseña actual: ")
    if contrasena_actual == password:
        nueva_contrasena = input("Ingresa la nueva contraseña: ")
        response = requests.post("http://127.0.0.1:4000/configuracion/cambiar_contrasena", json={
            "user_id": user_id,
            "contrasena_actual": contrasena_actual,
            "nueva_contrasena": nueva_contrasena
        })
        print(response.json().get("message"))
    else:
        print("Contraseña incorrecta")

def eliminar_cuenta(user_id,password):
    contrasena = input("Ingresa la contraseña: ")
    if contrasena == password:
        response = requests.delete("http://127.0.0.1:4000/configuracion/eliminar_cuenta", json={
            "user_id": user_id,
            "contrasena": contrasena
        })
        print(response.json().get("message"))
    else:
        print("contraseña incorrecta")



def obtener_citas_contratista(base_url, user_id):
    response = requests.get(f"{base_url}/citas/contratista/{user_id}")
    if response.status_code == 200:
        rows = response.json()
        for cita in rows:
            print("Profesional: ", cita["nombre_prof"])
            print("Fecha: ", cita["fecha"])
    else:
        print("No tenes citas disponibles")


def obtener_citas_profesional(base_url,nombre_prof):
    response = requests.get(f"{base_url}/citas/profesional/{nombre_prof}")
    if response.status_code == 200:
        rows = response.json()
        for citas in rows:
            print("Contratista: ",citas["userid"])
            print("Fecha: ",citas["fecha"])
    else:
        print("No tenes citas disponibles")





def main():
    while True:
        url = "http://127.0.0.1:4000"
        userid = input("Ingrese el userid: ")
        contrasenia = input("Ingrese la contraseña: ")
        categoria=EsProfesional(url,userid)
        pase=realizar_login(url, categoria, userid, contrasenia)
        if pase:
            if categoria=="contratistas":
                while True:
                    print()
                    print("MENÚ PRINCIPAL")
                    print("Opciones:")
                    print("1. Ver profesionales")
                    print("2. Ver citas proximas")
                    print("3. Salir")
                    print()
                    opcion=int(input("Elegí la opción que desees realizar: "))
                    if opcion==1:
                        verProfesionales(url,userid)
                    elif opcion==2:
                        obtener_citas_contratista(url,userid)
                        pass
                    elif opcion==3:
                        break
                    else:
                        print("Opciones no válidas")
            elif categoria=="profesionales":
                while True:
                    print()
                    print("MENU PRINCIPAL")
                    print("Opciones:")
                    print("1. Editar Perfil")
                    print("2. Configuración")
                    print("3. Ver citas")
                    print("4. Cerrar Sesión")
                    print()
                    opcion=int(input("Elegí la opción que desees realizar: "))
                    if opcion==1:
                        while True:
                            print("MODIFICAR PERFIL")
                            print("- precio")
                            print("- direccion")
                            print("- telefono")
                            campo= input("Ingresa que queres modificar: ")
                            if campo=="precio":
                                nuevo_valor=input("Ingresa el nuevo precio: ")
                                break
                            elif campo=="direccion":
                                nuevo_valor=input("Ingresa la nueva dirección: ")
                                break
                            elif campo=="telefono":
                                nuevo_valor=input("Ingresa el nuevo teléfono: ")
                                break
                            else:
                                print("Ingresa una opción válida")
                        actualizar_perfil(url,userid,campo,nuevo_valor)
                    elif opcion==2:
                        print("-----CONFIGURACIÓN-----")
                        opcion_configuracion = int(input("Elegí la opción que desees realizar: \n1. Modificar contraseña\n2. Eliminar cuenta\n"))
                        if opcion_configuracion==1:
                            cambiar_contraseña(userid,contrasenia)
                        elif opcion_configuracion==2:
                            eliminar_cuenta(userid,contrasenia)
                            break
                        else:
                            print("Opción no válida")
                    elif opcion==3:
                        obtener_citas_profesional(url,userid)
                    elif opcion==4:
                        break
                    else:
                        print("Opción no válida")
main()



