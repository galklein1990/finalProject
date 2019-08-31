const express = require('express');
const mongoose = require('mongoose');
const { body, validationResult } = require('express-validator');
const path = require('path');
const auth = require('http-auth');

const basic = auth.basic({
  file: path.join(__dirname, '../users.htpasswd'),
});

const Registration = require('../models/Registration'); 
//require('../models/Registration');  

const router = express.Router();
//const Registration = new Registration();

router.get('/', (req, res) => {
  //res.send('It works galosh!');
//  res.render('form');
res.render('form', { title: 'Registration form 3' });
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
  body('name')
    .isLength({ min: 1 })
    .withMessage('Please enter a name'),
  body('email')
    .isLength({ min: 1 })
    .withMessage('Please enter an email'),
],
(req, res) => {
  //res.render('form', { title: 'Registration form 5' });
  //...
  const errors = validationResult(req);
  
      if (errors.isEmpty()) {
        const registration = new Registration(req.body);
        registration.save()
          .then(() => { res.send('Thank you  gal for your registration!'); })
          .catch(() => { res.send('Sorry! Something went wrong.'); });
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


router.get('/registrations', auth.connect(basic),(req, res) => {
  //res.render('index', { title: 'Listing registrations' });
  Registration.find()
  .then((registrations) => {
    res.render('index', { title: 'Listing registrations', registrations });
  })
  .catch(() => { res.send('Sorry! Something went wrong.'); });
});


module.exports = router;