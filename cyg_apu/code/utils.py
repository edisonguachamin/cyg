# -*- coding: utf-8 -*-
###################################################
#
#    Módulo Sistema de Gestión de Profesionales de la Salud
#    Copyright (C) 2012 MSP (<http://www.msp.gob.ec>).
#    $autor: Evelyn Martínez Rosas<evelyn.martinez@msp.gob.ec>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################
from osv import osv, fields

def check_docs (self, cr, uid, doc, type='ced', context=None):

    if type in ['oth', 'pass'] or not doc:
        return True

    try:
        int(doc)
    except:
        raise osv.except_osv("Error", u"El documento debe contener sólo caracteres numéricos")

    if ( int ( doc[0:2] ) < 1 or int ( doc[0:2] ) > 24 ):
        raise osv.except_osv("Error", u"Los primeros caracteres deben contener códigos de provincias válidas")

    if type == 'ruc' and len(doc) == 13:
        if doc[2] == '6':
            tipo_ruc = "publico"
            coeficiente = "32765432"
            verificador = int ( doc[8] )
        else:
            if doc[2] == "9":
                tipo_ruc = "juridico"
                coeficiente = "432765432"
            else:
                if int ( doc[2] ) < 6:
                    tipo_ruc = "natural"
                    coeficiente = "212121212"
                else:
                    raise osv.except_osv("Error", u"Error en el tercer dígito del documento")
            verificador = int ( doc[9] )

        resultado = 0
        suma = 0
        if tipo_ruc == "publico":
            for i in range(8):
                resultado += ( int ( doc[i] ) * int ( coeficiente[i] ) )
                residuo = resultado % 11
            if residuo == 0:
                resultado = residuo
            else:
                resultado = 11 - residuo

        if tipo_ruc == "juridico":
            for i in range(9):
                resultado += ( int ( doc[i] ) * int ( coeficiente[i] ) )
                residuo = resultado % 11
            if residuo == 0:
                resultado = residuo
            else:
                resultado = 11 - residuo

        if tipo_ruc == "natural":
            for i in range(9):
                suma = ( int ( doc[i] ) * int ( coeficiente[i] ) )
                if suma > 10 :
                    str_suma = str ( suma )
                    suma = int ( str_suma[0] ) + int (str_suma [1])
                resultado += suma
            residuo = resultado % 10
            if residuo == 0:
                resultado = residuo
            else:
                resultado = 10 - residuo

        if resultado == verificador:
            return True
        else:
            raise osv.except_osv("Error", u"El documento no es válido")
    elif type=='ced' and len(doc)==10:
        valores = [ int(doc[x]) * (2 - x % 2) for x in range(9) ]
        suma = sum(map(lambda x: x > 9 and x - 9 or x, valores))
        if int(int( doc[9] if int(doc[9]) <> 0 else 10 )) == (10 - int(str(suma)[-1:])):
            return True
        else:
            raise osv.except_osv("Error", u"La cédula no es válida")
    raise osv.except_osv('Error', u'Error al validar, el documento no es válido')

