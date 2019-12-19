const express = require('express');
const mongoose = require('mongoose');
const { body, validationResult } = require('express-validator');
const path = require('path');
const auth = require('http-auth');
const Registration = require('../models/Registration');
const registrationHelper = require('../models/registrationHelper');
const email = require("../models/email");
const metorologyHelper = require('../models/meteorologyHelper');

const runProcess = require('../models/RunProcees');
var spawn = require("child_process").spawn;


var url = require('url');




var multer  = require('multer')
var upload = multer({ dest: 'uploads/' })
var app = express();
const router = express.Router();
const request = require('request');  
const querystring = require('querystring');

const imagesInputDir = "C:/Users/mdwq87/Desktop/img";
const imagesOutputDir = "C:/Users/mdwq87/Desktop/gal/project/uploads";
var registered = false;
let registrationFailed = true;
const TAG = "index->";
//const email = "email";
const password = "password";
var jsdom = require("jsdom");
var JSDOM = jsdom.JSDOM;

var fs = require('fs');


var storage = multer.diskStorage({
  destination: function (req, file, callback) {
    callback(null, './uploads');
  },
  filename: function (req, file, callback) {
    callback(null, file.fieldname + '-' + Date.now());
  }
});



var upload = multer({ storage : storage }).array('img',2);
const options = metorologyHelper.getRequestOptions('1','402','C');
//metorologyHelper.createMeteorology();



const basic = auth.basic({
  file: path.join(__dirname, '../users.htpasswd'),
});

  



router.get('/', (req, res) => {
  /*var dataString = '';
  let mode = ' ortho+images ';
  let ortho = 'C:/Users/mdwq87/Downloads/project/resizedOrtho.tif';
  let ortho_data = 'C:/Users/mdwq87/Downloads/project/resized.tfw';
  let pickle_file='';
  let image_path = 'C:/Users/mdwq87/Downloads/project/input';
  let output = 'C:/Users/mdwq87/Downloads/project/output';
  var py =spawn('python', ["C:/Users/mdwq87/Downloads/CTR_proj_main/CTR_proj_main/runMe.py",mode,ortho,
  ortho_data, pickle_file,image_path,output]);
  py.stdout.on('data', function(data){
    dataString += data.toString();
    console.log("data recevied = ",data.toString()) ;
  });
  py.stdout.on('end', function(){
    
    console.log('Finish all, dataString = ',dataString);
  });

  console.log(TAG, "we eill try to run python script.")*/
  //runProcess.runPythonScript();
  runProcess.runPythonScript();
  res.render('home');
 
  
 
 

});




router.get('/gal', (req, res) => {
    //res.send('It works galosh!');
    res.render('form');
  res.render('form', { title: 'Registration form 3' });
  });



//const path1 = require('path');

function writeImage(ImagePath,imgName,res){
   
  console.log(TAG,"imgName = ",imgName);
  let readImagefrom =  ImagePath + "/" + imgName//path.join( ImagePath , imgName);
  
  console.log("readImageFrom = ",readImagefrom)
  fs.readFile( readImagefrom, function (err, data) {
    console.log("readFile->","err = ", err);
    console.log(TAG,"writeImage -> DATA = ")
    console.log(data);
    var imageName = imgName;
    console.log("image name = " + imgName);
    // If there's an error
    if(!imageName){
      console.log("There was an error")
      res.redirect("/");
      res.end();
    } else {
      let temp = path.join(__dirname, 'uploads');
      var newPath =  path.join(imagesOutputDir, imageName);  //__dirname  +'/uploads/' +  + imageName;
      console.log("newPath = ",newPath);
      // write file to uploads/fullsize folder
      fs.writeFile(newPath, data, function (err) {
        // let's see it
        console.log("writeFile->","err = ", err);
        console.log(TAG,"we are in writefILE CALLBACK");
        res.redirect("/uploads/fullsize/" + imageName);
      });
    }
  });
}


router.post('/',

/**/[

  body('email')
    .isLength({ min: 1 })
    .withMessage('Please enter an email'),
  body('password')
    .isLength({ min: 4 })
    .withMessage('Please enter a proper password'),
],    ////upload.array('photos', 2),
(req, res,next) => {
  //console.log("rqe", req);
  console.log(TAG, "req.body = ", req.body)
  //console.log(TAG,"we are in post request in 'home' page");
 // console.log("req.headers = ",req.headers);
  console.log("req.headers.host = ",req.headers.host);
  //var pathname = url.parse(req.headers.host).pathname;
  //console.log("pathname = " , pathname)
  //console.log(req)
  let images = req.body.img;
  console.log(req.body.img);

  console.log("req.files = ")
  //console.log(req.files.length);
  if(req.body.img!= undefined){
  //   upload(req,res,function(err) {
  //     //console.log(req.body);
  //     //console.log(req.files);
  //     if(err) {
  //         return res.end("Error uploading file.");
  //     }
      
  //     res.end("File is uploaded");
  // });
    //writeImage(req.headers.host,req.body.img[0],res)
    console.log("images = ");
    //email.sendEmail();
  }


 


 
  let  errors = validationResult(req);
  if (errors.isEmpty()) 
  {  
    if(req.body.firstName != undefined) 
    {
      console.log(TAG,"we are in join now request");
      registrationHelper.registerNewUser(req,res);
    } 
    else 
    {
      console.log(TAG,"we are in sign in request");
      registrationHelper.checkRegistration(req,res,req.body.email,req.body.password);
    }

  }

  
}
);


router.get('/registrations',  auth.connect(basic),(req, res) => {
  //res.render('index', { title: 'Listing registrations' });
  Registration.find()
  .then((registrations) => {
    res.render('index', { title: 'Listing registrations', registrations });
  })
  .catch(() => { res.send('Sorry! Something went wrong.'); });
});


router.get('/join', (req, res) => {
if(registrationFailed){
  res.render('registration', {registerFailed: true, title: 'join us' });
}
else{
  res.render('registration', {title: 'join us' });
}
})


router.post('/myImages', (req, res) => {
  upload(req,res,function(err) {
    //console.log(req.body);
    //console.log(req.files);
    if(err) {
        return res.end("Error uploading file.");
    }
    res.end("File is uploaded");
});
  
});

router.get('/signIn', (req, res) => {

  res.render('signIn', { title: 'sign in' });
});



function objToString(obj) {
  var str = '';
  for (var p in obj) {
      if (obj.hasOwnProperty(p)) {
          str += p + '::' + obj[p] + '\n';
      }
  }
  return str;
}


module.exports = router;
