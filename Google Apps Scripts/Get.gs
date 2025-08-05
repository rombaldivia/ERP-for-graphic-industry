function doGet(e) {
  try {
    if (!e || !e.parameter) {
      return ContentService.createTextOutput('Error: No parameters received.').setMimeType(ContentService.MimeType.TEXT);
    }

    var ss = SpreadsheetApp.openById('1H5dl83yRZErMCHKaLQ_kzJNFJklsdweGdvgjkk0GoRI');
    var action = e.parameter.action;

    switch (action) {
      case 'loadOTs':
        return handleLoadOTs(ss);
      case 'assign':
        return handleAssign(ss, e);
      case 'remove':
        return handleRemove(ss, e);
      case 'checkComercial':
        return checkComercialComplete(ss); // Llama a la función que valida Comercial
      case 'checkDiagramacion':
        return checkDiagramacionComplete(ss); // Llama a la función que valida Diagramación
      case 'getRowData':
        var row = parseInt(e.parameter.row);
        if (isNaN(row)) {
          return ContentService.createTextOutput('Error: Invalid row parameter.').setMimeType(ContentService.MimeType.TEXT);
        }
        return getRowData(ss, row);
      case 'getAvailableDiagramacionRows':
        return getAvailableDiagramacionRows(ss);
      case 'getAvailableProductionRows':
        return getAvailableProductionRows(ss);
      case 'getLastProforma':
        return getLastProforma(ss);
      case 'getAllProformas': // ✅ Obtener todas las proformas desde la fila 3
        return getAllProformas(ss);
      case 'getFullProformaData': // ✅ Obtener todos los datos de una proforma específica
        var numeroProforma = e.parameter.numeroProforma;
        if (!numeroProforma) {
          return ContentService.createTextOutput('Error: No se proporcionó un número de proforma.').setMimeType(ContentService.MimeType.TEXT);
        }
        return getFullProformaData(ss, numeroProforma);
      default:
        return ContentService.createTextOutput('Action not recognized').setMimeType(ContentService.MimeType.TEXT);
    }
  } catch (error) {
    return ContentService.createTextOutput('Error: ' + error.message).setMimeType(ContentService.MimeType.TEXT);
  }
}

/* ======================================================================
   Manejo de OTs: cargar, asignar, eliminar
   ====================================================================== */
function handleLoadOTs(ss) {
  var processSheets = ['XL75', 'XL-UV', 'Barnizado', 'HOT STAMPING', 'Plastificado', 'Localizado', 'Sello Seco', 'CILINDRICA', 'EASY MATRIX', 'TIPOGRAFICA', 'Peg. 1 Punto', 'Peg. 3 Puntos', 'Perforado', 'Doblado', 'Compaginado', 'Engrapado', 'Emblocado', 'Engarrado', 'Pegado con Tesa'];
  var response = {};

  for (var i = 0; i < processSheets.length; i++) {
    var sheet = ss.getSheetByName(processSheets[i]);
    if (!sheet) continue;

    var lastRow = sheet.getLastRow();
    if (lastRow <= 1) continue;

    var data = sheet.getRange(2, 1, lastRow - 1, 5).getValues();
    var sheetData = [];

    for (var j = 0; j < data.length; j++) {
      var ot = data[j][0];
      var date = data[j][4] || "No asignada";

      if (ot !== "") {
        sheetData.push([ot, date]);
      }
    }

    if (sheetData.length > 0) {
      response[processSheets[i]] = sheetData;
    }
  }

  return ContentService.createTextOutput(JSON.stringify(response))
    .setMimeType(ContentService.MimeType.JSON);
}

function handleAssign(ss, e) {
  var process = e.parameter.process;
  var ot = e.parameter.ot;
  var date = e.parameter.date;

  var sheet = ss.getSheetByName(process);
  if (!sheet) {
    return ContentService.createTextOutput('Error: Sheet not found').setMimeType(ContentService.MimeType.TEXT);
  }

  var lastRow = sheet.getLastRow();
  if (lastRow <= 1) {
    return ContentService.createTextOutput('Error: No data to assign in sheet').setMimeType(ContentService.MimeType.TEXT);
  }

  var otData = sheet.getRange(2, 1, lastRow - 1, 1).getValues();
  for (var i = 0; i < otData.length; i++) {
    if (otData[i][0] == ot) {
      sheet.getRange(i + 2, 5).setValue(date);
      return ContentService.createTextOutput('Success').setMimeType(ContentService.MimeType.TEXT);
    }
  }

  return ContentService.createTextOutput('Error: OT not found in sheet').setMimeType(ContentService.MimeType.TEXT);
}

