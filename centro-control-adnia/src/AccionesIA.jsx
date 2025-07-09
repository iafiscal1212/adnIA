import React, { useContext, useEffect, useState } from "react";
import { ADNIAContext } from "./ADNIAContext";

const PALABRAS_CLAVE = [
  "sanción", "resolución", "plazo", "notificación", "requerimiento",
  "denegación", "recurso", "alegación", "expediente", "demanda",
  "inspección", "propuesta de liquidación", "despido", "subsanación",
  "reclamación", "ejecución", "apremio"
];

function generarBorradorLegal(texto, modulo) {
  switch (modulo) {
    case "Fiscal":
      return `
**Borrador de Recurso de Reposición Fiscal**  
A la atención de la Administración tributaria:

Por la presente, interpongo RECURSO DE REPOSICIÓN contra la resolución y/o liquidación notificada, alegando lo siguiente:  
1. Se han detectado posibles vicios de procedimiento o errores materiales.  
2. El plazo de alegaciones y la documentación requerida no ha sido correctamente señalada.  
3. Solicito la revisión íntegra del expediente, con suspensión de la ejecución hasta la resolución de este recurso.  
Texto detectado en el documento:  
"${texto.slice(0, 450)}..."  

(ADNIA puede ampliar, citar artículos, añadir argumentos y firmar si lo deseas).
      `;
    case "Penal":
      return `
**Borrador de Alegaciones en Proceso Penal**  
Al Juzgado de Instrucción que corresponda:

Mediante este escrito se formulan ALEGACIONES respecto al expediente o denuncia analizada.  
1. Se solicita el acceso íntegro al expediente y a las pruebas obrantes.  
2. Se solicita la adopción de medidas cautelares si procede, en defensa de los derechos fundamentales.  
Extracto clave del documento:  
"${texto.slice(0, 450)}..."  
(Firma: ADNIA. Puede completar, citar doctrina, y adaptar el escrito al caso concreto).
      `;
    case "Civil":
      return `
**Borrador de Demanda o Contestación Civil**  
Juzgado competente:

En nombre de mi representado, y atendiendo al contenido del documento analizado, se presenta DEMANDA (o contestación) en los siguientes términos:  
1. Resumen de hechos y fundamentos.  
2. Solicitud de prueba documental.  
Fragmento del documento cargado:  
"${texto.slice(0, 450)}..."  
(ADNIA puede completar el escrito según la materia y la fase procesal).
      `;
    case "Social":
      return `
**Borrador de Reclamación Laboral / Seguridad Social**  
A la Inspección de Trabajo o Juzgado Social:

Solicito RECLAMACIÓN sobre el asunto detectado: despido, reconocimiento de derechos o prestaciones, alegando:  
1. Incumplimientos o abusos identificados en el documento.  
2. Petición de medidas cautelares si corresponde.  
Extracto clave:  
"${texto.slice(0, 450)}..."  
(ADNIA puede redactar demanda, alegaciones, o recurso según proceda).
      `;
    case "Administrativo":
    default:
      return `
**Borrador de Recurso Administrativo / Alegaciones**  
A la Administración Pública:

Presento RECURSO o ALEGACIONES en relación con el expediente analizado.  
1. Solicito revisión de actuaciones, ampliación de plazos y suspensión de efectos mientras se resuelve el presente recurso.  
2. Extracto del documento:  
"${texto.slice(0, 450)}..."  
(ADNIA ajusta el escrito al tipo de procedimiento y amplía los fundamentos si lo necesitas).
      `;
  }
}

function AccionesIA({ modulo }) {
  const { documentoTexto, setSugerencia } = useContext(ADNIAContext);
  const [borrador, setBorrador] = useState("");

  useEffect(() => {
    if (documentoTexto) {
      const texto = documentoTexto.toLowerCase();
      const hayClave = PALABRAS_CLAVE.some(clave => texto.includes(clave));
      if (hayClave) {
        setSugerencia(`He detectado palabras clave legales en el documento. ¡ADNIA ha generado un borrador de acción jurídica! 📄👇`);
        setBorrador(generarBorradorLegal(documentoTexto, modulo));
      } else {
        setSugerencia("");
        setBorrador("");
      }
    } else {
      setSugerencia("");
      setBorrador("");
    }
    // eslint-disable-next-line
  }, [documentoTexto, modulo]);

  return (
    <div>
      {borrador && (
        <div style={{
          background: "#102032",
          color: "#00ffd9",
          border: "1px solid #00ffd9",
          borderRadius: "15px",
          margin: "24px 0",
          padding: "24px"
        }}>
          <b>🦾 Respuesta automática de ADNIA:</b>
          <pre style={{whiteSpace: "pre-wrap", fontFamily: "inherit"}}>{borrador}</pre>
        </div>
      )}
    </div>
  );
}
export default AccionesIA;
