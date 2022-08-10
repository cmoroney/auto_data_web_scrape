import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy
from scipy.optimize import curve_fit
from scipy.optimize import differential_evolution
import warnings
from scipy.optimize import least_squares

df = pd.read_csv("output.csv")

# df.head()
# df.count

# df[1:] # 0-60 time

# df['How much power?']
power = df['How much power?'].str.split(', ', n = 1, expand = True)
df['power_hp'] = power[0].str.extract('(\d+)').fillna(0).astype(int)
df['power_nm'] = power[1].str.split('Nm', n =1, expand = True)[0].str.extract('(\d+)')
df['power_lb_ft'] = power[1].str.split('Nm', n = 1, expand = True)[1].str.split(' ', n = 1, expand = True)[0].str.extract('(\d+)')
df.drop(columns = ['How much power?'], inplace = True)


# df['Body type ']
# df.groupby('Body type ').count()
# Need to split this column into cabriolet, combi, coupe, crossover, fastback, grant tourer, hatchback, liftback, mpg, minivan, offroad, pickup, roadster, suv, sedan

# df['Drive wheel ']
df.groupby('Drive wheel ').count()
conditions = [
 (df['Drive wheel '] == 'All wheel drive (4x4) '),
 (df['Drive wheel '] == 'Rear wheel drive '),
 (df['Drive wheel '] == 'Front wheel drive ')
]
choices = ['AWD', 'RWD', 'FWD']
df['drive'] = np.select(conditions, choices)
df.drop(columns = ['Drive wheel '])

# df['Compression ratio '][1]
type(df['Compression ratio '][1])
df['compression'] = df['Compression ratio ']
df.drop(columns = ['Drive wheel '])

df['bore_mm'] = df['Cylinder Bore '].str.split(' mm', n = 1, expand = True)[0]
df.drop(columns = ['Cylinder Bore '])

#
# df['Engine displacement ']
df['displacement_cm3'] = df['Engine displacement '].str.split('\n', n = 1, expand = True)[0].str.split(' ', n = 1, expand = True)[0]
df['displacement_in'] = df['Engine displacement '].str.split('\n', n = 1, expand = True)[1].str.split(' cu.', n = 1, expand = True)[0]
df.drop(columns = ['Engine displacement '])

# df['Fuel consumption (economy) - combined ']
df['consumption_l100'] = df['Fuel consumption (economy) - combined '].str.split(' l/100 km\r\n\t\t\t\t\t\t', n = 1, expand = True)[0]
df['consumption_mpg'] = df['Fuel consumption (economy) - combined '].str.split(' l/100 km\r\n\t\t\t\t\t\t', n = 1, expand = True)[1].str.split(' US mpg', n = 1, expand = True)[0]
df.drop(columns = ['Fuel consumption (economy) - combined '])

# df['How fast is?']
df['topspeed_kmh'] = df['How fast is?'].str.split('km/h', n = 1, expand = True)[0].str.extract('(\d+)')
# df['topspeed_kmh'] = (df['topspeed_kmh'])
df['0-60_mph'] = df['How fast is?'].str.split('km/h', n = 1, expand = True)[1].str.split('km/h', n = 1, expand = True)[1].str.split(' ', n = 1, expand = True)[0]
df['0-60_mph'] = df['0-60_mph'].fillna(0).astype(float)
df.drop(columns = ['How fast is?'])

# type(df['topspeed_kmh'][0])

# df['How many cylinders?']
df['cylinders'] = df['How many cylinders?'].str.split(', ', n = 1, expand = True)[0]
df['cylinder_orientation'] = df['How many cylinders?'].str.split(', ', n = 1, expand = True)[1]
df.drop(columns = ['How many cylinders?'])

# df['How many gears?']
df['gears'] = df['How many gears?'].fillna(0.0).astype(int)
df.drop(columns = ['How many gears?'])


# df['Maximum speed ']
df['max_speed_mph'] = df['Maximum speed '].str.split('km/h\r\n\t\t\t\t\t\t', n = 1, expand = True)[1].str.extract('(\d+)')[0].fillna(0.0).astype(int)
df.drop(columns = ['Maximum speed '])



# df['Number of valves per cylinder ']
df['valves_per_cylinder'] = df['Number of valves per cylinder '].fillna(0.0).astype(int)
df.drop(columns = ['Number of valves per cylinder '])

# df['Piston Stroke ']
df['stroke_mm'] = df['Piston Stroke '].str.split(' ', n = 1, expand = True)[0].astype(float)
df.drop(columns = ['Piston Stroke '])

df['peak_hp'] = df['Power '].str.split(' ', n = 1, expand = True)[0].str.extract('(\d+)').fillna(0).astype(int)
df['peak_hp_rpm'] = df['Power '].str.split('@ ', n = 1, expand = True)[1].str.extract('(\d+)')
df.drop(columns = ['Power '])

