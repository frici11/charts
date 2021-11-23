import PySimpleGUI as sg
from mychart import LineChart, ColChart, PieChart
import datetime
import random


def make_window():
    layout = [[LineChart((800,200),(0,0),(800,200), key="-LCH1-", enable_events=True,
                        background_color=sg.theme_input_background_color())],
              [LineChart((800,200),(0,0),(800,200), key="-LCH2-", enable_events=True,
                           background_color=sg.theme_input_background_color())],
              [ColChart((800, 200), (0, 0), (800, 200), key="-CCH-", enable_events=True,
                            background_color=sg.theme_input_background_color())],
              [PieChart((800, 200), (0, 0), (800, 200), key="-PCH-", enable_events=True,
                           background_color=sg.theme_input_background_color())]]
    newwindow = sg.Window("Test of charts", layout, finalize=True)
    return newwindow


window = make_window()

lch1 = window["-LCH1-"]
lch2 = window["-LCH2-"]
cch = window["-CCH-"]
pch = window["-PCH-"]

labels = ["one","two","three","four","five","six","seven"]

dates = []
for i in (1,2,3,4,5,6,9):
    dates.append(datetime.date(2021,i,1))
data11 = [10000,20000,18000,12000,25000,30000,23000]
step = 100
data12 = [d*random.randint(5,20)/10 for d in data11] #cum(dates,data11,step)
data2 = [[data11[i],int(data12[i])] for i in range(len(labels))]
data3 = [10000,20000,15000,8000,15000,100,31000]

lch1.activate("test1", ["value1", dates, data11, "shape=sp"])
lch2.activate("test2", ["value1", dates, data11, "shape=s"], ["value2", dates, data12, "shape=p"])
cch.activate("test", labels, data2, ["value1","value2"])
pch.activate("test", labels, data3, donut=True)

while True:
    event, values = window.read(10)
    if event in (None, sg.WIN_CLOSED):
        break
    if event == "-LCH1-":
        lch1.handler(event, values)
    elif event == "-LCH2-":
        lch2.handler(event, values)
    elif event == "-CCH-":
        cch.handler(event, values)
    elif event == "-PCH-":
        pch.handler(event, values)

window.close()