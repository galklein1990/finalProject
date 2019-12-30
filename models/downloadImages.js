
var multer  = require('multer')
//var dic ={""}
const TAG = "uploadImages->";
var fs = require('fs');
const path = require('path');
//const TAG = "downloadImages->";





function getStorage(){
console.log(TAG,"we are in getStorage...");
let pathes ={"jpg":"./uploads/inputDirectory","tif":"./uploads/tifOrthoFileFolder","tfw":"./uploads/tfwOrthoDataFolder"};
  return multer.diskStorage({
    
    destination: function (req, file, callback) {

      callback(null, pathes[file.originalname.split(".")[1].toLowerCase()  ] );
    },
    filename: function (req, file, callback) {
      callback(null, file.originalname);
    }
  });
}



exports.downloadAllImages = function(req,res){
  
  console.log(TAG," downloadAllImages...")
  var storage = getStorage();
  
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
    });

   

    

}