function handleRemove(ss, e) {
  var process = e.parameter.process;
  var ot = e.parameter.ot;

  var sheet = ss.getSheetByName(process);
  if (!sheet) {
    return ContentService.createTextOutput('Error: Sheet not found').setMimeType(ContentService.MimeType.TEXT);
  }

  var lastRow = sheet.getLastRow();
  if (lastRow <= 1) {
    return ContentService.createTextOutput('Error: No data to remove in sheet').setMimeType(ContentService.MimeType.TEXT);
  }

  var otData = sheet.getRange(2, 1, lastRow - 1, 1).getValues();
  for (var i = 0; i < otData.length; i++) {
    if (otData[i][0] == ot) {
      sheet.getRange(i + 2, 5).setValue('');
      return ContentService.createTextOutput('Success').setMimeType(ContentService.MimeType.TEXT);
    }
  }

  return ContentService.createTextOutput('Error: OT not found in sheet').setMimeType(ContentService.MimeType.TEXT);
}

/* ======================================================================
   Última proforma, filas disponibles, datos de proforma, etc.
   ====================================================================== */
function getLastProforma(ss) {
  try {
    var sheet = ss.getSheetByName('Hoja1');
    if (!sheet) {
      return ContentService.createTextOutput('Error: Sheet not found').setMimeType(ContentService.MimeType.TEXT);
    }

    var lastRow = sheet.getLastRow();
    if (lastRow < 2) {
      return ContentService
        .createTextOutput(JSON.stringify({ lastProforma: "0000" }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    var lastProforma = sheet.getRange(lastRow, 1).getValue();
    return ContentService
      .createTextOutput(JSON.stringify({ lastProforma: lastProforma }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    return ContentService
      .createTextOutput('Error: ' + error.message)
      .setMimeType(ContentService.MimeType.TEXT);
  }
}

function getAvailableDiagramacionRows(ss) {
  var sheet = ss.getSheetByName('Hoja1');
  var lastRow = sheet.getLastRow();
  var availableRows = [];

  for (var i = 2; i <= lastRow; i++) {
    var rowValues = sheet.getRange(i, 8, 1, 7).getValues()[0];
    if (rowValues.every(value => value.toString().trim() === "")) {
      availableRows.push({ row: i });
    }
  }

  return ContentService
    .createTextOutput(JSON.stringify({ availableRows: availableRows }))
    .setMimeType(ContentService.MimeType.JSON);
}

function getAvailableProductionRows(ss) {
  var sheet = ss.getSheetByName('Hoja1');
  var lastRow = sheet.getLastRow();
  var availableRows = [];

  for (var i = 2; i <= lastRow; i++) {
    var rowValues = sheet.getRange(i, 15, 1, 7).getValues()[0];
    if (rowValues.every(value => value.toString().trim() === "")) {
      availableRows.push({ row: i });
    }
  }

  return ContentService
    .createTextOutput(JSON.stringify({ availableRows: availableRows }))
    .setMimeType(ContentService.MimeType.JSON);
}

function getFullProformaData(ss, numeroProforma) {
  try {
    var sheet = ss.getSheetByName('Hoja1');
    if (!sheet) {
      return ContentService
        .createTextOutput(JSON.stringify({ error: "Error: Sheet not found" }))
        .setMimeType(ContentService.MimeType.JSON);
    }

    var data = sheet.getDataRange().getValues(); // Obtener todos los datos de la hoja

    // Definir rangos de columnas
    var comercialRange = { start: 0, end: 6 };  // Columnas A-G
    var diagramacionRange = { start: 7, end: 13 }; // Columnas H-N
    var produccionRange = { start: 14, end: 42 }; // Columnas O-AQ

    // Buscar la fila con la proforma específica
    for (var i = 1; i < data.length; i++) {
      if (data[i][0] == numeroProforma) { // Comparando con la columna de proforma

        // Dividir los valores en Comercial, Diagramación y Producción
        var proformaData = {
          "Comercial": data[i].slice(comercialRange.start, comercialRange.end + 1),
          "Diagramacion": data[i].slice(diagramacionRange.start, diagramacionRange.end + 1),
          "Produccion": data[i].slice(produccionRange.start, produccionRange.end + 1)
        };

        return ContentService
          .createTextOutput(JSON.stringify(proformaData))
          .setMimeType(ContentService.MimeType.JSON);
      }
    }

    return ContentService
      .createTextOutput(JSON.stringify({ error: "Error: Proforma not found" }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({ error: error.message }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

function getAllProformas(ss) {
  var sheet = ss.getSheetByName('Hoja1');
  if (!sheet) {
    return ContentService
      .createTextOutput('Error: Sheet not found')
      .setMimeType(ContentService.MimeType.TEXT);
  }

  var lastRow = sheet.getLastRow();
  if (lastRow < 3) { // 📌 Si no hay suficientes filas, devuelve un array vacío
    return ContentService
      .createTextOutput(JSON.stringify({ proformas: [] }))
      .setMimeType(ContentService.MimeType.JSON);
  }

  var data = sheet.getRange("A3:A" + lastRow).getValues(); // 📌 Desde la fila 3 hasta la última
  var proformas = data.flat().filter(value => value.toString().trim() !== ""); // 📌 Elimina celdas vacías

  return ContentService
    .createTextOutput(JSON.stringify({ proformas: proformas }))
    .setMimeType(ContentService.MimeType.JSON);
}

/* ======================================================================
   Funciones para checkComercialComplete, checkDiagramacionComplete, getRowData
   ====================================================================== */

// Verifica si (fila 2) en columnas A..G están completas
function checkComercialComplete(ss) {
  try {
    var sheet = ss.getSheetByName("Hoja1");
    if (!sheet) {
      return ContentService
        .createTextOutput("Error: Sheet not found")
        .setMimeType(ContentService.MimeType.TEXT);
    }

    // Por defecto, revisaremos la fila 2 (ajusta si necesitas otra)
    var row = 2;
    var rowValues = sheet.getRange(row, 1, 1, 7).getValues()[0]; // A..G
    var isComplete = rowValues.every(function(val) {
      return val.toString().trim() !== "";
    });

    return ContentService
      .createTextOutput(JSON.stringify({ completo: isComplete }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput("Error: " + err.message)
      .setMimeType(ContentService.MimeType.TEXT);
  }
}

// Verifica si (fila 2) en columnas H..N están completas
function checkDiagramacionComplete(ss) {
  try {
    var sheet = ss.getSheetByName("Hoja1");
    if (!sheet) {
      return ContentService
        .createTextOutput("Error: Sheet not found")
        .setMimeType(ContentService.MimeType.TEXT);
    }

    // Por defecto, revisaremos la fila 2
    var row = 2;
    var rowValues = sheet.getRange(row, 8, 1, 7).getValues()[0]; // H..N
    var isComplete = rowValues.every(function(val) {
      return val.toString().trim() !== "";
    });

    return ContentService
      .createTextOutput(JSON.stringify({ completo: isComplete }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput("Error: " + err.message)
      .setMimeType(ContentService.MimeType.TEXT);
  }
}

// Obtiene valores de una fila
function getRowData(ss, row) {
  try {
    var sheet = ss.getSheetByName("Hoja1");
    if (!sheet) {
      return ContentService
        .createTextOutput("Error: Sheet not found")
        .setMimeType(ContentService.MimeType.TEXT);
    }

    var lastCol = sheet.getLastColumn();
    var dataRow = sheet.getRange(row, 1, 1, lastCol).getValues()[0];

    return ContentService
      .createTextOutput(JSON.stringify({ fila: row, datos: dataRow }))
      .setMimeType(ContentService.MimeType.JSON);

  } catch (err) {
    return ContentService
      .createTextOutput("Error: " + err.message)
      .setMimeType(ContentService.MimeType.TEXT);
  }
}
