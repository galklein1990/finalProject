const TAG = 'runProccess'
var spawn = require("child_process").spawn;
const process = require('process');

let mode = ' ortho+images ';
let ortho = 'C:/Users/mdwq87/Downloads/project/resizedOrtho.tif';
let ortho_data = 'C:/Users/mdwq87/Downloads/project/resized.tfw';
let pickle_file='';
let image_path = 'C:/Users/mdwq87/Downloads/project/input';
let output = 'C:/Users/mdwq87/Downloads/project/output';


exports.runPythonScript = function () {
    var dataString = '';
    var py =spawn('python', ["C:/Users/mdwq87/Downloads/CTR_proj_main/CTR_proj_main/runMe.py",mode,ortho,
    ortho_data, pickle_file,image_path,output]);
    py.stdout.on('data', function(data){
        dataString += data.toString();
        console.log("data recevied = ",data.toString()) ;
      });
      py.stdout.on('end', function(){
        console.log('Finish all, dataString = ',dataString);
      });
};

    


    
    
       
        
   