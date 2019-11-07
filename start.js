require('dotenv').config();
const mongoose = require('mongoose');
const TAG = "start->";

listenToProgramCrash();

mongoose.connect(process.env.DATABASE,{ useNewUrlParser: true });
//mongoose.Promise = global.Promise;
mongoose.connection
  .on('connected', () => {
    console.log(TAG,`Mongoose connection open on ${process.env.DATABASE}`);
  })
  .on('error', (err) => {
    console.log(TAG,`Connection error: ${err.message}`);
  });
  
const app = require('./app');


const server = app.listen(3000, () => {
  console.log(TAG,`Express is running on port ${server.address().port}`);
});

function listenToProgramCrash() {
 // app.close()
  process.on('uncaughtException', function (err) {
    //process.emit("SIGINT");
    //server.close();
    console.error(TAG, 'Caught exception: ', err," wel close server");  
    
    //console.error(TAG, 'Caught exception: ', err);
  });


  process.on('SIGTERM', function () {

  })
}
