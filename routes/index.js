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
const downloadImages = require('../models/downloadImages');
var zipFolder = require('zip-folder');
//var spawn = require("child_process").spawn;


//const app = require('../app');


var url = require('url');

var userName = "";
var userPassword = "";


var multer  = require('multer')
//var upload = multer({ dest: 'uploads/' })
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

/*
var storage = multer.diskStorage({
  
  destination: function (req, file, callback) {
    console.log(TAG,"destination diskStorage...")
    callback(null, './uploads');
  },
  filename: function (req, file, callback) {
    console.log(TAG,"destination filename...")
    callback(null, file.fieldname + '-' + Date.now());
  }
});



var upload = multer({ storage : storage }).array('img',2);*/
const options = metorologyHelper.getRequestOptions('1','402','C');
//metorologyHelper.createMeteorology();



const basic = auth.basic({
  file: path.join(__dirname, '../users.htpasswd'),
});

  
router.get('/', (req, res) => {

  res.render('home');
 

});



router.get('/results', (req, res) => {
  fs.readdir("uploads/outputDirectory", function (err, list) {
    if(err){
      console.log("/results err = ", err)
    }
    res.render('uploaded',{ images: list });
  });
});




router.get('/gal', (req, res) => {
    //res.send('It works galosh!');
    res.render('form');
  res.render('form', { title: 'Registration form 3' });
  });

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

  console.log(TAG, "req.body = ", req.body)
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




router.get('/signIn', (req, res) => {

  res.render('signIn', { title: 'sign in' });
});

router.post('/handleRegistration',[

  body('email')
    .isLength({ min: 1 })
    .withMessage('Please enter an email'),
  body('password')
    .isLength({ min: 4 })
    .withMessage('Please enter a proper password'),
] ,(req, res) => {
 // email.sendEmail();
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


function numberOfImages(imageDir){
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
 console.log("lst = ",files)
})

}

var downloadIndex = 0;
router.post('/myImages', (req, res) => {
  downloadIndex++;
  console.log(TAG,"we are in myImages post req...",downloadIndex);
  
//var publicDir = require('path').join(__dirname,'../uploads/inputDirectory' );
//app.static(express.static(publicDir));
/*let mode = ' ortho+images ',ortho = 'C:/Users/mdwq87/Downloads/project/resizedOrtho.tif'
,ortho_data = 'C:/Users/mdwq87/Downloads/project/resized.tfw',pickle_file='',image_path = 'C:/Users/mdwq87/Downloads/project/input',
output = 'C:/Users/mdwq87/Desktop/gal/project/uploads/outputDirectory';
runProcess.runPythonScript(mode,ortho,ortho_data,pickle_file,image_path,output,res);
*/
//runProcess.runPythonScript();
//res.send("we will send an email when the algorthitrm is finished and pics are available!");
//console.log("req",req);
//downloadImages.downloadAllImages(req,res);  //("uploads/inputDirectory",req,res,'inputDirectory','img')


downloadImages.downloadAllImages(req,res);
});