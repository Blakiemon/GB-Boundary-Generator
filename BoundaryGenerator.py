import json
import os
import PySimpleGUI as sg
import threading
import time
import operator
import tkinter as tk
from tkinter import *

#setting up window
sg.theme('DarkGrey2')
layout = [[sg.Text('Choose a course. (.SSG4X or .SSG3X files)')],
          [sg.Text('\n\nIf you are running MacOS, select your course here.')],
          [sg.Column([[sg.Text('COURSE TO MODIFY', key='filetext', size=(20, 1)), sg.Input(key='input-file'), sg.FileBrowse(key='filebrowse')]], pad=(0,0), key='file')],
          [sg.Text('\n\nIf you are running Windows or Linux select your course here.\n\n(Or if you want to process files in a seperate folder)')],
          [sg.Column([[sg.Text('FOLDER TO MODIFY', key='foldertext', size=(20, 1)), sg.Input(key='input-folder'), sg.FolderBrowse(key='folderbrowse')]], pad=(0,0), key='folder')],
          [sg.Text('\n\nWhich hole(s) would you like to generate boundaries in?')],
          [sg.Checkbox('Hole 1 (level0.plist)', key='1')],
          [sg.Checkbox('Hole 2 (level1.plist)', key='2')],
          [sg.Checkbox('Hole 3 (level2.plist)', key='3')],
          [sg.Checkbox('Hole 4 (level3.plist)', key='4')],
          [sg.Checkbox('Hole 5 (level4.plist)', key='5')],
          [sg.Checkbox('Hole 6 (level5.plist)', key='6')],
          [sg.Checkbox('Hole 7 (level6.plist)', key='7')],
          [sg.Checkbox('Hole 8 (level7.plist)', key='8')],
          [sg.Checkbox('Hole 9 (level8.plist)', key='9'), sg.Button("Process Holes")],
          [sg.Multiline(size=(80, 30), key='_OUT_')],]

#finalizing window
window = sg.Window('Generate Boundaries', size=(500,750)).Layout(layout).Finalize()
window.Element('_OUT_').bind("<FocusIn>", '+FOCUS_IN+')
window.Element('_OUT_').bind("<FocusOut>", '+FOCUS_OUT+')
window['_OUT_'].update('Welcome!\n')

#terminate thread
#window['Process Holes'].update(disabled=False)
#parseThread.terminate()

#defining global variables
boundaryHoles = []
damagedHoles = []
notJsonHoles = []
missingHoles = []
holes = []
dir = ""

def parseInfo(path, holes):
    '''This is the thread that parses each hole and makes changes.'''
    
    #setting up template for boundary node
    template = '{"position-actions-repeat-mode":"1","nodeName":"Left Boundary","id":"","rotation-actions":[{"interpolate-mode":"0","type":"rotate","period":".01","rotation-rate":""}],"position-actions":[{"interpolate-mode":"0","type":"position","move-position":"","period":".01"}],"type":"LeftBoundaryNode","rotation-actions-repeat-mode":"1"}'
    
    #reference output widget
    text = window['_OUT_']
    
    #open holes
    for hole in holes:
        removes = []
        text.update(text.get()+'\nProcessing level' + str(hole) + '.plist')
        cleanpath = os.path.abspath(str(path) + '/level' + str(hole) + '.plist')
        with open(cleanpath, "r") as f:
            data = json.load(f)
        #parse nodes named LeftBoundary
        for node in data["nodes"]:
            if node["nodeName"] == "LeftBoundary":
                text.update(text.get()+'Found object "LeftBoundary"\nAdding real boundaries')
                boundary_node = json.loads(template)
                boundary_node["position-actions"][0]["move-position"] = node["position"]
                boundary_node["rotation-actions"][0]["rotation-rate"] = node["node-rotation"]
                boundary_node["id"] = node["id"]
                removes.append(node)
                data["nodes"].append(boundary_node)
                text.update(text.get()+'Attempting to delete textures associated with "LeftBoundary"')
                try:
                    os.remove(os.path.join(str(path) + '/level' + str(hole), node["Main Texture"]))
                except:
                    text.update(text.get()+'Log: ' + str(node["Main Texture"]) + ' not found for deletion, skipping')
                try:
                    os.remove(os.path.join(str(path) + '/level' + str(hole), node["texture"]))
                except:
                    text.update(text.get()+'Log: ' + str(node["texture"]) + ' not found for deletion, skipping')
                try:
                    os.remove(os.path.join(str(path) + '/level' + str(hole), node["alpha-texture"]))
                except:
                    text.update(text.get()+'Log: ' + str(node["alpha-texture"]) + ' not found for deletion, skipping')
                try:
                    os.remove(os.path.join(str(path) + '/level' + str(hole), node["texture-mask"]))
                except:
                    text.update(text.get()+'Log: ' + str(node["texture-mask"]) + ' not found for deletion, skipping')
                try:
                    os.remove(os.path.join(str(path) + '/level' + str(hole), node["Green Texture"]))
                except:
                    text.update(text.get()+'Log: ' + str(node["Green Texture"]) + ' not found for deletion, skipping')
        text.update(text.get()+'Removing all objects named "LeftBoundary"')
        for remove in removes:
            data["nodes"].remove(remove)
        text.update(text.get()+'Saving level' + str(hole) + '.plist')
        with open (cleanpath, 'w') as f:
            json.dump(data, f, separators=(',', ':'))
    text.update(text.get()+'All Done!')
    window.refresh()
    window['Process Holes'].update(disabled=False)


