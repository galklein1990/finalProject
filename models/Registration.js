const mongoose = require('mongoose');

const registrationSchema = new mongoose.Schema({
  name: {
    type: String,
    trim: true,
  },
  email: {
    type: String,
    trim: true,
  },
});

var Registartion  = mongoose.model('Registration', registrationSchema); 
module.exports = Registartion;