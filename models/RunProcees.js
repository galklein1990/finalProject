const TAG = 'runProccess';
var spawn = require("child_process").spawn;
const process = require('process');
const email =require("./email");

var fs = require('fs');
const path = require('path');

    

exports.runPythonScript = function (userEmail,tifFile,tfwFile ,res) {
console.log(TAG,"we are in runPythonScript...")
console.log("userEmail->",userEmail)
console.log("tifFile->",tifFile)
console.log("tfwFile->",tfwFile)
const mode = ' ortho+images ';
const ortho = 'C:/Users/mdwq87/Desktop/gal/project/uploads/' + userEmail +"/tifOrthoFileFolder/"+   tifFile;
const ortho_data = 'C:/Users/mdwq87/Desktop/gal/project/uploads/' + userEmail +"/tfwOrthoDataFolder/"+   tfwFile; 
const pickle_file='';
image_path = 'C:/Users/mdwq87/Desktop/gal/project/uploads/' + userEmail + "/inputDirectory"
//'C:/Users/mdwq87/Downloads/project/input';
//C:\Users\mdwq87\Desktop\gal\project\uploads
const output = 'C:/Users/mdwq87/Desktop/gal/project/uploads/' + userEmail + "/outputDirectory";
var dataString = '';
var py =spawn('python', ["C:/Users/mdwq87/Downloads/CTR_proj_main/CTR_proj_main/runMe.py",mode,ortho,
ortho_data, pickle_file,image_path,output]);
    py.stdout.on('data', function(data){
        dataString += data.toString();
        console.log("data recevied = ",data.toString()) ;
      });
    py.stdout.on('end', function(){
        console.log('Finish all, dataString = ',dataString);
        
          console.log("res is not null...")
          email.sendEmail(userEmail);
           
      });
};


    
    
       
        
   