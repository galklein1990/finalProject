
var multer  = require('multer')
//var dic ={""}
var TAG = "uploadImages->";
var fs = require('fs');
const path = require('path');



exports.uploadImagesFromInputToFolder2 = function(imageDir, req,res,folderName, inputName){
  console.log("numberOfImages....")
 fs.readdir(imageDir, function (err, list) {
  let fileType = '.png';
  let files =[]
  if(err){
    console.log("err = ",err);
  }
  for(let i=0; i<list.length; i++) {
      if(path.extname(list[i]) === fileType) {
          files.push(list[i]); //store the file name into the array files
      }
  }
  console.log("files 1 = ",files)
  uploadImagesFromInputToFolder (req,res,folderName, inputName,files);
})

}


function uploadImagesFromInputToFolder (req,res,folderName, inputName,files){
  var i = 0;
  var storage = multer.diskStorage({
      
        destination: function (req, file, callback) {
          console.log(TAG,"destination diskStorage...")
          callback(null, ('./uploads' + '/' + folderName) );
        },
        filename: function (req, file, callback) {
          i++;
          
          console.log(TAG,"destination filename...")
          callback(null, i +'.png');
        }
      });
    var upload = multer({ storage : storage }).array(inputName,3);
    upload(req,res,(err)=>{
      //var files = numberOfImages("uploads/inputDirectory");
      console.log("files 2 = ",files)
      if(err){
        console.log("error = " + err);
        return res.end("Error uploading file.");
      }
      alert("gal");
        res.render('uploaded', {
          email: req.body.email,  
          images:files,
          data: req.body,
        });
    
      
      //res.end("File is uploaded");
    });
}


function getStorage(pathToFolder,fileSuffix,i){
  var downloadFolders = ["inputDirectory","tifOrthoFileFolder","tfwOrthoDataFolder"];
 pathTofolderDic= {"jpg":"./uploads/inputDirectory","tif":"./uploads/tifOrthoFileFolder","tfw":"tfwOrthoDataFolder"}
  return multer.diskStorage({
      
    destination: function (req, file, callback) {
      let type = file.originalname.split(".")[1].toLowerCase();
      
      let pathToFolder = downloadFolders[type];
      console.log(TAG," destination diskStorage... type = ",type )
      callback(null, pathToFolder );
    },
      filename: function (req, file, callback) {
      let suffix = file.originalname.split(".")[1].toLowerCase();
      i++;
      console.log(TAG,"destination filename...suffix = ",suffix)
      //fileSuffix
      callback(null, i + "." + suffix);
    }
  });
}

exports.downloadAllImages = function(req,res,index = 0){
  var downloadFolders = ["inputDirectory","tifOrthoFileFolder","tfwOrthoDataFolder"];
  let suffix = [".png", ".tif" , ".tfw"];
  let pathToFolder = "./uploads/" + downloadFolders[index];
  let inputName  = downloadFolders[index];
  


  console.log("pathToFolder = ",pathToFolder);
  console.log("suffix[index] = ",suffix[index]);
  var storage = getStorage(pathToFolder,suffix[index],0);
  var upload = multer({ storage : storage }).array(inputName,100);
  upload(req,res,(err)=>{
    console.log("im here in upload callback with index " + index);
    if(err){
      console.log("error = " + err);
      //return res.end("Error uploading file.");
    }
    /*
    if(index != 0){
      exports.downloadAllImages(req,res,index+1);
    }
   */
  });
 /* let promise = new Promise(function(resolve, reject) {
     resolve(0);
  });
  promise.then(function(index){

                              }).then(function(index){

                                                      }).then(function(index){

                                                      })*/
  //exports.downloadImages(req,res,"./uploads/" + downloadFolders[i],downloadFolders[i],suffix[i])
 // for(let i = 0 ; i < 1; i++){
  //  exports.downloadImages(req,res,"./uploads/" + downloadFolders[i],downloadFolders[i],suffix[i])
  //}
}

exports.downloadImages = function(req,res,pathToFolder, inputName,fileSuffix,index = 0){
  console.log("pathToFolder =  ",pathToFolder);
  console.log("inputName =  ",inputName);
  var downloadFolders = ["inputDirectory","tifOrthoFileFolder","tfwOrthoDataFolder"];
  let suffix = [".png", ".tif" , ".tfw"];
  var i = 0;
  var storage = multer.diskStorage({
      
        destination: function (req, file, callback) {
          console.log(TAG,"destination diskStorage...")
          callback(null, pathToFolder );
        },
        filename: function (req, file, callback) {
          i++;
          console.log(TAG,"destination filename...")
         
          callback(null, i + fileSuffix);
        }
      });
    var upload = multer({ storage : storage }).array(inputName,100);
    upload(req,res,(err)=>{
      console.log("im here in upload callback");
      if(err){
        console.log("error = " + err);
        //return res.end("Error uploading file.");
      }
    })
      

}
exports.uploadImagesFromInputToFolder = function(req,res,pathToFolder, inputName,index = 0){
 
  var i = 0;
  var storage = multer.diskStorage({
      
        destination: function (req, file, callback) {
          console.log(TAG,"destination diskStorage...")
          callback(null, pathToFolder );
        },
        filename: function (req, file, callback) {
          i++;
          console.log(TAG,"destination filename...")
         
          callback(null, i +'.png');
        }
      });
    var upload = multer({ storage : storage }).array(inputName,1000);
    upload(req,res,(err)=>{
      var files = numberOfImages("uploads/inputDirectory");
      console.log("files 2 = ",files)
      if(err){
        console.log("error = " + err);
        return res.end("Error uploading file.");
      }
      
        res.render('uploaded', {
          email: req.body.email,  
          images:files,
          data: req.body,
        });
    
      
      //res.end("File is uploaded");
    });
}