def checkPlists(path, holes):
    '''This checks if the selected holes exist, if it is json,
        if the json contains an array of dictionaries with the key-name 'nodes',
        and if 'nodes' array contains a dictionary that contains at least one dictionary entry
        with a key name of 'nodeName' and a value entry of 'LeftBoundary.'''
    
    #Check if file exists
    skipCheck = 0
    for hole in holes:
        cleanpath = os.path.abspath(str(path) + '/level' + str(hole) + '.plist')
        try:
            open(cleanpath, "r")
        except:
            print(str(path) + '/level' + str(hole) + '.plist')
            missingHoles.append(hole)
            skipCheck = 1
        
        #Checks if is json
        if skipCheck != 1:
            try:
                with open(cleanpath, "r") as f:
                    holeJSON = json.load(f)
            except ValueError as err:
                skipCheck = 2
                notJsonHoles.append(hole)

        #Checks if contains array of dictionaries named 'nodes'
        if skipCheck != 2:
            try:
                hasBoundary = False
                for node in holeJSON["nodes"]:
                    #Checks if the array of dictionaries named 'nodes' has a special object needed for parsing
                    if node["nodeName"] == "LeftBoundary":
                        hasBoundary = True
                        break
                if hasBoundary == False:
                    boundaryHoles.append(hole)
            except:
                damagedHoles.append(hole)
    if missingHoles != []:
        return "missing"
    if notJsonHoles != []:
        return "notJson"
    if damagedHoles != []:
        return "damaged"
    if boundaryHoles != []:
        return "boundary"
    return ""

