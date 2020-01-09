var fs = require('fs');

exports.createUserDirectory = function(email){
    let directories = 
    ["./uploads/" + email,
    "./uploads/" + email + "/inputDirectory",
    "./uploads/" + email + "/tifOrthoFileFolder",
    "./uploads/" + email + "/tfwOrthoDataFolder",
     "./uploads/" + email + "/outputDirectory",
     "./uploads/" + email + "/forecast"
    ]
    for(let i = 0; i < directories.length; i++ ){
        createDirectory(directories[i]);
    }
}


function createDirectory(dirName){
if (!fs.existsSync(dirName)){
    fs.mkdirSync(dirName);
  }
}