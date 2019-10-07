const express = require('express');
const mongoose = require('mongoose');
const { body, validationResult } = require('express-validator');
const path = require('path');
const auth = require('http-auth');
const Registration = require('../models/Registration');
const registrationHelper = require('../models/registrationHelper');
const router = express.Router();

var registered = false;
let registrationFailed = true;
const TAG = "index->";
const email = "email";
const password = "password";

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

const basic = auth.basic({
  file: path.join(__dirname, '../users.htpasswd'),
});

  



router.get('/', (req, res) => {
  //res.send('It works galosh!');
  res.render('home');

});
 

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
router.post('/',
[
 /* body('firstName')
    .isLength({ min: 1 })
    .withMessage('Please enter first name'),
  body('lastName')
    .isLength({ min: 1 })
    .withMessage('Please enter an last name'),
  */

  body('email')
    .isLength({ min: 1 })
    .withMessage('Please enter an email'),
  body('password')
    .isLength({ min: 4 })
    .withMessage('Please enter a proper password'),
],
(req, res) => {
  console.log(TAG,"we are in post request in 'home' page");
  console.log(req.body.img);
  let images = req.body.images;
  if(images!= undefined){
    console.log("images = " + images);
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
  //res.send('It works galosh!');
//  res.render('form');
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