#This refreshes the GUI and detects any button clicks as well as widget updates
while True:             # Event Loop
    text = window['_OUT_']
    event, values = window.Read(timeout=200)
    
    #Kills window or popup if OK is pressed or something activates the 'Cancel' action
    if event in (None, 'Cancel'):
        break
    
    
    globalevent = event
    globalvalues = values
    if values['input-file']:
        disableFolder = True
        disableFile = False
    elif values['input-folder']:
        disableFolder = False
        disableFile = True
    else:
        disableFolder = False
        disableFile = False
    window['input-folder'].update(disabled=disableFolder)
    window['folderbrowse'].update(disabled=disableFolder)
    window['input-file'].update(disabled=disableFile)
    window['filebrowse'].update(disabled=disableFile)

    #Checks many neccesary conditions before running the json parser to ensure no errors occur.
    if event == 'Process Holes':
        window['Process Holes'].update(disabled=True)
        text.update(text.get()+'Starting...')
        holes = []
        if values['input-file'] != "":
            dir = values['input-file']
        elif values['input-folder'] != "":
            dir = values['input-folder']
        else:
            text.update(text.get()+'Error: no course selected')
            window['Process Holes'].update(disabled=False)
            sg.Popup('Please select a course.', keep_on_top=True, title='Error')
            continue
        parseThread = threading.Thread(target=parseInfo, args=(dir, holes,))
        if values['1']:
            holes.append(0)
        if values['2']:
            holes.append(1)
        if values['3']:
            holes.append(2)
        if values['4']:
            holes.append(3)
        if values['5']:
            holes.append(4)
        if values['6']:
            holes.append(5)
        if values['7']:
            holes.append(6)
        if values['8']:
            holes.append(7)
        if values['9']:
            holes.append(8)
        if holes == []:
            text.update(text.get()+'Error: no holes selected')
            window['Process Holes'].update(disabled=False)
            sg.Popup('Please select one or more holes.', keep_on_top=True, title='Error')
            continue
        boundaryHoles = []
        damagedHoles = []
        notJsonHoles = []
        missingHoles = []
        missingPlists = []
        plistCheck = checkPlists(dir, holes)
        if plistCheck == "missing":
            for number in missingHoles:
                missingPlists.append('level' + str(number) + '.plist')
            text.update(text.get()+'Error: plist(s): ' + str(missingPlists) + ' do not exist')
            window['Process Holes'].update(disabled=False)
            sg.Popup('Plist file(s) \n' + str(missingPlists) + ' \ndo not exist within the course directory. Please make sure they are there. (They are generated by the editor when loading a hole.)', keep_on_top=True, title='Error')
            continue
        elif plistCheck == "notJson":
            for number in notJsonHoles:
                    missingPlists.append('level' + str(number) + '.plist')
            text.update(text.get()+'Error: plist(s): ' + str(missingPlists) + ' are not in JSON')
            window['Process Holes'].update(disabled=False)
            sg.Popup('Plist file(s) \n' + str(missingPlists) + ' \ndoes not contain any JSON. Please delete and regenerate it by opening the hole in the editor.)', keep_on_top=True, title='Error')
            continue
        elif plistCheck == "damaged":
            for number in damagedHoles:
                missingPlists.append('level' + str(number) + '.plist')
            text.update(text.get()+'Error: plist(s): ' + str(missingPlists) + ' do not contain the proper data generated by the editor')
            window['Process Holes'].update(disabled=False)
            sg.Popup('Plist file(s) \n' + str(missingPlists) + ' \ndo not contain the proper data generated by the editor, if you are editing the JSON manually please make sure it contains an array of dictionaries named "nodes")', keep_on_top=True, title='Error')
            continue
        elif plistCheck == "boundary":
            for number in boundaryHoles:
                missingPlists.append('level' + str(number) + '.plist')
            text.update(text.get()+'Error: plist(s): ' + str(missingPlists) + ' do not have any objects named "LeftBoundary" to replace with boundaries')
            window['Process Holes'].update(disabled=False)
            sg.Popup('Plist file(s) \n' + str(missingPlists) + ' \ndo not have any objects named "LeftBoundary" to replace with  real boundaries, please make sure you followed the instructions on how to use this program and properly generate boundaries.)', keep_on_top=True, title='Error')
            continue
        _continue = sg.PopupYesNo('Warning: All objects named "LeftBoundary" will be replaced with real boundaries.\n\nPlease double check the placement of all "LeftBoundary" objects before continueing\n\nContinue the operation?', keep_on_top=True, title='Continue?')
        if _continue == "No":
            window['Process Holes'].update(disabled=False)
            text.update(text.get()+'Process canceled')
            continue
        parseThread.start()


    #makes the text box read only
    if event == '_OUT_+FOCUS_IN+':
        widget = window['_OUT_'].Widget
        widget.bind("<1>", widget.focus_set())
        window['_OUT_'].update(disabled=True)
    elif event == '_OUT_+FOCUS_OUT+':
        window['_OUT_'].Widget.unbind("<1>")
        window['_OUT_'].update(disabled=False)
