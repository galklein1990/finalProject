const express = require('express');
const path = require('path');
const routes = require('./routes/index');
const bodyParser = require('body-parser');
const session = require('express-session');

const app = express();


app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'pug');

app.use(bodyParser.urlencoded({ extended: true }));
app.use(bodyParser.json());
app.use(session({secret: 'ssshhhhh',resave:true,saveUninitialized:true}));

app.use('/', routes);
app.use(express.static('public'));
app.use(express.static('uploads'));
module.exports = app;

