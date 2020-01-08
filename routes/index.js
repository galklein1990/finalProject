const express = require('express');
const mongoose = require('mongoose');
const { body, validationResult } = require('express-validator');
const path = require('path');
const auth = require('http-auth');
const Registration = require('../models/Registration');
const registrationHelper = require('../models/registrationHelper');
const email = require("../models/email");
const metorologyHelper = require('../models/meteorologyHelper');
const createDirectory =require('../models/createDirectory');



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
let registrationFailed = false;
const TAG = "index->";
//const email = "email";
const password = "password";
var jsdom = require("jsdom");
var JSDOM = jsdom.JSDOM;

var fs = require('fs');






const options = metorologyHelper.getRequestOptions('1','402','C');
//metorologyHelper.createMeteorology();



const basic = auth.basic({
  file: path.join(__dirname, '../users.htpasswd'),
});

  
router.get('/', (req, res) => {

  res.render('home');
 

});



router.get('/results', (req, res) => {
  var dir = "uploads/" + req.session.email +"/outputDirectory"; 
  fs.readdir(dir, function (err, list) {
    if(err){
      console.log("/results err = ", err)
    }
    res.render('uploaded',{ images: list , dir: ("/" +req.session.email + "/outputDirectory" ) });
  });
});




router.get('/gal', (req, res) => {
    //res.send('It works galosh!');
    res.render('form');
  res.render('form', { title: 'Registration form 3' });
  });

router.post('/',(req, res,next) => { 
  let firstName = req.body.firstName;
  let email = req.body.email;
  let  errors = validationResult(req);
  if (errors.isEmpty()) 
  {  
    registrationHelper.deleteUser(firstName,email,res)

  }

  
}
);


router.get('/registrations',  auth.connect(basic),(req, res) => {
  //res.render('index', { title: 'Listing registrations' });
  Registration.find()
  .then((registrations) => {
    res.render('manageRegistrations', { title: 'Listing registrations', registrations });
  })
  .catch(() => { res.send('Sorry! Something went wrong.'); });
});



router.post('/registrations',  auth.connect(basic),(req, res) => {
console.log(TAG,"we are is post request registrations")
  Registration.find()
  .then((registrations) => {
    res.render('manageRegistrations', { title: 'Listing registrations', registrations });
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
  req.session.email = req.body.email;
  createDirectory.createUserDirectory(req.session.email);
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


router.post('/myImages', (req, res) => {
downloadImages.downloadAllImages(req,res);
});