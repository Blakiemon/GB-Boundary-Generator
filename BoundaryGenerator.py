import json
import os
import PySimpleGUI as sg
import threading
import time
import operator
import tkinter as tk
from tkinter import *
import shutil

#setting up window
sg.theme('DarkGrey2')
layout = [[sg.Text('Choose a course. (.SSG4X or .SSG3X files)')],
          [sg.Text('\n\nIf you are running MacOS, select your course here.')],
          [sg.Column([[sg.Text('COURSE TO MODIFY', key='filetext', size=(20, 1)), sg.Input(key='input-file'), sg.FileBrowse(key='filebrowse')]], pad=(0,0), key='file')],
          [sg.Text('\n\nIf you are running Windows or Linux select your course here.\n\n(Or if you want to process files in a seperate folder)')],
          [sg.Column([[sg.Text('FOLDER TO MODIFY', key='foldertext', size=(20, 1)), sg.Input(key='input-folder'), sg.FolderBrowse(key='folderbrowse')]], pad=(0,0), key='folder')],
          [sg.Checkbox('Convert Boundaries Back Instead', key='convert')],
          [sg.Text('\nWhich hole(s) would you like to generate boundaries in?')],
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
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

def convertInfo(path, holes):
    '''This thread parses each hole and converts boundaries to objects'''
    #setting up variables
    text = window['_OUT_']
    template = r'{"rotation-actions-repeat-mode":"0","texture-sdf":"iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAAAAABWESUoAAAM82lDQ1BrQ0dDb2xv\r\nclNwYWNlR2VuZXJpY0dyYXlHYW1tYTJfMgAAWIWlVwdYU8kWnluS0BJ6lRI60gwo\r\nXUqkBpBeBFGJIZBACDEFAbEhiyu4dhHBsqKiKIsdgcWGBQtrB7sLuigo6+IqNixv\r\nEopYdt\/7vnfzzb3\/nXPOnDpnbgBQ5TAFAh4KAMjki4WBUfSEKQmJVNJdIAe0gTKw\r\nB8pMlkhAj4gIhSyAn8Vng2+uV+0AkT6v2UnX+pb+rxchhS1iwedxOHJTRKxMAJCJ\r\nAJC6WQKhGAB5MzhvOlsskOIgiDUyYqJ8IU4CQE5pSFZ6GQWy+Wwhl0UNFDJzqYHM\r\nzEwm1dHekRohzErl8r5j9f97ZfIkI7rhUBJlRIfApz20vzCF6SfFrhDvZzH9o4fw\r\nk2xuXBjEPgCgJgLxpCiIgyGeKcmIpUNsC3FNqjAgFmIviG9yJEFSPAEATCuPExMP\r\nsSHEwfyZYeEQu0PMYYl8EyG2griSw2ZI8wRjhp3nihkxEEN92DNhVpSU3xoAfGIK\r\n289\/cB5PzcgKkdpgAvFBUXa0\/7DNeRzfsEFdeHs6MzgCYguIX7J5gVGD6xD0BOII\r\n6ZrwneDH54WFDvpFKGWLZP7Cd0K7mBMjzZkjAEQTsTAmatA2YkwqN4ABcQDEORxh\r\nUNSgv8SjAp6szmBMiO+FkqjYQR9JAWx+rHRNaV0sYAr9AwdjRWoCcQgTsEEWmAnv\r\nLMAHnYAKRIALsmUoDTBBJhxUaIEtHIGQiw+HEHKIQIaMQwi6RujDElIZAaRkgVTI\r\nyYNyw7NUkALlB+Wka2TBIX2Trtstm2MN6bOHw9dwO5DANw7ohXQORJNBh2wmB9qX\r\nCZ++cFYCaWkQj9YyKB8hs3XQBuqQ9T1DWrJktjBH5D7b5gvpfJAHZ0TDnuHaOA0f\r\nD4cHHop74jSZlBBy5AI72fxE2dyw1s+eS33rGdE6C9o62vvR8RqO4QkoJYbvPOgh\r\nfyg+ImjNeyiTMST9lZ8r9CRWAkHpskjG9KoRK6gFwhlc1qXlff+StW+1232Rt\/DR\r\ndSGrlJRv6gLqIlwlXCbcJ1wHVPj8g9BG6IboDuEu\/N36blSyRmKQBkfWSAWwv8gN\r\nG3LyZFq+tfNzzgbX+WoFBBvhpMtWkVIz4eDKeEQj+ZNALIb3VJm03Ve5C\/xab0t+\r\nkw6gti89fg5Qa1Qazn6Odhten3RNqSU\/lb9CTyCYXpU\/wBZ8pkrzwF4c9ioMFNjS\r\n9tJ6adtoNbQXtPufOWg3aH\/S2mhbIOUptho7hB3BGrBGrBVQ4VsjdgJrkKEarAn+\r\n9v1Dhad9p8KlFcMaqmgpVTxUU6Nrf3Rk6aOiJeUfjnD6P9Tr6IqRZux\/s2j0Ol92\r\nBPbnXUcxpThQSBRrihOFTkEoxvDnSPGByJRiQgmlaENqEMWS4kcZMxKP4VrnDWWY\r\n+8X+HrQ4AVKHK4Ev6y5MyCnlYA75+7WP1C+8lHrGHb2rEDLcVdxRPeF7vYj6xc6K\r\nhbJcMFsmL5Ltdr5MTvBF\/YlkXQjOIFNlOfyObbgh7oAzYAcKB1ScjjvhPkN4sCsN\r\n9yVZpnBvSPXC\/XBXaR\/7oi+w\/qv1o3cGm+hOtCT6Ey0\/04l+xCBiAHw6SOeJ44jB\r\nELtJucTsHLH0kPfNEuQKuWkcMZUOv3LYVAafZW9LdaQ5wNNN+s00+CnwIlL2LYRo\r\ntbIkwuzBOVx6IwAF+D2lAXThqWoKT2s7qNUFeMAz0x+ed+EgBuZ1OvSDA+0Wwsjm\r\ng4WgCJSAFWAtKAebwTZQDWrBfnAYNMEeewZcAJdBG7gDz5Mu8BT0gVdgAEEQEkJG\r\n1BFdxAgxR2wQR8QV8UL8kVAkCklAkpE0hI9IkHxkEVKCrELKkS1INbIPaUBOIOeQ\r\nK8gtpBPpQf5G3qEYqoRqoAaoBToOdUXpaAgag05D09BZaB5aiC5Dy9BKtAatQ0+g\r\nF9A2tAN9ivZjAFPEtDBjzA5zxXyxcCwRS8WE2DysGCvFKrFa2ANasGtYB9aLvcWJ\r\nuDpOxe1gFoPwWJyFz8Ln4UvxcnwnXoefwq\/hnXgf\/pFAJugTbAjuBAZhCiGNMJtQ\r\nRCglVBEOEU7DDt1FeEUkErVgflxg3hKI6cQ5xKXEjcQ9xOPEK8SHxH4SiaRLsiF5\r\nksJJTJKYVERaT6ohHSNdJXWR3sgpyhnJOcoFyCXK8eUK5Erldskdlbsq91huQF5F\r\n3lzeXT5cPkU+V365\/Db5RvlL8l3yAwqqCpYKngoxCukKCxXKFGoVTivcVXihqKho\r\nouimGKnIVVygWKa4V\/GsYqfiWyU1JWslX6UkJYnSMqUdSseVbim9IJPJFmQfciJZ\r\nTF5GriafJN8nv6GoU+wpDEoKZT6lglJHuUp5piyvbK5MV56unKdcqnxA+ZJyr4q8\r\nioWKrwpTZZ5KhUqDyg2VflV1VQfVcNVM1aWqu1TPqXarkdQs1PzVUtQK1baqnVR7\r\nqI6pm6r7qrPUF6lvUz+t3qVB1LDUYGika5Ro\/KJxUaNPU01zgmacZo5mheYRzQ4t\r\nTMtCi6HF01qutV+rXeudtoE2XZutvUS7Vvuq9mudMTo+OmydYp09Om0673Spuv66\r\nGbordQ\/r3tPD9az1IvVm623SO63XO0ZjjMcY1pjiMfvH3NZH9a31o\/Tn6G\/Vb9Xv\r\nNzA0CDQQGKw3OGnQa6hl6GOYbrjG8Khhj5G6kZcR12iN0TGjJ1RNKp3Ko5ZRT1H7\r\njPWNg4wlxluMLxoPmFiaxJoUmOwxuWeqYOpqmmq6xrTZtM\/MyGyyWb7ZbrPb5vLm\r\nruYc83XmLeavLSwt4i0WWxy26LbUsWRY5lnutrxrRbbytpplVWl1fSxxrOvYjLEb\r\nx162Rq2drDnWFdaXbFAbZxuuzUabK7YEWzdbvm2l7Q07JTu6XbbdbrtOey37UPsC\r\n+8P2z8aZjUsct3Jcy7iPNCcaD55udxzUHIIdChwaHf52tHZkOVY4Xh9PHh8wfv74\r\n+vHPJ9hMYE\/YNOGmk7rTZKfFTs1OH5xdnIXOtc49LmYuyS4bXG64arhGuC51PetG\r\ncJvkNt+tye2tu7O72H2\/+18edh4ZHrs8uidaTmRP3DbxoaeJJ9Nzi2eHF9Ur2etn\r\nrw5vY2+md6X3Ax9TnxSfKp\/H9LH0dHoN\/dkk2iThpEOTXvu6+871Pe6H+QX6Fftd\r\n9Ffzj\/Uv978fYBKQFrA7oC\/QKXBO4PEgQlBI0MqgGwwDBotRzegLdgmeG3wqRCkk\r\nOqQ85EGodagwtHEyOjl48urJd8PMw\/hhh8NBOCN8dfi9CMuIWRG\/RhIjIyIrIh9F\r\nOUTlR7VEq0fPiN4V\/SpmUszymDuxVrGS2OY45bikuOq41\/F+8aviO6aMmzJ3yoUE\r\nvQRuQn0iKTEusSqxf6r\/1LVTu5KckoqS2qdZTsuZdm663nTe9CMzlGcwZxxIJiTH\r\nJ+9Kfs8MZ1Yy+2cyZm6Y2cfyZa1jPU3xSVmT0sP2ZK9iP071TF2V2p3mmbY6rYfj\r\nzSnl9HJ9ueXc5+lB6ZvTX2eEZ+zI+MSL5+3JlMtMzmzgq\/Ez+KeyDLNysq4IbARF\r\ngo5Z7rPWzuoThgirRIhomqherAH\/YLZKrCQ\/SDqzvbIrst\/Mjpt9IEc1h5\/Tmmud\r\nuyT3cV5A3vY5+BzWnOZ84\/yF+Z1z6XO3zEPmzZzXPN90fuH8rgWBC3YuVFiYsfC3\r\nAlrBqoKXi+IXNRYaFC4ofPhD4A+7iyhFwqIbiz0Wb\/4R\/5H748Ul45esX\/KxOKX4\r\nfAmtpLTk\/VLW0vM\/OfxU9tOnZanLLi53Xr5pBXEFf0X7Su+VO1eprspb9XD15NV1\r\na6hrite8XDtj7bnSCaWb1ymsk6zrKAstq19vtn7F+vflnPK2ikkVezbob1iy4fXG\r\nlI1XN\/lsqt1ssLlk87ufuT\/f3BK4pa7SorJ0K3Fr9tZH2+K2tWx33V5dpVdVUvVh\r\nB39Hx86onaeqXaqrd+nvWr4b3S3Z3VOTVHP5F79f6mvtarfs0dpTshfslex9si95\r\nX\/v+kP3NB1wP1B40P7jhkPqh4jqkLreu7zDncEd9Qv2VhuCG5kaPxkO\/2v+6o8m4\r\nqeKI5pHlRxWOFh79dCzvWP9xwfHeE2knHjbPaL5zcsrJ66ciT108HXL67JmAMydb\r\n6C3HznqebTrnfq7hvOv5wxecL9S1OrUe+s3pt0MXnS\/WXXK5VH\/Z7XLjlYlXjl71\r\nvnrimt+1M9cZ1y+0hbVdaY9tv3kj6UbHzZSb3bd4t57fzr49cGcB\/Igvvqdyr\/S+\r\n\/v3K38f+vqfDueNIp19n64PoB3cesh4+\/UP0x\/uuwkfkR6WPjR5Xdzt2N\/UE9Fx+\r\nMvVJ11PB04Heoj9V\/9zwzOrZwb98\/mrtm9LX9Vz4\/NPfS1\/ovtjxcsLL5v6I\/vuv\r\nMl8NvC5+o\/tm51vXty3v4t89Hpj9nvS+7MPYD40fQz7e\/ZT56dN\/AC1d8BzqtvWA\r\nAAAAFUlEQVQ4EWNgGAWjITAaAqMhgD0EAAQgAAHF0iOaAAAAAElFTkSuQmCC","rotation-actions":[],"depthShaderEnabled":"0","snapped-nodes":[],"hideDepthEnabled":"0","id":"6E89CA34-8B2D-480B-885C-53D2A8E0C033","texture":"LeftBoundary.png","showContours":"0","texture-green-mask":"iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAAAAABWESUoAAAM82lDQ1BrQ0dDb2xv\r\nclNwYWNlR2VuZXJpY0dyYXlHYW1tYTJfMgAAWIWlVwdYU8kWnluS0BJ6lRI60gwo\r\nXUqkBpBeBFGJIZBACDEFAbEhiyu4dhHBsqKiKIsdgcWGBQtrB7sLuigo6+IqNixv\r\nEopYdt\/7vnfzzb3\/nXPOnDpnbgBQ5TAFAh4KAMjki4WBUfSEKQmJVNJdIAe0gTKw\r\nB8pMlkhAj4gIhSyAn8Vng2+uV+0AkT6v2UnX+pb+rxchhS1iwedxOHJTRKxMAJCJ\r\nAJC6WQKhGAB5MzhvOlsskOIgiDUyYqJ8IU4CQE5pSFZ6GQWy+Wwhl0UNFDJzqYHM\r\nzEwm1dHekRohzErl8r5j9f97ZfIkI7rhUBJlRIfApz20vzCF6SfFrhDvZzH9o4fw\r\nk2xuXBjEPgCgJgLxpCiIgyGeKcmIpUNsC3FNqjAgFmIviG9yJEFSPAEATCuPExMP\r\nsSHEwfyZYeEQu0PMYYl8EyG2griSw2ZI8wRjhp3nihkxEEN92DNhVpSU3xoAfGIK\r\n289\/cB5PzcgKkdpgAvFBUXa0\/7DNeRzfsEFdeHs6MzgCYguIX7J5gVGD6xD0BOII\r\n6ZrwneDH54WFDvpFKGWLZP7Cd0K7mBMjzZkjAEQTsTAmatA2YkwqN4ABcQDEORxh\r\nUNSgv8SjAp6szmBMiO+FkqjYQR9JAWx+rHRNaV0sYAr9AwdjRWoCcQgTsEEWmAnv\r\nLMAHnYAKRIALsmUoDTBBJhxUaIEtHIGQiw+HEHKIQIaMQwi6RujDElIZAaRkgVTI\r\nyYNyw7NUkALlB+Wka2TBIX2Trtstm2MN6bOHw9dwO5DANw7ohXQORJNBh2wmB9qX\r\nCZ++cFYCaWkQj9YyKB8hs3XQBuqQ9T1DWrJktjBH5D7b5gvpfJAHZ0TDnuHaOA0f\r\nD4cHHop74jSZlBBy5AI72fxE2dyw1s+eS33rGdE6C9o62vvR8RqO4QkoJYbvPOgh\r\nfyg+ImjNeyiTMST9lZ8r9CRWAkHpskjG9KoRK6gFwhlc1qXlff+StW+1232Rt\/DR\r\ndSGrlJRv6gLqIlwlXCbcJ1wHVPj8g9BG6IboDuEu\/N36blSyRmKQBkfWSAWwv8gN\r\nG3LyZFq+tfNzzgbX+WoFBBvhpMtWkVIz4eDKeEQj+ZNALIb3VJm03Ve5C\/xab0t+\r\nkw6gti89fg5Qa1Qazn6Odhten3RNqSU\/lb9CTyCYXpU\/wBZ8pkrzwF4c9ioMFNjS\r\n9tJ6adtoNbQXtPufOWg3aH\/S2mhbIOUptho7hB3BGrBGrBVQ4VsjdgJrkKEarAn+\r\n9v1Dhad9p8KlFcMaqmgpVTxUU6Nrf3Rk6aOiJeUfjnD6P9Tr6IqRZux\/s2j0Ol92\r\nBPbnXUcxpThQSBRrihOFTkEoxvDnSPGByJRiQgmlaENqEMWS4kcZMxKP4VrnDWWY\r\n+8X+HrQ4AVKHK4Ev6y5MyCnlYA75+7WP1C+8lHrGHb2rEDLcVdxRPeF7vYj6xc6K\r\nhbJcMFsmL5Ltdr5MTvBF\/YlkXQjOIFNlOfyObbgh7oAzYAcKB1ScjjvhPkN4sCsN\r\n9yVZpnBvSPXC\/XBXaR\/7oi+w\/qv1o3cGm+hOtCT6Ey0\/04l+xCBiAHw6SOeJ44jB\r\nELtJucTsHLH0kPfNEuQKuWkcMZUOv3LYVAafZW9LdaQ5wNNN+s00+CnwIlL2LYRo\r\ntbIkwuzBOVx6IwAF+D2lAXThqWoKT2s7qNUFeMAz0x+ed+EgBuZ1OvSDA+0Wwsjm\r\ng4WgCJSAFWAtKAebwTZQDWrBfnAYNMEeewZcAJdBG7gDz5Mu8BT0gVdgAEEQEkJG\r\n1BFdxAgxR2wQR8QV8UL8kVAkCklAkpE0hI9IkHxkEVKCrELKkS1INbIPaUBOIOeQ\r\nK8gtpBPpQf5G3qEYqoRqoAaoBToOdUXpaAgag05D09BZaB5aiC5Dy9BKtAatQ0+g\r\nF9A2tAN9ivZjAFPEtDBjzA5zxXyxcCwRS8WE2DysGCvFKrFa2ANasGtYB9aLvcWJ\r\nuDpOxe1gFoPwWJyFz8Ln4UvxcnwnXoefwq\/hnXgf\/pFAJugTbAjuBAZhCiGNMJtQ\r\nRCglVBEOEU7DDt1FeEUkErVgflxg3hKI6cQ5xKXEjcQ9xOPEK8SHxH4SiaRLsiF5\r\nksJJTJKYVERaT6ohHSNdJXWR3sgpyhnJOcoFyCXK8eUK5Erldskdlbsq91huQF5F\r\n3lzeXT5cPkU+V365\/Db5RvlL8l3yAwqqCpYKngoxCukKCxXKFGoVTivcVXihqKho\r\nouimGKnIVVygWKa4V\/GsYqfiWyU1JWslX6UkJYnSMqUdSseVbim9IJPJFmQfciJZ\r\nTF5GriafJN8nv6GoU+wpDEoKZT6lglJHuUp5piyvbK5MV56unKdcqnxA+ZJyr4q8\r\nioWKrwpTZZ5KhUqDyg2VflV1VQfVcNVM1aWqu1TPqXarkdQs1PzVUtQK1baqnVR7\r\nqI6pm6r7qrPUF6lvUz+t3qVB1LDUYGika5Ro\/KJxUaNPU01zgmacZo5mheYRzQ4t\r\nTMtCi6HF01qutV+rXeudtoE2XZutvUS7Vvuq9mudMTo+OmydYp09Om0673Spuv66\r\nGbordQ\/r3tPD9az1IvVm623SO63XO0ZjjMcY1pjiMfvH3NZH9a31o\/Tn6G\/Vb9Xv\r\nNzA0CDQQGKw3OGnQa6hl6GOYbrjG8Khhj5G6kZcR12iN0TGjJ1RNKp3Ko5ZRT1H7\r\njPWNg4wlxluMLxoPmFiaxJoUmOwxuWeqYOpqmmq6xrTZtM\/MyGyyWb7ZbrPb5vLm\r\nruYc83XmLeavLSwt4i0WWxy26LbUsWRY5lnutrxrRbbytpplVWl1fSxxrOvYjLEb\r\nx162Rq2drDnWFdaXbFAbZxuuzUabK7YEWzdbvm2l7Q07JTu6XbbdbrtOey37UPsC\r\n+8P2z8aZjUsct3Jcy7iPNCcaD55udxzUHIIdChwaHf52tHZkOVY4Xh9PHh8wfv74\r\n+vHPJ9hMYE\/YNOGmk7rTZKfFTs1OH5xdnIXOtc49LmYuyS4bXG64arhGuC51PetG\r\ncJvkNt+tye2tu7O72H2\/+18edh4ZHrs8uidaTmRP3DbxoaeJJ9Nzi2eHF9Ur2etn\r\nrw5vY2+md6X3Ax9TnxSfKp\/H9LH0dHoN\/dkk2iThpEOTXvu6+871Pe6H+QX6Fftd\r\n9Ffzj\/Uv978fYBKQFrA7oC\/QKXBO4PEgQlBI0MqgGwwDBotRzegLdgmeG3wqRCkk\r\nOqQ85EGodagwtHEyOjl48urJd8PMw\/hhh8NBOCN8dfi9CMuIWRG\/RhIjIyIrIh9F\r\nOUTlR7VEq0fPiN4V\/SpmUszymDuxVrGS2OY45bikuOq41\/F+8aviO6aMmzJ3yoUE\r\nvQRuQn0iKTEusSqxf6r\/1LVTu5KckoqS2qdZTsuZdm663nTe9CMzlGcwZxxIJiTH\r\nJ+9Kfs8MZ1Yy+2cyZm6Y2cfyZa1jPU3xSVmT0sP2ZK9iP071TF2V2p3mmbY6rYfj\r\nzSnl9HJ9ueXc5+lB6ZvTX2eEZ+zI+MSL5+3JlMtMzmzgq\/Ez+KeyDLNysq4IbARF\r\ngo5Z7rPWzuoThgirRIhomqherAH\/YLZKrCQ\/SDqzvbIrst\/Mjpt9IEc1h5\/Tmmud\r\nuyT3cV5A3vY5+BzWnOZ84\/yF+Z1z6XO3zEPmzZzXPN90fuH8rgWBC3YuVFiYsfC3\r\nAlrBqoKXi+IXNRYaFC4ofPhD4A+7iyhFwqIbiz0Wb\/4R\/5H748Ul45esX\/KxOKX4\r\nfAmtpLTk\/VLW0vM\/OfxU9tOnZanLLi53Xr5pBXEFf0X7Su+VO1eprspb9XD15NV1\r\na6hrite8XDtj7bnSCaWb1ymsk6zrKAstq19vtn7F+vflnPK2ikkVezbob1iy4fXG\r\nlI1XN\/lsqt1ssLlk87ufuT\/f3BK4pa7SorJ0K3Fr9tZH2+K2tWx33V5dpVdVUvVh\r\nB39Hx86onaeqXaqrd+nvWr4b3S3Z3VOTVHP5F79f6mvtarfs0dpTshfslex9si95\r\nX\/v+kP3NB1wP1B40P7jhkPqh4jqkLreu7zDncEd9Qv2VhuCG5kaPxkO\/2v+6o8m4\r\nqeKI5pHlRxWOFh79dCzvWP9xwfHeE2knHjbPaL5zcsrJ66ciT108HXL67JmAMydb\r\n6C3HznqebTrnfq7hvOv5wxecL9S1OrUe+s3pt0MXnS\/WXXK5VH\/Z7XLjlYlXjl71\r\nvnrimt+1M9cZ1y+0hbVdaY9tv3kj6UbHzZSb3bd4t57fzr49cGcB\/Igvvqdyr\/S+\r\n\/v3K38f+vqfDueNIp19n64PoB3cesh4+\/UP0x\/uuwkfkR6WPjR5Xdzt2N\/UE9Fx+\r\nMvVJ11PB04Heoj9V\/9zwzOrZwb98\/mrtm9LX9Vz4\/NPfS1\/ovtjxcsLL5v6I\/vuv\r\nMl8NvC5+o\/tm51vXty3v4t89Hpj9nvS+7MPYD40fQz7e\/ZT56dN\/AC1d8BzqtvWA\r\nAAAAFUlEQVQ4EWNgGAWjITAaAqMhgD0EAAQgAAHF0iOaAAAAAElFTkSuQmCC","position-actions":[],"caveNode":"0","type":"TerrainNode","position-actions-repeat-mode":"0","texture-sticky-mask":"iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAAAAABWESUoAAAM82lDQ1BrQ0dDb2xv\r\nclNwYWNlR2VuZXJpY0dyYXlHYW1tYTJfMgAAWIWlVwdYU8kWnluS0BJ6lRI60gwo\r\nXUqkBpBeBFGJIZBACDEFAbEhiyu4dhHBsqKiKIsdgcWGBQtrB7sLuigo6+IqNixv\r\nEopYdt\/7vnfzzb3\/nXPOnDpnbgBQ5TAFAh4KAMjki4WBUfSEKQmJVNJdIAe0gTKw\r\nB8pMlkhAj4gIhSyAn8Vng2+uV+0AkT6v2UnX+pb+rxchhS1iwedxOHJTRKxMAJCJ\r\nAJC6WQKhGAB5MzhvOlsskOIgiDUyYqJ8IU4CQE5pSFZ6GQWy+Wwhl0UNFDJzqYHM\r\nzEwm1dHekRohzErl8r5j9f97ZfIkI7rhUBJlRIfApz20vzCF6SfFrhDvZzH9o4fw\r\nk2xuXBjEPgCgJgLxpCiIgyGeKcmIpUNsC3FNqjAgFmIviG9yJEFSPAEATCuPExMP\r\nsSHEwfyZYeEQu0PMYYl8EyG2griSw2ZI8wRjhp3nihkxEEN92DNhVpSU3xoAfGIK\r\n289\/cB5PzcgKkdpgAvFBUXa0\/7DNeRzfsEFdeHs6MzgCYguIX7J5gVGD6xD0BOII\r\n6ZrwneDH54WFDvpFKGWLZP7Cd0K7mBMjzZkjAEQTsTAmatA2YkwqN4ABcQDEORxh\r\nUNSgv8SjAp6szmBMiO+FkqjYQR9JAWx+rHRNaV0sYAr9AwdjRWoCcQgTsEEWmAnv\r\nLMAHnYAKRIALsmUoDTBBJhxUaIEtHIGQiw+HEHKIQIaMQwi6RujDElIZAaRkgVTI\r\nyYNyw7NUkALlB+Wka2TBIX2Trtstm2MN6bOHw9dwO5DANw7ohXQORJNBh2wmB9qX\r\nCZ++cFYCaWkQj9YyKB8hs3XQBuqQ9T1DWrJktjBH5D7b5gvpfJAHZ0TDnuHaOA0f\r\nD4cHHop74jSZlBBy5AI72fxE2dyw1s+eS33rGdE6C9o62vvR8RqO4QkoJYbvPOgh\r\nfyg+ImjNeyiTMST9lZ8r9CRWAkHpskjG9KoRK6gFwhlc1qXlff+StW+1232Rt\/DR\r\ndSGrlJRv6gLqIlwlXCbcJ1wHVPj8g9BG6IboDuEu\/N36blSyRmKQBkfWSAWwv8gN\r\nG3LyZFq+tfNzzgbX+WoFBBvhpMtWkVIz4eDKeEQj+ZNALIb3VJm03Ve5C\/xab0t+\r\nkw6gti89fg5Qa1Qazn6Odhten3RNqSU\/lb9CTyCYXpU\/wBZ8pkrzwF4c9ioMFNjS\r\n9tJ6adtoNbQXtPufOWg3aH\/S2mhbIOUptho7hB3BGrBGrBVQ4VsjdgJrkKEarAn+\r\n9v1Dhad9p8KlFcMaqmgpVTxUU6Nrf3Rk6aOiJeUfjnD6P9Tr6IqRZux\/s2j0Ol92\r\nBPbnXUcxpThQSBRrihOFTkEoxvDnSPGByJRiQgmlaENqEMWS4kcZMxKP4VrnDWWY\r\n+8X+HrQ4AVKHK4Ev6y5MyCnlYA75+7WP1C+8lHrGHb2rEDLcVdxRPeF7vYj6xc6K\r\nhbJcMFsmL5Ltdr5MTvBF\/YlkXQjOIFNlOfyObbgh7oAzYAcKB1ScjjvhPkN4sCsN\r\n9yVZpnBvSPXC\/XBXaR\/7oi+w\/qv1o3cGm+hOtCT6Ey0\/04l+xCBiAHw6SOeJ44jB\r\nELtJucTsHLH0kPfNEuQKuWkcMZUOv3LYVAafZW9LdaQ5wNNN+s00+CnwIlL2LYRo\r\ntbIkwuzBOVx6IwAF+D2lAXThqWoKT2s7qNUFeMAz0x+ed+EgBuZ1OvSDA+0Wwsjm\r\ng4WgCJSAFWAtKAebwTZQDWrBfnAYNMEeewZcAJdBG7gDz5Mu8BT0gVdgAEEQEkJG\r\n1BFdxAgxR2wQR8QV8UL8kVAkCklAkpE0hI9IkHxkEVKCrELKkS1INbIPaUBOIOeQ\r\nK8gtpBPpQf5G3qEYqoRqoAaoBToOdUXpaAgag05D09BZaB5aiC5Dy9BKtAatQ0+g\r\nF9A2tAN9ivZjAFPEtDBjzA5zxXyxcCwRS8WE2DysGCvFKrFa2ANasGtYB9aLvcWJ\r\nuDpOxe1gFoPwWJyFz8Ln4UvxcnwnXoefwq\/hnXgf\/pFAJugTbAjuBAZhCiGNMJtQ\r\nRCglVBEOEU7DDt1FeEUkErVgflxg3hKI6cQ5xKXEjcQ9xOPEK8SHxH4SiaRLsiF5\r\nksJJTJKYVERaT6ohHSNdJXWR3sgpyhnJOcoFyCXK8eUK5Erldskdlbsq91huQF5F\r\n3lzeXT5cPkU+V365\/Db5RvlL8l3yAwqqCpYKngoxCukKCxXKFGoVTivcVXihqKho\r\nouimGKnIVVygWKa4V\/GsYqfiWyU1JWslX6UkJYnSMqUdSseVbim9IJPJFmQfciJZ\r\nTF5GriafJN8nv6GoU+wpDEoKZT6lglJHuUp5piyvbK5MV56unKdcqnxA+ZJyr4q8\r\nioWKrwpTZZ5KhUqDyg2VflV1VQfVcNVM1aWqu1TPqXarkdQs1PzVUtQK1baqnVR7\r\nqI6pm6r7qrPUF6lvUz+t3qVB1LDUYGika5Ro\/KJxUaNPU01zgmacZo5mheYRzQ4t\r\nTMtCi6HF01qutV+rXeudtoE2XZutvUS7Vvuq9mudMTo+OmydYp09Om0673Spuv66\r\nGbordQ\/r3tPD9az1IvVm623SO63XO0ZjjMcY1pjiMfvH3NZH9a31o\/Tn6G\/Vb9Xv\r\nNzA0CDQQGKw3OGnQa6hl6GOYbrjG8Khhj5G6kZcR12iN0TGjJ1RNKp3Ko5ZRT1H7\r\njPWNg4wlxluMLxoPmFiaxJoUmOwxuWeqYOpqmmq6xrTZtM\/MyGyyWb7ZbrPb5vLm\r\nruYc83XmLeavLSwt4i0WWxy26LbUsWRY5lnutrxrRbbytpplVWl1fSxxrOvYjLEb\r\nx162Rq2drDnWFdaXbFAbZxuuzUabK7YEWzdbvm2l7Q07JTu6XbbdbrtOey37UPsC\r\n+8P2z8aZjUsct3Jcy7iPNCcaD55udxzUHIIdChwaHf52tHZkOVY4Xh9PHh8wfv74\r\n+vHPJ9hMYE\/YNOGmk7rTZKfFTs1OH5xdnIXOtc49LmYuyS4bXG64arhGuC51PetG\r\ncJvkNt+tye2tu7O72H2\/+18edh4ZHrs8uidaTmRP3DbxoaeJJ9Nzi2eHF9Ur2etn\r\nrw5vY2+md6X3Ax9TnxSfKp\/H9LH0dHoN\/dkk2iThpEOTXvu6+871Pe6H+QX6Fftd\r\n9Ffzj\/Uv978fYBKQFrA7oC\/QKXBO4PEgQlBI0MqgGwwDBotRzegLdgmeG3wqRCkk\r\nOqQ85EGodagwtHEyOjl48urJd8PMw\/hhh8NBOCN8dfi9CMuIWRG\/RhIjIyIrIh9F\r\nOUTlR7VEq0fPiN4V\/SpmUszymDuxVrGS2OY45bikuOq41\/F+8aviO6aMmzJ3yoUE\r\nvQRuQn0iKTEusSqxf6r\/1LVTu5KckoqS2qdZTsuZdm663nTe9CMzlGcwZxxIJiTH\r\nJ+9Kfs8MZ1Yy+2cyZm6Y2cfyZa1jPU3xSVmT0sP2ZK9iP071TF2V2p3mmbY6rYfj\r\nzSnl9HJ9ueXc5+lB6ZvTX2eEZ+zI+MSL5+3JlMtMzmzgq\/Ez+KeyDLNysq4IbARF\r\ngo5Z7rPWzuoThgirRIhomqherAH\/YLZKrCQ\/SDqzvbIrst\/Mjpt9IEc1h5\/Tmmud\r\nuyT3cV5A3vY5+BzWnOZ84\/yF+Z1z6XO3zEPmzZzXPN90fuH8rgWBC3YuVFiYsfC3\r\nAlrBqoKXi+IXNRYaFC4ofPhD4A+7iyhFwqIbiz0Wb\/4R\/5H748Ul45esX\/KxOKX4\r\nfAmtpLTk\/VLW0vM\/OfxU9tOnZanLLi53Xr5pBXEFf0X7Su+VO1eprspb9XD15NV1\r\na6hrite8XDtj7bnSCaWb1ymsk6zrKAstq19vtn7F+vflnPK2ikkVezbob1iy4fXG\r\nlI1XN\/lsqt1ssLlk87ufuT\/f3BK4pa7SorJ0K3Fr9tZH2+K2tWx33V5dpVdVUvVh\r\nB39Hx86onaeqXaqrd+nvWr4b3S3Z3VOTVHP5F79f6mvtarfs0dpTshfslex9si95\r\nX\/v+kP3NB1wP1B40P7jhkPqh4jqkLreu7zDncEd9Qv2VhuCG5kaPxkO\/2v+6o8m4\r\nqeKI5pHlRxWOFh79dCzvWP9xwfHeE2knHjbPaL5zcsrJ66ciT108HXL67JmAMydb\r\n6C3HznqebTrnfq7hvOv5wxecL9S1OrUe+s3pt0MXnS\/WXXK5VH\/Z7XLjlYlXjl71\r\nvnrimt+1M9cZ1y+0hbVdaY9tv3kj6UbHzZSb3bd4t57fzr49cGcB\/Igvvqdyr\/S+\r\n\/v3K38f+vqfDueNIp19n64PoB3cesh4+\/UP0x\/uuwkfkR6WPjR5Xdzt2N\/UE9Fx+\r\nMvVJ11PB04Heoj9V\/9zwzOrZwb98\/mrtm9LX9Vz4\/NPfS1\/ovtjxcsLL5v6I\/vuv\r\nMl8NvC5+o\/tm51vXty3v4t89Hpj9nvS+7MPYD40fQz7e\/ZT56dN\/AC1d8BzqtvWA\r\nAAAAFUlEQVQ4EWNgGAWjITAaAqMhgD0EAAQgAAHF0iOaAAAAAElFTkSuQmCC","padding-left":"22","vertices-original":[],"position":"{290, 322}","collisionsEnabled":"0","zOrder":"0","padding-right":"22","height":64,"color":0,"node-rotation":"0.000000","padding-bottom":"22","texture-acid-mask":"iVBORw0KGgoAAAANSUhEUgAAACAAAAAgCAAAAABWESUoAAAM82lDQ1BrQ0dDb2xv\r\nclNwYWNlR2VuZXJpY0dyYXlHYW1tYTJfMgAAWIWlVwdYU8kWnluS0BJ6lRI60gwo\r\nXUqkBpBeBFGJIZBACDEFAbEhiyu4dhHBsqKiKIsdgcWGBQtrB7sLuigo6+IqNixv\r\nEopYdt\/7vnfzzb3\/nXPOnDpnbgBQ5TAFAh4KAMjki4WBUfSEKQmJVNJdIAe0gTKw\r\nB8pMlkhAj4gIhSyAn8Vng2+uV+0AkT6v2UnX+pb+rxchhS1iwedxOHJTRKxMAJCJ\r\nAJC6WQKhGAB5MzhvOlsskOIgiDUyYqJ8IU4CQE5pSFZ6GQWy+Wwhl0UNFDJzqYHM\r\nzEwm1dHekRohzErl8r5j9f97ZfIkI7rhUBJlRIfApz20vzCF6SfFrhDvZzH9o4fw\r\nk2xuXBjEPgCgJgLxpCiIgyGeKcmIpUNsC3FNqjAgFmIviG9yJEFSPAEATCuPExMP\r\nsSHEwfyZYeEQu0PMYYl8EyG2griSw2ZI8wRjhp3nihkxEEN92DNhVpSU3xoAfGIK\r\n289\/cB5PzcgKkdpgAvFBUXa0\/7DNeRzfsEFdeHs6MzgCYguIX7J5gVGD6xD0BOII\r\n6ZrwneDH54WFDvpFKGWLZP7Cd0K7mBMjzZkjAEQTsTAmatA2YkwqN4ABcQDEORxh\r\nUNSgv8SjAp6szmBMiO+FkqjYQR9JAWx+rHRNaV0sYAr9AwdjRWoCcQgTsEEWmAnv\r\nLMAHnYAKRIALsmUoDTBBJhxUaIEtHIGQiw+HEHKIQIaMQwi6RujDElIZAaRkgVTI\r\nyYNyw7NUkALlB+Wka2TBIX2Trtstm2MN6bOHw9dwO5DANw7ohXQORJNBh2wmB9qX\r\nCZ++cFYCaWkQj9YyKB8hs3XQBuqQ9T1DWrJktjBH5D7b5gvpfJAHZ0TDnuHaOA0f\r\nD4cHHop74jSZlBBy5AI72fxE2dyw1s+eS33rGdE6C9o62vvR8RqO4QkoJYbvPOgh\r\nfyg+ImjNeyiTMST9lZ8r9CRWAkHpskjG9KoRK6gFwhlc1qXlff+StW+1232Rt\/DR\r\ndSGrlJRv6gLqIlwlXCbcJ1wHVPj8g9BG6IboDuEu\/N36blSyRmKQBkfWSAWwv8gN\r\nG3LyZFq+tfNzzgbX+WoFBBvhpMtWkVIz4eDKeEQj+ZNALIb3VJm03Ve5C\/xab0t+\r\nkw6gti89fg5Qa1Qazn6Odhten3RNqSU\/lb9CTyCYXpU\/wBZ8pkrzwF4c9ioMFNjS\r\n9tJ6adtoNbQXtPufOWg3aH\/S2mhbIOUptho7hB3BGrBGrBVQ4VsjdgJrkKEarAn+\r\n9v1Dhad9p8KlFcMaqmgpVTxUU6Nrf3Rk6aOiJeUfjnD6P9Tr6IqRZux\/s2j0Ol92\r\nBPbnXUcxpThQSBRrihOFTkEoxvDnSPGByJRiQgmlaENqEMWS4kcZMxKP4VrnDWWY\r\n+8X+HrQ4AVKHK4Ev6y5MyCnlYA75+7WP1C+8lHrGHb2rEDLcVdxRPeF7vYj6xc6K\r\nhbJcMFsmL5Ltdr5MTvBF\/YlkXQjOIFNlOfyObbgh7oAzYAcKB1ScjjvhPkN4sCsN\r\n9yVZpnBvSPXC\/XBXaR\/7oi+w\/qv1o3cGm+hOtCT6Ey0\/04l+xCBiAHw6SOeJ44jB\r\nELtJucTsHLH0kPfNEuQKuWkcMZUOv3LYVAafZW9LdaQ5wNNN+s00+CnwIlL2LYRo\r\ntbIkwuzBOVx6IwAF+D2lAXThqWoKT2s7qNUFeMAz0x+ed+EgBuZ1OvSDA+0Wwsjm\r\ng4WgCJSAFWAtKAebwTZQDWrBfnAYNMEeewZcAJdBG7gDz5Mu8BT0gVdgAEEQEkJG\r\n1BFdxAgxR2wQR8QV8UL8kVAkCklAkpE0hI9IkHxkEVKCrELKkS1INbIPaUBOIOeQ\r\nK8gtpBPpQf5G3qEYqoRqoAaoBToOdUXpaAgag05D09BZaB5aiC5Dy9BKtAatQ0+g\r\nF9A2tAN9ivZjAFPEtDBjzA5zxXyxcCwRS8WE2DysGCvFKrFa2ANasGtYB9aLvcWJ\r\nuDpOxe1gFoPwWJyFz8Ln4UvxcnwnXoefwq\/hnXgf\/pFAJugTbAjuBAZhCiGNMJtQ\r\nRCglVBEOEU7DDt1FeEUkErVgflxg3hKI6cQ5xKXEjcQ9xOPEK8SHxH4SiaRLsiF5\r\nksJJTJKYVERaT6ohHSNdJXWR3sgpyhnJOcoFyCXK8eUK5Erldskdlbsq91huQF5F\r\n3lzeXT5cPkU+V365\/Db5RvlL8l3yAwqqCpYKngoxCukKCxXKFGoVTivcVXihqKho\r\nouimGKnIVVygWKa4V\/GsYqfiWyU1JWslX6UkJYnSMqUdSseVbim9IJPJFmQfciJZ\r\nTF5GriafJN8nv6GoU+wpDEoKZT6lglJHuUp5piyvbK5MV56unKdcqnxA+ZJyr4q8\r\nioWKrwpTZZ5KhUqDyg2VflV1VQfVcNVM1aWqu1TPqXarkdQs1PzVUtQK1baqnVR7\r\nqI6pm6r7qrPUF6lvUz+t3qVB1LDUYGika5Ro\/KJxUaNPU01zgmacZo5mheYRzQ4t\r\nTMtCi6HF01qutV+rXeudtoE2XZutvUS7Vvuq9mudMTo+OmydYp09Om0673Spuv66\r\nGbordQ\/r3tPD9az1IvVm623SO63XO0ZjjMcY1pjiMfvH3NZH9a31o\/Tn6G\/Vb9Xv\r\nNzA0CDQQGKw3OGnQa6hl6GOYbrjG8Khhj5G6kZcR12iN0TGjJ1RNKp3Ko5ZRT1H7\r\njPWNg4wlxluMLxoPmFiaxJoUmOwxuWeqYOpqmmq6xrTZtM\/MyGyyWb7ZbrPb5vLm\r\nruYc83XmLeavLSwt4i0WWxy26LbUsWRY5lnutrxrRbbytpplVWl1fSxxrOvYjLEb\r\nx162Rq2drDnWFdaXbFAbZxuuzUabK7YEWzdbvm2l7Q07JTu6XbbdbrtOey37UPsC\r\n+8P2z8aZjUsct3Jcy7iPNCcaD55udxzUHIIdChwaHf52tHZkOVY4Xh9PHh8wfv74\r\n+vHPJ9hMYE\/YNOGmk7rTZKfFTs1OH5xdnIXOtc49LmYuyS4bXG64arhGuC51PetG\r\ncJvkNt+tye2tu7O72H2\/+18edh4ZHrs8uidaTmRP3DbxoaeJJ9Nzi2eHF9Ur2etn\r\nrw5vY2+md6X3Ax9TnxSfKp\/H9LH0dHoN\/dkk2iThpEOTXvu6+871Pe6H+QX6Fftd\r\n9Ffzj\/Uv978fYBKQFrA7oC\/QKXBO4PEgQlBI0MqgGwwDBotRzegLdgmeG3wqRCkk\r\nOqQ85EGodagwtHEyOjl48urJd8PMw\/hhh8NBOCN8dfi9CMuIWRG\/RhIjIyIrIh9F\r\nOUTlR7VEq0fPiN4V\/SpmUszymDuxVrGS2OY45bikuOq41\/F+8aviO6aMmzJ3yoUE\r\nvQRuQn0iKTEusSqxf6r\/1LVTu5KckoqS2qdZTsuZdm663nTe9CMzlGcwZxxIJiTH\r\nJ+9Kfs8MZ1Yy+2cyZm6Y2cfyZa1jPU3xSVmT0sP2ZK9iP071TF2V2p3mmbY6rYfj\r\nzSnl9HJ9ueXc5+lB6ZvTX2eEZ+zI+MSL5+3JlMtMzmzgq\/Ez+KeyDLNysq4IbARF\r\ngo5Z7rPWzuoThgirRIhomqherAH\/YLZKrCQ\/SDqzvbIrst\/Mjpt9IEc1h5\/Tmmud\r\nuyT3cV5A3vY5+BzWnOZ84\/yF+Z1z6XO3zEPmzZzXPN90fuH8rgWBC3YuVFiYsfC3\r\nAlrBqoKXi+IXNRYaFC4ofPhD4A+7iyhFwqIbiz0Wb\/4R\/5H748Ul45esX\/KxOKX4\r\nfAmtpLTk\/VLW0vM\/OfxU9tOnZanLLi53Xr5pBXEFf0X7Su+VO1eprspb9XD15NV1\r\na6hrite8XDtj7bnSCaWb1ymsk6zrKAstq19vtn7F+vflnPK2ikkVezbob1iy4fXG\r\nlI1XN\/lsqt1ssLlk87ufuT\/f3BK4pa7SorJ0K3Fr9tZH2+K2tWx33V5dpVdVUvVh\r\nB39Hx86onaeqXaqrd+nvWr4b3S3Z3VOTVHP5F79f6mvtarfs0dpTshfslex9si95\r\nX\/v+kP3NB1wP1B40P7jhkPqh4jqkLreu7zDncEd9Qv2VhuCG5kaPxkO\/2v+6o8m4\r\nqeKI5pHlRxWOFh79dCzvWP9xwfHeE2knHjbPaL5zcsrJ66ciT108HXL67JmAMydb\r\n6C3HznqebTrnfq7hvOv5wxecL9S1OrUe+s3pt0MXnS\/WXXK5VH\/Z7XLjlYlXjl71\r\nvnrimt+1M9cZ1y+0hbVdaY9tv3kj6UbHzZSb3bd4t57fzr49cGcB\/Igvvqdyr\/S+\r\n\/v3K38f+vqfDueNIp19n64PoB3cesh4+\/UP0x\/uuwkfkR6WPjR5Xdzt2N\/UE9Fx+\r\nMvVJ11PB04Heoj9V\/9zwzOrZwb98\/mrtm9LX9Vz4\/NPfS1\/ovtjxcsLL5v6I\/vuv\r\nMl8NvC5+o\/tm51vXty3v4t89Hpj9nvS+7MPYD40fQz7e\/ZT56dN\/AC1d8BzqtvWA\r\nAAAAFUlEQVQ4EWNgGAWjITAaAqMhgD0EAAQgAAHF0iOaAAAAAElFTkSuQmCC","terrain-offset":"{0.5, 0.5}","glow":{"Glow 2":{"depth":0,"choke":0,"color":0},"Glow 1":{"depth":0,"choke":0,"color":0},"Glow 3":{"depth":0,"choke":0,"color":0}},"nodeName":"LeftBoundary","scale":"{1, 1}","padding-top":"22","width":64,"vertices-processed":[]}'
    
    for hole in holes:
        window.refresh()
        removes = []
        text.update(text.get()+'\nProcessing level' + str(hole) + '.plist')
        cleanpath = os.path.abspath(str(path) + '/level' + str(hole) + '.plist')
        copypath = os.path.abspath(str(path) + '/level' + str(hole))
        shutil.copy(os.path.join(__location__, 'LeftBoundary.png'), copypath)
        with open(cleanpath, "r") as f:
            data = json.load(f)
        #parse nodes that are boundaries
        for node in data["nodes"]:
            if node["type"] == "LeftBoundaryNode" and node["position-actions"] != []:
                text.update(text.get()+'Found Left Boundary Barrier\nAdding Terrain Object')
                boundary_node = json.loads(template)
                boundary_node["position"] = node["position-actions"][0]["move-position"]
                boundary_node["node-rotation"] = node["rotation-actions"][0]["rotation-rate"]
                boundary_node["id"] = node["id"]
                removes.append(node)
                data["nodes"].append(boundary_node)
        text.update(text.get()+'Removing all Left Boundary barriers')
        for remove in removes:
            data["nodes"].remove(remove)
        text.update(text.get()+'Saving level' + str(hole) + '.plist')
        with open (cleanpath, 'w') as f:
            json.dump(data, f, separators=(',', ':'))
    text.update(text.get()+'All Done!')
    window['Process Holes'].update(disabled=False)

    window['Process Holes'].update(disabled=False)

def parseInfo(path, holes):
    '''This is the thread that parses each hole and makes changes.'''
    
    #setting up variables
    template = '{"position-actions-repeat-mode":"1","nodeName":"Left Boundary","id":"","rotation-actions":[{"interpolate-mode":"0","type":"rotate","period":".01","rotation-rate":""}],"position-actions":[{"interpolate-mode":"0","type":"position","move-position":"","period":".01"}],"type":"LeftBoundaryNode","rotation-actions-repeat-mode":"1"}'
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
            if node["nodeName"] == "LeftBoundary" and node["type"] == "TerrainNode":
                text.update(text.get()+'Found object "LeftBoundary"\nAdding real boundary')
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
                    try:
                        text.update(text.get()+'Log: ' + str(node["Main Texture"]) + ' not found for deletion, skipping')
                    except:
                        pass
                try:
                    os.remove(os.path.join(str(path) + '/level' + str(hole), node["texture"]))
                except:
                    try:
                        text.update(text.get()+'Log: ' + str(node["texture"]) + ' not found for deletion, skipping')
                    except:
                        pass
                try:
                    os.remove(os.path.join(str(path) + '/level' + str(hole), node["alpha-texture"]))
                except:
                    try:
                        text.update(text.get()+'Log: ' + str(node["alpha-texture"]) + ' not found for deletion, skipping')
                    except:
                        pass
                try:
                    os.remove(os.path.join(str(path) + '/level' + str(hole), node["texture-mask"]))
                except:
                    try:
                        text.update(text.get()+'Log: ' + str(node["texture-mask"]) + ' not found for deletion, skipping')
                    except:
                        pass
                try:
                    os.remove(os.path.join(str(path) + '/level' + str(hole), node["Green Texture"]))
                except:
                    try:
                        text.update(text.get()+'Log: ' + str(node["Green Texture"]) + ' not found for deletion, skipping')
                    except:
                        pass
        text.update(text.get()+'Removing all objects named "LeftBoundary"')
        for remove in removes:
            data["nodes"].remove(remove)
        text.update(text.get()+'Saving level' + str(hole) + '.plist')
        with open (cleanpath, 'w') as f:
            json.dump(data, f, separators=(',', ':'))
    text.update(text.get()+'All Done!')
    window.refresh()
    window['Process Holes'].update(disabled=False)


def checkPlists(path, holes, convert = False):
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
                if not convert:
                    for node in holeJSON["nodes"]:
                        #Checks if the array of dictionaries named 'nodes' has a special object needed for parsing
                        if node["nodeName"] == "LeftBoundary" and node["type"] == "TerrainNode":
                            hasBoundary = True
                            break
                    if hasBoundary == False:
                        boundaryHoles.append(hole)
                else:
                    for node in holeJSON["nodes"]:
                        #Checks if the array of dictionaries named 'nodes' has extra boundaries for parsing
                        if node["type"] == "LeftBoundaryNode" and node["position-actions"] != []:
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
    return

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
        convertThread = threading.Thread(target=convertInfo, args=(dir, holes,))
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
        plistCheck = checkPlists(dir, holes, values['convert'])
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
            if not values['convert']:
                for number in boundaryHoles:
                    missingPlists.append('level' + str(number) + '.plist')
                text.update(text.get()+'Error: plist(s): ' + str(missingPlists) + ' do not have any objects named "LeftBoundary" to replace with boundaries')
                window['Process Holes'].update(disabled=False)
                sg.Popup('Plist file(s) \n' + str(missingPlists) + ' \ndo not have any objects named "LeftBoundary" to replace with  real boundaries, please make sure you followed the instructions on how to use this program and properly generate boundaries.)', keep_on_top=True, title='Error')
                continue
            else:
                for number in boundaryHoles:
                    missingPlists.append('level' + str(number) + '.plist')
                text.update(text.get()+'Error: plist(s): ' + str(missingPlists) + ' do not have any boundaries to convert back to objects.')
                window['Process Holes'].update(disabled=False)
                sg.Popup('Plist file(s) \n' + str(missingPlists) + ' \ndo not have any boundaries to convert back to objects, you have not run the boundary generator on this hole before. If you are trying to generate boundaries then leave the button to convert boundaries back to objects unchecked.)', keep_on_top=True, title='Error')
                continue
        if not values['convert']:
            _continue = sg.PopupYesNo('Warning: All objects named "LeftBoundary" will be replaced with real boundaries.\n\nPlease double check the placement of all "LeftBoundary" objects before continueing\n\nContinue the operation?', keep_on_top=True, title='Continue?')
        else:
            _continue = sg.PopupYesNo('Warning: All existing boundaries generated by Boundary Generator will be converted back to terrain objects.\n\nContinue the operation?', keep_on_top=True, title='Continue?')
        if _continue == "No":
            window['Process Holes'].update(disabled=False)
            text.update(text.get()+'Process canceled')
            continue
        if not values['convert']:
            parseThread.start()
        else:
            convertThread.start()


    #makes the text box read only
    if event == '_OUT_+FOCUS_IN+':
        widget = window['_OUT_'].Widget
        widget.bind("<1>", widget.focus_set())
        window['_OUT_'].update(disabled=True)
    elif event == '_OUT_+FOCUS_OUT+':
        window['_OUT_'].Widget.unbind("<1>")
        window['_OUT_'].update(disabled=False)
