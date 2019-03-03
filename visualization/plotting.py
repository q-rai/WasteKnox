
def plotAtLocation(df, location):
    baseCols = ["Type", "Month"]
    locationDict = {"Magnolia & Alice": "East Knoxville Recycling Center", 
                    "225 Moody": "South Knoxville Recycling Center",
                    "4440 Western Av.": "North Knoxville Recycling Center",
                    "341 Parkvillage": "West Knoxville Recycling Center",
                    "227 Willow Av.": "Downtown Knoxville Recycling Center",
                    "Curbside City-Wide": "Curbside City-Wide Pickup",
                    "Downtown": "Downtown Pickup",
                    "KPD": "KPD", # what is this?
                    "Recycling Trailer": "Recycling Trailer"}
    cols = baseCols+[location]
    locationDF = df[cols]
    locationDF.fillna(0)
    locationDF = locationDF.pivot(index='Month', columns='Type')
    source = ColumnDataSource(locationDF)
    colNames = source.column_names
    if location in locationDict:
        locationName = locationDict[location]
    else:
        locationName = location
        print(location, "not in dict")

    plot = figure(plot_width=800, plot_height=400, 
                  title="Weight of Waste: {}".format(locationName), 
                  x_axis_type="datetime")
    legendItems = []
    for i, colName in enumerate(colNames[1:]):
        groupname, varname = colName.split("_")
        currentLine = plot.line(x='Month', y=colName, source=source, color=colors[i], line_width=2)
        plot.xaxis.axis_label = "Month"
        plot.yaxis.axis_label = unit
        plot.legend.location = "bottom_center"
        plot.legend.click_policy = "mute"
        plot.legend.orientation = "horizontal"
        if sum(locationDF[groupname][varname]) > 0:
            legendItems.append((varname, [currentLine]))
    legend = Legend(items=legendItems)
    plot.add_layout(legend, 'right')
    show(plot)

def plotByVariable(variable):
#     cols = baseCols+[variable]
    locationDF = df[df["Type"] == variable]
    locationDF.fillna(0)
    print(locationDF)
    locationDF = locationDF.pivot(index='Month', columns=variable)
    recyclingTypes = list(locationDF.columns)
    source = ColumnDataSource(locationDF)
    colNames = source.column_names

    
