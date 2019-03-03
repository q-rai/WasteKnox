# Getting Started

# Waste and Resources

Our client stated that the goal was to have report materials that can
make for a more educated "garbage geek culture". She would like the
visualizations to update

# Technology

The goal of this project from a technology perspective was to show the
power of the open source python ecosystem to address the data
cataloging, calculation of key features, and interactive visualization
needs of our client. This pythonic approach is equally applicable in
other contexts such as banks where the data resources are located in
seperate databases and complex bussiness logic is required to produce
interactive visualizations.

## Data Processing and Data Catalog (Intake)

The waste and resources department has their data in one large excel 
file containing multiple sheets with several matrices each for different 
types of waste. We processed this excel sheet using pandas, saving the 
data out into one csv file per matrix. A data catalog was used to unify 
the data as a single resource and expose the data as a dataframe. Allowing 
each datasource to be manipulated in the same way. Additionally it allow
the data to update with each new month of data automatically.

```
import intake

catalog = intake.open_catalog('catalog.yml')
catalog.solid_waste_commodity_recycling
```

![Intake Design](https://github.com/q-rai/WasteKnox/raw/master/visualization/static/images/intake.png)

## Dashboard Visualization (Bokeh + LeafletJS)

Our client wanted to have accessible infographics about the current
waste month by month, plotting, and resources to create a more
educated "garbage geek culture". We thought a dynamic single page
dashboard application would address the needs of our customer. Uses a
bokeh python server running in background to provide richer
interactive experience.

![Bokeh Server](https://github.com/q-rai/WasteKnox/raw/master/visualization/static/images/bokeh_server.png)

### Filters

visitors can apply filters which update all graphs:
 - date range of data
 - change units that all plots are being calculated with

![Filters](https://github.com/q-rai/WasteKnox/raw/master/visualization/static/images/filters-demo.png)

### Dynamic "Did you know questions?"

Did you know questions python generated, randomly selected, and update
with current monthly data.

![Did you know?](https://github.com/q-rai/WasteKnox/raw/master/visualization/static/images/didyouknow.png)

### Dynamic Text Fields

Autoupdating text fields within dashboard that are calculated from
data.


# Development

1. Install anaconda version doesn't matter

2. Import anaconda environment: `conda env create -n hackathon -f hackathon.yml`

3. Switch to the new environment: `source activate hackathon`

4. Add the environment to your jupyter: `python -m ipykernel install --user --name hackathon --display-name "Hackathon"`. 

# Deployment

```
bokeh serve --show visualization
```

