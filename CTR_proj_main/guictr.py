from appJar import gui
import CTR_main1 as main

    

def press(btn):
    """
    gets info from input tab
    """
    paths = app.getAllEntries()
    mode = app.getOptionBox("mode")
    # print (paths)
    # print(mode)
    main.main_flow(mode,paths)
    
app=gui("Cotton Target Recognition app")#, "450x550")


app.addMessage('exp',text="""Please enter operation mode and input/output 
    paths. Note that input path for images, and output path to the output,
    should point to a directory (not a file).""")
app.addLabelOptionBox("mode", [ "ortho", "images",
                        "ortho+images"])
app.addLabel ('orthoRasterInLabel','ortho file')
app.addFileEntry("ortho")
app.addLabel ('orthoDataInLabel','ortho data (.tfw/.jfw)')
app.addFileEntry("ortho_data")
app.addLabel ('loadDataLabel','in case of loading, enter pickle file(.pkl)')
app.addFileEntry('pickle_file')
app.addLabel ('imagesInLabel','images directory')
app.addDirectoryEntry('image_path')
app.addLabel ('outputOutLabel','output directory')
app.addDirectoryEntry('output')

app.addButton("confirm", press)



app.go()