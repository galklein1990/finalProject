const mongoose = require('mongoose');

const meteorologySchema = new mongoose.Schema({
  Date:{
    type:String,
    trim: true,
  },
  LangId: {
    type: Number,
    trim: true,
  },
  LocationId: {
    type: Number,
    trim: true,
  },
  city: {
    type: String,
    trim: true,
  },  

  forcast: {
    type: String,
    trim: true,
  },
  maxTempDay: {
    type: String,
    trim: true,
  },
  minTempNight: {
    type: String,
    trim: true,
  },
  humidity: {
    type: String,
    trim: true,
  },
  windDirection: {
    type: String,
    trim: true,
  },
  frequentWindSpeed: {
    type: String,
    trim: true,
  },
  maxWindSpeed: {
    type: String,
    trim: true,
  }
});

var Meteorology  = mongoose.model('Meteorology', meteorologySchema); 
module.exports = Meteorology;