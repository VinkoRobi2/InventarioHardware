
const fs = require('fs');

// Ruta del archivo .txt a leer
const filePath = 'InventarioHardware/items.txt';

// Leer el archivo .txt de forma asíncrona
fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
        console.error(err);
        return;
    }
    // Aquí puedes trabajar con el contenido del archivo
    console.log(data)
});