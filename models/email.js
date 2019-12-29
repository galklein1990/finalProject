const nodemailer = require('nodemailer');
const TAG ="email->";

let transport = nodemailer.createTransport({
    service: 'gmail',
    auth: {
       user: 'gal.klein.1990@gmail.com',
       pass: 'pthsgvvqqjoktjxl'
    }
});


const message = {
    from: 'gal.klein.1990@gmail.com', // Sender address
    to: 'gal.klein.1990@gmail.com',         // List of recipients
    subject: 'pictures are ready!', // Subject line
    text: 'go to the website', // Plain text body
};

exports.sendEmail = function(){
    console.log(TAG,"we are is sendEmail"); 
    transport.sendMail(message, function(err, info) {
        console.log("info = " + info);
        if (err) {
            console.log(TAG, err);
        } 
        else {
            console.log(TAG, info);
        }
    });
}

