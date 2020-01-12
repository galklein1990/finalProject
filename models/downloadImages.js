
var multer  = require('multer')
//var dic ={""}
const TAG = "uploadImages->";
var fs = require('fs');
const path = require('path');
const runProcess = require('../models/RunProcees');
//const TAG = "downloadImages->";





function getStorage(email){
console.log(TAG,"we are in getStorage...");
let pathes ={"jpg":("./uploads/" + email + "/inputDirectory"),"tif":("./uploads/" + email + "/tifOrthoFileFolder"),
"tfw": ("./uploads/" + email + "/tfwOrthoDataFolder") };
  return multer.diskStorage({
    destination: function (req, file, callback) {
     saveFilesNameInSession(req,file.originalname)
      callback(null, pathes[file.originalname.split(".")[1].toLowerCase()  ] );
    },
    filename: function (req, file, callback) {
      callback(null, file.originalname);
    }
  });
}



function saveFilesNameInSession(req,fileName){
    if(fileName.toLowerCase().includes("tif") ){
        req.session.tifFile = fileName; 
    }
    if(fileName.toLowerCase().includes("tfw") ){
        req.session.tfwFile = fileName; 
    }
}

exports.downloadAllImages = function(req,res){
  
  console.log(TAG," downloadAllImages...")
  var storage = getStorage(req.session.email);
  
    var upload = multer({ storage : storage }).fields([{
      name: 'inputDirectory', maxCount: 100
    }, {
      name: 'tifOrthoFileFolder', maxCount: 1
    }, {
      name: 'tfwOrthoDataFolder', maxCount: 1
    }])
 
    upload(req,res,(err)=>{
      if(err){
        console.log("error " + err);
        return res.end("Error uploading file.");
      }
 
      console.log(TAG,"finish download....")
      console.log(TAG,"req.session = ", req.session)
      runProcess.runPythonScript(req.session.email, req.session.tifFile, req.session.tfwFile , res);      
    });

   

    

}