const express = require('express');
const mongoose = require('mongoose');
const { body, validationResult } = require('express-validator');
const path = require('path');
const auth = require('http-auth');
const Registration = require('../models/Registration');
const registrationHelper = require('../models/registrationHelper');
const email = require("../models/email");
const metorologyHelper = require('../models/meteorologyHelper');
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

const options = metorologyHelper.getRequestOptions('1','402','C');
//metorologyHelper.createMeteorology();
var registrationValidation = function RegistrationValidation(fields){
 // console.log("we got to registrationValidation");
  if(fields.firstName != undefined && fields.lastName != undefined ){ 
  return  fields.firstName.length > 1 &&
              fields.lastName.length > 1 &&
              fields.email.length > 1 &&
              fields.password.length > 3; 

  }
  return false;
}

var fs = require('fs');

const basic = auth.basic({
  file: path.join(__dirname, '../users.htpasswd'),
});

  



router.get('/', (req, res) => {

  res.render('home');
 
  
 
 

});
function reverse(s){
  return s.split("").reverse().join("");
}

function createDivContainer(htmlString){
  var d = document.createElement(htmlString);
  d.innerHTML = some_html;
  return d.firstChild;
}

router.get('/gal', (req, res) => {
    //res.send('It works galosh!');
    res.render('form');
  res.render('form', { title: 'Registration form 3' });
  });

/*router.post('/', (req, res) => {
    console.log(req.body);
    res.send('we post! It works galosh!');
    //res.render('form', { title: 'Registration form' });
  });
*/


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

app.post('/', upload.array('photos', 12), function (req, res, next) {
  console.log(TAG,"app.post was invoked")
 
  // req.files is array of `photos` files
  // req.body will contain the text fields, if there were any
})
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
  console.log(TAG,"we are in post request in 'home' page");
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
    //writeImage(req.headers.host,req.body.img[0],res)
    console.log("images = ");
    email.sendEmail();
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