# df['What is the gross weigh?']
df['weight_lbs'] = df['What is the gross weigh?'].str.split('  kg', n = 1, expand = True)[1].str.extract('(\d+)')[0].fillna(0).astype(int)
df.drop(columns = ['What is the gross weigh?'])


# Provides peak torque @ rpm - Nm and lb-ft
# df['Torque ']

# None of these columns are of any use
# df['Acceleration 0 - 100 km/h (CNG) ']
# df['Acceleration 0 - 100 km/h (LPG) ']
# df['Acceleration 0 - 200 km/h ']
# df['Acceleration 0 - 300 km/h ']
# df['Drag coefficient (Cd) ']
# df['System power ']
# df['System torque ']

# This column doesn't contain any data. This can be calculated using bore and stroke
# df['Maximum engine speed ']

# Engine information
# df['Modification (Engine) ']

# Use this to determine manual vs. automatic transmission # of gears
# df['Number of Gears (automatic transmission) ']
# df['Number of Gears (manual transmission) ']

# Compare to "how many cylinders" to see if there is any difference
# df['Number of cylinders ']

# Compare to orientation to see if it is any different
# df['Position of engine ']

# Useful?
# df['Tires size']
# df['Drag coefficient (Cd) ']

# df2 = df.dropna
# len(df2)
#
# df2 = pd.DataFrame(df['Power '],
#  df['What is the gross weigh?'],
#  df[1:])
#
# type(df2)

# Identifier columns
# list(df.columns)
df['brand'] = df['Brand']
df['model'] = df['Model ']
# df['model_engine'] = df['Model Engine ']
# df['description']
# df['title']
df['model_engine'] = df['Modification (Engine) '].str.split(' \(', n = 1, expand = True)[0]
df['production_start'] = df['Start of production '].str.split(' ', n = 1, expand = True)[0][0]
df['production_end'] = df['End of production '].str.split(' ', n = 1, expand = True)[0][0]
# df[['brand', 'model', 'model_engine', 'production_start', 'production_end']]

# Metric columns
# df[['drive', 'compression', 'bore_mm', 'displacement_cm3', 'displacement_in', 'consumption_l100', 'consumption_mpg',
#     'topspeed_kmh', '0-60_mph', 'cylinders', 'cylinder_orientation', 'gears', 'max_speed_mph', 'valves_per_cylinder',
#     'stroke_mm', 'peak_hp', 'peak_hp_rpm', 'weight_lbs']]


df['power_to_weight'] = df['power_hp'] / df['weight_lbs']



# Fitting a model to power to weight / 0-60
fig = plt.figure()

plt.scatter('power_to_weight', '0-60_mph', data = df, alpha = 0.1, c = 'blue')

plt.ylabel('0-60 mph (seconds)')
plt.xlabel('Power to weight ratio (hp/lbs)')

df_reg = df[['0-60_mph', 'power_to_weight']]
df_reg1 = df_reg.replace([np.inf, -np.inf], np.nan).dropna()
# df_reg2 = df_reg[df_reg['0-60_mph'] > 0]
df_reg3 = df_reg1[(df_reg1 > 0)].dropna()

yData = df_reg3['0-60_mph']
xData = df_reg3['power_to_weight']

params = np.array([1,1])

def funcinv(x, a, b):
    return b+ a/x

# def residuals(params, x, data):
#     a, b = params
#     func_eval = funcinv(x, a, b)
#     return(data - func_eval)
#
# res = least_squares(residuals, params, args = (xData,yData))

fittedParameters, pcov = curve_fit(funcinv, xData, yData)

res2 = curve_fit(funcinv, xData, yData, params) # the params arg is not necessary here, not sure why it is included

print(res2)

def ModelAndScatterPlot(graphWidth, graphHeight):
    f = plt.figure(figsize=(graphWidth/100.0, graphHeight/100.0), dpi=100)
    axes = f.add_subplot(111)

    # first the raw data as a scatter plot
    axes.plot(xData, yData,  'D')

    # create data for the fitted equation plot
    xModel = np.linspace(min(xData), max(xData)) # creates an array from the first arg to the second, default num = 50
    yModel = funcinv(xModel, *fittedParameters)

    # now the model as a line plot
    axes.plot(xModel, yModel)

    axes.set_xlabel('Power to weight (hp to lbs)') # X axis data label
    axes.set_ylabel('0-60 mph') # Y axis data label

    plt.show()
    # plt.close('all') # clean up after using pyplot

graphWidth = 800
graphHeight = 600
ModelAndScatterPlot(graphWidth, graphHeight)