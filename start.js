require('dotenv').config();
const mongoose = require('mongoose');
const TAG = "start->";
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