def cedula_validation(identification_number):
    if identification_number:
            numcc = identification_number
            suma = 0
            residuo = 0
            pri = False
            pub = False
            nat = False
            numeroProvincias = 24
            modulo = 11
            
            if len(numcc) < 10 or not identification_number.isdigit():
                return False
                # Los primeros dos digitos corresponden al codigo de la provincia
        
            provincia = int(numcc[0:2])
            if (provincia < 1) or (provincia > numeroProvincias):
                return False
                # Aqui almacenamos los digitos de la cedula en variables.
            d1 = int(numcc[0:1])
            d2 = int(numcc[1:2])
            d3 = int(numcc[2:3])
            d4 = int(numcc[3:4])
            d5 = int(numcc[4:5])
            d6 = int(numcc[5:6])
            d7 = int(numcc[6:7])
            d8 = int(numcc[7:8])
            d9 = int(numcc[8:9])
            d10 = int(numcc[9:10])
            # El tercer digito es:
            # 9 para sociedades privadas y extranjeros
            # 6 para sociedades publicas
            # menor que 6 (0,1,2,3,4,5) para personas naturales
            if (d3 == 7 or d3 == 8):
                return False
                #Solo para personas naturales (modulo 10)
            p1 = 0
            p2 = 0
            p3 = 0
            p4 = 0
            p5 = 0
            p6 = 0
            p7 = 0
            p8 = 0
            p9 = 0
            if d3 < 6:
                nat = True          
                p1 = d1 * 2
                if p1 >= 10: p1 -= 9    
                p2 = d2 * 1
                if p2 >= 10: p2 -= 9
                p3 = d3 * 2
                if p3 >= 10: p3 -= 9
                p4 = d4 * 1
                if p4 >= 10: p4 -= 9
                p5 = d5 * 2
                if p5 >= 10: p5 -= 9
                p6 = d6 * 1
                if p6 >= 10: p6 -= 9
                p7 = d7 * 2
                if p7 >= 10: p7 -= 9
                p8 = d8 * 1
                if p8 >= 10: p8 -= 9
                p9 = d9 * 2
                if p9 >= 10: p9 -= 9
                modulo = 10
                #Solo para sociedades publicas (modulo 11)
                #Aqui el digito verficador esta en la posicion 9, en las otras 2 en la pos. 10
            elif d3 == 6:
                pub = True
                p1 = d1 * 3
                p2 = d2 * 2
                p3 = d3 * 7
                p4 = d4 * 6                 
                p5 = d5 * 5
                p6 = d6 * 4
                p7 = d7 * 3
                p8 = d8 * 2
                p9 = 0
            #Solo para entidades privadas (modulo 11)
            elif d3 == 9:
                pri = True
                p1 = d1 * 4
                p2 = d2 * 3                     
                p3 = d3 * 2
                p4 = d4 * 7
                p5 = d5 * 6
                p6 = d6 * 5
                p7 = d7 * 4
                p8 = d8 * 3
                p9 = d9 * 2
            suma = p1 + p2 + p3 + p4 + p5 + p6 + p7 + p8 + p9
            residuo = suma % modulo
            #Si residuo=0, dig.ver.=0, caso contrario 10 - residuo
            if residuo == 0:
                digitoVerificador = residuo
            else:
                digitoVerificador = modulo - residuo
                #ahora comparamos el elemento de la posicion 10 con el dig. ver.
            if pub == True:
               if digitoVerificador != d9:
                    return False
                #El ruc de las empresas del sector publico terminan con 0001*/
               if (int(numcc[9: 13])) != 0001:
                    return False
            elif pri == True:
                if digitoVerificador != d10:
                    return False
                                                       
                if (int(numcc[10:13])) != 001:
                    return False
            elif nat == True:
                if digitoVerificador != d10:
                    return False
                if (len(numcc) > 10) and ((int(numcc[10:13])) != 001):
                    return False                                                                          
    return True


def cambiarTildes(texto):
    #print 'texto', texto
    sin_tilde={ 'Á':'A','É':'E','Í':'I','Ó':'O','Ú':'U',
                'Ç':'C','À':'A','È':'E','Ì':'I','Ò':'O','Ù':'U',
                'Ä':'A','Ë':'E','Ï':'I','Ö':'O','Ü':'U',
                'Â':'A','Ê':'E','Î':'I','Ô':'O','Û':'U',
                'á':'A','é':'E','í':'I','ó':'O','ú':'U','ç':'C',
                'à':'A','è':'E','ì':'I','ò':'O','ù':'U',
                'ä':'A','ë':'E','ï':'I','ö':'O','ü':'U',
                'â':'A','ê':'E','î':'I','ô':'O','û':'U'
              }
    cad=texto
    for item in sin_tilde:
        cad = cad.replace(item,sin_tilde[item])
    return cad

