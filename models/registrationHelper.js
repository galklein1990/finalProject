const Registration = require('./Registration');
const { body, validationResult } = require('express-validator');
const TAG = "registrationHelper->";


function register(req,res){
    const registration = new Registration(req.body);
        registration.save()
        .then(() => {
          //onResult(res); 
          console.log(TAG,"we saved a new one")
          //registrationSucceed(req,res);
          
          res.render('home', {
            email: req.body.email,
            title: 'Registration form we succsedd',
            registered: true,
            data: req.body,
          });
          
         })
        .catch(() => { 
          console.log(TAG,"we failed registering!"); 
          res.send('Sorry! Something went wrong.'); });
          
  
    }
  
  exports.registerNewUser = function(req,res){
    let errors = validationResult(req);
    Registration.find().then((registrations) => {
      let existEmail = false;
      registrations.forEach(function(registration)
      {
        if( new String(req.body.email).valueOf()== new String(registration.email).valueOf()){
            existEmail = true; 
          } 
      })
      if(!existEmail){
        console.log(TAG,"registerNewUser-> email not exist in db ")
        register(req,res);
      }
      else{
        console.log(TAG,"registerNewUser-> email exist in db ")
        res.render('registration', {  errors: errors.array(),email: 'Email is already in use', title: 'join us' });
      }
  
  })
  
  }
  
  
  
  
  
  
  
  exports.checkRegistration = function(req,res,email,password){
    let errors = validationResult(req);
    Registration.find().then((registrations) => {
      let existUser = false;
      
      registrations.forEach(function(registration)
      {
        if( new String(email).valueOf()== new String(registration.email).valueOf() && 
            new String(password).valueOf()== new String(registration.password).valueOf())
        {
            console.log(TAG,"checkRegistration-> we found a match");
            console.log(TAG, "checkRegistration-> registration.email = " + registration.email);
            console.log(TAG,"checkRegistration-> registration.password = " + registration.password);
            existUser = true;
            registrationFailed = false;
        } 
      })
      if(existUser){ //case user email allready exist
        registrationSucceed(req,res);
      }
      else {
        console.log(TAG,"checkRegistration we did not found a match");
        res.render('signIn', { registerFailed: true, errors: errors.array(),  title: 'join us' });
      }  //new user
        //registerNewUser(req,res);
       
      
  
  })
  }
  
  function isJoinNow(req){
    return req.body.firstName != undefined && req.body.lastName != undefined;
  }
  function registrationSucceed(req,res){
    res.render('home', {
      email: req.body.email,  
      title: 'Registration form we succsedd',
      registered: true,
      data: req.body,
    });
  }