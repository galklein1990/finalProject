const Meteorology = require('./Meteorology');
const { body, validationResult } = require('express-validator');
const fs = require('fs');
var jsdom = require("jsdom");
var JSDOM = jsdom.JSDOM;

const TAG = "meteorologyHelper->";

const request = require('request');  
const querystring = require('querystring');

const cityToLocationId = {
  "Eilat":520,
  "Mitzpe Ramon":106,
  "Beersheba":513,
  "Ein Gedi":105,
  "Jerusalem":510,
  "Lod": 204,
  "Ashdod": 114,
  "Tel Aviv": 402,
  "Haifa": 115,
  "Tzfat":507,
  "Katzrin":201,
  "Beit Shean":203,
  "Afula":209,
  "Tveria":202,
  "Nazareth":207,
}

const langId = 2;




/* 
in this module we will ask server http://www.ims.gov.il/ims/all_tahazit/
fro meterolgical info
*/




exports.getRequestOptions = function(langId,locationId,cf){
        
var form = {
    LangId: langId,
    LocationId: locationId,
    CF: cf
};
  
var formData = querystring.stringify(form);
var contentLength = formData.length;

const options = {
    url: 'http://www.ims.gov.il/IMS/Pages/IsrCitiesTodayForeCast.aspx',
    method: 'POST',
    headers: getHeaders(contentLength),
    body: formData,
    };
return options;

}



function getHeaders(contentLength){
      return {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Length': contentLength,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'www.ims.gov.il',
        'Origin': 'http://www.ims.gov.il',
        'Pragma': 'no-cache',
        'Referer': 'http://www.ims.gov.il/ims/all_tahazit/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.120 Safari/537.36',
        'X-Powered-By': 'CPAINT v2.0.3 :: http://sf.net/projects/cpaint'
    };
      

  }



 function createMeteorologyRecord(langId,LocationId,city,forcast,maxTempDay,minTempNight,
  humidity, windDirection,frequentWindSpeed, maxWindSpeed){
    console.log(TAG,"forecast = " , forcast);
    const meteorology = new Meteorology({
        Date: getDate(),
        LangId: langId,
        LocationId:LocationId,
        city: city,
        forcast: forcast,
        maxTempDay:maxTempDay,
        minTempNight:minTempNight,
        humidity:humidity,
        windDirection:windDirection,
        frequentWindSpeed:frequentWindSpeed,
        maxWindSpeed:maxWindSpeed
     })
     console.log("we are about to save this doc");
     meteorology.save()
     .then(() => {
        //onResult(res); 
        console.log(TAG,"we saved a new one")
        //registrationSucceed(req,res);
        
       })
      .catch(() => { 
        console.log(TAG,"we failed registering!"); 
        res.send('Sorry! Something went wrong.'); });
        
  };
 

  function getDate(){
    return new Date().toISOString().replace(/T/, ' ').replace(/\..+/, '').split(" ")[0];
  }


  function reverse(s){
    return s.split("").reverse().join("");
  }


/*
@#param 
langId: number for http req

*/   
//before langId,locationId were parameters
exports.createMetorlogyRequest = function(city, path = null){
console.log(TAG,"path to json folder = ",path);
    /*request.post({url:'http://www.ims.gov.il/IMS/Pages/IsrCitiesTodayForeCast.aspx', form: {key:'value'}}, function(err,httpResponse,body){
    console.log("httpResponse->" ,httpResponse)  
    //console.log("body->",body)
     })*/


    let locationId = cityToLocationId[city];
    console.log("location id is ...", locationId)
    let options = exports.getRequestOptions(langId,locationId,'C');
    request(options, function(err, res, body) {
        let html = "";
        
       /* for(let i = 0; i < body.length; i++){
          html += body[i];
        }
        console.log("html " ,html)*/
       
        global.document = new JSDOM(body).window.document;
        //console.log(" global.document = ",  global.document);
        //console.log(" global.document.body  ",  global.document.body.innerHTML);
      let forcast =  global.document.getElementById("tdForcast").innerHTML ; 
       console.log(TAG,"document.getElementById(tdForcast).innerHTML", forcast)
       let maxTempDay = global.document.getElementById("MaxTempDuringDayVal").innerHTML;
      
       let minTempNight = global.document.getElementById("MinTempNightVal").innerHTML;
      
       let humidity =  global.document.getElementById("RelHumidityNoonVal").innerHTML;
    
       let windDirection =  global.document.getElementById("WindDirectionVal").innerHTML;

       let frequentWindSpeed =  global.document.getElementById("FreqWindSpeedVal").innerHTML;
       
       let maxWindSpeed = global.document.getElementById("MaxWindSpeedVal").innerHTML;
      
       var meteorology = {
         forcast:forcast,
         maxTempDay:maxTempDay,
         maxTempDay:maxTempDay,
         minTempNight:minTempNight,
         humidity:humidity,
         windDirection:windDirection,
         frequentWindSpeed:frequentWindSpeed,
         maxWindSpeed:maxWindSpeed,
         city:city
       }

      let meteorologyData = JSON.stringify(meteorology);
      if(path != null ){
        fs.writeFileSync(path, meteorologyData);
      }
      
       console.log(TAG,"metrollogy = ",meteorology)

       /*createMeteorologyRecord(langId,locationId,"ashdod",forcast,
       maxTempDay,minTempNight,humidity,windDirection,frequentWindSpeed,maxWindSpeed);
     */
       
     
       /*  console.log(" global.document.Document = ",  global.document.Document);
        console.log(" global.document.location.href = ",  global.document.location.href);
      */
        //console.log(TAG,"body[0] = ",body[1]);
      });
}
 //createMeteorology();