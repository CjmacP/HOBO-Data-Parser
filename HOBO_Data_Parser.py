import pandas as pd
import numpy as np
import PySimpleGUI as sg

''' GUI SETUP'''

sg.ChangeLookAndFeel('GreenTan')

layout = [[sg.Text('   ')],
          [sg.Text('Load HOBO CSV file', size=(24, 1)), sg.InputText(tooltip='Click Browse to find file'), sg.FileBrowse()],
          [sg.Text('Input HOBO Bracket Elevation: ', size=(24, 1)), sg.InputText(size=(10, 1)), sg.Text('Ft.')],
          [sg.Text('Input HOBO offset: ', size=(24, 1)), sg.InputText(tooltip='0.0675', size=(10, 1)), sg.Text('Ft.')], [sg.Text('')],
          [sg.SaveAs('Name/Path output AQ CSV file', tooltip='Click to open Browser window', size=(23, 1)), sg.InputText('Click on button to the left'),],
          [sg.Text('')],
          [sg.Text("                                                                                              "
                   "  "), sg.Submit('Save and get Max Stage', tooltip='Click save', button_color=('black', 'light blue')), sg.Text(' '),
           sg.Quit(tooltip='Quit to Exit')]]

window = sg.Window('HOBO to AQ *.csv').Layout(layout)

event, (start, BracketElevation, Offset, finish,) = window.Read()

'''--Input Test--'''

# print(start)
# print(BracketElevation)
# print(Offset)
# print(finish)

'''--------------'''

while True:
    if event is None or event == 'Quit':
        window.Close()
        break
    else:
        if start == '':
            sg.PopupError('Oops, you forgot to input a HOBO *.csv file')

        elif BracketElevation == '':
            sg.PopupError('Oops, you forgot to input a HOBO bracket elevation')

        elif Offset == '':
            sg.PopupError('Oops, you forgot to enter in a HOBO offset elevation')

        elif finish == '':
            sg.PopupError('Oops, you forgot Name/Path output AQ CSV file')

        else:

            df = pd.read_csv(start)
            shape = int(df.shape[1])

            # print(df.head())

            if shape < 2:       # if header has only one column
                df = pd.read_csv(start, header=1)
                new = df.filter(regex='Date | Depth')
                # print(int(df.shape[1]))
                # print('this')

            else:
                new = df.filter(regex='Date | Depth')
                # print(int(df.shape[1]))
                # print('that')
                # print(new.shape)

            HOBO_Bracket_Elevation = float(BracketElevation)

            HOBO_Offset = float(Offset)

            Adjusted_HOBO_elevation = HOBO_Bracket_Elevation + HOBO_Offset

            sensor_depth = new.filter(regex='Depth')
            total_depth = Adjusted_HOBO_elevation + sensor_depth

            # print(new)
            # print(new.shape)

            new.columns = ['Date and Time', 'HOBO Sensor Depth']
            new['Adjusted Elevation'] = total_depth

            new['Import to Aquarius'] = np.where(total_depth.astype(float) >= Adjusted_HOBO_elevation,
                                                 total_depth.astype(float), '')
            new['Import to Aquarius'] = pd.to_numeric(new['Import to Aquarius'])

            decimals3 = 3
            decimals2 = 2

            new['Adjusted Elevation'] = new['Adjusted Elevation'].apply(lambda x: round(x, decimals3))
            new['Import to Aquarius'] = new['Import to Aquarius'].apply(lambda x: round(x, decimals3))

            max1 = new.loc[new['Import to Aquarius'].idxmax(), ['Date and Time', 'Import to Aquarius']]

            new['Adjusted Elevation'] = new['Adjusted Elevation'].apply(lambda x: round(x, decimals2))
            new['Import to Aquarius'] = new['Import to Aquarius'].apply(lambda x: round(x, decimals2))

            new['Date and Time'] = pd.to_datetime(new['Date and Time']).apply(lambda x: x.strftime('%m/%d/%Y %H:%M'))  # To convert to pandas DateTime format

            # print(max2.iloc[0]['Date and Time'])
            # print(max2.iloc[0]['HOBO Sensor Depth'])

            max2 = (new.sort_values(['HOBO Sensor Depth'], ascending=[False]))[0:1]

            try:
                if '.csv' in finish:
                    new.to_csv(finish, index=False)

                    sg.Popup('The max stage is:',
                             '----------------------',
                             max2.iloc[0]['Date and Time'],
                             str(max2.iloc[0]['Import to Aquarius']) + ' Feet',
                             '----------------------',
                             'File save at: ' + str(finish), '')
                else:
                    new.to_csv(finish + '.csv', index=False)

                    sg.Popup('The max stage is:',
                             '----------------------',
                             max2.iloc[0]['Date and Time'],
                             str(max2.iloc[0]['Import to Aquarius']) + ' Feet',
                             '----------------------',
                             'File save at: ' + str(finish), '')
            except Exception as a:
                sg.Popup(a, '-------------------', 'FATAL ERROR: Failed To Execute')

    event, (start, BracketElevation, Offset, finish,) = window.Read()

    continue

window.Close()
