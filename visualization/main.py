import datetime as dt
import random

from bokeh.plotting import figure, output_file, curdoc
from bokeh.layouts import layout, column
from bokeh.models import ColumnDataSource, Legend
from bokeh.models.widgets import Panel, Tabs, DateRangeSlider, Div, RadioButtonGroup

import intake

def repeatImage(image, n):
    images = ""
    for i in range(int(n)):
        images+='<img src="/visualization/static/images/{}.svg" height="50px" margin="5px"/> '.format(image)
    return images

learnMore = "You can learn more about how much citizens of Knoxville have recycled on this page!"
# FACTS
FACTS = [
#         '''<p class=fact>Last year, people in Knoxville produced the weight of over {} {} in non-recyclable trash! <br /> <br /> {} <br /> <br /> <br /> {}</p>'''.format(94, "Sunspheres", repeatImage("Sunspheres", 94), learnMore),
#         '''<p class=fact>East Knoxville Recycling Center collected the weight of over {} {} in recyclables! <br /> <br /> {} </p>'''.format(3.5, "Space Shuttles", repeatImage("Space Shuttles", 3.5), learnMore),
#         '''<p class=fact>South Knoxville Recycling Center collected the weight of over {} {} in recyclables! <br /> <br /> {} </p>'''.format(5.6, "Space Shuttles", repeatImage("Space Shuttles", 5.6, learnMore),
#         '''<p class=fact>North Knoxville Recycling Center collected the weight of over {} {} in recyclables! <br /> <br /> {} </p>'''.format(3.6, "Space Shuttles", repeatImage("Space Shuttles", 3.6), learnMore),
         '''<p class=fact>West Knoxville Recycling Center collected the weight of over {} {} in recyclables! <br /> <br /> {} </p>'''.format(14.8, "Space Shuttles", repeatImage("Space Shuttles", 14.8), learnMore),
#         '''<p class=fact>Downtown Knoxville Recycling Center collected the weight of over {} {} in recyclables! <br /> <br /> {} </p>'''.format(3.1, "Space Shuttles", repeatImage("Space Shuttles", 3.1), learnMore),
#         '''<p class=fact>Curb-Side Pickup collected the weight of over {} {} in recyclables! <br /> <br /> {} </p>'''.format(56.9, "Space Shuttles", repeatImage("Space Shuttles", 56.9), learnMore),
#         '''<p class=fact></p>''',
#         '''<p class=fact></p>''',
#    '''An <h1>elephant</h1> does? The answer is''',
#    '''What is the <img src="/visualization/static/images/Humans.svg" height="20px"/> capital? Yeah im not <b>sure</b>''',
]

# UNIT
UNIT_CONVERSION = {
    "Pounds": 1.0,
    "Humans": 1 / 170.0,
    "Tons": 1/2000,
    "Metric Tons": 1 / 2204.62,
    "Elephants": 1 / 23500,
    "School Buses": 1 / 23500,
    "Space Shuttles": 1 / 150000,
    "Sunspheres": 1 / (600*2204.62),
}
UNIT_CONVERSION_MAP = list(UNIT_CONVERSION.keys())


# THEME
DISCRETE_COLORS =  ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00", "#ffff33", "#a65628", "#f781bf", "#999999"]


# GLOBALS (TO MODIFY PLOTS/DIVS)
_state = {
    'date_range': (
        dt.datetime(year=2018, month=1, day=1),
        dt.datetime(year=2018, month=12, day=1)),
    'units': 0,
}

ELEMENT_CALLBACKS = []


def fetch_bokeh_sources(catalog_filename):
    """Define Bokeh Data Sources

    """
    catalog = intake.open_catalog(catalog_filename)
    dataframes = {
        'mulch': catalog.solid_waste_mulch.read().pivot(index='Month', columns='Type')
    }
    sources = {
        'mulch': ColumnDataSource(dataframes['mulch']),
    }

    comm_df = catalog.solid_waste_commodity_recycling.read()
    comm_df = comm_df.rename(columns={
        "Magnolia & Alice": "East Knoxville Recycling Center",
        "225 Moody": "South Knoxville Recycling Center",
        "4440 Western Av.": "North Knoxville Recycling Center",
        "341 Parkvillage": "West Knoxville Recycling Center",
        "227 Willow Av.": "Downtown Knoxville Recycling Center",
        "Curbside City-Wide": "Curbside City-Wide Pickup",
        "Downtown": "Downtown Pickup",
        "KPD": "KPD", # what is this?
        "Recycling Trailer": "Recycling Trailer"
    })
    for material in {'Glass', 'Cardboard', 'Mixed Paper', 'Plastics ("Commingled")'}:
        dataframes[f'commodity_{material}'] = comm_df[comm_df.Type == material].fillna(0).pivot(index='Month', columns='Type')
        sources[f'commodity_{material}'] = ColumnDataSource(dataframes[f'commodity_{material}'])

    return {'dataframes': dataframes, 'sources': sources}


