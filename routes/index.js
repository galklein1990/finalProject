const express = require('express');
const mongoose = require('mongoose');
const { body, validationResult } = require('express-validator');
const path = require('path');
const auth = require('http-auth');

const email = "email";
const password = "password";

const Registration = require('../models/Registration'); 
var registered = false;

var isRegistered= function isRegistered(email,password){
  console.log("email im looking =" + email);
  console.log("password im looking =" + password);
  //let registered = false;
  let myRegis=0;
  console.log("Registration.find() = " +Registration.find());
  Registration.find().then((registrations) => {
    myRegis = registrations.length;
    registered = true;
    
    registrations.forEach(function(registration){
      if( new String(email).valueOf()== new String(registration.email).valueOf() &&
      new String(password).valueOf()== new String(registration.password).valueOf()
          //password.equals(registration.password) 
        ) {
        console.log("lovi dovi we found a match");
        registered = true;
        
      }
      
      //console.log("registration =" + registration);
      console.log("registration.email = " + registration.email);
      console.log("registration.password = " + registration.password);
    })
   });
   console.log("myRegis = " + myRegis);
   if(registered){
     console.log("indeed registered changed to true");
   }
   return true;

}

var onResult =  function OnResult(res){
  console.log("gal klein the king 1");
  res.render('home', {
    title: 'Registration form we succsedd',
    registered: true,
    data: req.body,
  });
}
var registrationValidation = function RegistrationValidation(fields){
  console.log("we got to registrationValidation");
  if(fields.firstName != undefined && fields.lastName != undefined ){ 
  return  fields.firstName.length > 1 &&
              fields.lastName.length > 1 &&
              fields.email.length > 1 &&
              fields.password.length > 4; 

  }
  return false;
/*return  body('firstName').isLength({ min: 1 }) &&
body('lastName').isLength({ min: 1 }) &&
body('email').isLength({ min: 1 }) &&
body('password').isLength({ min: 4 });
*/
}

const basic = auth.basic({
  file: path.join(__dirname, '../users.htpasswd'),
});

//require('../models/Registration');  

const router = express.Router();
//const Registration = new Registration();

router.get('/', (req, res) => {
  //res.send('It works galosh!');
  res.render('home');
//res.render('form', { title: 'Registration form 3' });
});
 

router.get('/gal', (req, res) => {
    //res.send('It works galosh!');
  //  res.render('form');
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
  //res.render('form', { title: 'Registration form 5' });
  //...
  const errors = validationResult(req);
  
      if (errors.isEmpty()) {
        console.log("req.body.firstName" + req.body.firstName);
        console.log("req.body.lastName" + req.body.lastName);
        console.log("req.body.email" + req.body.email);
        console.log("req.body.password" + req.body.password);
        if(registrationValidation(req.body)){
          const registration = new Registration(req.body);
          
          registration.save()
          .then(() => {
            //onResult(res); 
            
            res.render('home', {
              email: req.body.email,
              title: 'Registration form we succsedd',
              registered: true,
              data: req.body,
            });
            
           })
          .catch(() => { 
            console.log("we got here"); 
            res.send('Sorry! Something went wrong.'); });
            
        }
        else if(isRegistered(req.body.email, req.body.password)){
            res.render('home', {
            email: req.body.email,  
            title: 'Registration form we succsedd',
            registered: true,
            data: req.body,
          });
        }
       
      } 
      else {
        res.render('form', {
          title: 'Registration form we failed',
          errors: errors.array(),
          data: req.body,
        });

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
  //res.send('It works galosh!');
//  res.render('form');
  res.render('registration', { title: 'join us' });
});

router.get('/signIn', (req, res) => {
  //res.send('It works galosh!');
//  res.render('form');
  res.render('signIn', { title: 'sign in' });
});
module.exports = router;