def source_filters(sources):
    def _handle_state_filter():
        for fullname in sources['dataframes']:
            df = sources['dataframes'][fullname]
            df = df[(df.index >= _state['date_range'][0]) & (df.index <= _state['date_range'][1])]
            units = UNIT_CONVERSION_MAP[_state['units']]
            df = df * UNIT_CONVERSION[units]
            sources['sources'][fullname].data = ColumnDataSource(df).data

        for callback in ELEMENT_CALLBACKS:
            callback(sources=sources, **_state)

    def _date_slider_handler(attr, old, new):
        start_time, end_time = new
        start_date = dt.datetime.fromtimestamp(start_time / 1000)
        end_date = dt.datetime.fromtimestamp(end_time / 1000)
        _state['date_range'] = (start_date, end_date)
        _handle_state_filter()

    start_date = dt.datetime(year=2018, month=12, day=1)
    end_date = dt.datetime(year=2018, month=12, day=1)
    date_slider = DateRangeSlider(start=_state['date_range'][0], end=_state['date_range'][1], value=_state['date_range'], step=1, title="Date Range", height=100)
    date_slider.on_change('value', _date_slider_handler)

    def _radio_button_group_handler(attr, old, new):
        _state['units'] = int(new)
        _handle_state_filter()

    radio_button_group = RadioButtonGroup(labels=UNIT_CONVERSION_MAP, active=0, width=700, height=100)

    radio_button_group.on_change('active', _radio_button_group_handler)

    div_button_group_selection = Div(text=f'<img src="/visualization/static/images/{UNIT_CONVERSION_MAP[_state["units"]]}.svg" height="100px"/>', height=100)

    def _update_div_button_group(**kwargs):
        units = UNIT_CONVERSION_MAP[kwargs['units']]
        div_button_group_selection.text = f'<img src="/visualization/static/images/{units}.svg" height="100px"/>'
    ELEMENT_CALLBACKS.append(_update_div_button_group)

    return [date_slider, radio_button_group, div_button_group_selection]


def commodity_plot(sources, material):
    comm_source = sources['sources'][material]
    df = comm_source.to_df()

    color_iter = iter(DISCRETE_COLORS)

    plot = figure(plot_width=800, plot_height=400, title=f"Weight of {material.split('_')[-1]}",
                  x_axis_type="datetime")

    legend_items = []
    for column_name in comm_source.column_names[2:-1]:
        group_name, var_name = column_name.split('_')
        current_line = plot.line(x='Month', y=column_name, source=comm_source, color=next(color_iter))
        if sum(df[column_name]) > 0:
            legend_items.append((group_name, [current_line]))

    legend = Legend(items=legend_items)
    plot.add_layout(legend, 'right')
    plot.legend.location = "bottom_center"
    plot.legend.click_policy = "mute"
    plot.xaxis.axis_label = "Month"
    plot.yaxis.axis_label = "Pounds"
    plot.toolbar.logo = None
    plot.toolbar_location = None

    def _update_plot_yaxis(**kwargs):
        plot.yaxis.axis_label = UNIT_CONVERSION_MAP[kwargs['units']]

    ELEMENT_CALLBACKS.append(_update_plot_yaxis)
    return plot


def mulch_line_plot(sources):
    mulch_source = sources['sources']['mulch']

    color_iter = iter(DISCRETE_COLORS)

    plot = figure(plot_width=1200, plot_height=400,
                  title="Tons of Leaves/Brush by Month", x_axis_type="datetime")

    plot.line(x='Month', y='Mulch_Brush', source=mulch_source,
              legend='Brush', color=next(color_iter))
    plot.line(x='Month', y='Mulch_Leaves', source=mulch_source,
              legend='Leaves', color=next(color_iter))

    plot.xaxis.axis_label = "Month"
    plot.yaxis.axis_label = "Pounds"
    plot.toolbar.logo = None
    plot.toolbar_location = None

    def _update_plot_yaxis(**kwargs):
        plot.yaxis.axis_label = UNIT_CONVERSION_MAP[kwargs['units']]

    ELEMENT_CALLBACKS.append(_update_plot_yaxis)
    return plot


def mulch_summary_data(sources):
    df = sources['sources']['mulch'].to_df()
    message = '''
      <h2>Totals</h2>
      <h3>Brush: {bunch_sum:6.4f} [{units}]</h3>
      <h3>Leaves: {leaves_sum:6.4f} [{units}]</h3>
    '''
    mulch_summary = Div(text=message.format(
        units=UNIT_CONVERSION_MAP[0],
        bunch_sum=df["Mulch_Brush"].sum(),
        leaves_sum=df["Mulch_Leaves"].sum(),
        width=400, height=100))

    def _update_mulch_summary(**kwargs):
        df = kwargs['sources']['sources']['mulch'].to_df()
        mulch_summary.text = message.format(
            units=UNIT_CONVERSION_MAP[kwargs['units']],
            bunch_sum=df["Mulch_Brush"].sum(),
            leaves_sum=df["Mulch_Leaves"].sum())

    ELEMENT_CALLBACKS.append(_update_mulch_summary)
    return mulch_summary


def main():
    catalog_filename = 'catalog.yml'
    sources = fetch_bokeh_sources(catalog_filename)

    output_file('visualization.html')

    main_panel = Panel(child=Div(text=open('visualization/static/main.html').read().replace('+++random_fact+++', random.choice(FACTS))),
                       title='Main Page')

    mulch_panel = Panel(child=layout([
        source_filters(sources),
        [mulch_line_plot(sources), mulch_summary_data(sources)]
    ]), title="Compostable")

    commodity_recycling_panel = Panel(child=layout([
        source_filters(sources),
        [commodity_plot(sources, 'commodity_Glass'), commodity_plot(sources, 'commodity_Cardboard')],
        [commodity_plot(sources, 'commodity_Mixed Paper'), commodity_plot(sources, 'commodity_Plastics ("Commingled")')],
    ]), title="Commodity Recycling")

    how_to_recycle_panel = Panel(child=Div(text=open('visualization/static/recycle.html').read()),
                                 title='What can I Recycle?')


    return layout([
        Div(text=open('visualization/static/header.html').read()),
        Tabs(tabs=[
            main_panel,
            mulch_panel,
            commodity_recycling_panel,
            how_to_recycle_panel,
        ], width=1000)
    ])


curdoc().title = 'WasteKnox -- the Final Frontier of Recycling in Knoxville'
curdoc().add_root(main())
